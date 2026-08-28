# LTMD-U1 — FTRL completion ledger 0.7

**Effective date:** 2026-08-28  
**Status:** active after verified W7 Formación Cívica y Ética computational and archival closure of the source-admitted cohort.

## What changes in 0.7

Ledger 0.7 promotes only the **25 source-admitted W7 identities** from `pending/not_started` to `validated/archival_complete`. The five documented source retentions remain excluded from FTRL processing and retain `blocked_active_retention` status:

- `H2014P5FCA` — one unresolved internal source position; its 224 served JPEGs do not authorize partial admission;
- `H2018P3FCA`;
- `H2018P4FCA`;
- `H2018P5FCA`;
- `H2018P6FCA`.

No alias, imputation or inferred equivalence is introduced for those identities.

The exhaustive run `33207787127` on commit `02024976ec3d87827460b8b610abe499d870db13` validated the exact union of **3,261/3,261 source pages** across the 25 admitted books. JSONL OCR page cardinality, SQLite pages, FTS5 rows and detailed QC are each 3,261. The public global evidence contains 150 product descriptors (75 restricted-product hashes and 75 text-free-product hashes), not restricted plaintext.

Each of the 25 restricted book handoffs was encrypted before temporary Actions upload, copied to the private archive, redownloaded and SHA-256 verified. The handoffs were then decrypted only in a private transient workspace. All **150/150 contained products** matched the public evidence by byte size and SHA-256. The private consolidated archive contains those 150 products plus its private manifest, is **6,666,433 bytes**, and has SHA-256 `f81272e4a86e432dd27cf0d4c769f06f7561a31e22236af74554bb2d024bcbd9`. Its redownload from the private archive reproduced the same size and checksum. The private archive-closure record was likewise persisted and redownload-verified.

## Derived U1 FTRL state

After W7 promotion:

- documentary denominator: **542 identities**;
- effective technical coverage: **524/542** — unchanged;
- FTRL `validated + archival_complete`: **273/542 identities**;
- validated canonical FTRL objects: **245**;
- canonical source pages represented by validated FTRL objects: **41,315**;
- strict terminal identities (`validated` + final technical exceptions): **278/542**;
- remaining identities: **264**;
- processable FTRL identities still pending: **251**;
- active source retentions: **13**;
- final technical exceptions: **5**;
- `text_verified`: **0/542**;
- `semantic_ready`: **0/542**.

These values are generated from the exhaustive 542-row ledger. W7 contributes exactly 25 validated identities; its five retained identities remain outside the numerator.

## Epistemic boundary

W7 is computationally and archivally closed **for the 25 source-admitted canonical objects**. This does not make the five retained identities complete, does not mean OCR has been human-verified, and does not validate semantic coding or historical interpretation.

The following inequalities remain binding:

`computationally_validated != semantic_ready`  
`ocr_available != text_verified`  
`retained_source_identity != alias_candidate`  
`search_hit != historical_claim`  
`zero_hits != demonstrated_absence`

Human semantic work remains intentionally paused.

## Next technical lane

With W7 closed, the preregistered non-human FTRL sequence continues with **W8 Artes**, followed by W10, W11 and W2. Any later recovery of a retained W7 source must enter through explicit source evidence and a new versioned reconciliation; it cannot be inferred from the present closure.
