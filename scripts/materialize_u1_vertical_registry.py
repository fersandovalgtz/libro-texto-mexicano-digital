#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, sqlite3
from pathlib import Path

MATERIALIZATION_VERSION='LTMD_U1_VERTICAL_MATERIALIZATION_0.1'
BUILDER_VERSION='LTMD_U1_VERTICAL_MATERIALIZER_0.1'
INDEX_VERSION='LTMD_U1_UNIVERSAL_INDEX_0.1'
REUSE_VERSION='LTMD_U1_REUSE_SIMILARITY_0.1'
REGISTRY_VERSION='LTMD_U1_VERTICAL_REGISTRY_0.1'
DIMENSIONS={'generation':'catalog_generation','grade_code':'grade_code','wave':'wave'}
SHA_RE=re.compile(r'^[a-f0-9]{64}$')

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def verify(path:Path,expected:str|None,label:str)->str:
    if not path.is_file(): raise RuntimeError(f'{label} unavailable')
    actual=sha256_file(path)
    if expected:
        e=expected.strip().lower()
        if not SHA_RE.fullmatch(e): raise RuntimeError(f'invalid expected {label} sha')
        if actual!=e: raise RuntimeError(f'{label} SHA mismatch')
    return actual

def decode_meta(c,table):
    out={}
    for k,v in c.execute(f'SELECT key,value FROM {table}'):
        try: out[k]=json.loads(v)
        except Exception: out[k]=v
    return out

def validate_index(c):
    tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
    if not {'pages','pages_fts','index_meta'}<=tables: raise RuntimeError('invalid universal index')
    if decode_meta(c,'index_meta').get('builder_version')!=INDEX_VERSION: raise RuntimeError('unsupported universal index')

def validate_reuse(c):
    req={'meta','exact_source_groups','exact_source_members','exact_text_groups','exact_text_members','similarity_candidates'}
    tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not req<=tables: raise RuntimeError('invalid reuse artifact')
    if decode_meta(c,'meta').get('artifact_version')!=REUSE_VERSION: raise RuntimeError('unsupported reuse artifact')

def load_registry(path):
    d=json.loads(path.read_text(encoding='utf-8'))
    if d.get('registry_version')!=REGISTRY_VERSION or d.get('frozen_before_materialization') is not True: raise RuntimeError('registry is not frozen 0.1')
    if d.get('result_state')!='exploratory_signal': raise RuntimeError('registry state mismatch')
    return d

def count_scope(c,dimension=None,value=None):
    if dimension is None:
        row=c.execute('SELECT COUNT(*),COUNT(DISTINCT canonical_viewer_key) FROM pages').fetchone()
    else:
        col=DIMENSIONS[dimension]
        row=c.execute(f'SELECT COUNT(*),COUNT(DISTINCT canonical_viewer_key) FROM pages WHERE {col}=?',(value,)).fetchone()
    return int(row[0]),int(row[1])

def hit_rowids(c,expr):
    try:
        return [int(r[0]) for r in c.execute("SELECT p.id FROM pages_fts f JOIN pages p ON p.id=f.rowid WHERE pages_fts MATCH ? ORDER BY p.id",(expr,))]
    except sqlite3.OperationalError as e:
        raise RuntimeError(f'invalid FTS expression: {expr}') from e

def metrics(c,expr):
    try:
        row=c.execute("SELECT COUNT(*),COUNT(DISTINCT p.canonical_viewer_key) FROM pages_fts f JOIN pages p ON p.id=f.rowid WHERE pages_fts MATCH ?",(expr,)).fetchone()
    except sqlite3.OperationalError as e:
        raise RuntimeError(f'invalid FTS expression: {expr}') from e
    corpus_pages,corpus_books=count_scope(c)
    pages,books=int(row[0]),int(row[1])
    return {'candidate_pages':pages,'candidate_books':books,'corpus_pages_in_scope':corpus_pages,'corpus_books_in_scope':corpus_books,'candidate_pages_per_1000':pages/corpus_pages*1000 if corpus_pages else None}

