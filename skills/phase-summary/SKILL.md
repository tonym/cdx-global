---
name: phase-summary
description: Create or update a detailed Markdown phase/epic context summary file (goal, outcome, invariants, key decisions, constraints, failure modes, out-of-scope items, open questions, and end state). Use when asked to “write a phase summary”, “epic recap”, “phase context summary”, “project phase wrap-up”, or “milestone summary”.
---

# Phase summary

## Defaults

- Default summary folder: `memory/summary/`
- Default file naming: `<timestamp>-<slug>.md` (timestamp format: `YYYY-MM-DD-HHMMSS`)

## Workflow

1. Confirm (or choose) `phase title` and output folder/path.
2. If the phase is unnamed, choose a short, human-recognizable label that communicates what the phase accomplished (this becomes the slug).
3. Create the summary file if it doesn’t exist.
4. Write a “Context Summary” using `assets/phase-summary-template.md`.
5. If task handoffs exist for this phase (typically under `memory/handoff/`), use them as input for outcome, decisions, constraints, and failure modes (do not paste large diffs).
6. Keep it detailed enough to onboard someone new, but still scannable (sections + bullets).

## Script (recommended)

Prefer generating the summary with:

```bash
python3 skills/phase-summary/scripts/write_phase_summary.py --title "..." --path memory/summary/ --handoff-glob "memory/handoff/*.md"
```

Notes:

- If `--path` points at a directory, the script creates `<timestamp>-<slug>.md` inside it.
- If `--handoff-glob` matches files, use them as source material for the summary.

## Output constraints

- Prefer sections and bullets; avoid long prose.
- Don’t paste large diffs or code; link to repo paths instead.
