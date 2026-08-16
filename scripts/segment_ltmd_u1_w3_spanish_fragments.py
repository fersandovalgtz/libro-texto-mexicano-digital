#!/usr/bin/env python3
"""Per-viewer, SHA-verified FRAGSEG for canonical LTMD-U1 W3 Español/Lengua."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import subprocess
import tempfile
import time
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

STRUCTURE = Path('data/catalog/ltmd_u1_w3_spanish_page_structure.csv')
MANIFEST = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
VERSION = 'FRAGSEG_LTMD_U1_W3_SPANISH_0.1'
ELIGIBLE = {'textual', 'mixed_text_image'}
UA = 'LibroTextoMexicanoDigital/U1-W3 Spanish FRAGSEG 0.1'
IMPERATIVES = [
    'observa','describe','escribe','explica','compara','clasifica','mide','realiza','investiga','discute',
    'comenta','elabora','construye','dibuja','resuelve','contesta','responde','identifica','señala','anota',
    'registra','lee','analiza','calcula','reúne','busca','consulta','organiza','completa','marca','subraya',
    'recorta','pega','coloca','haz','forma','trabaja','elige','decide','propón','propone','predice','infiere',
    'redacta','copia','relaciona','ordena','encierra','pronuncia','repite'
]
QUESTION_START = ['qué','que','cómo','como','cuál','cual','cuáles','cuales','por qué','por que','dónde','donde','cuándo','cuando','quién','quien']
MATERIAL_WORDS = ['materiales','necesitas','vas a necesitar','material']
PROJECT_WORDS = ['proyecto','proyectos']
EXPERIMENT_WORDS = ['experimento','experimenta','experimentación','procedimiento','hipótesis']
ASSESS_WORDS = ['evaluación','autoevaluación','qué aprendí','lo que aprendí','evalúa']
ACTIVITY_WORDS = ['actividad','en equipo','trabaja en equipo','por equipos','con tus compañeros']
FIELDS = [
    'fragment_id','page_id','viewer_key','catalog_generation','grade','title_core','viewer_page',
    'fragment_sequence','candidate_type','token_count','char_count','question_mark_count',
    'imperative_signal_count','material_signal','project_signal','experiment_signal','assessment_signal',
    'activity_signal','text_sha256','segmenter_version','source_structure_class',
    'classification_certainty','uncertain_boundary'
]


def norm(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()


def low(text):
    return norm(text).casefold()


def token_count(text):
    return len(re.findall(r'\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b', text, flags=re.UNICODE))


def signal_count(text, terms):
    t = low(text)
    return sum(t.count(x.casefold()) for x in terms)


def candidate_type(text):
    t = low(text)
    q = text.count('?') + text.count('¿')
    imp = signal_count(text, IMPERATIVES)
    mat = int(any(x in t for x in MATERIAL_WORDS))
    proj = int(any(x in t for x in PROJECT_WORDS))
    exp = int(any(x in t for x in EXPERIMENT_WORDS))
    assess = int(any(x in t for x in ASSESS_WORDS))
    activity = int(any(x in t for x in ACTIVITY_WORDS))
    starts_q = any(t.startswith(x + ' ') or t.startswith('¿' + x) for x in QUESTION_START)
    if assess:
        typ = 'assessment_candidate'
    elif proj:
        typ = 'project_candidate'
    elif exp or (mat and imp):
        typ = 'experiment_candidate'
    elif activity:
        typ = 'activity_candidate'
    elif q or starts_q:
        typ = 'question_candidate'
    elif imp:
        typ = 'instruction_candidate'
    elif token_count(text) <= 12 and len(text) <= 100:
        typ = 'short_residual_candidate'
    elif token_count(text) >= 4:
        typ = 'expository_candidate'
    else:
        typ = 'other_candidate'
    return typ, {'q': q, 'imp': imp, 'mat': mat, 'proj': proj, 'exp': exp, 'assess': assess, 'activity': activity}


def read_tsv(path):
    with path.open(encoding='utf-8', errors='replace', newline='') as f:
        out = []
        for row in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            if row.get('level') != '5':
                continue
            text = norm(row.get('text', ''))
            if text:
                out.append(row | {'text': text})
        return out


def reconstruct_paragraphs(rows):
    groups = defaultdict(list)
    order = []
    for row in rows:
        key = (row.get('page_num'), row.get('block_num'), row.get('par_num'))
        if key not in groups:
            order.append(key)
        groups[key].append(row)
    paragraphs = []
    for key in order:
        line_groups = defaultdict(list)
        line_order = []
        for row in groups[key]:
            line = row.get('line_num')
            if line not in line_groups:
                line_order.append(line)
            line_groups[line].append(row)
        text = norm(' '.join(norm(' '.join(x['text'] for x in line_groups[line])) for line in line_order))
        if text:
            paragraphs.append(text)
    return paragraphs


def sentence_units(paragraph):
    return [norm(x) for x in re.split(r'(?<=[\?\!\.])\s+(?=[¿¡A-ZÁÉÍÓÚÜÑ0-9])', paragraph) if norm(x)]


def merge_units(units):
    out = []
    for unit in units:
        typ, sig = candidate_type(unit)
        n = token_count(unit)
        if not out:
            out.append([unit, typ, sig, n])
            continue
        prev = out[-1]
        if typ == 'expository_candidate' and prev[1] == typ and prev[3] + n <= 120:
            prev[0] = norm(prev[0] + ' ' + unit)
            prev[3] += n
            for key, value in sig.items():
                prev[2][key] += value
        else:
            out.append([unit, typ, sig, n])
    return out


def download_verify(src, dest, attempts=3):
    last = None
    for attempt in range(1, attempts + 1):
        try:
            h = hashlib.sha256()
            total = 0
            with urlopen(Request(src['source_asset_url'], headers={'User-Agent': UA}), timeout=45) as response, dest.open('wb') as f:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    h.update(block)
                    total += len(block)
                    f.write(block)
            if h.hexdigest() != src['sha256']:
                raise RuntimeError('canonical source SHA mismatch')
            if src.get('byte_size') and total != int(src['byte_size']):
                raise RuntimeError('canonical source byte-size mismatch')
            return
        except Exception as exc:
            last = exc
            dest.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(attempt * 2)
    raise last


def run_tesseract(image, outbase, psm):
    env = os.environ.copy()
    env['OMP_THREAD_LIMIT'] = '1'
    cp = subprocess.run(
        ['tesseract', str(image), str(outbase), '-l', 'spa', '--psm', str(psm), 'tsv'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90, check=False, env=env
    )
    return cp.returncode == 0 and outbase.with_suffix('.tsv').exists()


def process_page(row, src, temp):
    page = int(row['viewer_page'])
    psm = row['selected_psm'] or '3'
    stem = re.sub(r'[^A-Za-z0-9_.-]+', '_', row['page_id'])
    image = temp / f'{stem}.jpg'
    outbase = temp / stem
    download_verify(src, image)
    if not run_tesseract(image, outbase, psm):
        return [], 'ocr_failed'
    units = []
    for paragraph in reconstruct_paragraphs(read_tsv(outbase.with_suffix('.tsv'))):
        units.extend(sentence_units(paragraph))
    fragments = []
    for seq, (text, typ, sig, n) in enumerate(merge_units(units), 1):
        if n == 0:
            continue
        fragments.append({
            'fragment_id': f"{row['page_id']}-F{seq:03d}",
            'page_id': row['page_id'],
            'viewer_key': row['viewer_key'],
            'catalog_generation': row['catalog_generation'],
            'grade': row['grade'],
            'title_core': row['title_core'],
            'viewer_page': page,
            'fragment_sequence': seq,
            'candidate_type': typ,
            'token_count': n,
            'char_count': len(text),
            'question_mark_count': sig['q'],
            'imperative_signal_count': sig['imp'],
            'material_signal': sig['mat'],
            'project_signal': sig['proj'],
            'experiment_signal': sig['exp'],
            'assessment_signal': sig['assess'],
            'activity_signal': sig['activity'],
            'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'segmenter_version': VERSION,
            'source_structure_class': row['primary_structure'],
            'classification_certainty': row['classification_certainty'],
            'uncertain_boundary': int(n > 500 or (typ == 'other_candidate' and n < 4)),
        })
    return fragments, 'ok'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewer-key', required=True)
    parser.add_argument('--output-dir', default='data/work/ltmd_u1_w3_spanish_fragments')
    args = parser.parse_args()

    structure = [
        r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8', newline=''))
        if r['viewer_key'] == args.viewer_key and r['primary_structure'] in ELIGIBLE
    ]
    sources = {
        (r['viewer_key'], int(r['viewer_page'])): r
        for r in csv.DictReader(MANIFEST.open(encoding='utf-8', newline=''))
        if r['asset_status'] == 'source_jpeg'
    }
    if not structure:
        raise SystemExit(f'no eligible PAGESTRUCT rows for {args.viewer_key}')

    allfrags = []
    failures = []
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w3-spanish-frag-') as td:
        temp = Path(td)
        for row in structure:
            try:
                fragments, status = process_page(row, sources[(args.viewer_key, int(row['viewer_page']))], temp)
            except Exception as exc:
                fragments, status = [], f'exception:{type(exc).__name__}'
            if status != 'ok' or not fragments:
                failures.append((row['page_id'], row['viewer_key'], status, len(fragments)))
            allfrags.extend(fragments)
            for path in temp.iterdir():
                path.unlink(missing_ok=True)

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f'fragment_{args.viewer_key.lower()}.csv'
    fail = outdir / f'fragment_{args.viewer_key.lower()}_failures.csv'
    with out.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(allfrags)
    with fail.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['page_id','viewer_key','status','fragment_count'])
        writer.writerows(failures)

    fatal = [x for x in failures if x[2] != 'ok']
    empty = len(failures) - len(fatal)
    print(f'{args.viewer_key}: eligible_pages={len(structure)} fragments={len(allfrags)} empty_pages={empty} fatal_failures={len(fatal)}')
    if fatal:
        raise SystemExit(f'{args.viewer_key}: {len(fatal)} source/OCR execution failures; refusing shard publication')


if __name__ == '__main__':
    main()
