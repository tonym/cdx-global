# cdx-global

Versioned backup for Codex “global” artifacts (skills, automations, templates) used on this machine.

This repo is not meant to be a production app repo; it’s a workflow/tools repo.

## Layout

- `skills/`: Codex skills intended to live under `~/.codex/skills/`

## Install / sync skills

Option A (copy):

```bash
rsync -a skills/ ~/.codex/skills/
```

Option B (symlink a single skill):

```bash
ln -s "$(pwd)/skills/task-handoff" ~/.codex/skills/task-handoff
```

## Included skills

### task-handoff

Append a compact task handoff entry to a Markdown file.

```bash
python3 skills/task-handoff/scripts/update_handoff.py --title "My task" --path memory/handoff/
```

### phase-summary

Write a detailed phase/epic summary (optionally rolling up task handoffs).

```bash
python3 skills/phase-summary/scripts/write_phase_summary.py --title "Phase label" --path memory/summary/ --handoff-glob "memory/handoff/*.md"
```

### figma-extract

Extract Prism UI Core Figma variables via Figma Console MCP (read-only) and write deterministic snapshots aligned with the ui-core authoring contract.
