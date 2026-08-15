#!/usr/bin/env python3
"""Extract a private regional OCR hypothesis from full-page Tesseract TSV.

This script implements the alignment rule preregistered in
`docs/OCR_REGION_ALIGNMENT_ADDENDUM_2026-08-15.md`:

- OCR is produced on the full source page using the pipeline-selected PSM.
- The human evaluation region is defined independently in source-image pixels.
- A TSV word is included iff the geometric center of its bounding box is inside
  the region: x0 <= cx < x1 and y0 <= cy < y1.
- Selected words are reconstructed in Tesseract's TSV reading order, with words
  separated by spaces and OCR lines separated by newlines.

The resulting text is PRIVATE WORKING DATA. Do not commit output files to the
public repository. This script contains no source text itself.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable


def inside_center(row: dict[str, str], box: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = box
    left = float(row['left'])
    top = float(row['top'])
    width = float(row['width'])
    height = float(row['height'])
    cx = left + width / 2.0
    cy = top + height / 2.0
    return x0 <= cx < x1 and y0 <= cy < y1


def word_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for r in rows:
        text = (r.get('text') or '').strip()
        try:
            level = int(r.get('level') or 0)
        except ValueError:
            continue
        if level == 5 and text:
            out.append(r)
    return out


def extract(tsv_path: Path, box: tuple[float, float, float, float]) -> str:
    with tsv_path.open(encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh, delimiter='\t'))

    selected = [r for r in word_rows(rows) if inside_center(r, box)]
    # Tesseract TSV is already emitted in reading order. The tuple below also
    # makes that assumption explicit and deterministic if input rows are ever
    # reordered during private handling.
    selected.sort(key=lambda r: (
        int(r['page_num']), int(r['block_num']), int(r['par_num']),
        int(r['line_num']), int(r['word_num'])
    ))

    lines: list[str] = []
    current_key = None
    current_words: list[str] = []
    for r in selected:
        key = (r['page_num'], r['block_num'], r['par_num'], r['line_num'])
        if current_key is not None and key != current_key:
            if current_words:
                lines.append(' '.join(current_words))
            current_words = []
        current_key = key
        current_words.append(r['text'].strip())
    if current_words:
        lines.append(' '.join(current_words))
    return '\n'.join(lines).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('tsv', type=Path, help='Private full-page Tesseract TSV')
    ap.add_argument('--box', nargs=4, type=float, metavar=('X0','Y0','X1','Y1'), required=True,
                    help='Evaluation region in source-image pixels')
    ap.add_argument('--output', type=Path, help='Private output text file; default stdout')
    args = ap.parse_args()

    x0, y0, x1, y1 = args.box
    if not (x0 < x1 and y0 < y1):
        raise SystemExit('Invalid box: require x0 < x1 and y0 < y1')
    text = extract(args.tsv, (x0, y0, x1, y1))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + ('\n' if text else ''), encoding='utf-8')
        print(f'Wrote private regional hypothesis to {args.output}; chars={len(text)}')
    else:
        print(text)


if __name__ == '__main__':
    main()
