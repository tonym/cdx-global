---
name: phase-summary
description: Create or update a detailed Markdown phase/epic summary file (phase goal, scope, deliverables, highlights, decisions, risks, architectural impact, handoff/task rollups, and next phase guidance). Use when asked to “write a phase summary”, “epic recap”, “project phase wrap-up”, “milestone summary”, or to summarize multiple task handoffs into one phase document.
---

# Phase summary

## Defaults

- Default summary folder: `memory/summary/`
- Default file naming: `<timestamp>-<slug>.md` (timestamp format: `YYYY-MM-DD-HHMMSS`)

## Workflow

1. Confirm (or choose) `phase title` and output folder/path.
2. If the phase is unnamed, choose a short, human-recognizable label that communicates what the phase accomplished (this becomes the slug).
3. Create the summary file if it doesn’t exist.
4. Append or write a new entry using `assets/phase-summary-template.md`.
5. If task handoffs exist for this phase (typically under `memory/handoff/`), include a rollup list of those handoff files and summarize them.
6. Keep it detailed enough to onboard someone new, but still scannable (sections + bullets).

## Script (recommended)

Prefer generating the summary with:

```bash
python3 skills/phase-summary/scripts/write_phase_summary.py --title "..." --path memory/summary/ --handoff-glob "memory/handoff/*.md"
```

Notes:

- If `--path` points at a directory, the script creates `<timestamp>-<slug>.md` inside it.
- If `--handoff-glob` matches files, the script lists them in the summary and leaves structured placeholders for a rollup.
- If git info can’t be detected, the script leaves placeholders for repo state and changed files.

## Output constraints

- Prefer sections and bullets; avoid long prose.
- Don’t paste large diffs or code; link to repo paths instead.
- Always include a short “Seed for next thread” block at the end.
