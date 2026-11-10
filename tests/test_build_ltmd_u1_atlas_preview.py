"""Privacy, scientific integrity and determinism gates for offline atlas preview."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "build_ltmd_u1_atlas_preview.py"
SPEC = importlib.util.spec_from_file_location("ltmd_u1_atlas_preview", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def fixture(tmp_path):
    rows = [
        ["generation", "corpus_total_pages", "candidate_pages", "explicit_general_pages", "named_language_contextual_pages", "candidate_books", "candidate_pages_per_1000_corpus_pages", "epistemic_state"],
    ]
    candidates = 0
    for year in mod.YEARS:
        count = 2 if year == 1993 else 1
        candidates += count
        rows.append([year, 1000, count, 1, 1, 1, str(float(count)), "exploratory_signal"])
    items = {
        mod.FILES["generations"]: rows,
        mod.FILES["terms"]: [list(mod.TERM_COLUMNS), ["lengua indigena", "1993", "2", "1", "computational_candidate"]],
        mod.FILES["validation"]: [["validation_status", "candidate_pages"], ["not_visually_validated", candidates]],
    }
    manifest = {"scientific_state": {"human_validation_complete": False, "semantic_ready_promotions": 0},
                "version": "LTMD_ANALYTICS_INDIGENOUS_0.1", "source_analysis_version": "fixture",
                "cardinality": {"candidate_pages": candidates, "generation_rows": 11, "explicit_term_rows": 1}, "outputs": {}}
    for name, table in items.items():
        with (tmp_path / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerows(table)
        manifest["outputs"][name] = {"sha256": mod.sha256(tmp_path / name)}
    (tmp_path / "ltmd_analytics_indigenous_manifest_0_1.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path, manifest


def test_build_payload_and_self_contained_html(tmp_path):
    directory, _ = fixture(tmp_path)
    p = mod.build_payload(directory)
    html = mod.render_html(p)
    assert p["totals"]["generation_observations"] == 12
    assert len(p["generation_rows"]) == 11
    assert p["human_validation_complete"] is False
    assert "1993" in html and "<svg id=\"chart\"" in html
    assert "not validated" not in html  # Spanish epistemic warning, not fake English state
    assert "No inferir ausencia" in html
    assert "<script src=" not in html  # no remote JS dependencies; SVG namespace is a non-network URL
    assert mod.render_html(p) == html


def test_refuse_source_leakage(tmp_path):
    d, manifest = fixture(tmp_path)
    path = d / mod.FILES["terms"]
    path.write_text(path.read_text().replace("explicit_term,generation", "page_id,explicit_term,generation"), encoding="utf-8")
    manifest["outputs"][path.name]["sha256"] = mod.sha256(path)
    (d / "ltmd_analytics_indigenous_manifest_0_1.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected CSV fields"):
        mod.build_payload(d)


def test_reject_mismatched_sha(tmp_path):
    d, _ = fixture(tmp_path)
    (d / mod.FILES["terms"]).write_text("manipulated", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        mod.build_payload(d)


def test_no_human_validation_promotion(tmp_path):
    d, manifest = fixture(tmp_path)
    manifest["scientific_state"]["human_validation_complete"] = True
    (d / "ltmd_analytics_indigenous_manifest_0_1.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported human validation"):
        mod.build_payload(d)


def test_refuse_false_rate_and_duplicates(tmp_path):
    d, manifest = fixture(tmp_path)
    path = d / mod.FILES["generations"]
    path.write_text(path.read_text().replace("1993,1000,2,1,1,1,2.0", "1993,1000,2,1,1,1,9.0"), encoding="utf-8")
    manifest["outputs"][path.name]["sha256"] = mod.sha256(path)
    (d / "ltmd_analytics_indigenous_manifest_0_1.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="rate/denominator mismatch"):
        mod.build_payload(d)


def test_escape_embedded_script_payload():
    txt = mod.render_html({"x": "</script><script>alert(1)</script>"})
    assert "</script><script>alert(1)</script>" not in txt
    assert "\\u003c/script\\u003e" in txt


def test_git_lf_checkout_equivalent_to_upstream_crlf_hash(tmp_path):
    d, manifest = fixture(tmp_path)
    for name in mod.FILES.values():
        raw = (d / name).read_bytes()  # synthetic Git LF checkout
        manifest["outputs"][name]["sha256"] = mod.sha256(d / name) if b"\r" in raw else __import__("hashlib").sha256(raw.replace(b"\n", b"\r\n")).hexdigest()
    (d / "ltmd_analytics_indigenous_manifest_0_1.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert mod.build_payload(d)["totals"]["generation_observations"] == 12
