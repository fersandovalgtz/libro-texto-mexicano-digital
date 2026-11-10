#!/usr/bin/env python3
"""Build a portable, public-safe longitudinal LTMD-U1 atlas research preview.

Offline preview only, not the operated LTMD Research interface. No private ledger,
OCR, page identifiers, source assets or credentials may enter this build.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

VERSION = "LTMD_U1_LONGITUDINAL_ATLAS_PREVIEW_0.1"
FILES = {
    "generations": "ltmd_analytics_indigenous_generation_0_1.csv",
    "terms": "ltmd_analytics_indigenous_explicit_terms_0_1.csv",
    "validation": "ltmd_analytics_indigenous_validation_state_0_1.csv",
}
GEN_COLUMNS = ("generation", "corpus_total_pages", "candidate_pages", "explicit_general_pages",
               "named_language_contextual_pages", "candidate_books",
               "candidate_pages_per_1000_corpus_pages", "epistemic_state")
TERM_COLUMNS = ("explicit_term", "generation", "candidate_pages", "candidate_books", "epistemic_state")
YEARS = (1960, 1966, 1972, 1982, 1988, 1993, 2008, 2011, 2014, 2018, 2019)
COHORTS = {1960: "1960–1966", 1966: "1960–1966", 1972: "1972–1988",
           1982: "1972–1988", 1988: "1972–1988", 1993: "1993",
           2008: "2008–2011", 2011: "2008–2011", 2014: "2014–2019",
           2018: "2014–2019", 2019: "2014–2019"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_csv(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != columns:
            raise ValueError(f"unexpected CSV fields in {path.name}; refuse possible source leakage")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"malformed CSV rows: {path.name}")
    return rows


def positive_int(raw: str, field: str, *, zero: bool = True) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if value < 0 or (not zero and value == 0):
        raise ValueError(f"invalid {field}")
    return value


def build_payload(data_dir: Path) -> dict:
    manifest_path = data_dir / "ltmd_analytics_indigenous_manifest_0_1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    state = manifest["scientific_state"]
    if state.get("human_validation_complete") is not False or state.get("semantic_ready_promotions") != 0:
        raise ValueError("unsupported human validation state; do not relabel results")
    for name in FILES.values():
        expected = manifest["outputs"][name]["sha256"]
        actual = sha256(data_dir / name)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {name}: expected {expected}, found {actual}")

    generation_rows = strict_csv(data_dir / FILES["generations"], GEN_COLUMNS)
    term_rows = strict_csv(data_dir / FILES["terms"], TERM_COLUMNS)
    validation_rows = strict_csv(data_dir / FILES["validation"], ("validation_status", "candidate_pages"))
    if len(validation_rows) != 1 or validation_rows[0]["validation_status"] != "not_visually_validated":
        raise ValueError("human validation state is not the expected deferred state")
    generations = []
    for row in generation_rows:
        year = positive_int(row["generation"], "generation", zero=False)
        pages = positive_int(row["corpus_total_pages"], "corpus_total_pages", zero=False)
        candidates = positive_int(row["candidate_pages"], "candidate_pages")
        explicit = positive_int(row["explicit_general_pages"], "explicit_general_pages")
        named = positive_int(row["named_language_contextual_pages"], "named_language_contextual_pages")
        books = positive_int(row["candidate_books"], "candidate_books")
        if year not in YEARS or row["epistemic_state"] != "exploratory_signal":
            raise ValueError("unexpected generation or epistemic state")
        if max(candidates, explicit, named) > pages or explicit > candidates or named > candidates or books > candidates:
            raise ValueError("invalid generation counts")
        rate = round(1000 * candidates / pages, 4)
        if abs(rate - float(row["candidate_pages_per_1000_corpus_pages"])) > 0.00015:
            raise ValueError(f"rate/denominator mismatch in {year}")
        generations.append({"year": year, "cohort": COHORTS[year], "pages": pages, "candidates": candidates,
                            "explicit": explicit, "named": named, "books": books, "rate": rate})
    if [r["year"] for r in generations] != list(YEARS):
        raise ValueError("generation identity/order/coverage mismatch")
    if len(generations) != manifest["cardinality"]["generation_rows"]:
        raise ValueError("generation cardinality mismatch")
    if sum(r["candidates"] for r in generations) != manifest["cardinality"]["candidate_pages"]:
        raise ValueError("candidate total mismatch")
    if sum(r["candidates"] for r in generations) != positive_int(validation_rows[0]["candidate_pages"], "validation candidates"):
        raise ValueError("validation state total mismatch")

    terms = []
    for row in term_rows:
        year = positive_int(row["generation"], "generation", zero=False)
        pages = positive_int(row["candidate_pages"], "candidate_pages")
        books = positive_int(row["candidate_books"], "candidate_books")
        label = row["explicit_term"].strip()
        if year not in YEARS or not label or len(label) > 90 or books > pages or row["epistemic_state"] != "computational_candidate":
            raise ValueError("invalid explicit term aggregation")
        if pages > next(r["candidates"] for r in generations if r["year"] == year):
            raise ValueError("term count exceeds generation candidates")
        terms.append({"term": label, "year": year, "candidates": pages, "books": books})
    if len(terms) != manifest["cardinality"]["explicit_term_rows"]:
        raise ValueError("term cardinality mismatch")

    return {
        "version": VERSION,
        "source_version": manifest["version"],
        "source_analysis_version": manifest["source_analysis_version"],
        "source_manifest_sha256": sha256(manifest_path),
        "human_validation_complete": False,
        "state": "exploratory_signal",
        "warning": "Coincidencias automáticas NO validadas visualmente; no son prevalencias históricas confirmadas.",
        "generation_rows": generations,
        "explicit_term_rows": terms,
        "totals": {"generation_observations": sum(r["candidates"] for r in generations),
                   "corpus_pages": sum(r["pages"] for r in generations)},
    }


HTML = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LTMD-U1 · Atlas longitudinal exploratorio</title>
<style>
:root{--wine:#71192b;--blue:#12304a;--gold:#b88a35;--paper:#f6f3ec;--line:#d7d4cd}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:#1b2833;font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header{padding:28px max(22px,calc((100% - 1150px)/2));background:var(--blue);color:#fff}h1{margin:.2em 0;font-size:clamp(1.5rem,3vw,2.6rem)}
main{max-width:1150px;margin:auto;padding:24px}h2{font-size:1.35rem;color:var(--blue)}.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:.75rem;color:#d8bb77}
.note{background:#fff5d7;border-left:5px solid var(--gold);padding:14px 18px;margin:18px 0}
.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px;margin:18px 0;box-shadow:0 3px 12px #12304a0b}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{background:#f8f8f7;padding:12px;border-radius:10px}.card strong{font-size:1.8rem;color:var(--wine);display:block}
.controls{display:flex;flex-wrap:wrap;gap:14px;margin:16px 0}label{font-weight:600;display:grid;gap:5px}select,button{font:inherit;padding:9px;border:1px solid #8998a3;border-radius:7px;background:#fff;color:#142b40}
button{background:var(--wine);border-color:var(--wine);color:white;cursor:pointer}button:focus-visible,select:focus-visible{outline:3px solid var(--gold)}
#chart{width:100%;height:auto;overflow:visible} .chartwrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:.92rem}th,td{padding:9px 8px;border-bottom:1px solid var(--line);text-align:left}thead{background:#edf0f2}td.num{text-align:right;font-variant-numeric:tabular-nums}th.num{text-align:right}
small,.muted{color:#52616b}.legend{display:flex;align-items:center;gap:8px;font-size:.9rem;margin:8px 0}.square{width:13px;height:13px;background:var(--wine)}
@media(max-width:720px){.cards{grid-template-columns:1fr}main{padding:12px}.panel{padding:14px}header{padding:22px}}
</style></head><body><header><div class="eyebrow">Universidad CEEES · Investigación documental</div><h1>Atlas longitudinal de libros de texto mexicanos</h1><div>LTMD-U1 · Lenguas indígenas · Demostración local de resultados agregados, no despliegue público</div></header>
<main><div class="note" role="status"><strong>Alcance científico:</strong> resultados computacionales exploratorios, sin validación visual/humana. No inferir ausencia, continuidad histórica ni cambios curriculares verificados. Sin PDF, páginas fuente ni OCR reproducido.</div>
<section class="panel" aria-labelledby="resumen"><h2 id="resumen">Cobertura y observaciones</h2><div class="cards"><div class="card"><small>Generaciones representadas</small><strong id="totalgenerations"></strong><small>observaciones editoriales, no años continuos</small></div><div class="card"><small>Páginas del corpus en cortes observados</small><strong id="totalpages"></strong><small>denominador agregado</small></div><div class="card"><small>Páginas candidatas</small><strong id="totalcandidates"></strong><small>automáticas, no validadas</small></div></div></section>
<section class="panel" aria-labelledby="serie"><h2 id="serie">Serie de candidatos por 1,000 páginas</h2><p class="muted">Cada punto representa una generación realmente observada. Los años sin medición no se interpolan; las barras no implican continuidad anual.</p><div class="chartwrap"><svg id="chart" viewBox="0 0 980 390" role="img" aria-label="Tasa de páginas candidatas por 1.000 páginas según generación" xmlns="http://www.w3.org/2000/svg"></svg></div><div class="legend"><span class="square"></span>Tasa observada (candidatos por 1,000 páginas)</div><p><small>La unidad es la generación documental, no la población de estudiantes. Se registran posibles reutilizaciones editoriales entre generaciones.</small></p></section>
<section class="panel" aria-labelledby="comparacion"><h2 id="comparacion">Comparar dos generaciones</h2><div class="controls"><label>Generación A <select id="yearA"></select></label><label>Generación B <select id="yearB"></select></label><label>Término explícito <select id="term"><option value="">Todos los términos — mostrar por separado</option></select></label></div><div id="comparison" aria-live="polite"></div><p><small>Las categorías «explícito general» y «lengua nombrada en contexto» se solapan. No se deben sumar. Los libros candidatos no pueden agregarse entre generaciones para deducir libros únicos.</small></p></section>
<section class="panel" aria-labelledby="terminos"><h2 id="terminos">Términos explícitos registrados</h2><p class="muted">La selección de un término no modifica la serie general: cada término representa un subconjunto de coincidencias, que puede superponerse con otros.</p><div style="overflow-x:auto"><table><thead><tr><th>Término</th><th>Generación</th><th class="num">Páginas candidatas</th><th class="num">Libros candidatos</th></tr></thead><tbody id="termsbody"></tbody></table></div></section>
<section class="panel"><h2>Procedencia, límites y descarga</h2><p id="provenance"></p><p><button type="button" id="download">Exportar selección a JSON</button></p><p><small>Fuente original: <a href="https://github.com/fersandovalgtz/libro-texto-mexicano-digital/tree/main/data/analytics">derivados agregados de LTMD-U1</a>. Uso exploratorio; resultado reproducible contra el manifiesto versionado. La exportación no contiene OCR, texto fuente, claves de página ni documentos protegidos.</small></p></section>
</main><script id="ltmd-data" type="application/json">__DATA_JSON__</script>
<script>
'use strict';const data=JSON.parse(document.getElementById('ltmd-data').textContent),generations=data.generation_rows,terms=data.explicit_term_rows;
const $=id=>document.getElementById(id), fmt=n=>new Intl.NumberFormat('es-MX').format(n);
$('totalgenerations').textContent=generations.length;$('totalpages').textContent=fmt(data.totals.corpus_pages);$('totalcandidates').textContent=fmt(data.totals.generation_observations);
const yearA=$('yearA'),yearB=$('yearB'),term=$('term');
for(const g of generations){for(const select of [yearA,yearB]){const opt=document.createElement('option');opt.value=g.year;opt.textContent=g.year+' · '+g.cohort;select.appendChild(opt)}}
yearA.value='1993';yearB.value='2014';for(const t of [...new Set(terms.map(t=>t.term))].sort()){const o=document.createElement('option');o.value=t;o.textContent=t;term.appendChild(o)}
const ns='http://www.w3.org/2000/svg';function node(tag,attrs={},txt){const el=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));if(txt!==undefined)el.textContent=txt;return el}
function chart(){const svg=$('chart');svg.replaceChildren();const x0=68,x1=938,y0=32,y1=320,max=Math.ceil(Math.max(...generations.map(g=>g.rate))/5)*5;
for(let v=0;v<=max;v+=5){let y=y1-(y1-y0)*v/max;svg.appendChild(node('line',{x1:x0,y1:y,x2:x1,y2:y,stroke:'#d9dee1'}));svg.appendChild(node('text',{x:55,y:y+4,'text-anchor':'end','font-size':13,fill:'#435261'},String(v)))}
const pts=generations.map((g,i)=>[x0+i*(x1-x0)/(generations.length-1),y1-(y1-y0)*g.rate/max]);
generations.forEach((g,i)=>{let [x,y]=pts[i];const bar=node('rect',{x:x-15,y,width:30,height:y1-y,fill:'#71192b'});bar.appendChild(node('title',{},`${g.year}: ${g.rate} candidatos por 1,000 páginas`));svg.appendChild(bar);svg.appendChild(node('text',{x,y:345,'text-anchor':'middle','font-size':13,fill:'#12304a'},String(g.year)))});svg.appendChild(node('text',{x:28,y:20,'font-size':12,fill:'#4a5b68'},'Candidatos por 1,000 páginas'))}
function compare(){const a=generations.find(g=>String(g.year)===yearA.value),b=generations.find(g=>String(g.year)===yearB.value);const rows=[['Páginas del corpus',a.pages,b.pages],['Páginas candidatas',a.candidates,b.candidates],['Tasa por 1,000 páginas',a.rate,b.rate],['Candidatas explícitas generales',a.explicit,b.explicit],['Candidatas lengua nombrada en contexto',a.named,b.named],['Libros candidatos por generación',a.books,b.books]];
const table=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const t of ['Indicador',String(a.year),String(b.year)]){const th=document.createElement('th');th.textContent=t;tr.append(th)}head.append(tr);table.append(head);const body=document.createElement('tbody');for(const [label,av,bv] of rows){const tr=document.createElement('tr');for(const v of [label,fmt(av),fmt(bv)]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}table.append(body);$('comparison').replaceChildren(table);
const selected=terms.filter(t=>(!term.value||t.term===term.value)&&(t.year===a.year||t.year===b.year));const tbody=$('termsbody');tbody.replaceChildren();for(const t of selected.sort((x,y)=>x.term.localeCompare(y.term)||x.year-y.year)){const tr=document.createElement('tr');for(const v of [t.term,t.year,t.candidates,t.books]){const td=document.createElement('td');td.textContent=String(v);tr.append(td)}tbody.append(tr)}if(!selected.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=4;td.textContent='Sin coincidencias registradas para la selección';tr.append(td);tbody.append(tr)}}
for(const c of [yearA,yearB,term])c.addEventListener('change',compare);$('provenance').textContent=`Versión: ${data.version} · materialización: ${data.source_version} · análisis: ${data.source_analysis_version} · SHA-256 del manifiesto: ${data.source_manifest_sha256}. Validación humana completa: NO. Estados: exploratory_signal / computational_candidate.`;
$('download').addEventListener('click',()=>{const chosen=new Set([Number(yearA.value),Number(yearB.value)]),payload={version:data.version,source_manifest_sha256:data.source_manifest_sha256,state:data.state,human_validation_complete:false,warnings:[data.warning,'Las sumas de términos o de libros entre generaciones NO son conteos únicos.'],generations:generations.filter(x=>chosen.has(x.year)),terms:terms.filter(x=>chosen.has(x.year)&&(!term.value||x.term===term.value))};const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));a.href=u;a.download='ltmd_u1_comparacion_exploratoria.json';a.click();URL.revokeObjectURL(u)});
chart();compare();
</script></body></html>'''


def render_html(payload: dict) -> str:
    # Keep only allowlisted aggregate structures. JSON escaped for inline script safety.
    safe = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    safe = safe.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return HTML.replace("__DATA_JSON__", safe)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "analytics")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_payload(args.input_dir)
    rendered = render_html(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({"version": VERSION, "output": str(args.output),
                      "generations": len(result["generation_rows"]),
                      "candidate_observations": result["totals"]["generation_observations"],
                      "corpus_pages": result["totals"]["corpus_pages"],
                      "human_validation_complete": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
