#!/usr/bin/env python3
"""Per-book, hash-verified FRAGSEG for strict Ciencias Naturales Wave 2."""
from __future__ import annotations
import argparse,csv,hashlib,re,subprocess,tempfile,time,unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

STRUCTURE=Path('data/expansion/cn_wave2_page_structure.csv')
MANIFEST=Path('data/expansion/cn_wave2_page_manifest.csv')
VERSION='FRAGSEG_CN_WAVE2_0.1';ELIGIBLE={'textual','mixed_text_image'};UA='LibroTextoMexicanoDigital/0.1 CN Wave2 FRAGSEG'
IMPERATIVES=['observa','describe','escribe','explica','compara','clasifica','mide','realiza','investiga','discute','comenta','elabora','construye','dibuja','resuelve','contesta','responde','identifica','señala','anota','registra','lee','analiza','calcula','reúne','busca','consulta','organiza','completa','marca','subraya','recorta','pega','coloca','haz','forma','trabaja','elige','decide','propón','propone','predice','infiere']
QUESTION_START=['qué','que','cómo','como','cuál','cual','cuáles','cuales','por qué','por que','dónde','donde','cuándo','cuando','quién','quien'];MATERIAL_WORDS=['materiales','necesitas','vas a necesitar','material'];PROJECT_WORDS=['proyecto','proyectos'];EXPERIMENT_WORDS=['experimento','experimenta','experimentación','procedimiento','hipótesis'];ASSESS_WORDS=['evaluación','autoevaluación','qué aprendí','lo que aprendí','evalúa'];ACTIVITY_WORDS=['actividad','en equipo','trabaja en equipo','por equipos','con tus compañeros']
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).strip()
def low(s):return norm(s).casefold()
def token_count(s):return len(re.findall(r'\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b',s,flags=re.UNICODE))
def signal_count(text,terms):t=low(text);return sum(t.count(x.casefold()) for x in terms)
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
        lg=defaultdict(list);lo=[]
        for r in groups[k]:
            lk=r.get('line_num')
            if lk not in lg:lo.append(lk)
            lg[lk].append(r)
        text=norm(' '.join(norm(' '.join(x['text'] for x in lg[lk])) for lk in lo))
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
        except Exception as e:last=e;dest.unlink(missing_ok=True);time.sleep(attempt*2 if attempt<attempts else 0)
    raise last
def run_tesseract(img,outbase,psm):
    cp=subprocess.run(['tesseract',str(img),str(outbase),'-l','spa','--psm',str(psm),'tsv'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=90,check=False)
    return cp.returncode==0 and outbase.with_suffix('.tsv').exists()
def process_page(r,src,temp):
    p=int(r['viewer_page']);psm=r['selected_psm'] or '3';stem=re.sub(r'[^A-Za-z0-9_.-]+','_',r['page_id']);img=temp/f'{stem}.jpg';outbase=temp/stem;download_verify(src,img)
    if not run_tesseract(img,outbase,psm):return [],'ocr_failed'
    units=[]
    for para in reconstruct_paragraphs(read_tsv(outbase.with_suffix('.tsv'))):units.extend(sentence_units(para))
    fragments=[]
    for seq,(text,typ,sig,n) in enumerate(merge_units(units),1):
        if n==0:continue
        fragments.append({'fragment_id':f"{r['page_id']}-F{seq:03d}",'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'fragment_sequence':seq,'candidate_type':typ,'token_count':n,'char_count':len(text),'question_mark_count':sig['q'],'imperative_signal_count':sig['imp'],'material_signal':sig['mat'],'project_signal':sig['proj'],'experiment_signal':sig['exp'],'assessment_signal':sig['assess'],'activity_signal':sig['activity'],'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'segmenter_version':VERSION,'source_structure_class':r['primary_structure'],'classification_certainty':r['classification_certainty'],'uncertain_boundary':int(n>500 or (typ=='other_candidate' and n<4))})
    return fragments,'ok'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/cn_wave2_fragments');args=ap.parse_args()
    structure=[r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8')) if r['book_id']==args.book_id and r['primary_structure'] in ELIGIBLE];sources={r['page_id']:r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if r['book_id']==args.book_id and r['asset_status']=='source_jpeg'}
    if not structure:raise SystemExit(f'no eligible PAGESTRUCT rows for {args.book_id}')
    allfrags=[];failures=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn-wave2-frag-') as td:
        temp=Path(td)
        for r in structure:
            try:fr,status=process_page(r,sources[r['page_id']],temp)
            except Exception as e:fr=[];status=f'exception:{type(e).__name__}'
            if status!='ok' or not fr:failures.append((r['page_id'],r['book_id'],status,len(fr)))
            allfrags.extend(fr)
            for p in temp.iterdir():p.unlink(missing_ok=True)
    d=Path(args.output_dir);d.mkdir(parents=True,exist_ok=True);slug=args.book_id.lower().replace('ltmd-','');out=d/f'fragment_{slug}.csv';fail=d/f'fragment_{slug}_failures.csv'
    fields=['fragment_id','page_id','book_id','catalog_generation','grade','viewer_page','fragment_sequence','candidate_type','token_count','char_count','question_mark_count','imperative_signal_count','material_signal','project_signal','experiment_signal','assessment_signal','activity_signal','text_sha256','segmenter_version','source_structure_class','classification_certainty','uncertain_boundary']
    with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(allfrags)
    with fail.open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['page_id','book_id','status','fragment_count']);w.writerows(failures)
    print(f'{args.book_id}: eligible_pages={len(structure)} fragments={len(allfrags)} failures={len(failures)}')

if __name__=='__main__':main()
