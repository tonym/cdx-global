#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import glob
import os
import re
import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: Path | None) -> str | None:
    try:
        out = subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="replace").strip()
    except Exception:
        return None


def _is_git_repo(cwd: Path) -> bool:
    return _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd) == "true"


def _git_info(repo_root: Path) -> dict[str, str]:
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root) or ""
    commit = _run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root) or ""
    return {"branch": branch, "commit": commit}


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "phase"


def _load_template(skill_dir: Path) -> str:
    template_path = skill_dir / "assets" / "phase-summary-template.md"
    return template_path.read_text(encoding="utf-8")


def _render(template: str, values: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return re.sub(r"\{\{([a-z0-9_]+)\}\}", repl, template)


def _format_handoff_files(paths: list[str], repo_root: Path | None) -> str:
    if not paths:
        return "(none)"

    result: list[str] = []
    for p in paths[:200]:
        pp = Path(p)
        if repo_root:
            try:
                pp = pp.resolve().relative_to(repo_root.resolve())
            except Exception:
                pass
        result.append(str(pp))

    if len(paths) > 200:
        result.append("…")

    return ", ".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a phase summary Markdown file (one file per phase).")
    parser.add_argument("--title", required=True, help="Human-readable phase title/label.")
    parser.add_argument("--path", default="memory/summary/", help="Summary file path or directory.")
    parser.add_argument("--handoff-glob", default="memory/handoff/*.md", help="Glob for task handoff files to include.")
    parser.add_argument("--phase-goal", default="(fill in)", help="Phase goal / objective.")
    parser.add_argument("--deliverables", default="(fill in)", help="Key deliverables shipped.")
    parser.add_argument("--highlights", default="(fill in)", help="Notable achievements.")
    parser.add_argument("--decisions", default="(fill in)", help="Key decisions/tradeoffs.")
    parser.add_argument("--architectural-impact", default="None", help="None | Minor | Significant.")
    parser.add_argument("--next-phase", default="(fill in)", help="What happens next.")
    parser.add_argument("--open-questions", default="(none)", help="Open questions / unknowns.")
    args = parser.parse_args()

    now = dt.datetime.now()
    date = now.date().isoformat()
    timestamp = now.strftime("%Y-%m-%d-%H%M%S")

    skill_dir = Path(__file__).resolve().parents[1]
    target = Path(args.path)
    if target.suffix.lower() != ".md":
        target.mkdir(parents=True, exist_ok=True)
        filename = f"{timestamp}-{_slugify(args.title)}.md"
        target = target / filename
    else:
        target.parent.mkdir(parents=True, exist_ok=True)

    repo_root: Path | None = None
    cwd = Path.cwd()
    if _is_git_repo(cwd):
        root = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
        if root:
            repo_root = Path(root)

    git_values = {"branch": "", "commit": ""}
    if repo_root:
        git_values = _git_info(repo_root)

    matched_handoffs = sorted(glob.glob(args.handoff_glob))
    handoff_files = _format_handoff_files(matched_handoffs, repo_root=repo_root)

    template = _load_template(skill_dir)
    entry = _render(
        template,
        {
            "date": date,
            "title": args.title,
            "phase_goal": args.phase_goal,
            "scope_in": "(fill in)",
            "scope_out": "(fill in)",
            "deliverables": args.deliverables,
            "highlights": args.highlights,
            "decisions": args.decisions,
            "architectural_impact": args.architectural_impact,
            "risks_tradeoffs": "(fill in)",
            "handoff_files": handoff_files,
            "files_changed_high_level": "(fill in)",
            "whats_done": "(fill in)",
            "whats_not_done": "(fill in)",
            "next_phase": args.next_phase,
            "open_questions": args.open_questions,
            **git_values,
        },
    ).strip()

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        prefix = "" if existing.endswith("\n") else "\n"
        to_write = existing + prefix + "\n---\n\n" + entry + "\n"
    else:
        header = "# Phase summary\n\n"
        to_write = header + entry + "\n"

    target.write_text(to_write, encoding="utf-8")
    print(f"Wrote phase summary to: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
