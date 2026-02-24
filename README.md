<!-- README.md -->
# Ops QA Auditor

A configurable **operations QA audit tool** that evaluates support transcripts against a checklist and generates
**scored QA reports** (JSON + Markdown). Designed to showcase process quality, consistency, and feedback loops.

## Why this exists
Quality assurance in ops isn’t “vibes.” It’s repeatable checks, clear standards, and useful feedback.
This tool demonstrates:
- Checklist-based auditing
- Scoring + pass/fail thresholds
- Actionable findings + recommendations
- Batch reporting for operational workflows

## Quickstart

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"