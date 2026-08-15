#!/usr/bin/env python3
"""Read JPEG dimensions from a small ranged prefix of QC sample assets.

The script requests at most the first 64 KiB using HTTP Range. If the server
does not honor Range (HTTP 206), it closes the response without reading the
body. No source image is written to disk.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 JPEG header audit"
SOF_MARKERS = {0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF}
FIELDS = (
    "page_id","book_id","catalog_generation","viewer_page","qc_slot",
    "source_asset_url","http_status","content_range","bytes_read",
    "width_px","height_px","orientation","probe_status","error",
)


def jpeg_size(data: bytes) -> tuple[int,int] | None:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(data):
            break
        seglen = int.from_bytes(data[i:i+2], "big")
        if seglen < 2 or i + seglen > len(data):
            break
        if marker in SOF_MARKERS and seglen >= 7:
            height = int.from_bytes(data[i+3:i+5], "big")
            width = int.from_bytes(data[i+5:i+7], "big")
            return width, height
        i += seglen
    return None


def probe(row: dict[str,str], timeout: int = 10) -> dict[str,str|int]:
    req = Request(
        row["source_asset_url"],
        headers={"User-Agent": USER_AGENT, "Range": "bytes=0-65535"},
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            status = getattr(response, "status", "")
            content_range = response.headers.get("Content-Range", "")
            if status != 206:
                return {"http_status":status,"content_range":content_range,"bytes_read":0,
                        "width_px":"","height_px":"","orientation":"",
                        "probe_status":"range_not_honored","error":"response body not read"}
            data = response.read(65536)
        dims = jpeg_size(data)
        if not dims:
            return {"http_status":status,"content_range":content_range,"bytes_read":len(data),
                    "width_px":"","height_px":"","orientation":"",
                    "probe_status":"dimensions_not_found","error":"JPEG SOF marker not found in ranged prefix"}
        width, height = dims
        orientation = "portrait" if height > width else "landscape" if width > height else "square"
        return {"http_status":status,"content_range":content_range,"bytes_read":len(data),
                "width_px":width,"height_px":height,"orientation":orientation,
                "probe_status":"ok","error":""}
    except HTTPError as exc:
        return {"http_status":exc.code,"content_range":"","bytes_read":0,
                "width_px":"","height_px":"","orientation":"",
                "probe_status":"http_error","error":f"HTTPError: {exc}"}
    except Exception as exc:
        return {"http_status":"","content_range":"","bytes_read":0,
                "width_px":"","height_px":"","orientation":"",
                "probe_status":"error","error":f"{type(exc).__name__}: {exc}"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/derived/page_manifest.csv")
    ap.add_argument("--output", default="data/derived/qc_jpeg_dimensions.csv")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    with Path(args.manifest).open(encoding="utf-8", newline="") as fh:
        selected = [r for r in csv.DictReader(fh) if r["qc_positional_candidate"] == "yes"]

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(probe, selected))

    rows=[]
    for src,res in zip(selected,results):
        rows.append({
            "page_id":src["page_id"],"book_id":src["book_id"],
            "catalog_generation":src["catalog_generation"],"viewer_page":src["viewer_page"],
            "qc_slot":src["qc_slot"],"source_asset_url":src["source_asset_url"],**res,
        })

    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)

    ok=sum(r["probe_status"]=="ok" for r in rows)
    print(f"Dimension probes: {ok}/{len(rows)} successful")
    for r in rows:
        print(r["page_id"], r["http_status"], r["width_px"], r["height_px"], r["probe_status"])


if __name__ == "__main__":
    main()
