#!/usr/bin/env python3
"""Build a machine-derived technical status for LTMD-U1 waves.

The status is intentionally limited to source/provenance, OCR, PAGESTRUCT,
FRAGSEG and exact-reuse layers. It never upgrades semantic validity merely
because a technical layer exists.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

OUT = Path('docs/LTMD_U1_TECHNICAL_STATUS.md')
VERSION = 'LTMD_U1_TECHNICAL_STATUS_0.1'


def read(path: str):
    p = Path(path)
    return list(csv.DictReader(p.open(encoding='utf-8', newline=''))) if p.exists() else None


def yes(path: str) -> bool:
    return Path(path).exists()


def w2():
    frag = read('data/catalog/ltmd_u1_w2_math_fragment_manifest.csv')
    if frag is None:
        # canonical W2 names may predate the U1 naming convention; use completion doc as state only.
        return {'state': 'complete' if yes('docs/LTMD_U1_W2_COMPLETION.md') else 'unknown'}
    return {'state': 'complete', 'fragments': len(frag)}


def wave3():
    d = {'state': 'source_reconciled'}
    proc = read('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
    man = read('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
    if proc:
        d['identities'] = len(proc)
        d['canonicals'] = sum(r['is_canonical_processing_object'] == '1' for r in proc)
        d['aliases'] = sum(r['ocr_identity_eligible'] == '1' and r['is_canonical_processing_object'] != '1' for r in proc)
        d['source_gaps'] = sum(int(r['persistent_internal_source_gaps'] or 0) for r in proc if r['is_canonical_processing_object'] == '1')
    if man:
        d['source_pages'] = len(man)
    ocr = read('data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv')
    if ocr:
        d['state'] = 'ocr_complete'
        d['ocr_pages'] = len(ocr)
        d['sha_verified'] = sum(r['source_sha256_verified'] == '1' for r in ocr)
        d['text_detected'] = sum(r['ocr_class'] == 'text_detected' for r in ocr)
        d['no_text'] = sum(r['ocr_class'] == 'no_text_detected' for r in ocr)
        d['unresolved'] = sum(r['ocr_class'] == 'unresolved' or r['ocr_status'] != 'ok' for r in ocr)
    struct = read('data/catalog/ltmd_u1_w3_spanish_page_structure.csv')
    if struct:
        d['state'] = 'pagestruct_complete'
        c = Counter(r['primary_structure'] for r in struct)
        d['structure'] = c
        d['frag_eligible'] = c['textual'] + c['mixed_text_image']
    frag = read('data/catalog/ltmd_u1_w3_spanish_fragment_manifest.csv')
    if frag:
        d['state'] = 'fragseg_complete'
        d['fragments'] = len(frag)
        d['fragment_ids_unique'] = len({r['fragment_id'] for r in frag})
        d['candidate_types'] = Counter(r['candidate_type'] for r in frag)
    units = read('data/catalog/ltmd_u1_w3_spanish_exact_content_units.csv')
    overlap = read('data/catalog/ltmd_u1_w3_spanish_exact_viewer_overlap.csv')
    if units is not None and overlap is not None:
        d['state'] = 'exact_reuse_complete'
        d['unique_units'] = len(units)
        d['repeated_units'] = sum(int(r['canonical_occurrence_count']) > 1 for r in units)
        d['cross_viewer_units'] = sum(int(r['canonical_viewer_count']) > 1 for r in units)
        d['overlap_pairs'] = len(overlap)
    if yes('docs/LTMD_U1_W3_COMPLETION.md'):
        d['state'] = 'complete'
    return d


def wave4():
    d = {'state': 'source_reconciled'}
    proc = read('data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv')
    man = read('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv')
    if proc:
        d['identities'] = len(proc)
        d['canonicals'] = sum(r['is_canonical_processing_object'] == '1' for r in proc)
        d['aliases'] = sum(r['ocr_identity_eligible'] == '1' and r['is_canonical_processing_object'] != '1' for r in proc)
        d['source_gaps'] = sum(int(r['persistent_internal_source_gaps'] or 0) for r in proc)
        d['terminal_synthetic'] = sum(int(r['terminal_synthetic_candidates'] or 0) for r in proc)
    if man:
        d['source_pages'] = len(man)
    ocr = read('data/catalog/ltmd_u1_w4_social_sciences_ocr_metrics.csv')
    if ocr:
        d['state'] = 'ocr_complete'
        d['ocr_pages'] = len(ocr)
        d['sha_verified'] = sum(r['source_sha256_verified'] == '1' for r in ocr)
        d['text_detected'] = sum(r['ocr_class'] == 'text_detected' for r in ocr)
        d['no_text'] = sum(r['ocr_class'] == 'no_text_detected' for r in ocr)
        d['unresolved'] = sum(r['ocr_class'] == 'unresolved' or r['ocr_status'] != 'ok' for r in ocr)
    struct = read('data/catalog/ltmd_u1_w4_social_sciences_page_structure.csv')
    if struct:
        d['state'] = 'pagestruct_complete'
        c = Counter(r['primary_structure'] for r in struct)
        d['structure'] = c
        d['frag_eligible'] = c['textual'] + c['mixed_text_image']
    frag = read('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest.csv')
    if frag:
        d['state'] = 'fragseg_complete'
        d['fragments'] = len(frag)
        d['fragment_ids_unique'] = len({r['fragment_id'] for r in frag})
        d['candidate_types'] = Counter(r['candidate_type'] for r in frag)
    units = read('data/catalog/ltmd_u1_w4_social_sciences_exact_content_units.csv')
    overlap = read('data/catalog/ltmd_u1_w4_social_sciences_exact_viewer_overlap.csv')
    if units is not None and overlap is not None:
        d['state'] = 'exact_reuse_complete'
        d['unique_units'] = len(units)
        d['repeated_units'] = sum(int(r['occurrence_count']) > 1 for r in units)
        d['cross_viewer_units'] = sum(int(r['viewer_count']) > 1 for r in units)
        d['overlap_pairs'] = len(overlap)
    if yes('docs/LTMD_U1_W4_COMPLETION.md'):
        d['state'] = 'complete'
    return d


def render_wave(name: str, d: dict):
    lines = [f'## {name}', '', f'Estado técnico derivado: **`{d.get("state", "unknown")}`**.', '']
    simple = [
        ('identities','Identidades'), ('canonicals','Objetos canónicos'), ('aliases','Aliases por provenance'),
        ('source_pages','Páginas fuente canónicas'), ('source_gaps','Huecos internos persistentes'),
        ('terminal_synthetic','Terminales sintéticos excluidos'), ('ocr_pages','Páginas OCR'),
        ('sha_verified','SHA verificados'), ('text_detected','Texto detectado'), ('no_text','Sin texto detectado'),
        ('unresolved','Unresolved'), ('frag_eligible','Páginas elegibles FRAGSEG'), ('fragments','Fragmentos técnicos'),
        ('fragment_ids_unique','IDs de fragmento únicos'), ('unique_units','Unidades textuales exactas únicas'),
        ('repeated_units','Unidades exactas repetidas'), ('cross_viewer_units','Unidades presentes en ≥2 visores'),
        ('overlap_pairs','Pares de visores con solapamiento exacto')
    ]
    for key,label in simple:
        if key in d:
            lines.append(f'- {label}: **{d[key]:,}**.')
    if 'structure' in d:
        lines += ['', '### PAGESTRUCT', '']
        for key in ['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']:
            lines.append(f'- `{key}`: {d["structure"][key]:,}.')
    if 'candidate_types' in d:
        lines += ['', '### Tipos FRAGSEG candidatos', '']
        for key in sorted(d['candidate_types']):
            lines.append(f'- `{key}`: {d["candidate_types"][key]:,}.')
    return lines


def main():
    w3 = wave3(); w4 = wave4(); w2s = w2()
    lines = [
        '# LTMD-U1 — estado técnico derivado por máquina',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Este documento se reconstruye desde los artefactos versionados del repositorio. No convierte la disponibilidad de una capa técnica en validación semántica.',
        '',
        '## Frontera epistemológica vigente',
        '',
        'El proyecto opera temporalmente sin referencia humana. OCR, PAGESTRUCT, FRAGSEG, hashes exactos, provenance y dependencia documental pueden avanzar. CER/WER validado contra referencia, confiabilidad intercodificador, consenso humano y validación SEMB03 permanecen cerrados. `SEMB03` sigue en `WAITING_HUMAN_REFERENCE`.',
        '',
        '## W2 — Matemáticas',
        '',
        f'Estado técnico: **`{w2s.get("state", "unknown")}`**. Véase `docs/LTMD_U1_W2_COMPLETION.md` para el cierre congelado.',
        ''
    ]
    lines += render_wave('W3 — Español/Lengua', w3)
    lines += ['', *render_wave('W4 — Ciencias Sociales', w4)]
    lines += [
        '',
        '## Regla de lectura',
        '',
        'Los conteos anteriores son controles de infraestructura científica. `text_detected` no es CER/WER; las clases PAGESTRUCT son estructurales; los tipos FRAGSEG son candidatos técnicos; y la igualdad de hash sólo documenta igualdad dentro de la representación técnica correspondiente.'
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
