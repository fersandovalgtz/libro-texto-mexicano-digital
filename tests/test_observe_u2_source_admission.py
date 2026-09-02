import hashlib
import importlib.util
from email.message import Message
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "observe_u2_source_admission.py"
spec = importlib.util.spec_from_file_location("observe_u2_source_admission", MODULE_PATH)
observer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(observer)


class FakeResponse:
    status = 200

    def __init__(self, payload: bytes):
        self.payload = payload
        self.offset = 0
        headers = Message()
        headers["Content-Type"] = "application/pdf"
        headers["Content-Length"] = str(len(payload))
        self.headers = headers

    def read(self, size: int) -> bytes:
        if self.offset >= len(self.payload):
            return b""
        data = self.payload[self.offset : self.offset + size]
        self.offset += len(data)
        return data


def test_inspect_stream_hashes_without_needing_a_persisted_source():
    payload = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\nstartxref\n12\n%%EOF\n"
    result = observer.inspect_stream(FakeResponse(payload))
    assert result["http_status"] == 200
    assert result["content_type"] == "application/pdf"
    assert result["bytes_received"] == len(payload)
    assert result["sha256"] == hashlib.sha256(payload).hexdigest()
    assert result["pdf_signature"] is True
    assert result["eof_marker"] is True
    assert result["startxref_in_tail"] is True


def test_inspect_stream_detects_missing_pdf_markers():
    payload = b"not a pdf"
    result = observer.inspect_stream(FakeResponse(payload))
    assert result["pdf_signature"] is False
    assert result["eof_marker"] is False
    assert result["startxref_in_tail"] is False
