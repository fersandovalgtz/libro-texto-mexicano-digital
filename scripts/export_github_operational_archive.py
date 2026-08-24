#!/usr/bin/env python3
"""Export public GitHub operational history for persistent LTMD archiving.

The exporter captures repository-level collections exhaustively via GitHub API
pagination, then enriches pull requests with reviews and Actions runs with jobs
and retained log bytes. Missing/expired dynamic resources are recorded as
negative results rather than fabricated or silently omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "LTMD_GITHUB_OPERATIONAL_EXPORT_0.1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def gh_json(endpoint: str, output: Path, *, paginate: bool = True) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["gh", "api"]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    cmd.append(endpoint)
    with output.open("wb") as out:
        subprocess.run(cmd, check=True, stdout=out)


def gh_binary(endpoint: str, output: Path) -> tuple[bool, str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as out:
        proc = subprocess.run(
            ["gh", "api", endpoint],
            stdout=out,
            stderr=subprocess.PIPE,
            check=False,
        )
    if proc.returncode == 0 and output.stat().st_size > 0:
        return True, ""
    output.unlink(missing_ok=True)
    return False, proc.stderr.decode("utf-8", errors="replace").strip()


def flatten_page_arrays(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for page in data:
        if isinstance(page, list):
            out.extend(x for x in page if isinstance(x, dict))
    return out


def flatten_object_collection(path: Path, key: str) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for page in data:
        if isinstance(page, dict):
            value = page.get(key, [])
            if isinstance(value, list):
                out.extend(x for x in value if isinstance(x, dict))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--output-dir", type=Path, default=Path("local/github-operational-archive"))
    args = parser.parse_args()

    if not args.repository or "/" not in args.repository:
        raise SystemExit("--repository owner/name is required")
    if not os.environ.get("GH_TOKEN"):
        raise SystemExit("GH_TOKEN is required")
    if subprocess.run(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        raise SystemExit("GitHub CLI is required")

    root = args.output_dir
    data_dir = root / "data"
    dynamic_dir = root / "dynamic"
    logs_dir = root / "actions-logs"
    root.mkdir(parents=True, exist_ok=True)

    repo = args.repository
    single = {
        "repository.json": f"repos/{repo}",
        "languages.json": f"repos/{repo}/languages",
    }
    collections = {
        "issues_pages.json": f"repos/{repo}/issues?state=all&per_page=100",
        "issue_comments_pages.json": f"repos/{repo}/issues/comments?per_page=100",
        "issue_events_pages.json": f"repos/{repo}/issues/events?per_page=100",
        "pulls_pages.json": f"repos/{repo}/pulls?state=all&per_page=100",
        "pull_review_comments_pages.json": f"repos/{repo}/pulls/comments?per_page=100",
        "releases_pages.json": f"repos/{repo}/releases?per_page=100",
        "tags_pages.json": f"repos/{repo}/tags?per_page=100",
        "branches_pages.json": f"repos/{repo}/branches?per_page=100",
        "labels_pages.json": f"repos/{repo}/labels?per_page=100",
        "milestones_pages.json": f"repos/{repo}/milestones?state=all&per_page=100",
        "commit_comments_pages.json": f"repos/{repo}/comments?per_page=100",
        "contributors_pages.json": f"repos/{repo}/contributors?anon=1&per_page=100",
        "actions_workflows_pages.json": f"repos/{repo}/actions/workflows?per_page=100",
        "actions_runs_pages.json": f"repos/{repo}/actions/runs?per_page=100",
        "actions_artifacts_pages.json": f"repos/{repo}/actions/artifacts?per_page=100",
    }

    for filename, endpoint in single.items():
        gh_json(endpoint, data_dir / filename, paginate=False)
    for filename, endpoint in collections.items():
        gh_json(endpoint, data_dir / filename, paginate=True)

    negative: list[dict] = []

    pulls = flatten_page_arrays(data_dir / "pulls_pages.json")
    for pr in pulls:
        number = int(pr["number"])
        try:
            gh_json(
                f"repos/{repo}/pulls/{number}/reviews?per_page=100",
                dynamic_dir / "pull-reviews" / f"pr_{number}.json",
                paginate=True,
            )
        except subprocess.CalledProcessError as exc:
            negative.append({"type": "pull_reviews", "id": number, "error": f"exit={exc.returncode}"})

    runs = flatten_object_collection(data_dir / "actions_runs_pages.json", "workflow_runs")
    log_available = 0
    log_unavailable = 0
    for run in runs:
        run_id = int(run["id"])
        try:
            gh_json(
                f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100",
                dynamic_dir / "run-jobs" / f"run_{run_id}.json",
                paginate=True,
            )
        except subprocess.CalledProcessError as exc:
            negative.append({"type": "run_jobs", "id": run_id, "error": f"exit={exc.returncode}"})

        ok, error = gh_binary(
            f"repos/{repo}/actions/runs/{run_id}/logs",
            logs_dir / f"run_{run_id}.zip",
        )
        if ok:
            log_available += 1
        else:
            log_unavailable += 1
            negative.append({"type": "run_logs", "id": run_id, "error": error or "unavailable"})

    negative_path = root / "negative_results.jsonl"
    with negative_path.open("w", encoding="utf-8", newline="\n") as fh:
        for item in negative:
            fh.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in {"archive_manifest.json", "SHA256SUMS.txt"}:
            continue
        files.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    manifest = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at,
        "repository": repo,
        "source_commit": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "pull_requests_exported": len(pulls),
        "actions_runs_exported": len(runs),
        "actions_log_available_count": log_available,
        "actions_log_unavailable_count": log_unavailable,
        "negative_result_count": len(negative),
        "actions_artifact_bytes_policy": "inventory_only_here; canonical bytes are preserved by product-specific or repository-snapshot flows",
        "files": files,
    }
    (root / "archive_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    checksum_paths = [p for p in sorted(root.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.txt"]
    with (root / "SHA256SUMS.txt").open("w", encoding="utf-8", newline="\n") as fh:
        for path in checksum_paths:
            fh.write(f"{sha256(path)}  {path.relative_to(root).as_posix()}\n")

    print(json.dumps({
        "status": "ok",
        "repository": repo,
        "pull_requests": len(pulls),
        "actions_runs": len(runs),
        "logs_available": log_available,
        "logs_unavailable": log_unavailable,
        "negative_results": len(negative),
        "files": len(files),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
