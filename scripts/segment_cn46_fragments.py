#!/usr/bin/env python3
"""Book-aware, hash-verified FRAGSEG for the CN4/CN6 expansion.

Reuses the pilot segmentation semantics but fixes source identity: source URL and
SHA-256 come from the page manifest, and selection is by `book_id`, not by one
hard-coded viewer per catalog generation. OCR text exists only in temporary files.
"""
from __future__ import annotations
import argparse,csv,hashlib,re,subprocess,tempfile,time,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

STRUCTURE=Path('data/expansion/cn46_page_structure.csv')
MANIFEST=Path('data/expansion/cn46_page_manifest.csv')
VERSION='FRAGSEG_CN46_0.1'
ELIGIBLE={'textual','mixed_text_image'}
UA='LibroTextoMexicanoDigital/0.1 CN46 FRAGSEG'

IMPERATIVES=['observa','describe','escribe','explica','compara','clasifica','mide','realiza','investiga','discute','comenta','elabora','construye','dibuja','resuelve','contesta','responde','identifica','señala','anota','registra','lee','analiza','calcula','reúne','busca','consulta','organiza','completa','marca','subraya','recorta','pega','coloca','haz','forma','trabaja','elige','decide','propón','propone','predice','infiere']
QUESTION_START=['qué','que','cómo','como','cuál','cual','cuáles','cuales','por qué','por que','dónde','donde','cuándo','cuando','quién','quien']
MATERIAL_WORDS=['materiales','necesitas','vas a necesitar','material']
PROJECT_WORDS=['proyecto','proyectos']
EXPERIMENT_WORDS=['experimento','experimenta','experimentación','procedimiento','hipótesis']
ASSESS_WORDS=['evaluación','autoevaluación','qué aprendí','lo que aprendí','evalúa']
ACTIVITY_WORDS=['actividad','en equipo','trabaja en equipo','por equipos','con tus compañeros']

def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).strip()
def low(s):return norm(s).casefold()
def token_count(s):return len(re.findall(r'\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b',s,flags=re.UNICODE))
def signal_count(text,terms):
    t=low(text);return sum(t.count(term.casefold()) for term in terms)

def candidate_type(text):
    t=low(text);q=text.count('?')+text.count('¿');imp=signal_count(text,IMPERATIVES);mat=int(any(x in t for x in MATERIAL_WORDS));proj=int(any(x in t for x in PROJECT_WORDS));exp=int(any(x in t for x in EXPERIMENT_WORDS));assess=int(any(x in t for x in ASSESS_WORDS));activity=int(any(x in t for x in ACTIVITY_WORDS));starts_q=any(t.startswith(x+' ') or t.startswith('¿'+x) for x in QUESTION_START)
    if assess:typ='assessment_candidate'
    elif proj:typ='project_candidate'
    elif exp or (mat and imp):typ='experiment_candidate'
    elif activity:typ='activity_candidate'
    elif q or starts_q:typ='question_candidate'
    elif imp:typ='instruction_candidate'
    elif token_count(text)<=12 and len(text)<=100:typ='short_residual_candidate'
    elif token_count(text)>=4:typ='expository_candidate'
    else:typ='other_candidate'
    return typ,{'q':q,'imp':imp,'mat':mat,'proj':proj,'exp':exp,'assess':assess,'activity':activity}

def read_tsv(path):
    with path.open(encoding='utf-8',errors='replace',newline='') as f:
        out=[]
        for r in csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE):
            if r.get('level')!='5':continue
            text=norm(r.get('text',''))
            if text:out.append(r|{'text':text})
        return out

def reconstruct_paragraphs(rows):
    groups=defaultdict(list);order=[]
    for r in rows:
        k=(r.get('page_num'),r.get('block_num'),r.get('par_num'))
        if k not in groups:order.append(k)
        groups[k].append(r)
    paras=[]
    for k in order:
        line_groups=defaultdict(list);line_order=[]
        for r in groups[k]:
            lk=r.get('line_num')
            if lk not in line_groups:line_order.append(lk)
            line_groups[lk].append(r)
        text=norm(' '.join(norm(' '.join(x['text'] for x in line_groups[lk])) for lk in line_order))
        if text:paras.append(text)
    return paras

def sentence_units(p):return [norm(x) for x in re.split(r'(?<=[\?\!\.])\s+(?=[¿¡A-ZÁÉÍÓÚÜÑ0-9])',p) if norm(x)]
def merge_units(units):
    out=[]
    for u in units:
        typ,sig=candidate_type(u);n=token_count(u)
        if not out:out.append([u,typ,sig,n]);continue
        prev=out[-1]
        if typ=='expository_candidate' and prev[1]==typ and prev[3]+n<=120:
            prev[0]=norm(prev[0]+' '+u);prev[3]+=n
            for k,v in sig.items():prev[2][k]+=v
        else:out.append([u,typ,sig,n])
    return out

