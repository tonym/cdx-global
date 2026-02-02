---
name: task-handoff
description: Create or update a Markdown handoff summary file (goal, decisions, work completed, files changed, commands/tests run, next steps) to seed the next Codex/Chat thread or hand off work between Codex Desktop and the IDE plugin. Use when asked to “write a handoff”, “summarize this task/thread”, “create a context seed”, “end-of-task summary”, or “update docs/handoff.md”.
---

# Task handoff

## Defaults

- Default handoff path: `docs/handoff.md`
- If the user prefers one-file-per-task: `docs/handoff/YYYY-MM-DD-<slug>.md`

## Workflow

1. Confirm (or choose) `title` and `path`.
2. Create the handoff file if it doesn’t exist.
3. Append a new entry using `assets/handoff-template.md`.
4. If the repo is a git repo, auto-fill “Files changed” and “Repo state” from git.
5. Keep the entry compact and action-oriented; it should be safe to paste into a new thread.

## Script (recommended)

Prefer generating/updating the entry with:

```bash
python3 skills/task-handoff/scripts/update_handoff.py --title "..." --path docs/handoff.md
```

Notes:

- If `--path` points at a directory, the script creates `YYYY-MM-DD-<slug>.md` inside it.
- If git info can’t be detected, the script leaves placeholders for repo state and files changed.

## Output constraints

- Use short bullets; avoid long prose.
- Don’t paste large diffs or code; link to repo paths instead.
- Always include a short “Seed for next thread” block at the end.
