# src/ops_qa_auditor/scoring.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .utils import readability


@dataclass(frozen=True)
class ScoreBreakdown:
    total: int
    passed: bool
    details: dict[str, Any]


def _component_score(weight: int, ok: bool) -> int:
    return int(weight) if ok else 0


def score_audit(
    *,
    weights: dict[str, int],
    required_ok: bool,
    forbidden_ok: bool,
    sections_ok: bool,
    text: str,
    readability_cfg: dict[str, int],
    pass_threshold: int,
) -> ScoreBreakdown:
    stats = readability(text)
    min_wc = int(readability_cfg.get("min_word_count", 0))
    max_wc = int(readability_cfg.get("max_word_count", 10**9))
    readability_ok = (stats.word_count >= min_wc) and (stats.word_count <= max_wc)

    total = 0
    total += _component_score(int(weights.get("required_phrases", 0)), required_ok)
    total += _component_score(int(weights.get("forbidden_phrases", 0)), forbidden_ok)
    total += _component_score(int(weights.get("required_sections", 0)), sections_ok)
    total += _component_score(int(weights.get("readability", 0)), readability_ok)

    # Clamp to [0, 100] if your weights sum to 100 (recommended); otherwise clamp anyway.
    total = max(0, min(100, total))
    passed = total >= int(pass_threshold)

    return ScoreBreakdown(
        total=total,
        passed=passed,
        details={
            "readability": {
                "word_count": stats.word_count,
                "sentence_count": stats.sentence_count,
                "min_word_count": min_wc,
                "max_word_count": max_wc,
                "passed": readability_ok,
            },
            "components": {
                "required_phrases": {"weight": int(weights.get("required_phrases", 0)), "passed": required_ok},
                "forbidden_phrases": {"weight": int(weights.get("forbidden_phrases", 0)), "passed": forbidden_ok},
                "required_sections": {"weight": int(weights.get("required_sections", 0)), "passed": sections_ok},
                "readability": {"weight": int(weights.get("readability", 0)), "passed": readability_ok},
            },
            "pass_threshold": int(pass_threshold),
        },
    )