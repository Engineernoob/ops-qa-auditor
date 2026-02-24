# src/ops_qa_auditor/cli.py
from __future__ import annotations

import argparse
from pathlib import Path

from .engine import audit_text, load_checklist, validate_checklist
from .reporting import ensure_reports_dir, write_json_report, write_md_report
from .summary import build_batch_summary_payload, write_summary_csv, write_summary_json

PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # .../src
PROJECT_ROOT = PACKAGE_ROOT.parent                 # repo root
DEFAULT_CHECKLIST = PROJECT_ROOT / "data" / "checklist.yml"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _print_checklist_warnings(checklist_path: str) -> tuple[object, int]:
    p = Path(checklist_path)
    if not p.exists():
        raise FileNotFoundError(
            f"Checklist not found at: {p}\n"
            f"Run from repo root or pass --checklist explicitly.\n"
            f"Default expected: {DEFAULT_CHECKLIST}"
        )

    checklist = load_checklist(p)
    warnings = validate_checklist(checklist)
    if warnings:
        print("Checklist warnings:")
        for w in warnings:
            print(f"- {w}")
        print()
    return checklist, len(warnings)


def cmd_audit_file(args: argparse.Namespace) -> int:
    checklist, _ = _print_checklist_warnings(args.checklist)

    in_path = Path(args.path)
    text = _read_text(in_path)
    payload = audit_text(text, checklist, source_name=in_path.name)

    out_dir = Path(args.out_dir)
    ensure_reports_dir(out_dir)
    json_path = out_dir / f"{in_path.stem}.json"
    md_path = out_dir / f"{in_path.stem}.md"

    write_json_report(json_path, payload)
    write_md_report(md_path, payload)

    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")
    print(f"Score: {payload['result']['score']['total']}  Pass: {payload['result']['score']['passed']}")
    return 0


def cmd_audit_batch(args: argparse.Namespace) -> int:
    checklist, _ = _print_checklist_warnings(args.checklist)

    in_dir = Path(args.dir)
    out_dir = Path(args.out_dir)
    ensure_reports_dir(out_dir)

    files = sorted([p for p in in_dir.glob("*.txt") if p.is_file()])
    if not files:
        print(f"No .txt transcripts found in {in_dir}")
        return 1

    results = []
    passed = 0

    for p in files:
        payload = audit_text(_read_text(p), checklist, source_name=p.name)
        results.append(payload)

        write_json_report(out_dir / f"{p.stem}.json", payload)
        write_md_report(out_dir / f"{p.stem}.md", payload)

        if payload["result"]["score"]["passed"]:
            passed += 1

    summary_payload = build_batch_summary_payload(results)
    write_summary_json(out_dir / "batch_summary.json", summary_payload)
    write_summary_csv(out_dir / "batch_summary.csv", summary_payload)

    print(f"Audited {len(files)} transcripts. Passed {passed}/{len(files)}.")
    print(f"Saved: {out_dir / 'batch_summary.json'}")
    print(f"Saved: {out_dir / 'batch_summary.csv'}")
    return 0


def cmd_checklist_validate(args: argparse.Namespace) -> int:
    checklist = load_checklist(Path(args.checklist))
    warnings = validate_checklist(checklist)
    if not warnings:
        print("Checklist looks good ✅")
        return 0

    print("Checklist issues / warnings:")
    for w in warnings:
        print(f"- {w}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ops-qa-auditor",
        description="Ops QA checklist-based transcript auditor.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit transcripts against a checklist.")
    audit_sub = audit.add_subparsers(dest="mode", required=True)

    f = audit_sub.add_parser("file", help="Audit a single transcript file.")
    f.add_argument("path", help="Path to transcript (.txt)")
    f.add_argument("--checklist", default=str(DEFAULT_CHECKLIST), help="Path to checklist.yml")
    f.add_argument("--out-dir", default="reports", help="Output directory for reports")
    f.set_defaults(func=cmd_audit_file)

    b = audit_sub.add_parser("batch", help="Audit all .txt transcripts in a folder.")
    b.add_argument("dir", help="Directory containing .txt transcripts")
    b.add_argument("--checklist", default=str(DEFAULT_CHECKLIST), help="Path to checklist.yml")
    b.add_argument("--out-dir", default="reports", help="Output directory for reports")
    b.set_defaults(func=cmd_audit_batch)

    cv = sub.add_parser("checklist", help="Checklist utilities.")
    cv_sub = cv.add_subparsers(dest="mode", required=True)

    v = cv_sub.add_parser("validate", help="Validate checklist.yml")
    v.add_argument("checklist", help="Path to checklist.yml")
    v.set_defaults(func=cmd_checklist_validate)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))