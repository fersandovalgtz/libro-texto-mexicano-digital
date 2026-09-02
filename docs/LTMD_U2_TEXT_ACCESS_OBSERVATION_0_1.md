# LTMD-U2 — Text-access observation 0.1

## Scope

This layer records whether the 39 canonical LTMD-U2 source objects can be opened for content inspection with three independent PDF implementations using the empty password only.

It is a technical access observation, not a decryption procedure and not a textual-content assessment. The observer does not discover, guess, recover, derive, or bypass passwords.

## Result

Observation date: 2026-09-02.

For all 39 admitted source objects:

- the complete remote PDF body was re-downloaded temporarily and verified against the canonical byte count and SHA-256 from source admission 0.1;
- `pypdf 6.16.2` reported `encrypted=true`, empty-password result `NOT_DECRYPTED`, and content access raised `FileNotDecryptedError`;
- `PyMuPDF 1.28.2` reported `needs_password=true`, empty-password authentication result `0`, and page text access raised `ValueError`;
- `pikepdf 10.12.0` could not open the file with an empty password and raised `PasswordError`;
- the resulting state is `blocked_by_password_required_encryption` for 39/39 objects;
- source PDF bytes persisted by LTMD: 0;
- extracted text persisted by LTMD: 0.

The public materialization is `data/catalog/ltmd_u2_text_access_observation_2026_09_02.csv`. It contains only identifiers and non-substitutive technical states.

## Interpretation boundary

The result supports only this claim: **under the pinned parser implementations and an empty-password attempt, content access is blocked by password-required PDF encryption for all 39 observed objects.**

It does **not** establish any of the following:

- that the PDF contains no embedded text;
- that OCR is available;
- that OCR is required;
- that text has been extracted or verified;
- that a source is openly licensed;
- that any semantic claim can be made from the book content.

Accordingly:

- `source_admitted != embedded_text_observed`;
- `content_access_blocked != no_embedded_text`;
- `content_access_blocked != ocr_needed`;
- `ocr_available != text_verified`;
- `publicly_accessible != openly_licensed`.

`embedded_text_sample_state` therefore remains `not_assessed_due_to_access_block`, while `ocr_available_state` and `text_verified_state` remain `not_assessed`.

## Method and reproducibility

The production observer is `scripts/observe_u2_text_access.py`. It:

1. reads the canonical 39-object source-admission registry;
2. requires exactly the parser versions used in the successful experimental run;
3. downloads one source at a time to an ephemeral temporary directory;
4. checks the complete body against the canonical byte count and SHA-256 before any parser probe;
5. attempts only the empty password in each implementation;
6. records parser state/error classes;
7. deletes the temporary source before advancing;
8. writes no source page and no extracted text.

Because network access and third-party source downloads are required, the observer is not executed by ordinary CI. CI validates the already materialized CSV, its manifest hash, cardinality, identity reconciliation, parser-state consensus, and non-persistence guards.

Pinned implementations:

- `pypdf 6.16.2`;
- `PyMuPDF 1.28.2`;
- `pikepdf 10.12.0`;
- `cryptography 50.0.1`.

## Experimental provenance

A bounded three-object pilot preceded the exhaustive observation. The full-universe experimental run then reproduced the same state for 39/39 objects.

- pilot run: `33655284272`;
- pilot head: `5af45798a5d1e0cfdeb16d32d14a58f4f016ac8a`;
- pilot artifact: `9856455028`;
- exhaustive run: `33655606562`;
- exhaustive head: `d81338cae13d2448c420ac00a52e53c936fb83ae`;
- exhaustive artifact: `9856646645`.

The experimental artifacts were preserved privately outside the public repository before production materialization. Their digests and the raw CSV/JSON digests are fixed in `data/catalog/ltmd_u2_text_access_observation_0_1.manifest.json`.

## Rights and next step

The books remain third-party institutional materials. Public availability in the CONALITEG reader does not imply an open redistribution license. This layer therefore publishes no PDF bytes and no extracted text.

The next decision is not to circumvent the password requirement. Any subsequent OCR or image-based processing must be separately justified under the documented rights policy, use a technically legitimate acquisition path, remain private when required, and preserve the distinction between OCR availability, text verification, computational candidates, and semantic readiness.
