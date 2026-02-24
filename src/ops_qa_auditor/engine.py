# src/ops_qa_auditor/engine.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .reporting import serialize_score
from .rules import check_forbidden_phrases, check_required_phrases, check_required_sections
from .scoring import score_audit


@dataclass(frozen=True)
class Checklist:
    name: str
    pass_threshold: int
    weights: dict[str, int]
    required_phrases: list[str]
    forbidden_phrases: list[str]
    required_sections: list[str]
    readability: dict[str, int]


def load_checklist(path: Path) -> Checklist:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Checklist(
        name=str(raw.get("name", "Unnamed Checklist")),
        pass_threshold=int(raw.get("pass_threshold", 80)),
        weights=dict(raw.get("weights", {})),
        required_phrases=list(raw.get("required_phrases", [])),
        forbidden_phrases=list(raw.get("forbidden_phrases", [])),
        required_sections=list(raw.get("required_sections", [])),
        readability=dict(raw.get("readability", {})),
    )


def validate_checklist(checklist: Checklist) -> list[str]:
    errs: list[str] = []
    if not checklist.weights:
        errs.append("weights are missing.")
    # Encourage weights sum to 100, but don't hard-fail.
    total_w = sum(int(v) for v in checklist.weights.values())
    if total_w != 100:
        errs.append(f"weights sum to {total_w}, recommended sum is 100.")
    if checklist.pass_threshold < 0 or checklist.pass_threshold > 100:
        errs.append("pass_threshold must be between 0 and 100.")
    return errs


def audit_text(text: str, checklist: Checklist, source_name: str = "transcript") -> dict[str, Any]:
    req = check_required_phrases(text, checklist.required_phrases)
    forb = check_forbidden_phrases(text, checklist.forbidden_phrases)
    secs = check_required_sections(text, checklist.required_sections)

    score = score_audit(
        weights=checklist.weights,
        required_ok=req.passed,
        forbidden_ok=forb.passed,
        sections_ok=secs.passed,
        text=text,
        readability_cfg=checklist.readability,
        pass_threshold=checklist.pass_threshold,
    )

    recommendations: list[str] = []
    if not req.passed:
        recommendations.append("Add missing required phrases or elements to meet checklist standards.")
    if not forb.passed:
        recommendations.append("Remove forbidden language and replace with compliant, non-diagnostic phrasing.")
    if not secs.passed:
        recommendations.append("Add missing required sections (e.g., SUMMARY, NEXT STEPS) for consistency.")
    if not score.details["readability"]["passed"]:
        recommendations.append("Adjust transcript length to fit readability bounds (word count).")

    payload = {
        "meta": {
            "checklist_name": checklist.name,
            "source_name": source_name,
        },
        "result": {
            "score": serialize_score(score),
            "findings": {
                "missing_required_phrases": req.findings,
                "found_forbidden_phrases": forb.findings,
                "missing_required_sections": secs.findings,
            },
            "recommendations": recommendations,
        },
    }
    return payload