import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "observe_u2_page_count_resolution.py"
SPEC = importlib.util.spec_from_file_location("observe_u2_page_count_resolution", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_last_startxref_uses_latest_eof_marker():
    tail = b"startxref\n100\n%%EOF\nnoise\nstartxref\n250\n%%EOF\n"
    assert mod.last_startxref(tail) == 250


def test_parse_classic_xref_extracts_entries_root_and_prev():
    section = (
        b"xref\n"
        b"0 3\n"
        b"0000000000 65535 f \n"
        b"0000000017 00000 n \n"
        b"0000000099 00000 n \n"
        b"trailer\n"
        b"<< /Size 3 /Root 2 0 R /Prev 500 >>\n"
        b"startxref\n700\n%%EOF\n"
    )
    entries, root, prev = mod.parse_classic_xref(section)
    assert entries == {1: 17, 2: 99}
    assert root == (2, 0)
    assert prev == 500


def test_parse_classic_xref_rejects_xref_stream_marker():
    with pytest.raises(RuntimeError, match="not_classic"):
        mod.parse_classic_xref(b"42 0 obj\n<< /Type /XRef >>\n")


def test_parse_classic_xref_rejects_truncated_subsection():
    section = b"xref\n0 2\n0000000000 65535 f \n"
    with pytest.raises(RuntimeError, match="truncated"):
        mod.parse_classic_xref(section)


def test_ref_text_preserves_indirect_reference():
    assert mod.ref_text((113184, 0)) == "113184 0 R"
    assert mod.ref_text(None) == "not_observed"
