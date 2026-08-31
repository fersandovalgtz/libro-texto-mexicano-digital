#!/usr/bin/env python3
"""Build LTMD-U1 cross-corpus reuse/similarity private analytics layer.

Version: LTMD_U1_REUSE_SIMILARITY_BUILDER_0.1

Evidence hierarchy is deliberately separated:
- exact_source_reuse: equality of source_sha256 (byte-representation evidence)
- exact_text_representation_reuse: equality of search_text_sha256 after fixed low-information gate
- similarity_candidate: approximate normalized-token resemblance, verified by exact 5-shingle Jaccard

No layer creates aliases or establishes bibliographic, curricular, pedagogical, historical,
or semantic equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

import numpy as np

BUILDER_VERSION = "LTMD_U1_REUSE_SIMILARITY_BUILDER_0.1"
ARTIFACT_VERSION = "LTMD_U1_REUSE_SIMILARITY_0.1"
INDEX_VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
LEXICAL_VERSION = "LTMD_U1_LEXICAL_POSITIONS_0.1"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

TEXT_MIN_CHARS = 200
TEXT_MIN_WORDS = 30
SHINGLE_N = 5
MIN_DISTINCT_SHINGLES = 50
MINHASH_COMPONENTS = 96
LSH_BANDS = 12
LSH_ROWS = 8
SIMILARITY_MIN_JACCARD = 0.80
NEAR_EXACT_MIN_JACCARD = 0.95
SIMILARITY_MIN_SHARED_SHINGLES = 40

TERM_BITS = 18
SHINGLE_COEFF = np.array([
    0x9E3779B185EBCA87,
    0xC2B2AE3D27D4EB4F,
    0x165667B19E3779F9,
    0x85EBCA77C2B2AE63,
    0x27D4EB2F165667C5,
], dtype=np.uint64)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha(path: Path, expected: str | None, label: str) -> str | None:
    if not path.is_file():
        raise RuntimeError(f"{label} artifact is unavailable")
    if expected is None:
        return None
    exp = expected.strip().lower()
    if not SHA256_RE.fullmatch(exp):
        raise RuntimeError(f"expected {label} SHA-256 is invalid")
    actual = sha256_file(path)
    if actual != exp:
        raise RuntimeError(f"{label} SHA-256 mismatch")
    return actual


def _decode_json(raw: str):
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def load_index_meta(c: sqlite3.Connection) -> dict:
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
    if not {"pages", "index_meta"}.issubset(tables):
        raise RuntimeError("not an LTMD Universal Index")
    meta = {k: _decode_json(v) for k, v in c.execute("SELECT key,value FROM index_meta")}
    if meta.get("builder_version") != INDEX_VERSION:
        raise RuntimeError("unsupported Universal Index version")
    return meta


def load_lexical_meta(c: sqlite3.Connection) -> dict:
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {"meta", "pages", "terms", "token_positions"}
    if not required.issubset(tables):
        raise RuntimeError("not an LTMD lexical-position artifact")
    meta = {k: _decode_json(v) for k, v in c.execute("SELECT key,value FROM meta")}
    version = meta.get("artifact_version", meta.get("version"))
    if version != LEXICAL_VERSION:
        raise RuntimeError("unsupported lexical-position artifact version")
    return meta


def _splitmix64(x):
    x = np.asarray(x, dtype=np.uint64)
    z = x + np.uint64(0x9E3779B97F4A7C15)
    z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))


MINHASH_SALTS = _splitmix64(np.arange(MINHASH_COMPONENTS, dtype=np.uint64) + np.uint64(0x1234ABCD))


def shingle_hashes(terms, offsets) -> np.ndarray:
    a = np.asarray(terms, dtype=np.uint64)
    o = np.asarray(offsets, dtype=np.int64)
    if a.size < SHINGLE_N:
        return np.empty(0, dtype=np.uint64)
    valid = (
        (o[1:-3] == o[:-4] + 1)
        & (o[2:-2] == o[:-4] + 2)
        & (o[3:-1] == o[:-4] + 3)
        & (o[4:] == o[:-4] + 4)
    )
    if not np.any(valid):
        return np.empty(0, dtype=np.uint64)
    x = (
        (a[:-4] * SHINGLE_COEFF[0])
        ^ (a[1:-3] * SHINGLE_COEFF[1])
        ^ (a[2:-2] * SHINGLE_COEFF[2])
        ^ (a[3:-1] * SHINGLE_COEFF[3])
        ^ (a[4:] * SHINGLE_COEFF[4])
    )
    return np.unique(_splitmix64(x[valid]))


def minhash_signature(shingles: np.ndarray) -> np.ndarray:
    sig = np.empty(MINHASH_COMPONENTS, dtype=np.uint64)
    for start in range(0, MINHASH_COMPONENTS, 12):
        salts = MINHASH_SALTS[start : start + 12, None]
        sig[start : start + 12] = _splitmix64(shingles[None, :] ^ salts).min(axis=1)
    return sig


def _remove_sqlite_family(path: Path) -> None:
    for p in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
        if p.exists():
            p.unlink()


def _create_output(path: Path) -> sqlite3.Connection:
    out = sqlite3.connect(path, timeout=120)
    out.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    PRAGMA cache_size=-200000;
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID;
    CREATE TABLE objects(object_id INTEGER PRIMARY KEY, canonical_viewer_key TEXT NOT NULL UNIQUE);
    CREATE TABLE exact_source_groups(
        group_id INTEGER PRIMARY KEY, hash TEXT NOT NULL UNIQUE, page_count INTEGER NOT NULL,
        object_count INTEGER NOT NULL, generation_count INTEGER NOT NULL,
        cross_object INTEGER NOT NULL, cross_generation INTEGER NOT NULL);
    CREATE TABLE exact_source_members(
        group_id INTEGER NOT NULL,page_rowid INTEGER NOT NULL,object_id INTEGER NOT NULL,generation INTEGER,
        PRIMARY KEY(group_id,page_rowid)) WITHOUT ROWID;
    CREATE TABLE exact_text_groups(
        group_id INTEGER PRIMARY KEY, hash TEXT NOT NULL UNIQUE, page_count INTEGER NOT NULL,
        object_count INTEGER NOT NULL, generation_count INTEGER NOT NULL,grade_count INTEGER NOT NULL,
        wave_count INTEGER NOT NULL,cross_object INTEGER NOT NULL,cross_generation INTEGER NOT NULL);
    CREATE TABLE exact_text_members(
        group_id INTEGER NOT NULL,page_rowid INTEGER NOT NULL,object_id INTEGER NOT NULL,generation INTEGER,
        PRIMARY KEY(group_id,page_rowid)) WITHOUT ROWID;
    CREATE TABLE exact_object_pairs(
        evidence_type TEXT NOT NULL,object_a INTEGER NOT NULL,object_b INTEGER NOT NULL,
        shared_groups INTEGER NOT NULL,PRIMARY KEY(evidence_type,object_a,object_b)) WITHOUT ROWID;
    CREATE TABLE similarity_candidates(
        page_a INTEGER NOT NULL,page_b INTEGER NOT NULL,object_a INTEGER NOT NULL,object_b INTEGER NOT NULL,
        jaccard REAL NOT NULL,shared_shingles INTEGER NOT NULL,shingles_a INTEGER NOT NULL,shingles_b INTEGER NOT NULL,
        tier TEXT NOT NULL,PRIMARY KEY(page_a,page_b)) WITHOUT ROWID;
    CREATE TABLE similarity_object_pairs(
        object_a INTEGER NOT NULL,object_b INTEGER NOT NULL,candidate_pairs INTEGER NOT NULL,
        near_exact_pairs INTEGER NOT NULL,max_jaccard REAL NOT NULL,
        PRIMARY KEY(object_a,object_b)) WITHOUT ROWID;
    """)
    return out


