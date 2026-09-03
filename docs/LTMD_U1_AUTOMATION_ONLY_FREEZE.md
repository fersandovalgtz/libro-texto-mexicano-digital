# LTMD-U1 automation-only freeze

## Purpose

This document defines the maximum reproducible freeze that LTMD-U1 can reach without human content validation and without a definitive institutional answer from CONALITEG/SEP on OCR, images, fragments, or other potentially substitutive derivatives.

## Non-negotiable state separation

`routing_resolved != downstream_processed`

`downstream_processed != ftrl_validated`

`ftrl_validated != text_verified`

`text_verified != semantic_ready`

No automated workflow may promote `text_verified` or `semantic_ready` solely because routing, source integrity, OCR execution, index integrity, or text-free metrics pass.

## What may be frozen automatically

The U1 automation-only freeze may include:

- canonical and historical identifiers;
- bibliographic and technical metadata;
- source provenance and institutional URLs;
- SHA-256 checksums;
- source/page cardinalities;
- technical coverage states;
- routing decisions and their evidence;
- pipeline/software versions;
- OCR quality metrics that do not disclose OCR text;
- FTRL cardinalities and integrity results;
- SQLite/FTS integrity summaries;
- text-free run manifests;
- aggregate research counts and candidate-page counts explicitly labeled as unvalidated by humans.

## What the freeze must not claim

The automation-only freeze does not establish:

- semantic correctness of OCR;
- historical interpretation of candidate passages;
- visual verification of page content;
- human coding validity;
- inter-coder agreement;
- legal authorization to redistribute source images, PDFs, complete OCR, or reconstructive derivatives.

## Human-validation state

For the present phase:

`human_validation_state = deferred`

`semantic_ready = false`

Research outputs derived from automated search must use labels such as `candidate`, `explicit_machine_detected`, `exploratory`, or equivalent wording that prevents machine retrieval from being represented as a verified historical claim.

## Rights state

Issue #2 remains the controlling rights gate. Institutional silence is not authorization.

Until the gate changes:

- complete OCR remains local/private;
- source JPEG/PDF files are not versioned or published;
- public artifacts are restricted to the green publication class described in #2;
- no password discovery, guessing, recovery, bypass, circumvention, or neutralization is attempted.

## W2 DMA 2018

The four route-resolved identities are:

- `H2018P3DMA`
- `H2018P4DMA`
- `H2018P5DMA`
- `H2018P6DMA`

Their independently reverified source cardinality is 892 institutional JPEGs. `scripts/run_ftrl_w2_dma_2018.py` provides a local/private execution path that discovers only those four identities, requires the expected 892-page cardinality, verifies source SHA-256 through the existing FTRL builder, validates SQLite/FTS integrity, and emits a text-free provenance manifest.

The runner intentionally does not update a completion ledger. Ledger promotion must be a separate, evidence-based step after the run manifest has been inspected and preserved.

## Freeze acceptance criteria

An automation-only LTMD-U1 freeze is ready when all of the following are true:

1. all intended technical waves have resolved routing or an explicit final exception state;
2. source-admitted canonical objects have preserved technical evidence;
3. applicable FTRL runs have text-free validation manifests;
4. unresolved rights constraints are explicitly represented rather than inferred away;
5. human validation is represented as deferred, not completed;
6. public release artifacts contain no restricted full-text or source-image material;
7. release notes distinguish technical reproducibility from semantic validation.

## Research phase after freeze

Automated work may continue on longitudinal counts, rankings, cohort comparisons, candidate detection, and atlas-ready aggregate datasets. These outputs remain exploratory until human validation is later introduced.