def breakdown(c,expr,dim):
    col=DIMENSIONS[dim]
    scopes={r[0]:(int(r[1]),int(r[2])) for r in c.execute(f'SELECT {col},COUNT(*),COUNT(DISTINCT canonical_viewer_key) FROM pages WHERE {col} IS NOT NULL GROUP BY {col} ORDER BY {col}')}
    try:
        hits={r[0]:(int(r[1]),int(r[2])) for r in c.execute(f'SELECT p.{col},COUNT(*),COUNT(DISTINCT p.canonical_viewer_key) FROM pages_fts f JOIN pages p ON p.id=f.rowid WHERE pages_fts MATCH ? AND p.{col} IS NOT NULL GROUP BY p.{col}',(expr,))}
    except sqlite3.OperationalError as e:
        raise RuntimeError(f'invalid FTS expression: {expr}') from e
    rows=[]
    for value,(cp,cb) in scopes.items():
        hp,hb=hits.get(value,(0,0))
        rows.append({'dimension':dim,'value':str(value),'result_state':'exploratory_signal','metrics':{'candidate_pages':hp,'candidate_books':hb,'corpus_pages_in_scope':cp,'corpus_books_in_scope':cb,'candidate_pages_per_1000':hp/cp*1000 if cp else None}})
    return rows

def empty_context():
    return {'context_version':'LTMD_VERTICAL_REUSE_CONTEXT_0.1','result_state':'exploratory_signal','metrics':{
        'candidate_pages':0,'mapped_candidate_pages':0,'unmapped_candidate_pages':0,
        'candidate_pages_with_exact_source_cross_object_reuse':0,'candidate_pages_with_exact_source_cross_generation_reuse':0,
        'candidate_pages_with_exact_text_cross_object_reuse':0,'candidate_pages_with_exact_text_cross_generation_reuse':0,
        'candidate_pages_with_similarity_signal':0,'candidate_pages_with_near_exact_signal':0,
        'candidate_pages_with_cross_generation_similarity_signal':0,'candidate_pages_with_any_reuse_similarity_signal':0,
        'candidate_pages_with_cross_generation_reuse_similarity_signal':0,'candidate_pages_without_reuse_similarity_signal':0,
        'internal_similarity_pairs':0,'internal_near_exact_pairs':0,'share_candidate_pages_with_any_reuse_similarity_signal':None},
        'warnings':['Reuse/similarity context is computational evidence and does not create aliases or establish semantic equivalence.','Counts qualify lexical candidates; they do not validate or invalidate the vertical.']}

def reuse_context(index,reuse,rowids):
    n=len(rowids)
    if not n: return empty_context()
    reuse.execute('DROP TABLE IF EXISTS temp.vertical_candidates')
    reuse.execute('CREATE TEMP TABLE vertical_candidates(page_rowid INTEGER PRIMARY KEY) WITHOUT ROWID')
    reuse.executemany('INSERT INTO vertical_candidates VALUES(?)',((x,) for x in rowids))
    def count_member(members,groups,col):
        return int(reuse.execute(f'SELECT COUNT(DISTINCT m.page_rowid) FROM {members} m JOIN vertical_candidates v ON v.page_rowid=m.page_rowid JOIN {groups} g ON g.group_id=m.group_id WHERE g.{col}=1').fetchone()[0])
    es_obj=count_member('exact_source_members','exact_source_groups','cross_object')
    es_gen=count_member('exact_source_members','exact_source_groups','cross_generation')
    et_obj=count_member('exact_text_members','exact_text_groups','cross_object')
    et_gen=count_member('exact_text_members','exact_text_groups','cross_generation')
    candidate=set(rowids)
    q=','.join('?'*n)
    gen={int(a):b for a,b in index.execute(f'SELECT id,catalog_generation FROM pages WHERE id IN ({q})',rowids)}
    sim_rows=reuse.execute('SELECT s.page_a,s.page_b,s.tier FROM similarity_candidates s WHERE EXISTS(SELECT 1 FROM vertical_candidates v WHERE v.page_rowid=s.page_a) OR EXISTS(SELECT 1 FROM vertical_candidates v WHERE v.page_rowid=s.page_b)').fetchall()
    counterparts={int(p) for a,b,_ in sim_rows for p in (a,b) if int(p) not in gen}
    if counterparts:
        vals=list(counterparts);q2=','.join('?'*len(vals));gen.update({int(a):b for a,b in index.execute(f'SELECT id,catalog_generation FROM pages WHERE id IN ({q2})',vals)})
    sim_pages=set();near=set();crosssim=set();internal=0;internal_near=0
    for a,b,tier in sim_rows:
        a=int(a);b=int(b);touched={p for p in (a,b) if p in candidate};sim_pages.update(touched)
        if tier=='near_exact_candidate': near.update(touched)
        if gen.get(a)!=gen.get(b): crosssim.update(touched)
        if a in candidate and b in candidate:
            internal+=1;internal_near+=int(tier=='near_exact_candidate')
    any_pages=set(sim_pages);cross_any=set(crosssim)
    for members,groups,col,target in [
        ('exact_source_members','exact_source_groups','cross_object',any_pages),('exact_text_members','exact_text_groups','cross_object',any_pages),
        ('exact_source_members','exact_source_groups','cross_generation',cross_any),('exact_text_members','exact_text_groups','cross_generation',cross_any)]:
        target.update(int(r[0]) for r in reuse.execute(f'SELECT DISTINCT m.page_rowid FROM {members} m JOIN vertical_candidates v ON v.page_rowid=m.page_rowid JOIN {groups} g ON g.group_id=m.group_id WHERE g.{col}=1'))
    m={'candidate_pages':n,'mapped_candidate_pages':n,'unmapped_candidate_pages':0,
       'candidate_pages_with_exact_source_cross_object_reuse':es_obj,'candidate_pages_with_exact_source_cross_generation_reuse':es_gen,
       'candidate_pages_with_exact_text_cross_object_reuse':et_obj,'candidate_pages_with_exact_text_cross_generation_reuse':et_gen,
       'candidate_pages_with_similarity_signal':len(sim_pages),'candidate_pages_with_near_exact_signal':len(near),
       'candidate_pages_with_cross_generation_similarity_signal':len(crosssim),'candidate_pages_with_any_reuse_similarity_signal':len(any_pages),
       'candidate_pages_with_cross_generation_reuse_similarity_signal':len(cross_any),'candidate_pages_without_reuse_similarity_signal':n-len(any_pages),
       'internal_similarity_pairs':internal,'internal_near_exact_pairs':internal_near,
       'share_candidate_pages_with_any_reuse_similarity_signal':len(any_pages)/n}
    return {'context_version':'LTMD_VERTICAL_REUSE_CONTEXT_0.1','result_state':'exploratory_signal','metrics':m,
            'warnings':['Reuse/similarity context is computational evidence and does not create aliases or establish semantic equivalence.','Counts qualify lexical candidates; they do not validate or invalidate the vertical.']}