def _object_maps(index: sqlite3.Connection):
    keys = [r[0] for r in index.execute("SELECT DISTINCT canonical_viewer_key FROM pages ORDER BY canonical_viewer_key")]
    key_to_id = {k: i + 1 for i, k in enumerate(keys)}
    return keys, key_to_id


def _materialize_exact(index, out, key_to_id):
    source_groups = list(index.execute("""
        SELECT source_sha256,COUNT(*),COUNT(DISTINCT canonical_viewer_key),COUNT(DISTINCT catalog_generation)
        FROM pages GROUP BY source_sha256 HAVING COUNT(*)>=2 ORDER BY source_sha256
    """))
    source_gid = {h: gid for gid,(h,*_) in enumerate(source_groups,1)}
    out.executemany(
        "INSERT INTO exact_source_groups VALUES(?,?,?,?,?,?,?)",
        ((gid,h,pages,objects,generations,int(objects>=2),int(generations>=2))
         for gid,(h,pages,objects,generations) in enumerate(source_groups,1))
    )
    rows = index.execute("""
        WITH repeated AS (
          SELECT source_sha256 h FROM pages GROUP BY source_sha256 HAVING COUNT(*)>=2
        )
        SELECT p.source_sha256,p.id,p.canonical_viewer_key,p.catalog_generation
        FROM pages p JOIN repeated r ON r.h=p.source_sha256
        ORDER BY p.source_sha256,p.id
    """)
    out.executemany(
        "INSERT INTO exact_source_members VALUES(?,?,?,?)",
        ((source_gid[h],pid,key_to_id[obj],gen) for h,pid,obj,gen in rows)
    )
    out.commit()

    text_groups = list(index.execute(f"""
        SELECT search_text_sha256,COUNT(*),COUNT(DISTINCT canonical_viewer_key),COUNT(DISTINCT catalog_generation),
               COUNT(DISTINCT grade_code),COUNT(DISTINCT wave)
        FROM pages
        WHERE ocr_char_count>={TEXT_MIN_CHARS} AND ocr_word_count>={TEXT_MIN_WORDS}
        GROUP BY search_text_sha256 HAVING COUNT(*)>=2 ORDER BY search_text_sha256
    """))
    text_gid = {h: gid for gid,(h,*_) in enumerate(text_groups,1)}
    out.executemany(
        "INSERT INTO exact_text_groups VALUES(?,?,?,?,?,?,?,?,?)",
        ((gid,h,pages,objects,generations,grades,waves,int(objects>=2),int(generations>=2))
         for gid,(h,pages,objects,generations,grades,waves) in enumerate(text_groups,1))
    )
    rows = index.execute(f"""
        WITH repeated AS (
          SELECT search_text_sha256 h
          FROM pages
          WHERE ocr_char_count>={TEXT_MIN_CHARS} AND ocr_word_count>={TEXT_MIN_WORDS}
          GROUP BY search_text_sha256 HAVING COUNT(*)>=2
        )
        SELECT p.search_text_sha256,p.id,p.canonical_viewer_key,p.catalog_generation
        FROM pages p JOIN repeated r ON r.h=p.search_text_sha256
        WHERE p.ocr_char_count>={TEXT_MIN_CHARS} AND p.ocr_word_count>={TEXT_MIN_WORDS}
        ORDER BY p.search_text_sha256,p.id
    """)
    out.executemany(
        "INSERT INTO exact_text_members VALUES(?,?,?,?)",
        ((text_gid[h],pid,key_to_id[obj],gen) for h,pid,obj,gen in rows)
    )
    out.commit()

    for evidence, table in (("exact_source_reuse","exact_source_members"),("exact_text_representation_reuse","exact_text_members")):
        out.execute(f"""
            INSERT INTO exact_object_pairs
            SELECT ?,a.object_id,b.object_id,COUNT(DISTINCT a.group_id)
            FROM {table} a JOIN {table} b ON a.group_id=b.group_id AND a.object_id<b.object_id
            GROUP BY a.object_id,b.object_id
        """, (evidence,))
    out.commit()

