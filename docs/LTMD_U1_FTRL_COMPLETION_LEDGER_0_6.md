# LTMD-U1 — FTRL completion ledger 0.6

**Effective date:** 2026-08-27  
**Status:** active after verified W9 Educación Física computational and archival closure.

## What changes in 0.6

Ledger 0.6 promotes only W9 Educación Física from `pending/not_started` to `validated/archival_complete` after the current FTRL contract was rerun over the already versioned SHA-256 source topology.

W9 comprises four historical identities and four canonical processing objects:

- `H2008P1ED252` — 114 source pages;
- `H2008P2ED260` — 106 source pages;
- `H2008P5ED280` — 114 source pages;
- `H2008P6ED287` — 114 source pages.

The exhaustive run `33124903433` on commit `ac1cb91220cb09aeb24cce11c1f9a44f303fdacc` validated the exact 448-page union, SHA-bound source assets, page OCR corpus, SQLite/FTS5 cardinality and technical QC. The restricted products were encrypted before temporary Actions handoff. Four encrypted handoffs were then preserved independently, redownloaded and checksum-verified in the private archive. Their decrypted contents were validated transiently, consolidated into a private archive, persisted, redownloaded and SHA-256 verified again. The public repository stores only metadata and text-free evidence.

The prior W9 OCR metrics remain provenance/continuity evidence only; the older full OCR text was not persisted and therefore was not promoted directly into FTRL.

## Derived U1 FTRL state

After W9 promotion:

- documentary denominator: **542 identities**;
- effective technical coverage: **524/542** — unchanged;
- FTRL `validated + archival_complete`: **248/542 identities**;
- validated canonical FTRL objects: **220**;
- canonical source pages represented by validated FTRL objects: **38,054**;
- strict terminal identities (`validated` + final technical exceptions): **253/542**;
- remaining identities: **289**;
- processable FTRL identities still pending: **276**;
- active source retentions: **13**;
- final technical exceptions: **5**;
- `text_verified`: **0/542**;
- `semantic_ready`: **0/542**.

These quantities are generated from the exhaustive 542-row ledger. They are not estimates and do not modify the canonical U1 coverage denominator or the retained-source lifecycle.

## Epistemic boundary

W9 is computationally and archivally closed. That statement does **not** mean that OCR text has been human-verified, that semantic codes are validated, or that search results constitute historical findings.

The following inequalities remain binding:

`computationally_validated != semantic_ready`  
`ocr_available != text_verified`  
`search_hit != historical_claim`  
`zero_hits != demonstrated_absence`

Human semantic work remains intentionally paused. No `model lock`, private validation holdout opening or historical semantic inference follows from this FTRL promotion.

## Next technical lane

With W9 closed, the preregistered non-human FTRL sequence continues with **W7 Formación Cívica y Ética**, followed by W8, W10, W11 and W2. W7 must preserve its documentary distinction between the **25 source-admitted identities** available for processing and the **5 active retentions**; those five retentions cannot be silently absorbed into the FTRL numerator.
