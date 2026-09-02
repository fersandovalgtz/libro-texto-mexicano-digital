# LTMD-U2 — Coverage / Analytics 0.1

## Purpose

This layer reconciles the already observed LTMD-U2 technical states into two explicit analytical denominators without accessing or redistributing source-book content.

The denominators are intentionally separate:

- **42 catalog entries**: pedagogical/editorial appearances by grade;
- **39 source objects**: unique canonical CONALITEG viewer/source identities.

`catalog_entry != source_object` is therefore an invariant, not a data-cleaning inconvenience. Three teacher-book source objects are shared across adjacent grades and must not be silently duplicated when reporting source-object coverage.

## Materialized outputs

- `data/analytics/ltmd_u2_source_coverage_0_1.csv` — one row per canonical source object (39 rows);
- `data/analytics/ltmd_u2_catalog_entry_coverage_0_1.csv` — one row per catalog entry (42 rows), with source-object states propagated through the verified viewer-key relation;
- `data/analytics/ltmd_u2_coverage_analytics_manifest_0_1.json` — denominators, state counts, total observed source-object pages, separation guards, and SHA-256 values for both CSVs.

The layer is built deterministically by `scripts/build_u2_coverage_analytics.py` from the versioned catalog, identity, reader-shell, asset-resolution, page-count, source-admission, and text-access registries. It requires no network access.

## Current state — observation cut 2026-09-02

At the **source-object denominator (n=39)**:

- `cataloged_state=cataloged`: 39/39;
- `reader_shell_state=resolved`: 39/39;
- `asset_resolution_state=resolved_pdf`: 39/39;
- `page_count_state=observed`: 39/39;
- total observed pages across unique source objects: **10,392**;
- `source_admission_state=admitted_full_body_verified`: 39/39;
- `text_access_observation_state=blocked_by_password_required_encryption`: 39/39;
- `embedded_text_sample_state=not_assessed_due_to_access_block`: 39/39;
- `ocr_available_state=not_assessed`: 39/39;
- `text_verified_state=not_assessed`: 39/39;
- `semantic_ready_state=not_assessed`: 39/39.

At the **catalog-entry denominator (n=42)** the verified source-object state is propagated to each editorial/grade appearance. Those 42 rows are useful for grade-level catalog coverage, but they must never be reported as 42 distinct source books.

## Epistemic boundary

Coverage aggregation does not create new evidence about book content. In particular:

- `source_admitted != embedded_text_observed`;
- `content_access_blocked != no_embedded_text`;
- `content_access_blocked != ocr_needed`;
- `ocr_available != text_verified`;
- `computational_candidate != semantic_ready`;
- `publicly_accessible != openly_licensed`.

The `semantic_ready_state` is `not_assessed`; the layer does not infer `false` from the absence of semantic work. Likewise, a password-required access state is not converted into an OCR requirement.

## Rights and publication boundary

These outputs contain only non-substitutive metadata and technical states. They contain no source PDF/JPEG bytes, OCR, extracted text, page images, or semantic reconstruction. The source books remain third-party institutional materials and public accessibility in the CONALITEG reader is not treated as an open redistribution license.

## Validation

`scripts/validate_u2_coverage_analytics.py` verifies offline that:

- the denominators remain exactly 42 catalog entries and 39 source objects;
- both identity universes reconcile with their canonical registries;
- source-object page counts match the page-count layer;
- entry rows propagate states only through the canonical viewer/source identity relation;
- no OCR, text-verification, embedded-text, or semantic state is promoted;
- manifest guards remain explicit;
- materialized CSV SHA-256 values match the manifest.

`tests/test_build_u2_coverage_analytics.py` also rebuilds both CSVs in a temporary directory and requires byte-for-byte hash equality with the canonical materialization.

## Analytical use

This is the first safe bridge from U2 acquisition/provenance work into Analytics. It supports coverage dashboards, cohort summaries, grade-level catalog counts, source-object completeness checks, and later inter-cycle comparisons without conflating U2 with the historical U1 denominator.

It does **not** yet supply searchable book text. Any future local OCR or image-based processing remains a separate technical and rights decision.