def _similarity_inputs(index, lexical, key_to_id):
    max_page = int(index.execute("SELECT MAX(id) FROM pages").fetchone()[0])
    eligible = np.zeros(max_page + 1, dtype=bool)
    search_hash = np.empty(max_page + 1, dtype=object)
    page_object = np.zeros(max_page + 1, dtype=np.uint16)
    page_generation = np.zeros(max_page + 1, dtype=np.int16)
    page_grade = np.full(max_page + 1, -1, dtype=np.int16)
    wave_values = sorted({r[0] for r in index.execute("SELECT DISTINCT wave FROM pages WHERE wave IS NOT NULL")})
    wave_code_map = {v:i for i,v in enumerate(wave_values)}
    page_wave = np.full(max_page + 1, -1, dtype=np.int16)
    for pid,obj,gen,grade,wave,h in index.execute(f"""
        SELECT id,canonical_viewer_key,catalog_generation,grade_code,wave,search_text_sha256
        FROM pages WHERE ocr_char_count>={TEXT_MIN_CHARS} AND ocr_word_count>={TEXT_MIN_WORDS}
    """):
        eligible[pid] = True
        page_object[pid] = key_to_id[obj]
        page_generation[pid] = gen if gen is not None else -1
        page_grade[pid] = grade if grade is not None else -1
        page_wave[pid] = wave_code_map.get(wave,-1)
        search_hash[pid] = h

    page_ids=[]; objects=[]; shingle_sets=[]; signatures=[]
    last=None; terms=[]; offsets=[]
    def flush(pid, terms, offsets):
        if pid is None or not eligible[pid]:
            return
        sh = shingle_hashes(terms, offsets)
        if sh.size < MIN_DISTINCT_SHINGLES:
            return
        page_ids.append(pid); objects.append(int(page_object[pid])); shingle_sets.append(sh); signatures.append(minhash_signature(sh))
    for pid,term,offset in lexical.execute("SELECT page_rowid,term_id,token_offset FROM token_positions ORDER BY page_rowid,token_offset"):
        if last is None: last=pid
        if pid!=last:
            flush(last,terms,offsets); last=pid; terms=[]; offsets=[]
        terms.append(term); offsets.append(offset)
    flush(last,terms,offsets)
    return (
        np.asarray(page_ids,dtype=np.uint32),np.asarray(objects,dtype=np.uint16),shingle_sets,
        np.vstack(signatures) if signatures else np.empty((0,MINHASH_COMPONENTS),dtype=np.uint64),
        search_hash,page_generation,page_grade,page_wave,
    )