def materialize(registry_path,index_path,reuse_path,expected_index=None,expected_reuse=None):
    registry_sha=sha256_file(registry_path);index_sha=verify(index_path,expected_index,'index');reuse_sha=verify(reuse_path,expected_reuse,'reuse')
    reg=load_registry(registry_path)
    index=sqlite3.connect(f'file:{index_path}?mode=ro',uri=True);reuse=sqlite3.connect(f'file:{reuse_path}?mode=ro',uri=True)
    try:
        validate_index(index);validate_reuse(reuse)
        total_pages,total_books=count_scope(index)
        verticals=[]
        for spec in reg['verticals']:
            overall=metrics(index,spec['union_expression'])
            ids=hit_rowids(index,spec['union_expression'])
            breakdowns={dim:breakdown(index,spec['union_expression'],dim) for dim in reg['dimensions']}
            probes=[]
            for p in spec['probes']:
                probes.append({'probe_id':p['probe_id'],'label_es':p['label_es'],'fts5_expression':p['fts5_expression'],'result_state':'exploratory_signal','metrics':metrics(index,p['fts5_expression'])})
            verticals.append({'vertical_id':spec['vertical_id'],'label_es':spec['label_es'],'status':'materialized_exploratory',
                'union_expression':spec['union_expression'],'interpretation_boundary':spec['interpretation_boundary'],'result_state':'exploratory_signal',
                'metrics':overall,'breakdowns':breakdowns,'probes':probes,'reuse_context':reuse_context(index,reuse,ids),
                'warnings':['FTS5 matches are lexical/OCR-derived exploratory signals, not validated semantic classifications.','Zero hits do not demonstrate historical absence.']})
        return {'materialization_version':MATERIALIZATION_VERSION,'builder_version':BUILDER_VERSION,'registry_version':REGISTRY_VERSION,
            'result_state':'exploratory_signal','corpus':{'pages':total_pages,'canonical_objects':total_books},
            'provenance':{'registry_sha256':registry_sha,'universal_index_sha256':index_sha,'reuse_similarity_sha256':reuse_sha,'human_validation_complete':False},
            'scientific_state':{'text_verified':False,'semantic_ready':False,'aliases_created':False},
            'privacy':{'page_identifiers_emitted':False,'object_identifiers_emitted':False,'pair_identifiers_emitted':False,'ocr_text_emitted':False,'source_hash_values_emitted':False},
            'verticals':verticals}
    finally:
        index.close();reuse.close()

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--registry',required=True);p.add_argument('--index',required=True);p.add_argument('--reuse',required=True);p.add_argument('--expected-index-sha256');p.add_argument('--expected-reuse-sha256');p.add_argument('--output',required=True);a=p.parse_args(argv)
    out=materialize(Path(a.registry),Path(a.index),Path(a.reuse),a.expected_index_sha256,a.expected_reuse_sha256)
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return 0
if __name__=='__main__': raise SystemExit(main())
