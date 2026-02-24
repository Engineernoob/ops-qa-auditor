# tests/test_rules.py
from ops_qa_auditor.rules import check_forbidden_phrases, check_required_phrases, check_required_sections


def test_required_phrases_missing():
    text = "hello world"
    rr = check_required_phrases(text, ["NEXT STEPS", "SUMMARY"])
    assert rr.passed is False
    assert "NEXT STEPS" in rr.findings


def test_forbidden_phrases_found():
    text = "I guarantee this works."
    rr = check_forbidden_phrases(text, ["I guarantee", "diagnose"])
    assert rr.passed is False
    assert "I guarantee" in rr.findings


def test_required_sections():
    text = "SUMMARY:\nX\nNEXT STEPS:\nY"
    rr = check_required_sections(text, ["SUMMARY:", "NEXT STEPS:"])
    assert rr.passed is True
    assert rr.findings == []