#!/usr/bin/env python3
"""Audit LTMD's public repository surface without external dependencies.

The audit is intentionally conservative: it verifies controls that can be
established from the checked-out repository and does not claim to certify
GitHub settings, legal status, scientific validity, or FAIR compliance.

Legacy workflow write capabilities are treated as explicit technical debt:
existing violations on ``origin/main`` are reported, while any new violation
or any touched legacy workflow that still retains a violation fails the gate.
This lets LTMD harden incrementally without normalizing additional direct
repository writes.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_REF = "origin/main"

REQUIRED_FILES = (
    "README.md",
    "README.en.md",
    "LICENSE",
    "DATA_LICENSE.md",
    "CITATION.cff",
    "codemeta.json",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "GOVERNANCE.md",
    "PROVENANCE.md",
    "FAIR_ASSESSMENT.md",
    "SCIENTIFIC_REPOSITORY_STANDARD.md",
    "docs/LTMD_PRODUCT_BOUNDARIES.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/data_methodology.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/dependabot.yml",
    ".github/workflows/release-preflight.yml",
    ".github/workflows/repository-quality.yml",
)

REQUIRED_GITIGNORE_RULES = (
    "local/",
    "private/",
    ".env",
    ".env.*",
    "*.pdf",
)

FORBIDDEN_TRACKED_PREFIXES = ("local/", "private/")
FORBIDDEN_TRACKED_NAMES = {".env"}
CONTENTS_WRITE_RE = re.compile(r"(?m)^\s*contents:\s*write\s*(?:#.*)?$")
GIT_PUSH_RE = re.compile(r"(?m)^(?!\s*#).*\bgit\s+push(?:\s|$)")


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [item.decode("utf-8") for item in proc.stdout.split(b"\0") if item]


def git_text(*args: str) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        return None
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def base_workflow(relative: str) -> str | None:
    return git_text("show", f"{BASE_REF}:{relative}")


def touched_workflows() -> set[str]:
    diff = git_text("diff", "--name-only", f"{BASE_REF}...HEAD", "--", ".github/workflows")
    if diff is None:
        return set()
    return {line.strip() for line in diff.splitlines() if line.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        dest="json_path",
        help="Optional path for a machine-readable audit report.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(f"missing required repository surface: {relative}", failures)

    gitignore_path = ROOT / ".gitignore"
    if not gitignore_path.is_file():
        fail("missing .gitignore", failures)
        gitignore = ""
    else:
        gitignore = gitignore_path.read_text(encoding="utf-8")

    for rule in REQUIRED_GITIGNORE_RULES:
        if rule not in gitignore.splitlines():
            fail(f".gitignore does not contain required rule: {rule}", failures)

    try:
        tracked = tracked_files()
    except (subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        fail(f"unable to inspect tracked files: {exc}", failures)
        tracked = []

    for path in tracked:
        if path in FORBIDDEN_TRACKED_NAMES or any(
            path.startswith(prefix) for prefix in FORBIDDEN_TRACKED_PREFIXES
        ):
            fail(f"restricted local/private path is tracked: {path}", failures)

    codemeta_path = ROOT / "codemeta.json"
    if codemeta_path.is_file():
        try:
            codemeta = json.loads(codemeta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            fail(f"codemeta.json is not valid UTF-8 JSON: {exc}", failures)
        else:
            for key in ("@context", "@type", "name", "codeRepository", "version", "license", "author"):
                if key not in codemeta:
                    fail(f"codemeta.json missing key: {key}", failures)

    workflows_dir = ROOT / ".github" / "workflows"
    workflows_without_permissions: list[str] = []
    workflows_with_contents_write: list[str] = []
    workflows_with_git_push: list[str] = []
    legacy_contents_write: list[str] = []
    legacy_git_push: list[str] = []
    changed = touched_workflows()

    if workflows_dir.is_dir():
        for path in sorted(workflows_dir.glob("*.y*ml")):
            text = path.read_text(encoding="utf-8")
            relative = str(path.relative_to(ROOT))
            if "permissions:" not in text:
                workflows_without_permissions.append(relative)

            base_text = base_workflow(relative)
            has_contents_write = bool(CONTENTS_WRITE_RE.search(text))
            has_git_push = bool(GIT_PUSH_RE.search(text))
            base_has_contents_write = bool(base_text and CONTENTS_WRITE_RE.search(base_text))
            base_has_git_push = bool(base_text and GIT_PUSH_RE.search(base_text))

            if has_contents_write:
                workflows_with_contents_write.append(relative)
                if base_has_contents_write and relative not in changed:
                    legacy_contents_write.append(relative)
                else:
                    fail(
                        "new or modified workflow requests contents: write; scientific outputs "
                        f"must enter main through review: {relative}",
                        failures,
                    )

            if has_git_push:
                workflows_with_git_push.append(relative)
                if base_has_git_push and relative not in changed:
                    legacy_git_push.append(relative)
                else:
                    fail(
                        "new or modified workflow contains direct git push; CI must not mutate "
                        f"repository refs: {relative}",
                        failures,
                    )

    if workflows_without_permissions:
        warning = (
            f"{len(workflows_without_permissions)} workflow(s) do not declare explicit "
            "GITHUB_TOKEN permissions; audit progressively before changing legacy jobs"
        )
        warnings.append(warning)
        print(f"WARNING: {warning}")

    if legacy_contents_write:
        warning = (
            f"{len(legacy_contents_write)} unchanged legacy workflow(s) retain contents: write; "
            "they are grandfathered only as migration debt and must not grow"
        )
        warnings.append(warning)
        print(f"WARNING: {warning}")

    if legacy_git_push:
        warning = (
            f"{len(legacy_git_push)} unchanged legacy workflow(s) retain direct git push; "
            "branch protection is the mandatory external containment until migration"
        )
        warnings.append(warning)
        print(f"WARNING: {warning}")

    report = {
        "audit": "LTMD repository quality",
        "status": "pass" if not failures else "fail",
        "required_files_checked": len(REQUIRED_FILES),
        "tracked_files_checked": len(tracked),
        "workflow_contents_write": workflows_with_contents_write,
        "workflow_direct_git_push": workflows_with_git_push,
        "legacy_workflow_contents_write": legacy_contents_write,
        "legacy_workflow_direct_git_push": legacy_git_push,
        "touched_workflows": sorted(changed),
        "failures": failures,
        "warnings": warnings,
        "scope_note": (
            "Repository-content regression audit only; legacy workflow writes remain migration "
            "debt and require GitHub branch protection as external containment. Legal review, "
            "scientific validity and external FAIR certification are out of scope."
        ),
    }

    if args.json_path:
        output = ROOT / args.json_path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
