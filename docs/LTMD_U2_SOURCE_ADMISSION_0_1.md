# LTMD-U2 — Source admission 0.1

## Scope

This layer establishes source admission for the 39 canonical LTMD-U2 source objects corresponding to CONALITEG primary-school materials in the 2026–2027 catalog cohort.

Source admission is deliberately narrower than textual availability. An object is `admitted_full_body_verified` only when the institutional PDF response was streamed in full and the observation simultaneously satisfied all of the following conditions:

- HTTP 200;
- `application/pdf` content type;
- received byte count equal to the byte count previously observed in the asset-resolution layer;
- valid `%PDF-` signature;
- `startxref` and `%%EOF` markers in the terminal window;
- complete SHA-256 calculated over the streamed body.

The source body is discarded while streaming. LTMD does not persist or redistribute the source PDF in this layer.

## Result

Observation date: 2026-09-02.

- canonical source objects: 39;
- admitted full source bodies: 39/39;
- total source bytes streamed: 1,861,996,041;
- full SHA-256 values materialized: 39;
- source PDF bytes persisted by LTMD: 0;
- OCR availability: not assessed;
- text verification: not assessed;
- semantic validation: not assessed.

The materialized public evidence is `data/catalog/ltmd_u2_source_admission_2026_09_02.csv`. It contains identifiers, institutional URLs, exact byte counts, SHA-256 values, transport/format checks, previously observed page counts, and explicit state guards. It does not contain source pages or source text.

## Reproducibility

The production observer is `scripts/observe_u2_source_admission.py`. It requires network access and is intentionally not run by ordinary CI. CI validates the already materialized evidence with `scripts/validate_u2_source_admission.py` and tests its invariants without downloading source books.

The exhaustive observation was first executed in an isolated experimental branch:

- workflow run: `33652358626`;
- experimental commit: `5dabbdc5d4023767d0fa4821cd8389f280a75936`;
- Actions artifact: `9855311501`;
- artifact SHA-256: `6974a83a81d40569ccdaeec2d8b04b4bf3b21ea33ffc054216bc54361fc5c256`.

The raw experimental artifact was preserved privately outside the public repository before production materialization. The production manifest records hashes for the raw CSV/JSON and the canonical CSV.

## Encryption pilot and text boundary

Before scaling source admission to the full universe, a three-size pilot used P5LPM, P4PEA, and P0CMA. In those three cases `pypdf` reported encrypted PDFs and could not complete parser/text inspection with a blank password. This observation belongs only to the three-object pilot; it must not be generalized to the remaining 36 objects without direct evidence.

More importantly, parser accessibility is not the criterion for source admission. A source body can be fully transported, hashed, size-reconciled, and structurally identified as a PDF even when an independent parser cannot inspect its contents.

Accordingly, this layer preserves the following separations:

- `source_admitted != ocr_available`;
- `source_admitted != text_verified`;
- `source_admitted != openly_licensed`;
- `source_admitted != semantic_ready`.

The next textual layer must independently determine whether a technically usable embedded-text or OCR path exists and must not infer that state from source admission alone.

## Rights and preservation policy

The source books remain third-party institutional materials. Public accessibility does not imply an open license. LTMD therefore publishes only non-substitutive evidence such as identifiers, URLs, hashes, byte counts, structural states, and technical metrics. Full source PDFs and full OCR/text are excluded from this public source-admission layer.
