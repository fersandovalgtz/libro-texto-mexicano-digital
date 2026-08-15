import tempfile
import unittest
from pathlib import Path
import importlib.util

SPEC = importlib.util.spec_from_file_location(
    "extract_region_from_tsv", Path(__file__).parents[1] / "scripts" / "extract_region_from_tsv.py"
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class ExtractRegionTSVTest(unittest.TestCase):
    def test_unmatched_quote_in_ocr_token_does_not_absorb_following_rows(self):
        tsv = (
            "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
            "5\t1\t1\t1\t1\t1\t10\t10\t50\t10\t90\t\"mantenerla\n"
            "5\t1\t1\t1\t1\t2\t70\t10\t40\t10\t90\taseada,\n"
            "5\t1\t1\t1\t2\t1\t10\t30\t35\t10\t90\tevitar\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.tsv"
            path.write_text(tsv, encoding="utf-8")
            result = mod.extract(path, (0, 0, 200, 100))
        self.assertEqual(result, '\"mantenerla aseada,\nevitar')


if __name__ == "__main__":
    unittest.main()
