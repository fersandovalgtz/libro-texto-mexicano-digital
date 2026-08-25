#!/usr/bin/env python3
"""Block any W3 OCR runtime until exhaustive W1 is technically validated."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
EXPECTED_W1_IDENTITIES = 40


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit machine-readable status")
    args = parser.parse_args()

    with LEDGER.open(encoding="utf-8", newline="") as fh:
        rows = [row for row in csv.DictReader(fh) if row.get("wave") == "W1"]

    if len(rows) != EXPECTED_W1_IDENTITIES:
        raise SystemExit(
            f"W1 denominator drift: {len(rows)} != {EXPECTED_W1_IDENTITIES}"
        )

    validated = [row for row in rows if row.get("ftrl_status") == "validated"]
    corpus_ready = [row for row in rows if row.get("corpus_ready") == "1"]
    ocr_available = [row for row in rows if row.get("ocr_available") == "1"]
    archival_complete = [row for row in rows if row.get("archival_status") == "archival_complete"]
    semantic_promotions = [row for row in rows if row.get("semantic_ready") == "1"]
    text_promotions = [row for row in rows if row.get("text_verified") == "1"]

    ready = (
        len(validated) == EXPECTED_W1_IDENTITIES
        and len(corpus_ready) == EXPECTED_W1_IDENTITIES
        and len(ocr_available) == EXPECTED_W1_IDENTITIES
        and len(archival_complete) == EXPECTED_W1_IDENTITIES
        and not semantic_promotions
        and not text_promotions
    )

    status = {
        "schema": "LTMD_FTRL_W3_ACTIVATION_GUARD_0.1",
        "w1_historical_identities": len(rows),
        "w1_validated_identities": len(validated),
        "w1_corpus_ready_identities": len(corpus_ready),
        "w1_ocr_available_identities": len(ocr_available),
        "w1_archival_complete_identities": len(archival_complete),
        "w1_text_verified_identities": len(text_promotions),
        "w1_semantic_ready_identities": len(semantic_promotions),
        "w3_runtime_allowed": ready,
        "rule": "W3 OCR runtime requires exhaustive computational and archival W1 closure; text/semantic validation remain separate",
    }
    if args.json:
        print(json.dumps(status, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "W3 activation gate: "
            f"W1 validated={len(validated)}/{EXPECTED_W1_IDENTITIES}, "
            f"corpus_ready={len(corpus_ready)}/{EXPECTED_W1_IDENTITIES}, "
            f"ocr_available={len(ocr_available)}/{EXPECTED_W1_IDENTITIES}, "
            f"archival_complete={len(archival_complete)}/{EXPECTED_W1_IDENTITIES}"
        )

    if not ready:
        raise SystemExit(
            "W3 OCR runtime BLOCKED: exhaustive W1 has not yet reached validated/corpus_ready/ocr_available/archival_complete for 40/40 identities in the canonical ledger"
        )


if __name__ == "__main__":
    main()
