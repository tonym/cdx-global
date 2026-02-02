#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import glob
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
    parser = argparse.ArgumentParser(description="Write a phase context summary Markdown file (one file per phase).")
    parser.add_argument("--title", required=True, help="Human-readable phase title/label.")
    parser.add_argument("--path", default="memory/summary/", help="Summary file path or directory.")
    parser.add_argument("--handoff-glob", default="memory/handoff/*.md", help="Glob for task handoff files to include.")
    parser.add_argument("--goal", default="(fill in)", help="What this phase was supposed to accomplish.")
    parser.add_argument("--outcome", default="(fill in)", help="What is now true that was not true before.")
    parser.add_argument("--invariants", default="* (fill in)", help="Bulleted list of invariants (rules/guarantees).")
    parser.add_argument("--key-decisions", default="* (fill in)", help="Bulleted list of key decisions and rationale.")
    parser.add_argument("--system-constraints", default="* (fill in)", help="Bulleted list of system constraints enforced.")
    parser.add_argument("--failure-modes", default="* (fill in)", help="Bulleted list of explicit failure modes / errors.")
    parser.add_argument("--out-of-scope", default="* (fill in)", help="Bulleted list of what is explicitly out of scope.")
    parser.add_argument("--open-questions", default="* (none)", help="Bulleted list of open questions / inputs to next phase.")
    parser.add_argument("--implementation-notes", default="* (optional)", help="Bulleted list of implementation notes.")
    parser.add_argument("--end-state", default="(fill in)", help="1–2 sentences describing the new stable state.")
    args = parser.parse_args()

    now = dt.datetime.now()
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

    if matched_handoffs:
        handoff_hint = f"* Source handoffs: {handoff_files}"
        invariants = f"{args.invariants}\n\n{handoff_hint}"
        key_decisions = f"{args.key_decisions}\n\n{handoff_hint}"
        system_constraints = f"{args.system_constraints}\n\n{handoff_hint}"
        failure_modes = f"{args.failure_modes}\n\n{handoff_hint}"
        open_questions = f"{args.open_questions}\n\n{handoff_hint}"
    else:
        invariants = args.invariants
        key_decisions = args.key_decisions
        system_constraints = args.system_constraints
        failure_modes = args.failure_modes
        open_questions = args.open_questions

    template = _load_template(skill_dir)
    entry = _render(
        template,
        {
            "title": args.title,
            "goal": args.goal,
            "outcome": args.outcome,
            "invariants": invariants,
            "key_decisions": key_decisions,
            "system_constraints": system_constraints,
            "failure_modes": failure_modes,
            "out_of_scope": args.out_of_scope,
            "open_questions": open_questions,
            "implementation_notes": args.implementation_notes,
            "end_state": args.end_state,
            **git_values,
        },
    ).strip()

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        prefix = "" if existing.endswith("\n") else "\n"
        to_write = existing + prefix + "\n---\n\n" + entry + "\n"
    else:
        to_write = entry + "\n"

    target.write_text(to_write, encoding="utf-8")
    print(f"Wrote phase summary to: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