def download_verify(src,dest,attempts=3):
    last=None
    for attempt in range(1,attempts+1):
        try:
            h=hashlib.sha256()
            with urlopen(Request(src['source_asset_url'],headers={'User-Agent':UA}),timeout=45) as r,dest.open('wb') as f:
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);f.write(b)
            if h.hexdigest()!=src['sha256']:raise RuntimeError('source SHA mismatch')
            return
        except Exception as e:
            last=e;dest.unlink(missing_ok=True)
            if attempt<attempts:time.sleep(attempt*2)
    raise last

def run_tesseract(img,outbase,psm):
    cp=subprocess.run(['tesseract',str(img),str(outbase),'-l','spa','--psm',str(psm),'tsv'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=90,check=False)
    return cp.returncode==0 and outbase.with_suffix('.tsv').exists()

def process_page(r,src,temp):
    p=int(r['viewer_page']);psm=r['selected_psm'] or '3';stem=re.sub(r'[^A-Za-z0-9_.-]+','_',r['page_id']);img=temp/f'{stem}.jpg';outbase=temp/stem
    download_verify(src,img)
    if not run_tesseract(img,outbase,psm):return [],'ocr_failed'
    paras=reconstruct_paragraphs(read_tsv(outbase.with_suffix('.tsv')));units=[]
    for para in paras:units.extend(sentence_units(para))
    merged=merge_units(units);fragments=[]
    for seq,(text,typ,sig,n) in enumerate(merged,1):
        if n==0:continue
        fragments.append({'fragment_id':f"{r['page_id']}-F{seq:03d}",'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'fragment_sequence':seq,'candidate_type':typ,'token_count':n,'char_count':len(text),'question_mark_count':sig['q'],'imperative_signal_count':sig['imp'],'material_signal':sig['mat'],'project_signal':sig['proj'],'experiment_signal':sig['exp'],'assessment_signal':sig['assess'],'activity_signal':sig['activity'],'text_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),'segmenter_version':VERSION,'source_structure_class':r['primary_structure'],'classification_certainty':r['classification_certainty'],'uncertain_boundary':int(n>500 or (typ=='other_candidate' and n<4))})
    return fragments,'ok'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--book-id');ap.add_argument('--out',default='data/expansion/cn46_fragment_manifest.csv');args=ap.parse_args()
    structure=list(csv.DictReader(STRUCTURE.open(encoding='utf-8')));sources={r['page_id']:r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if r['asset_status']=='source_jpeg'}
    rows=[r for r in structure if r['primary_structure'] in ELIGIBLE and (not args.book_id or r['book_id']==args.book_id)]
    allfrags=[];failures=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn46-frag-') as td:
        temp=Path(td)
        for i,r in enumerate(rows,1):
            try:fr,status=process_page(r,sources[r['page_id']],temp)
            except Exception as e:fr=[];status=f'exception:{type(e).__name__}'
            if status!='ok' or not fr:failures.append((r['page_id'],r['book_id'],status,len(fr)))
            allfrags.extend(fr)
            for p in temp.iterdir():
                try:p.unlink()
                except Exception:pass
            if i%100==0:print('pages',i,'/',len(rows),'fragments',len(allfrags))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    fields=['fragment_id','page_id','book_id','catalog_generation','grade','viewer_page','fragment_sequence','candidate_type','token_count','char_count','question_mark_count','imperative_signal_count','material_signal','project_signal','experiment_signal','assessment_signal','activity_signal','text_sha256','segmenter_version','source_structure_class','classification_certainty','uncertain_boundary']
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(allfrags)
    fail=out.with_name(out.stem+'_failures.csv')
    with fail.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['page_id','book_id','status','fragment_count']);w.writerows(failures)
    summary=out.with_name(out.stem+'_summary.csv');counts=defaultdict(Counter)
    for r in allfrags:counts[r['book_id']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1
    types=sorted({r['candidate_type'] for r in allfrags});srows=[]
    for bid in sorted([x for x in counts if x!='ALL'])+['ALL']:
        c=counts[bid];row={'book_id':bid,'fragment_count':sum(c.values())};row.update({t:c[t] for t in types});srows.append(row)
    with summary.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(srows[0]));w.writeheader();w.writerows(srows)
    print('eligible_pages',len(rows),'fragments',len(allfrags),'failures',len(failures),'out',out)

if __name__=='__main__':main()