def _lsh_candidates(page_ids, objects, signatures, search_hash):
    candidates=set(); raw_band_pair_occurrences=0
    for band in range(LSH_BANDS):
        arr=np.ascontiguousarray(signatures[:,band*LSH_ROWS:(band+1)*LSH_ROWS])
        keys=arr.view(np.dtype((np.void,arr.dtype.itemsize*LSH_ROWS))).ravel()
        order=np.argsort(keys,kind="stable"); sorted_keys=keys[order]
        starts=np.r_[0,np.flatnonzero(sorted_keys[1:]!=sorted_keys[:-1])+1]
        ends=np.r_[starts[1:],len(sorted_keys)]
        for start,end in zip(starts,ends):
            if end-start<2: continue
            inds=order[start:end]
            for i in range(len(inds)-1):
                a=inds[i]
                for j in range(i+1,len(inds)):
                    b=inds[j]; raw_band_pair_occurrences+=1
                    if objects[a]==objects[b]: continue
                    pa,pb=int(page_ids[a]),int(page_ids[b])
                    if search_hash[pa] == search_hash[pb]:
                        continue
                    if pa>pb: pa,pb=pb,pa
                    candidates.add((pa,pb))
    return raw_band_pair_occurrences, sorted(candidates)


def _verify_similarity(page_ids, objects, shingle_sets, candidates, page_generation, page_grade, page_wave):
    page_index={int(pid):i for i,pid in enumerate(page_ids)}
    results=[]
    cross_generation=cross_grade=cross_wave=0
    for pa,pb in candidates:
        ia,ib=page_index[pa],page_index[pb]
        a,b=shingle_sets[ia],shingle_sets[ib]
        if min(len(a),len(b))/max(len(a),len(b)) < SIMILARITY_MIN_JACCARD:
            continue
        shared=int(np.intersect1d(a,b,assume_unique=True).size)
        union=len(a)+len(b)-shared
        jaccard=shared/union if union else 0.0
        if jaccard < SIMILARITY_MIN_JACCARD or shared < SIMILARITY_MIN_SHARED_SHINGLES:
            continue
        tier="near_exact_candidate" if jaccard>=NEAR_EXACT_MIN_JACCARD else "similarity_candidate"
        oa,ob=int(objects[ia]),int(objects[ib])
        results.append((pa,pb,oa,ob,jaccard,shared,len(a),len(b),tier))
        cross_generation += int(page_generation[pa]!=page_generation[pb])
        cross_grade += int(page_grade[pa]!=page_grade[pb])
        cross_wave += int(page_wave[pa]!=page_wave[pb])
    return results,cross_generation,cross_grade,cross_wave


