# LTMD-U1 — FTRL completion ledger 0.8

**Effective date:** 2026-08-28  
**Status:** active after verified W8 Artes computational and archival closure of the source-admitted cohort.

## What changes in 0.8

Ledger 0.8 promotes only the **16 source-admitted W8 identities** from `pending/not_started` to `validated/archival_complete`. The four documented 2018 source retentions remain excluded from FTRL processing and retain `blocked_active_retention` status:

- `H2018P3EAA`;
- `H2018P4EAA`;
- `H2018P5EAA`;
- `H2018P6EAA`.

No alias, imputation or inferred equivalence is introduced for those identities.

The exhaustive run `33220988830` on commit `cae2bed8ff79b45675ae194a855abfed9b86aca4` validated the exact union of **1,490/1,490 source pages** across the 16 admitted books. JSONL OCR page cardinality, SQLite pages, FTS5 rows and detailed QC are each 1,490. The public global evidence contains 96 product descriptors: 48 restricted-product hashes and 48 text-free-product hashes, never restricted plaintext.

Each of the 16 restricted book handoffs was encrypted before temporary Actions upload, copied to the private archive, redownloaded and SHA-256 verified. The handoffs were then decrypted only in a private transient workspace. All **96/96 contained products** matched the public evidence by byte size and SHA-256. The private consolidated archive is **3,090,776 bytes** and has SHA-256 `92a7dd0f8eb38c28c582954d947ac8c695020ef21118b13566e2702d51b937d4`. Its redownload from the private archive reproduced the same size and checksum. The private archive-closure record was likewise persisted and redownload-verified.

## Derived U1 FTRL state

After W8 promotion:

- documentary denominator: **542 identities**;
- effective technical coverage: **524/542** — unchanged;
- FTRL `validated + archival_complete`: **289/542 identities**;
- validated canonical FTRL objects: **261**;
- canonical source pages represented by validated FTRL objects: **42,805**;
- strict terminal identities (`validated` + final technical exceptions): **294/542**;
- remaining identities: **248**;
- processable FTRL identities still pending: **235**;
- active source retentions: **13**;
- final technical exceptions: **5**;
- `text_verified`: **0/542**;
- `semantic_ready`: **0/542**.

These values are generated from the exhaustive 542-row ledger. W8 contributes exactly 16 validated identities; its four retained identities remain outside the numerator.

## Epistemic boundary

W8 is computationally and archivally closed **for the 16 source-admitted canonical objects**. This does not make the four retained identities complete, does not mean OCR has been human-verified, and does not validate semantic coding or historical interpretation.

The following inequalities remain binding:

`computationally_validated != semantic_ready`  
`ocr_available != text_verified`  
`retained_source_identity != alias_candidate`  
`search_hit != historical_claim`  
`zero_hits != demonstrated_absence`

Human semantic work remains intentionally paused.

## Next technical lane

With W8 closed, the preregistered non-human FTRL sequence continues with **W10 Integrados y Multiarea**, followed by W11 and W2. Any later recovery of a retained W8 source must enter through explicit source evidence and a new versioned reconciliation; it cannot be inferred from the present closure.
