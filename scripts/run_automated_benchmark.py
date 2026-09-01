#!/usr/bin/env python3
"""Run LTMD Automated Benchmark 0.1 using only public, versioned inputs.

This benchmark evaluates engineering/scientific-infrastructure invariants only.
It does not provide human semantic validation or construct validity.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

BENCHMARK_VERSION = "LTMD_AUTOMATED_BENCHMARK_0.1"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_version(root: Path) -> str:
    return read_text(root / "VERSION").strip()


def version_in_cff(text: str, version: str) -> bool:
    pattern = rf"(?m)^version:\s*['\"]?{re.escape(version)}['\"]?\s*$"
    return bool(re.search(pattern, text))


def version_in_codemeta(text: str, version: str) -> bool:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return False
    return str(payload.get("version", "")) == version


def forbidden_public_source_files(root: Path) -> list[str]:
    forbidden_extensions = {".pdf", ".jpg", ".jpeg"}
    violations: list[str] = []
    for base in (root / "data" / "catalog", root / "data" / "derived"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in forbidden_extensions:
                violations.append(path.relative_to(root).as_posix())
    return sorted(violations)


def guard_present(texts: list[str], guard: str) -> bool:
    return any(guard in text for text in texts)


def walk_json(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_json(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_json(child, path + (str(index),))
    else:
        yield path, value


def analytics_contract_audit(root: Path) -> dict[str, Any]:
    analytics_dir = root / "data" / "analytics"
    files = sorted(analytics_dir.glob("*materialization*.json"))
    invalid_json: list[str] = []
    forbidden_state_true: list[str] = []
    invalid_sha256: list[str] = []
    private_not_preserved: list[str] = []

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            payload = json.loads(read_text(path))
        except json.JSONDecodeError:
            invalid_json.append(relative)
            continue

        for key_path, value in walk_json(payload):
            dotted = ".".join(key_path)
            last = key_path[-1] if key_path else ""
            if last in {"semantic_ready", "text_verified", "human_validated"} and value is True:
                forbidden_state_true.append(f"{relative}:{dotted}")
            if "sha256" in last.lower() and isinstance(value, str) and not SHA256_RE.fullmatch(value.lower()):
                invalid_sha256.append(f"{relative}:{dotted}")
            if last == "preserved_private" and value is False:
                private_not_preserved.append(f"{relative}:{dotted}")

    return {
        "files_checked": len(files),
        "invalid_json": sorted(invalid_json),
        "forbidden_state_true": sorted(forbidden_state_true),
        "invalid_sha256": sorted(invalid_sha256),
        "private_not_preserved": sorted(private_not_preserved),
    }


def documentary_genealogy_audit(root: Path, expected: dict[str, Any]) -> dict[str, Any]:
    path = root / "data" / "analytics" / "ltmd_u1_reuse_similarity_materialization_0_1.json"
    payload = json.loads(read_text(path))
    counts = payload["counts"]
    protocol = payload["protocol"]
    privacy = payload["privacy"]
    state = payload["scientific_state"]
    private = payload["private_artifact"]

    checks = {
        "canonical_objects": counts["canonical_objects"] == expected["u1_canonical_objects"],
        "corpus_pages": counts["corpus_pages"] == expected["u1_corpus_pages"],
        "page_partition": (
            counts["text_admissible_pages"] + counts["text_excluded_low_information_pages"]
            == counts["corpus_pages"]
        ),
        "exact_source_cross_generation_baseline": (
            counts["exact_source_cross_generation_groups"]
            == expected["reuse_exact_source_cross_generation_groups"]
        ),
        "exact_source_repeated_baseline": (
            counts["exact_source_repeated_groups"]
            == expected["reuse_exact_source_repeated_groups"]
        ),
        "exact_text_cross_generation_baseline": (
            counts["exact_text_cross_generation_groups"]
            == expected["reuse_exact_text_cross_generation_groups"]
        ),
        "exact_text_repeated_baseline": (
            counts["exact_text_repeated_groups"]
            == expected["reuse_exact_text_repeated_groups"]
        ),
        "text_admissible_baseline": (
            counts["text_admissible_pages"] == expected["reuse_text_admissible_pages"]
        ),
        "low_information_baseline": (
            counts["text_excluded_low_information_pages"]
            == expected["reuse_text_excluded_low_information_pages"]
        ),
        "source_cross_generation_subset": (
            counts["exact_source_cross_generation_groups"] <= counts["exact_source_repeated_groups"]
        ),
        "text_cross_generation_subset": (
            counts["exact_text_cross_generation_groups"] <= counts["exact_text_repeated_groups"]
        ),
        "shingle_eligible_subset": (
            counts["similarity_shingle_eligible_pages"] <= counts["text_admissible_pages"]
        ),
        "thresholds_preregistered": bool(
            protocol["similarity"].get("thresholds_preregistered_before_candidate_inspection")
        ),
        "similarity_not_alias": state.get("similarity_creates_alias") is False,
        "similarity_not_semantic_equivalence": state.get("similarity_is_semantic_equivalence") is False,
        "semantic_ready_false": state.get("semantic_ready") is False,
        "text_verified_false": state.get("text_verified") is False,
        "private_artifact_preserved": private.get("preserved_private") is True,
        "private_artifact_sha256_valid": bool(SHA256_RE.fullmatch(str(private.get("sha256", "")).lower())),
        "privacy_all_false": all(value is False for value in privacy.values()),
    }

    return {
        "path": path.relative_to(root).as_posix(),
        "counts": counts,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def benchmark(root: Path) -> dict[str, Any]:
    baseline_path = root / "data" / "benchmarks" / "ltmd_automated_benchmark_0_1_baseline.json"
    baseline = json.loads(read_text(baseline_path))
    expected = baseline["expected"]

    retained_path = root / "data" / "catalog" / "ltmd_u1_retained_source_register.csv"
    contemporary_path = root / "data" / "catalog" / "conaliteg_primaria_2026_2027_inventory.csv"

    retained = read_csv(retained_path)
    contemporary = read_csv(contemporary_path)

    retained_keys = [row["viewer_key"] for row in retained]
    retained_status = Counter(row["status"] for row in retained)

    contemporary_keys = [row["viewer_key"] for row in contemporary]
    contemporary_key_counts = Counter(contemporary_keys)
    contemporary_shared = sorted(key for key, count in contemporary_key_counts.items() if count > 1)

    release_version = extract_version(root)
    cff = read_text(root / "CITATION.cff")
    codemeta = read_text(root / "codemeta.json")
    readme = read_text(root / "README.md")
    automated_ceiling = read_text(root / "docs" / "AUTOMATED_WORK_CEILING_0_1.md")
    benchmark_doc = read_text(root / "docs" / "LTMD_AUTOMATED_BENCHMARK_0_1.md")
    rights_doc = read_text(root / "docs" / "LTMD_HISTORICAL_CONTEXT_AND_RIGHTS.md")
    data_license = read_text(root / "DATA_LICENSE.md")

    guard_texts = [automated_ceiling, benchmark_doc, rights_doc, data_license, readme]
    analytics_audit = analytics_contract_audit(root)
    genealogy_audit = documentary_genealogy_audit(root, expected)

    checks: dict[str, bool] = {
        "retained_total": len(retained) == expected["u1_retained_total"],
        "retained_unique_viewer_keys": len(retained_keys) == len(set(retained_keys)),
        "retained_active_count": retained_status.get("active_retention", 0) == expected["u1_active_retentions"],
        "retained_final_exception_count": retained_status.get("final_exception", 0) == expected["u1_final_exceptions"],
        "retained_status_vocabulary": set(retained_status) <= {"active_retention", "final_exception"},
        "contemporary_catalog_entries": len(contemporary) == expected["contemporary_catalog_entries"],
        "contemporary_unique_viewers": len(set(contemporary_keys)) == expected["contemporary_unique_viewers"],
        "contemporary_shared_viewers": contemporary_shared == sorted(expected["contemporary_shared_viewers"]),
        "contemporary_shared_viewer_multiplicity": all(contemporary_key_counts[key] == 2 for key in contemporary_shared),
        "contemporary_cycle": {row["cycle"] for row in contemporary} == {expected["contemporary_cycle"]},
        "contemporary_level": {row["level"] for row in contemporary} == {expected["contemporary_level"]},
        "contemporary_repo_status": {row["public_repo_status"] for row in contemporary} == {expected["contemporary_public_repo_status"]},
        "release_version": release_version == expected["release_version"],
        "version_cff": version_in_cff(cff, release_version),
        "version_codemeta": version_in_codemeta(codemeta, release_version),
        "version_readme": release_version in readme,
        "u1_universe_readme": "542" in readme,
        "u1_technical_coverage_readme": "524/542" in readme or "524 / 542" in readme,
        "u1_canonical_objects_readme": "492/542" in readme or "492 / 542" in readme,
        "guard_ocr_text": guard_present(guard_texts, "ocr_available != text_verified"),
        "guard_search_claim": guard_present(guard_texts, "search_hit != historical_claim"),
        "guard_candidate_semantic": guard_present(guard_texts, "computational_candidate != semantic_ready"),
        "guard_access_license": guard_present(guard_texts, "publicly_accessible != openly_licensed"),
        "guard_no_automatic_ground_truth": "llamar “verdad de referencia” a etiquetas producidas por un LLM" in automated_ceiling,
        "rights_source_exclusion": "no posee ni reclama derechos" in rights_doc.lower(),
        "rights_ccby_scope": "CC BY 4.0" in data_license and "CONALITEG" in data_license,
        "no_public_source_files": len(forbidden_public_source_files(root)) == 0,
        "analytics_materializations_present": analytics_audit["files_checked"] >= 5,
        "analytics_json_valid": len(analytics_audit["invalid_json"]) == 0,
        "analytics_no_false_semantic_promotion": len(analytics_audit["forbidden_state_true"]) == 0,
        "analytics_sha256_well_formed": len(analytics_audit["invalid_sha256"]) == 0,
        "analytics_private_artifacts_preserved": len(analytics_audit["private_not_preserved"]) == 0,
        "documentary_genealogy": genealogy_audit["status"] == "PASS",
    }

    passed = sum(checks.values())
    total = len(checks)
    score = round(100.0 * passed / total, 2) if total else 0.0

    input_paths = [
        baseline_path,
        retained_path,
        contemporary_path,
        root / "data" / "analytics" / "ltmd_u1_reuse_similarity_materialization_0_1.json",
        root / "VERSION",
        root / "CITATION.cff",
        root / "codemeta.json",
        root / "README.md",
        root / "DATA_LICENSE.md",
        root / "docs" / "AUTOMATED_WORK_CEILING_0_1.md",
        root / "docs" / "LTMD_AUTOMATED_BENCHMARK_0_1.md",
        root / "docs" / "LTMD_HISTORICAL_CONTEXT_AND_RIGHTS.md",
    ]

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "automated_integrity_reproducibility_only",
        "human_validation": False,
        "construct_validity_claimed": False,
        "release_version": release_version,
        "metrics": {
            "u1_universe": expected["u1_universe"],
            "u1_effective_technical_coverage": expected["u1_effective_technical_coverage"],
            "u1_canonical_objects": expected["u1_canonical_objects"],
            "u1_corpus_pages": expected["u1_corpus_pages"],
            "u1_retained_total": len(retained),
            "u1_active_retentions": retained_status.get("active_retention", 0),
            "u1_final_exceptions": retained_status.get("final_exception", 0),
            "contemporary_catalog_entries": len(contemporary),
            "contemporary_unique_viewers": len(set(contemporary_keys)),
            "contemporary_shared_viewers": contemporary_shared,
            "analytics_materialization_files_checked": analytics_audit["files_checked"],
            "genealogy_exact_source_cross_generation_groups": genealogy_audit["counts"]["exact_source_cross_generation_groups"],
            "genealogy_exact_text_cross_generation_groups": genealogy_audit["counts"]["exact_text_cross_generation_groups"],
            "engineering_readiness_score": score,
        },
        "checks": checks,
        "analytics_contract_audit": analytics_audit,
        "documentary_genealogy_audit": genealogy_audit,
        "violations": {
            "public_source_files": forbidden_public_source_files(root),
            "failed_checks": sorted(name for name, ok in checks.items() if not ok),
        },
        "input_sha256": {
            path.relative_to(root).as_posix(): sha256_file(path)
            for path in input_paths
        },
        "interpretation_guard": (
            "PASS means the declared automated integrity/reproducibility invariants hold; "
            "it does not imply human semantic validation, OCR ground-truth accuracy, construct validity, or historical truth."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LTMD Automated Benchmark 0.1")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Fail if any mandatory invariant fails")
    args = parser.parse_args()

    result = benchmark(args.root.resolve())
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    if args.check and result["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
