# tests/test_engine.py
from pathlib import Path

from ops_qa_auditor.engine import audit_text, load_checklist


def test_audit_text_smoke():
    checklist = load_checklist(Path("data/checklist.yml"))
    text = "SUMMARY:\nA\n\nNEXT STEPS:\nI can help you navigate."
    payload = audit_text(text, checklist, source_name="x.txt")
    assert "result" in payload
    assert "score" in payload["result"]
    assert 0 <= payload["result"]["score"]["total"] <= 100