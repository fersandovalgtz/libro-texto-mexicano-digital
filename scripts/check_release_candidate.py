#!/usr/bin/env python3
"""Preflight the LTMD v0.1.0-rc.1 scientific release candidate.

The check separates technical RC readiness from public-release readiness and
validates the substance and scope of the adopted code/data licenses.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0-rc.1"
INTEGRITY_VERSION = "LTMD_INTEGRITY_0.6"
INTEGRITY_CRITICAL_COUNT = 166
OUT_JSON = Path("data/derived/release_candidate_preflight.json")
OUT_MD = Path("data/derived/release_candidate_preflight.md")

REQUIRED = [
    "VERSION",
    "CITATION.cff",
    "CHANGELOG.md",
    "LICENSE",
    "DATA_LICENSE.md",
    "requirements-release.txt",
    "README.md",
    "docs/RELEASE_NOTES_v0.1.0-rc.1.md",
    "docs/REPRODUCIBILITY_ENVIRONMENT_0_1.md",
    "docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md",
    "docs/RELEASE_OUTPUTS_0_1.md",
    "docs/RIGHTS_AND_REUSE_0_1.md",
    "docs/RIGHTS_PUBLICATION_MATRIX_0_2.md",
    "docs/LICENSE_DECISION_MEMO_0_1.md",
    "docs/RELEASE_CHECKLIST_0_1.md",
    "docs/METHOD_INDEX.md",
    "docs/METHODS_ARTICLE_DRAFT_0_2.md",
    "data/derived/research_integrity_manifest.json",
    "data/derived/methods_article_claim_check.json",
]

FORBIDDEN_TRACKED_PREFIXES = (
    "private/",
    "data/raw/",
    "data/work/",
    "downloads/",
    "working/",
)
FORBIDDEN_TRACKED_SUFFIXES = (".pdf", ".tif", ".tiff", ".jp2", ".zip")


def git_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def tracked_files() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"])
    return [p.decode("utf-8") for p in raw.split(b"\0") if p]


def check(condition: bool, code: str, detail: str, checks: list[dict]) -> None:
    checks.append({"code": code, "passed": bool(condition), "detail": detail})


def validate_publish_licenses() -> list[str]:
    """Return blockers unless adopted licenses match the release policy."""
    blockers: list[str] = []

    license_path = Path("LICENSE")
    if not license_path.exists():
        blockers.append("code_license_not_selected")
    else:
        text = license_path.read_text(encoding="utf-8", errors="replace")
        if "Apache License" not in text or "Version 2.0, January 2004" not in text:
            blockers.append("code_license_not_apache_2_0")

    data_path = Path("DATA_LICENSE.md")
    if not data_path.exists():
        blockers.append("derived_data_license_not_selected")
    else:
        text = data_path.read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        cc_ok = "cc by 4.0" in low or "creativecommons.org/licenses/by/4.0" in low
        source_exclusion = (
            "conaliteg" in low
            and "sep" in low
            and ("no se aplica" in low or "exclu" in low or "does not apply" in low)
        )
        scope_ok = "en la medida" in low or "to the extent" in low
        if not cc_ok:
            blockers.append("derived_data_license_not_cc_by_4_0")
        if not source_exclusion:
            blockers.append("derived_data_license_missing_source_exclusion")
        if not scope_ok:
            blockers.append("derived_data_license_missing_rights_scope")

    return blockers


def main() -> None:
    checks: list[dict] = []
    missing = [p for p in REQUIRED if not Path(p).exists()]
    check(not missing, "required_release_files", f"missing={missing}", checks)

    version = Path("VERSION").read_text(encoding="utf-8").strip() if Path("VERSION").exists() else ""
    check(version == VERSION, "version_file", f"VERSION={version!r}", checks)

    cff = Path("CITATION.cff").read_text(encoding="utf-8") if Path("CITATION.cff").exists() else ""
    check(f'version: "{VERSION}"' in cff, "citation_version", f"expected {VERSION}", checks)
    check("date-released: 2026-08-15" in cff, "citation_date", "expected 2026-08-15", checks)
    check("DOI se añadirá únicamente después" in cff, "no_invented_doi", "CFF explicitly defers DOI until real deposit", checks)

    integrity = {}
    if Path("data/derived/research_integrity_manifest.json").exists():
        integrity = json.loads(Path("data/derived/research_integrity_manifest.json").read_text(encoding="utf-8"))
    integrity_ok = (
        integrity.get("integrity_version") == INTEGRITY_VERSION
        and integrity.get("critical_count") == integrity.get("critical_present_count")
        and integrity.get("critical_count") == INTEGRITY_CRITICAL_COUNT
        and integrity.get("missing_critical") == []
    )
    check(
        integrity_ok,
        "integrity_0_6",
        f"version={integrity.get('integrity_version')} critical={integrity.get('critical_present_count')}/{integrity.get('critical_count')}",
        checks,
    )

    claim = {}
    if Path("data/derived/methods_article_claim_check.json").exists():
        claim = json.loads(Path("data/derived/methods_article_claim_check.json").read_text(encoding="utf-8"))
    check(claim.get("passed") is True and claim.get("failures") == [], "methods_claim_check", f"passed={claim.get('passed')}", checks)

    req = Path("requirements-release.txt").read_text(encoding="utf-8") if Path("requirements-release.txt").exists() else ""
    check("sentence-transformers==5.6.1" in req, "direct_semantic_dependency_pinned", "sentence-transformers==5.6.1", checks)

    rights_matrix = Path("docs/RIGHTS_PUBLICATION_MATRIX_0_2.md").read_text(encoding="utf-8") if Path("docs/RIGHTS_PUBLICATION_MATRIX_0_2.md").exists() else ""
    check("Apache License 2.0" in rights_matrix and "CC BY 4.0" in rights_matrix, "license_policy_documented", "Apache-2.0 + CC BY 4.0 policy documented", checks)

    gitignore = Path(".gitignore").read_text(encoding="utf-8") if Path(".gitignore").exists() else ""
    for entry in ("private/", "data/work/", ".env"):
        check(entry in gitignore, f"gitignore_{entry.replace('/', '_').replace('.', '_')}", f"requires {entry}", checks)

    tracked = tracked_files()
    forbidden = [
        p for p in tracked
        if p.startswith(FORBIDDEN_TRACKED_PREFIXES) or p.lower().endswith(FORBIDDEN_TRACKED_SUFFIXES)
    ]
    check(not forbidden, "no_forbidden_source_or_work_files_tracked", f"forbidden={forbidden[:20]}", checks)

    # Semantic stage gate must remain closed in this methodological release.
    human_outputs = [
        "data/validation/semb03_human_reference_consensus.csv",
        "data/validation/semb03_locked_validation_reference.csv",
        "data/derived/semb03_model_lock.json",
        "data/derived/semb03_locked_validation_result.json",
    ]
    premature = [p for p in human_outputs if Path(p).exists()]
    check(not premature, "semb03_human_gate_still_closed", f"premature_outputs={premature}", checks)

    technical_failures = [c for c in checks if not c["passed"]]
    rc_technical_ready = not technical_failures

    publish_blockers = validate_publish_licenses()
    publish_ready = rc_technical_ready and not publish_blockers

    result = {
        "preflight_version": "LTMD_RELEASE_PREFLIGHT_0.2",
        "release_candidate": f"v{VERSION}",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "rc_technical_ready": rc_technical_ready,
        "publish_ready": publish_ready,
        "technical_failures": technical_failures,
        "publish_blockers": publish_blockers,
        "integrity_version": integrity.get("integrity_version"),
        "integrity_critical": f"{integrity.get('critical_present_count')}/{integrity.get('critical_count')}",
        "methods_claim_check_passed": claim.get("passed"),
        "checks": checks,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Preflight de release candidata LTMD",
        "",
        f"Candidata: **v{VERSION}**.",
        "",
        f"Commit observado: `{result['git_head']}`.",
        "",
        f"RC técnicamente lista: **{'SÍ' if rc_technical_ready else 'NO'}**.",
        f"Lista para publicación pública: **{'SÍ' if publish_ready else 'NO'}**.",
        "",
        f"Integridad: **{result['integrity_critical']}** (`{result['integrity_version']}`).",
        f"Verificación de cifras del artículo: **{'PASS' if result['methods_claim_check_passed'] else 'FAIL'}**.",
        "",
        "## Controles técnicos",
        "",
    ]
    for c in checks:
        lines.append(f"- [{'x' if c['passed'] else ' '}] `{c['code']}` — {c['detail']}")

    lines += ["", "## Blockers de publicación", ""]
    if publish_blockers:
        for b in publish_blockers:
            lines.append(f"- `{b}`")
    else:
        lines.append("- Ninguno.")

    lines += [
        "",
        "## Interpretación",
        "",
        "`rc_technical_ready` significa que el corte puede auditarse como candidata metodológica. `publish_ready` exige además licencias materializadas y consistentes con la política documentada. El DOI no se exige antes de la publicación real: debe añadirse únicamente después de que Zenodo archive el tag correspondiente.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("rc_technical_ready", rc_technical_ready)
    print("publish_ready", publish_ready)
    print("publish_blockers", ",".join(publish_blockers) or "none")
    if technical_failures:
        raise SystemExit("release candidate technical preflight failed")


if __name__ == "__main__":
    main()
