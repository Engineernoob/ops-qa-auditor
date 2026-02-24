# src/ops_qa_auditor/summary.py
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BatchSummary:
    total: int
    passed: int
    failed: int
    avg_score: float


def build_batch_summary_payload(results: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [int(r["result"]["score"]["total"]) for r in results]
    passed = sum(1 for r in results if bool(r["result"]["score"]["passed"]))
    total = len(results)
    failed = total - passed
    avg = (sum(scores) / total) if total else 0.0

    return {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "avg_score": round(avg, 2),
        },
        "results": [
            {
                "source_name": r["meta"]["source_name"],
                "score": int(r["result"]["score"]["total"]),
                "passed": bool(r["result"]["score"]["passed"]),
                "missing_required_phrases": r["result"]["findings"]["missing_required_phrases"],
                "found_forbidden_phrases": r["result"]["findings"]["found_forbidden_phrases"],
                "missing_required_sections": r["result"]["findings"]["missing_required_sections"],
            }
            for r in results
        ],
    }


def write_summary_json(out_path: Path, payload: dict[str, Any]) -> None:
    import json

    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_summary_csv(out_path: Path, payload: dict[str, Any]) -> None:
    rows = payload["results"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "source_name",
                "score",
                "passed",
                "missing_required_phrases_count",
                "found_forbidden_phrases_count",
                "missing_required_sections_count",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r["source_name"],
                    r["score"],
                    r["passed"],
                    len(r["missing_required_phrases"]),
                    len(r["found_forbidden_phrases"]),
                    len(r["missing_required_sections"]),
                ]
            )