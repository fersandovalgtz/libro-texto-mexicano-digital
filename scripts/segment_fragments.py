#!/usr/bin/env python3
"""Deterministic OCR-to-fragment segmentation for LTMD.

Processes only pages classified textual/mixed_text_image. OCR text exists only in
memory/temp files and is not written to public outputs. Public output contains
hashes, counts and functional candidate signals.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

STRUCTURE = Path("data/derived/page_structure.csv")
VERSION = "FRAGSEG_0.1"
SOURCE_CODES = {
    "1972": "H1972P5CI084",
    "1988": "H1988P5CI123",
    "1993": "H1993P5CI200",
    "2014": "H2014P5CNA",
}
ELIGIBLE = {"textual", "mixed_text_image"}

IMPERATIVES = [
    "observa","describe","escribe","explica","compara","clasifica","mide","realiza",
    "investiga","discute","comenta","elabora","construye","dibuja","resuelve","contesta",
    "responde","identifica","señala","anota","registra","lee","analiza","calcula","reúne",
    "busca","consulta","organiza","completa","marca","subraya","recorta","pega","coloca",
    "haz","forma","trabaja","elige","decide","propón","propone","predice","infiere",
]
QUESTION_START = ["qué","que","cómo","como","cuál","cual","cuáles","cuales","por qué","por que","dónde","donde","cuándo","cuando","quién","quien"]
MATERIAL_WORDS = ["materiales","necesitas","vas a necesitar","material"]
PROJECT_WORDS = ["proyecto","proyectos"]
EXPERIMENT_WORDS = ["experimento","experimenta","experimentación","procedimiento","hipótesis"]
ASSESS_WORDS = ["evaluación","autoevaluación","qué aprendí","lo que aprendí","evalúa"]
ACTIVITY_WORDS = ["actividad","en equipo","trabaja en equipo","por equipos","con tus compañeros"]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def low(s: str) -> str:
    return norm(s).casefold()


def token_count(s: str) -> int:
    return len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b", s, flags=re.UNICODE))


def signal_count(text: str, terms: list[str]) -> int:
    t = low(text)
    return sum(t.count(term.casefold()) for term in terms)


def candidate_type(text: str) -> tuple[str, dict[str,int]]:
    t = low(text)
    q = text.count("?") + text.count("¿")
    imp = signal_count(text, IMPERATIVES)
    mat = int(any(x in t for x in MATERIAL_WORDS))
    proj = int(any(x in t for x in PROJECT_WORDS))
    exp = int(any(x in t for x in EXPERIMENT_WORDS))
    assess = int(any(x in t for x in ASSESS_WORDS))
    activity = int(any(x in t for x in ACTIVITY_WORDS))
    starts_q = any(t.startswith(x + " ") or t.startswith("¿" + x) for x in QUESTION_START)
    if assess:
        typ = "assessment_candidate"
    elif proj:
        typ = "project_candidate"
    elif exp or (mat and imp):
        typ = "experiment_candidate"
    elif activity:
        typ = "activity_candidate"
    elif q or starts_q:
        typ = "question_candidate"
    elif imp:
        typ = "instruction_candidate"
    elif token_count(text) <= 12 and len(text) <= 100:
        typ = "heading_candidate"
    elif token_count(text) >= 4:
        typ = "expository_candidate"
    else:
        typ = "other_candidate"
    return typ, {"q":q,"imp":imp,"mat":mat,"proj":proj,"exp":exp,"assess":assess,"activity":activity}


def read_tsv(tsv_path: Path):
    with tsv_path.open(encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        rows = []
        for r in reader:
            if r.get("level") != "5":
                continue
            text = norm(r.get("text", ""))
            if not text:
                continue
            rows.append(r | {"text": text})
        return rows


def reconstruct_paragraphs(rows):
    groups = defaultdict(list)
    order = []
    for r in rows:
        key = (r.get("page_num"), r.get("block_num"), r.get("par_num"))
        if key not in groups:
            order.append(key)
        groups[key].append(r)
    paras = []
    for key in order:
        words = groups[key]
        line_groups = defaultdict(list); line_order=[]
        for r in words:
            lk = r.get("line_num")
            if lk not in line_groups:
                line_order.append(lk)
            line_groups[lk].append(r)
        lines = [norm(" ".join(x["text"] for x in line_groups[lk])) for lk in line_order]
        text = norm(" ".join(lines))
        if text:
            paras.append(text)
    return paras


def sentence_units(paragraph: str):
    # Preserve questions/exclamations as natural boundaries; full stops split only
    # when followed by likely new sentence marker. OCR can omit punctuation, so the
    # paragraph remains intact if no reliable boundary is present.
    parts = re.split(r"(?<=[\?\!\.])\s+(?=[¿¡A-ZÁÉÍÓÚÜÑ0-9])", paragraph)
    return [norm(p) for p in parts if norm(p)]


def merge_units(units):
    out=[]
    for u in units:
        typ, sig = candidate_type(u)
        n=token_count(u)
        if not out:
            out.append([u,typ,sig,n])
            continue
        prev=out[-1]
        # Merge adjacent expository sentences to avoid sentence-level oversegmentation;
        # retain questions/instructions/activities as autonomous units.
        if typ=="expository_candidate" and prev[1]==typ and prev[3]+n <= 120:
            prev[0]=norm(prev[0]+" "+u); prev[3]+=n
            for k,v in sig.items(): prev[2][k]+=v
        else:
            out.append([u,typ,sig,n])
    return out


def run_tesseract(img: Path, outbase: Path, psm: str):
    cp = subprocess.run(
        ["tesseract", str(img), str(outbase), "-l", "spa", "--psm", str(psm), "tsv"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90, check=False,
    )
    return cp.returncode == 0 and outbase.with_suffix(".tsv").exists()


def process_page(r, temp: Path):
    gen=r["catalog_generation"]; p=int(r["viewer_page"]); psm=r["selected_psm"] or "3"
    img=temp/f"{gen}_{p:03d}.jpg"; outbase=temp/f"{gen}_{p:03d}"
    url=f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg"
    urllib.request.urlretrieve(url,img)
    if not run_tesseract(img,outbase,psm):
        return [], "ocr_failed"
    rows=read_tsv(outbase.with_suffix('.tsv'))
    paras=reconstruct_paragraphs(rows)
    units=[]
    for para in paras:
        units.extend(sentence_units(para))
    merged=merge_units(units)
    fragments=[]
    for seq,(text,typ,sig,n) in enumerate(merged,1):
        if n==0:
            continue
        uncertain=int(n>500 or (typ=="other_candidate" and n<4))
        fragments.append({
            "fragment_id":f"{r['page_id']}-F{seq:03d}",
            "page_id":r["page_id"],
            "book_id":r["book_id"],
            "catalog_generation":gen,
            "viewer_page":p,
            "fragment_sequence":seq,
            "candidate_type":typ,
            "token_count":n,
            "char_count":len(text),
            "question_mark_count":sig["q"],
            "imperative_signal_count":sig["imp"],
            "material_signal":sig["mat"],
            "project_signal":sig["proj"],
            "experiment_signal":sig["exp"],
            "assessment_signal":sig["assess"],
            "activity_signal":sig["activity"],
            "text_sha256":hashlib.sha256(text.encode('utf-8')).hexdigest(),
            "segmenter_version":VERSION,
            "source_structure_class":r["primary_structure"],
            "classification_certainty":r["classification_certainty"],
            "uncertain_boundary":uncertain,
        })
    return fragments, "ok"


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--generation", required=True, choices=SOURCE_CODES); ap.add_argument("--out", required=True)
    args=ap.parse_args()
    rows=[r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8')) if r['catalog_generation']==args.generation and r['primary_structure'] in ELIGIBLE]
    allfrags=[]; failures=[]
    with tempfile.TemporaryDirectory(prefix=f"ltmd-frag-{args.generation}-") as td:
        temp=Path(td)
        for i,r in enumerate(rows,1):
            try:
                fr,status=process_page(r,temp)
            except Exception as e:
                fr=[]; status=f"exception:{type(e).__name__}"
            if status!='ok' or not fr:
                failures.append((r['page_id'],status,len(fr)))
            allfrags.extend(fr)
            for p in temp.glob(f"{args.generation}_{int(r['viewer_page']):03d}*"):
                try: p.unlink()
                except Exception: pass
            if i%25==0: print(args.generation, 'pages', i, '/', len(rows), 'fragments', len(allfrags))
    fields=["fragment_id","page_id","book_id","catalog_generation","viewer_page","fragment_sequence","candidate_type","token_count","char_count","question_mark_count","imperative_signal_count","material_signal","project_signal","experiment_signal","assessment_signal","activity_signal","text_sha256","segmenter_version","source_structure_class","classification_certainty","uncertain_boundary"]
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(allfrags)
    failpath=out.with_name(out.stem+'_failures.csv')
    with failpath.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['page_id','status','fragment_count']); w.writerows(failures)
    print('eligible_pages',len(rows),'fragments',len(allfrags),'failures',len(failures),'out',out)

if __name__=='__main__':
    main()
