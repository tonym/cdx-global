#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
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

    files_staged = _run(["git", "diff", "--name-only", "--cached"], cwd=repo_root) or ""
    files_unstaged = _run(["git", "diff", "--name-only"], cwd=repo_root) or ""

    def format_files(s: str) -> str:
        items = [line.strip() for line in s.splitlines() if line.strip()]
        if not items:
            return "(none)"
        return ", ".join(items[:40]) + (" …" if len(items) > 40 else "")

    return {
        "branch": branch,
        "commit": commit,
        "files_staged": format_files(files_staged),
        "files_unstaged": format_files(files_unstaged),
    }


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "task"


def _load_template(skill_dir: Path) -> str:
    template_path = skill_dir / "assets" / "handoff-template.md"
    return template_path.read_text(encoding="utf-8")


def _render(template: str, values: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return re.sub(r"\{\{([a-z0-9_]+)\}\}", repl, template)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a task handoff entry to a Markdown file.")
    parser.add_argument("--title", required=True, help="Human-readable task title.")
    parser.add_argument("--path", default="memory/handoff/", help="Handoff file path or directory.")
    parser.add_argument("--goal", default="(fill in)", help="One-line goal.")
    parser.add_argument("--work-completed", default="(fill in)", help="High-level work completed.")
    parser.add_argument("--decisions", default="(fill in)", help="Key decisions or tradeoffs.")
    parser.add_argument("--next-steps", default="(fill in)", help="Concrete next steps.")
    parser.add_argument("--open-questions", default="(none)", help="Open questions / unknowns.")
    args = parser.parse_args()

    now = dt.datetime.now()
    today = now.date().isoformat()
    timestamp = now.strftime("%Y-%m-%d-%H%M%S")
    skill_dir = Path(__file__).resolve().parents[1]

    target = Path(args.path)
    if target.suffix.lower() != ".md":
        target.mkdir(parents=True, exist_ok=True)
        filename = f"{timestamp}-{_slugify(args.title)}.md"
        target = target / filename
    else:
        target.parent.mkdir(parents=True, exist_ok=True)

    repo_root = None
    cwd = Path.cwd()
    if _is_git_repo(cwd):
        root = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
        if root:
            repo_root = Path(root)

    git_values = {"branch": "", "commit": "", "files_staged": "(unknown)", "files_unstaged": "(unknown)"}
    if repo_root:
        git_values = _git_info(repo_root)

    template = _load_template(skill_dir)
    entry = _render(
        template,
        {
            "date": today,
            "title": args.title,
            "goal": args.goal,
            "scope_in": "(fill in)",
            "scope_out": "(fill in)",
            "decisions": args.decisions,
            "work_completed": args.work_completed,
            "commands_tests": "(fill in)",
            "next_steps": args.next_steps,
            "open_questions": args.open_questions,
            **git_values,
        },
    ).strip()

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        prefix = "" if existing.endswith("\n") else "\n"
        to_write = existing + prefix + "\n---\n\n" + entry + "\n"
    else:
        header = "# Handoff\n\n"
        to_write = header + entry + "\n"

    target.write_text(to_write, encoding="utf-8")
    print(f"Wrote handoff entry to: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
