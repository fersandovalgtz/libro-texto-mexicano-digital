# Universal Full-Text Research Layer (FTRL)

## Purpose

The LTMD Full-Text Research Layer is a reproducible technical pipeline for building page-level OCR and a searchable local full-text index across the source-admitted universe of *Libros de Texto Gratuitos* represented in the repository. Its architecture is deliberately independent of any one subject, historical period, query, or wave.

The processing chain is:

`global LTMD coverage → canonical identity topology → heterogeneous source manifests → normalized source contract → SHA-256 verified page assets → reproducible OCR → SQLite FTS5 → arbitrary research queries`

W5 (Historia) remains useful as a bounded real-world integration fixture because it was the first wave on which the OCR path was exercised end to end. It is not the conceptual center of the FTRL and does not define universal counts, schemas, search examples, or execution logic.

## Scientific status of each layer

The pipeline distinguishes technical availability from scholarly interpretation. `ocr_available` does not mean `text_verified`; a search hit is not by itself a historical claim; zero hits are not a demonstrated absence; and a shared or contextually similar page asset does not by itself establish semantic equivalence between historical identities. Technical validation, OCR-quality assessment, semantic verification, and historical interpretation are separate stages.

The identity map also preserves the distinction between historical identities and canonical processing objects. An inherited alias can point to a canonical source object for reproducible processing without erasing the historical identity or asserting that every scholarly use should treat the two records as equivalent.

## Source normalization

`data/catalog/ltmd_u1_ftrl_source_registry.csv` is the declarative registry of audited page manifests. Each source dataset maps its native column names to one common contract. `scripts/normalize_ftrl_sources.py` reads only registered manifests and the global coverage/identity topology; it does not discover or download new assets.

The normalized source contract records, at minimum:

- source dataset and manifest provenance;
- wave and operational domain;
- canonical viewer key;
- catalog generation and grade;
- title when authoritative or recoverable from the global coverage registry;
- viewer/page coordinates;
- effective source asset URL;
- admitted asset status;
- source byte size when known; and
- audited source SHA-256.

Missing optional metadata is not imputed. Admitted page rows require a valid SHA-256 before entering OCR.

## Universal execution

A metadata-only plan can be produced without downloading images or invoking OCR:

```bash
python scripts/run_ftrl_universal.py --plan-only
```

This first normalizes every default-enabled registered source and derives the expected page count from the resulting admitted rows. No wave-specific total is hard-coded.

A resumable local execution can then use multiple canonical-object shards:

```bash
python scripts/run_ftrl_universal.py \
  --work-dir local/ftrl-u1 \
  --workers 4 \
  --resume
```

The runner partitions sorted canonical viewer keys deterministically, invokes the page OCR builder, merges shard outputs in a stable order, verifies that the merged page count equals the normalized source universe, builds the universal SQLite FTS5 index, and runs corpus/database validation.

Full OCR JSONL, cached page images, and SQLite databases belong under `local/` by default and are intentionally excluded from normal Git history.

## Querying

The index supports arbitrary FTS5 queries and orthogonal metadata filters. For example:

```bash
python scripts/query_ocr_corpus.py \
  --db local/ftrl-u1/fulltext.sqlite \
  --query 'territorio' \
  --wave W6 \
  --domain geografia_atlas \
  --format json
```

Filters are available for wave, catalog generation, grade, operational domain, viewer identity, and source dataset. Results include page locators, source hashes, provenance, OCR hashes, snippets, ranking, and the historical identities mapped to the canonical processing object.

Search output is evidence for locating candidate passages, not a substitute for inspecting the source page and validating the OCR in scholarly use.

## Continuous integration

`.github/workflows/validate-ftrl-universal.yml` performs only bounded, text-safe validation. It compiles the pipeline scripts, normalizes and plans the complete registered source universe without downloading assets, and exercises the universal SQLite/query contract on a synthetic cross-wave/cross-domain fixture. CI artifacts contain normalization evidence and planning metadata, not a mass OCR corpus.

A full U1 OCR run is therefore a separately controlled research execution rather than an automatic pull-request side effect.

## Rights and archival policy

Source hashes, provenance, schemas, manifests, code, and small text-free validation evidence can be versioned in GitHub. Complete OCR text and bulk source-image derivatives require separate rights review before publication. Large research derivatives may be archived outside GitHub, but any such archive should be accompanied by a repository-side artifact manifest recording its stable location or identifier, byte size, SHA-256, generating software version, source Git commit, generation timestamp, and rights status.