def build(index_path: Path, lexical_path: Path, output_path: Path, *, overwrite=False):
    index_path=index_path.expanduser().resolve(); lexical_path=lexical_path.expanduser().resolve(); output_path=output_path.expanduser().resolve()
    if output_path.exists() and not overwrite:
        raise RuntimeError("output already exists; pass --overwrite to replace it")
    if overwrite: _remove_sqlite_family(output_path)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    index=sqlite3.connect(f"file:{index_path}?mode=ro",uri=True,timeout=120)
    lexical=sqlite3.connect(f"file:{lexical_path}?mode=ro",uri=True,timeout=120)
    try:
        imeta=load_index_meta(index); lmeta=load_lexical_meta(lexical)
        if int(imeta.get("unique_pages",0)) != int(lmeta.get("unique_pages",0)):
            raise RuntimeError("Universal Index and lexical artifact page counts differ")
        keys,key_to_id=_object_maps(index)
        out=_create_output(output_path)
        try:
            out.executemany("INSERT INTO objects VALUES(?,?)",((i+1,k) for i,k in enumerate(keys))); out.commit()
            _materialize_exact(index,out,key_to_id)
            page_ids,objects,shingles,signatures,search_hash,pgen,pgrade,pwave=_similarity_inputs(index,lexical,key_to_id)
            raw_band_pairs,candidates=_lsh_candidates(page_ids,objects,signatures,search_hash)
            verified,cross_gen,cross_grade,cross_wave=_verify_similarity(page_ids,objects,shingles,candidates,pgen,pgrade,pwave)
            out.executemany("INSERT INTO similarity_candidates VALUES(?,?,?,?,?,?,?,?,?)",verified); out.commit()
            pair_agg=defaultdict(lambda:[0,0,0.0])
            for _,_,oa,ob,j,_,_,_,tier in verified:
                if oa>ob: oa,ob=ob,oa
                rec=pair_agg[(oa,ob)]; rec[0]+=1; rec[1]+=int(tier=="near_exact_candidate"); rec[2]=max(rec[2],j)
            out.executemany("INSERT INTO similarity_object_pairs VALUES(?,?,?,?,?)",
                            ((oa,ob,v[0],v[1],v[2]) for (oa,ob),v in sorted(pair_agg.items()))); out.commit()

            admitted_pages=int(index.execute(f"SELECT COUNT(*) FROM pages WHERE ocr_char_count>={TEXT_MIN_CHARS} AND ocr_word_count>={TEXT_MIN_WORDS}").fetchone()[0])
            counts={
                "corpus_pages":int(index.execute("SELECT COUNT(*) FROM pages").fetchone()[0]),
                "canonical_objects":len(keys),
                "text_admissible_pages":admitted_pages,
                "text_excluded_low_information_pages":int(index.execute("SELECT COUNT(*) FROM pages").fetchone()[0])-admitted_pages,
                "exact_source_repeated_groups":int(out.execute("SELECT COUNT(*) FROM exact_source_groups").fetchone()[0]),
                "exact_source_cross_object_groups":int(out.execute("SELECT COUNT(*) FROM exact_source_groups WHERE cross_object=1").fetchone()[0]),
                "exact_source_cross_generation_groups":int(out.execute("SELECT COUNT(*) FROM exact_source_groups WHERE cross_generation=1").fetchone()[0]),
                "exact_source_object_pairs":int(out.execute("SELECT COUNT(*) FROM exact_object_pairs WHERE evidence_type='exact_source_reuse'").fetchone()[0]),
                "exact_text_repeated_groups":int(out.execute("SELECT COUNT(*) FROM exact_text_groups").fetchone()[0]),
                "exact_text_cross_object_groups":int(out.execute("SELECT COUNT(*) FROM exact_text_groups WHERE cross_object=1").fetchone()[0]),
                "exact_text_cross_generation_groups":int(out.execute("SELECT COUNT(*) FROM exact_text_groups WHERE cross_generation=1").fetchone()[0]),
                "exact_text_object_pairs":int(out.execute("SELECT COUNT(*) FROM exact_object_pairs WHERE evidence_type='exact_text_representation_reuse'").fetchone()[0]),
                "similarity_shingle_eligible_pages":len(page_ids),
                "lsh_raw_band_pair_occurrences":raw_band_pairs,
                "lsh_distinct_nonexact_cross_object_candidates":len(candidates),
                "verified_similarity_candidates":len(verified),
                "similarity_candidates":sum(v[-1]=="similarity_candidate" for v in verified),
                "near_exact_candidates":sum(v[-1]=="near_exact_candidate" for v in verified),
                "similarity_object_pairs":len(pair_agg),
                "similarity_cross_generation_pairs":cross_gen,
                "similarity_cross_grade_pairs":cross_grade,
                "similarity_cross_wave_pairs":cross_wave,
            }
            protocol={
                "text_admissibility":{"min_ocr_chars":TEXT_MIN_CHARS,"min_ocr_words":TEXT_MIN_WORDS},
                "exact_source_reuse":{"basis":"source_sha256 equality","low_information_gate":False},
                "exact_text_representation_reuse":{"basis":"search_text_sha256 equality","low_information_gate":True},
                "similarity":{"shingle_n":SHINGLE_N,"min_distinct_shingles":MIN_DISTINCT_SHINGLES,
                    "minhash_components":MINHASH_COMPONENTS,"lsh_bands":LSH_BANDS,"lsh_rows":LSH_ROWS,
                    "exact_jaccard_min":SIMILARITY_MIN_JACCARD,"near_exact_jaccard_min":NEAR_EXACT_MIN_JACCARD,
                    "min_shared_shingles":SIMILARITY_MIN_SHARED_SHINGLES,"cross_object_only":True,
                    "exclude_exact_text_equality":True,"thresholds_preregistered_before_candidate_inspection":True},
            }
            metadata={"builder_version":BUILDER_VERSION,"artifact_version":ARTIFACT_VERSION,**counts,
                      "protocol":protocol,"private":True,"text_verified":False,"semantic_ready":False,
                      "default_result_state":"exploratory_signal","similarity_creates_alias":False,
                      "similarity_is_semantic_equivalence":False}
            for k,v in metadata.items(): out.execute("INSERT INTO meta VALUES(?,?)",(k,json.dumps(v,ensure_ascii=False,sort_keys=True)))
            out.commit()
            if out.execute("PRAGMA quick_check").fetchone()[0] != "ok": raise RuntimeError("reuse/similarity artifact quick_check failed")
            out.execute("PRAGMA wal_checkpoint(TRUNCATE)"); out.execute("PRAGMA journal_mode=DELETE"); out.commit()
        finally: out.close()
    finally: index.close(); lexical.close()
    return {"builder_version":BUILDER_VERSION,"artifact_version":ARTIFACT_VERSION,"counts":counts,"protocol":protocol,
            "private_artifact":{"bytes":output_path.stat().st_size,"sha256":sha256_file(output_path),"publish":False},
            "privacy":{"source_hash_values_emitted_publicly":False,"text_hash_values_emitted_publicly":False,
                       "page_identifiers_emitted_publicly":False,"object_identifiers_emitted_publicly":False,
                       "candidate_pairs_emitted_publicly":False,"ocr_text_emitted_publicly":False},
            "scientific_state":{"text_verified":False,"semantic_ready":False,"default_result_state":"exploratory_signal",
                                "similarity_creates_alias":False,"similarity_is_semantic_equivalence":False}}


def run(index_path,lexical_path,output_path,*,expected_index_sha256=None,expected_lexical_sha256=None,overwrite=False):
    idx_sha=verify_sha(index_path,expected_index_sha256,"Universal Index")
    lex_sha=verify_sha(lexical_path,expected_lexical_sha256,"lexical-position")
    result=build(index_path,lexical_path,output_path,overwrite=overwrite)
    result["sources"]={"universal_index_sha256":idx_sha,"lexical_positions_sha256":lex_sha}
    return result


def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--index",required=True); p.add_argument("--lexical",required=True); p.add_argument("--output",required=True)
    p.add_argument("--summary"); p.add_argument("--expected-index-sha256"); p.add_argument("--expected-lexical-sha256"); p.add_argument("--overwrite",action="store_true")
    a=p.parse_args(argv)
    result=run(Path(a.index),Path(a.lexical),Path(a.output),expected_index_sha256=a.expected_index_sha256,expected_lexical_sha256=a.expected_lexical_sha256,overwrite=a.overwrite)
    payload=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.summary: Path(a.summary).write_text(payload,encoding="utf-8")
    else: print(payload,end="")
    return 0

if __name__=="__main__": raise SystemExit(main())
