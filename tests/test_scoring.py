# tests/test_scoring.py
from ops_qa_auditor.scoring import score_audit


def test_score_all_pass():
    s = score_audit(
        weights={"required_phrases": 40, "forbidden_phrases": 30, "required_sections": 20, "readability": 10},
        required_ok=True,
        forbidden_ok=True,
        sections_ok=True,
        text="SUMMARY:\nhello. NEXT STEPS:\nworld. " + ("x " * 50),
        readability_cfg={"min_word_count": 10, "max_word_count": 200},
        pass_threshold=80,
    )
    assert s.total == 100
    assert s.passed is True


def test_score_fail_required():
    s = score_audit(
        weights={"required_phrases": 40, "forbidden_phrases": 30, "required_sections": 20, "readability": 10},
        required_ok=False,
        forbidden_ok=True,
        sections_ok=True,
        text="SUMMARY:\nhello. NEXT STEPS:\nworld. " + ("x " * 50),
        readability_cfg={"min_word_count": 10, "max_word_count": 200},
        pass_threshold=80,
    )
    assert s.total == 60
    assert s.passed is False