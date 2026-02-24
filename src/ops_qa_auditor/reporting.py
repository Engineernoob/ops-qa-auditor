# src/ops_qa_auditor/reporting.py
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .scoring import ScoreBreakdown


def ensure_reports_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json_report(out_path: Path, payload: dict[str, Any]) -> None:
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_md_report(out_path: Path, payload: dict[str, Any]) -> None:
    # Keep the markdown simple and skim-friendly.
    lines: list[str] = []
    lines.append(f"# QA Audit Report: {payload['meta']['source_name']}")
    lines.append("")
    lines.append(f"**Score:** {payload['result']['score']['total']} / 100")
    lines.append(f"**Pass:** {'✅' if payload['result']['score']['passed'] else '❌'}")
    lines.append("")

    lines.append("## Findings")
    for k in ("missing_required_phrases", "found_forbidden_phrases", "missing_required_sections"):
        items = payload["result"]["findings"][k]
        label = k.replace("_", " ").title()
        lines.append(f"### {label}")
        if items:
            for it in items:
                lines.append(f"- {it}")
        else:
            lines.append("- None")
        lines.append("")

    rb = payload["result"]["score"]["details"]["readability"]
    lines.append("## Readability")
    lines.append(f"- Word count: {rb['word_count']} (min {rb['min_word_count']}, max {rb['max_word_count']})")
    lines.append(f"- Sentence count: {rb['sentence_count']}")
    lines.append(f"- Passed: {'✅' if rb['passed'] else '❌'}")
    lines.append("")

    lines.append("## Recommendations")
    recs = payload["result"]["recommendations"]
    if recs:
        for r in recs:
            lines.append(f"- {r}")
    else:
        lines.append("- None")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def serialize_score(score: ScoreBreakdown) -> dict[str, Any]:
    d = asdict(score)
    return d