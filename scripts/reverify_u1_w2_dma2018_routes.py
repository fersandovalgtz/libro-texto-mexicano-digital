#!/usr/bin/env python3
"""Reverify the four retained LTMD-U1 W2 DMA 2018 institutional routes.

Source JPEG bodies are read only in memory to compute SHA-256 and are never
written to disk. The result is technical metadata only. Every newly observed
served-image hash is compared with the versioned W2 asset manifest already in
the repository, making this run independent of the legacy write-capable
workflow topology.
"""
from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CONFIG = Path("data/catalog/ltmd_u1_w2_math_dma_config.csv")
LEGACY = Path("data/catalog/ltmd_u1_w2_math_asset_manifest.csv")
OUT_CSV = Path("u1-w2-dma2018-reverification.csv")
OUT_JSON = Path("u1-w2-dma2018-reverification.json")
BASE = "https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg"
UA = "LibroTextoMexicanoDigital/U1-W2-DMA2018-reverify-0.1"
VIEWERS = ("H2018P3DMA", "H2018P4DMA", "H2018P5DMA", "H2018P6DMA")
EXPECTED_SERVED = {
    "H2018P3DMA": 225,
    "H2018P4DMA": 257,
    "H2018P5DMA": 225,
    "H2018P6DMA": 185,
}


def fetch(url: str, attempts: int = 3) -> dict:
    last = ""
    for attempt in range(1, attempts + 1):
        try:
            h = hashlib.sha256()
            size = 0
            with urlopen(Request(url, headers={"User-Agent": UA}), timeout=45) as response:
                status = getattr(response, "status", None)
                ctype = response.headers.get("Content-Type", "")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    h.update(chunk)
                    size += len(chunk)
            if status == 200 and "image" in ctype.lower() and size > 0:
                return {
                    "state": "served_image",
                    "http_status": 200,
                    "content_type": ctype,
                    "byte_size": size,
                    "sha256": h.hexdigest(),
                    "attempts": attempt,
                    "error": "",
                }
            last = f"unexpected status={status} type={ctype} size={size}"
        except HTTPError as exc:
            if exc.code == 404:
                return {
                    "state": "http_404",
                    "http_status": 404,
                    "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
                    "byte_size": "",
                    "sha256": "",
                    "attempts": attempt,
                    "error": "HTTP 404",
                }
            last = f"HTTPError {exc.code}"
        except (URLError, TimeoutError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
        if attempt < attempts:
            time.sleep(attempt)
    return {
        "state": "probe_error",
        "http_status": "",
        "content_type": "",
        "byte_size": "",
        "sha256": "",
        "attempts": attempts,
        "error": last,
    }


def load_prior_hashes() -> dict[tuple[str, int], str]:
    prior: dict[tuple[str, int], str] = {}
    with LEGACY.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"viewer_key", "source_image_index", "sha256"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"legacy manifest missing fields: {sorted(missing)}")
        for row in reader:
            key = row.get("viewer_key", "")
            if key not in VIEWERS or not row.get("sha256"):
                continue
            try:
                idx = int(row["source_image_index"])
            except ValueError:
                continue
            prior[(key, idx)] = row["sha256"].lower()
    return prior


def main() -> None:
    config = {
        row["viewer_key"]: row
        for row in csv.DictReader(CONFIG.open(encoding="utf-8", newline=""))
        if row["viewer_key"] in VIEWERS
    }
    if set(config) != set(VIEWERS):
        raise SystemExit(f"missing DMA config rows: {sorted(set(VIEWERS) - set(config))}")

    prior = load_prior_hashes()
    observations: list[dict] = []
    per_viewer: dict[str, dict] = {}

    for viewer in VIEWERS:
        n = int(config[viewer]["ag_pages"])
        served = terminal_404 = internal_404 = errors = stable_hash = missing_prior = 0
        byte_sum = 0
        for page in range(1, n + 1):
            idx = 0 if page == 1 else page
            url = BASE.format(key=viewer, idx=idx)
            probe = fetch(url)
            final = page == n
            if probe["state"] == "served_image":
                status = "source_jpeg"
                served += 1
                byte_sum += int(probe["byte_size"])
            elif probe["state"] == "http_404" and final:
                status = "terminal_synthetic_candidate"
                terminal_404 += 1
            elif probe["state"] == "http_404":
                status = "internal_unserved"
                internal_404 += 1
            else:
                status = "probe_error"
                errors += 1

            old_hash = prior.get((viewer, idx), "")
            if status == "source_jpeg":
                if old_hash and old_hash == probe["sha256"].lower():
                    comparison = "match"
                    stable_hash += 1
                elif old_hash:
                    comparison = "mismatch"
                else:
                    comparison = "missing_prior"
                    missing_prior += 1
            else:
                comparison = "not_applicable"

            observations.append({
                "verification_version": "LTMD_U1_W2_DMA2018_ROUTE_REVERIFY_0.1",
                "viewer_key": viewer,
                "viewer_page": page,
                "declared_positions": n,
                "source_image_index": idx,
                "source_asset_url": url,
                "is_final_declared_position": int(final),
                "asset_status": status,
                "http_status": probe["http_status"],
                "content_type": probe["content_type"],
                "byte_size": probe["byte_size"],
                "sha256": probe["sha256"],
                "prior_sha256": old_hash,
                "prior_hash_comparison": comparison,
                "attempts": probe["attempts"],
                "error": probe["error"],
            })

        per_viewer[viewer] = {
            "declared_positions": n,
            "served_images": served,
            "expected_served_images": EXPECTED_SERVED[viewer],
            "terminal_404": terminal_404,
            "internal_404": internal_404,
            "probe_errors": errors,
            "byte_sum": byte_sum,
            "stable_hash_matches": stable_hash,
            "missing_prior_hashes": missing_prior,
        }
        print(viewer, json.dumps(per_viewer[viewer], sort_keys=True))

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(observations[0]))
        writer.writeheader()
        writer.writerows(observations)

    all_pass = all(
        s["served_images"] == s["expected_served_images"]
        and s["terminal_404"] == 1
        and s["internal_404"] == 0
        and s["probe_errors"] == 0
        and s["stable_hash_matches"] == s["served_images"]
        and s["missing_prior_hashes"] == 0
        for s in per_viewer.values()
    )
    summary = {
        "verification_version": "LTMD_U1_W2_DMA2018_ROUTE_REVERIFY_0.1",
        "scope": list(VIEWERS),
        "institutional_route_template": BASE,
        "source_body_persistence": "none",
        "comparison_basis": "versioned ltmd_u1_w2_math_asset_manifest.csv",
        "per_viewer": per_viewer,
        "total_served_images": sum(v["served_images"] for v in per_viewer.values()),
        "total_bytes_streamed": sum(v["byte_sum"] for v in per_viewer.values()),
        "total_stable_hash_matches": sum(v["stable_hash_matches"] for v in per_viewer.values()),
        "all_pass": all_pass,
    }
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    if not all_pass:
        raise SystemExit("DMA 2018 reverification did not satisfy closure gate")


if __name__ == "__main__":
    main()
