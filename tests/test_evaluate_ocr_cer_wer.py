import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "evaluate_ocr_cer_wer.py"
SPEC = importlib.util.spec_from_file_location("evaluate_ocr_cer_wer", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class EvaluateOcrCerWerTest(unittest.TestCase):
    def test_normalization_preserves_orthography_and_removes_layout_artifacts(self):
        text = "Árbol\u00a0— ‘ni-\nño’ . . . ."
        self.assertEqual(mod.normalize_orthographic(text), "Árbol - 'niño'")
        self.assertEqual(mod.normalize_lexical(text), "árbol niño")

    def test_edit_distance_handles_strings_and_token_lists(self):
        self.assertEqual(mod.edit_distance("casa", "casa"), 0)
        self.assertEqual(mod.edit_distance("casa", "cosa"), 1)
        self.assertEqual(mod.edit_distance([], ["uno", "dos"]), 2)
        self.assertEqual(mod.edit_distance(["uno", "dos"], ["uno", "tres"]), 1)

    def test_metric_family_counts_blank_hypothesis_as_total_error(self):
        metrics = mod.metric_family("texto válido", "", "lexical")
        self.assertEqual(metrics["reference_chars_lexical"], 12)
        self.assertEqual(metrics["hypothesis_chars_lexical"], 0)
        self.assertEqual(metrics["char_edits_lexical"], 12)
        self.assertEqual(metrics["cer_lexical"], "1.000000")
        self.assertEqual(metrics["reference_words_lexical"], 2)
        self.assertEqual(metrics["word_edits_lexical"], 2)
        self.assertEqual(metrics["wer_lexical"], "1.000000")

    def test_metric_family_leaves_rates_blank_without_reference(self):
        metrics = mod.metric_family("", "texto espurio", "lexical")
        self.assertEqual(metrics["cer_lexical"], "")
        self.assertEqual(metrics["wer_lexical"], "")

    def test_scope_validation_rejects_invalid_crop(self):
        scope, error = mod.validate_scope({
            "reference_scope": "crop_block",
            "crop_x0": "0.8", "crop_y0": "0.1",
            "crop_x1": "0.2", "crop_y1": "0.9",
        })
        self.assertEqual(scope, "crop_block")
        self.assertEqual(error, "invalid_crop_bounds")

    def test_cli_keeps_blank_ocr_in_metrics_and_omits_private_text(self):
        fields = [
            "sample_id", "book_id", "generation", "page_id", "reference_scope",
            "human_reference_text_private", "ocr_region_text_private",
        ]
        rows = [
            {
                "sample_id": "EXACT", "book_id": "B1", "generation": "1972",
                "page_id": "P1", "reference_scope": "full_page",
                "human_reference_text_private": "Hola mundo",
                "ocr_region_text_private": "Hola mundo",
            },
            {
                "sample_id": "BLANK-OCR", "book_id": "B1", "generation": "1972",
                "page_id": "P2", "reference_scope": "full_page",
                "human_reference_text_private": "Texto visible",
                "ocr_region_text_private": "",
            },
            {
                "sample_id": "NO-REF", "book_id": "B1", "generation": "1972",
                "page_id": "P3", "reference_scope": "full_page",
                "human_reference_text_private": "",
                "ocr_region_text_private": "Texto OCR",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "private.csv"
            output = td / "metrics.csv"
            with source.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--output", str(output)],
                check=True, capture_output=True, text=True,
            )
            with output.open(encoding="utf-8", newline="") as fh:
                result = list(csv.DictReader(fh))

        self.assertIn("CER/WER computed for 2/3 rows", proc.stdout)
        self.assertNotIn("human_reference_text_private", result[0])
        self.assertNotIn("ocr_region_text_private", result[0])
        by_id = {row["validation_id"]: row for row in result}
        self.assertEqual(by_id["EXACT"]["status"], "ok")
        self.assertEqual(by_id["EXACT"]["cer"], "0.000000")
        self.assertEqual(by_id["EXACT"]["wer"], "0.000000")
        self.assertEqual(by_id["BLANK-OCR"]["status"], "ok_blank_hypothesis")
        self.assertEqual(by_id["BLANK-OCR"]["cer"], "1.000000")
        self.assertEqual(by_id["BLANK-OCR"]["wer"], "1.000000")
        self.assertEqual(by_id["NO-REF"]["status"], "missing_reference")
        self.assertEqual(by_id["NO-REF"]["cer"], "")
        self.assertEqual(by_id["NO-REF"]["wer"], "")


if __name__ == "__main__":
    unittest.main()
