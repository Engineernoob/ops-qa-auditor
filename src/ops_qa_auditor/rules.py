# src/ops_qa_auditor/rules.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .utils import contains_phrase, normalize


@dataclass(frozen=True)
class RuleResult:
    passed: bool
    findings: list[str]


def check_required_phrases(text: str, required: Iterable[str]) -> RuleResult:
    missing = [p for p in required if not contains_phrase(text, p)]
    return RuleResult(passed=(len(missing) == 0), findings=missing)


def check_forbidden_phrases(text: str, forbidden: Iterable[str]) -> RuleResult:
    found = [p for p in forbidden if contains_phrase(text, p)]
    return RuleResult(passed=(len(found) == 0), findings=found)


def check_required_sections(text: str, required_sections: Iterable[str]) -> RuleResult:
    # Section check is slightly stricter: require exact header token after normalization, still case-insensitive.
    t = normalize(text).lower()
    missing = []
    for sec in required_sections:
        token = normalize(sec).lower()
        if token not in t:
            missing.append(sec)
    return RuleResult(passed=(len(missing) == 0), findings=missing)