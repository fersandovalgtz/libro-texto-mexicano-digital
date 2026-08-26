from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "probe_ltmd_u1_w7_source_recovery.py"
spec = importlib.util.spec_from_file_location("w7_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


class InspectPayloadTests(unittest.TestCase):
    def test_valid_jpeg_is_verified_and_hashed(self):
        data = b"\xff\xd8\xff" + b"ltmd-test" + b"\xff\xd9"
        verified, signature, digest, hash_match, reason = probe.inspect_payload(data, "image/jpeg")
        self.assertTrue(verified)
        self.assertEqual(signature, "jpeg")
        self.assertEqual(digest, hashlib.sha256(data).hexdigest())
        self.assertIsNone(hash_match)
        self.assertEqual(reason, "")

    def test_html_is_rejected(self):
        verified, signature, _, _, reason = probe.inspect_payload(
            b"<!doctype html><html></html>", "text/html"
        )
        self.assertFalse(verified)
        self.assertEqual(signature, "html")
        self.assertIn("HTML", reason)

    def test_expected_hash_mismatch_fails_closed(self):
        data = b"%PDF-1.7\n%%EOF\n"
        verified, signature, _, hash_match, reason = probe.inspect_payload(
            data, "application/pdf", "0" * 64
        )
        self.assertFalse(verified)
        self.assertEqual(signature, "hash-mismatch")
        self.assertFalse(hash_match)
        self.assertIn("sha256", reason)


class SequenceGateTests(unittest.TestCase):
    def result(self, index, expected=2, *, verified=True, provenance="verified", rights="verified"):
        return probe.AssetResult(
            probe.VERSION, "X", f"https://example.invalid/{index}", f"https://example.invalid/{index}",
            index, expected, True, verified, 200, "image/jpeg", 10, "a" * 64, "", None, "jpeg",
            provenance, rights, "", "",
        )

    def test_complete_verified_sequence_can_be_admissible(self):
        summary = probe.summarize([self.result(1), self.result(2)])[0]
        self.assertTrue(summary["sequence_verified"])
        self.assertTrue(summary["admissible"])

    def test_missing_sequence_item_is_not_admissible(self):
        summary = probe.summarize([self.result(1)])[0]
        self.assertFalse(summary["sequence_verified"])
        self.assertFalse(summary["admissible"])

    def test_unknown_rights_blocks_admissibility(self):
        summary = probe.summarize([self.result(1, rights="unknown"), self.result(2)])[0]
        self.assertTrue(summary["sequence_verified"])
        self.assertFalse(summary["rights_verified"])
        self.assertFalse(summary["admissible"])


if __name__ == "__main__":
    unittest.main()
