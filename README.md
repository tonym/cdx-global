# cdx-global

Versioned backup for Codex “global” artifacts (skills, automations, templates) used on this machine.

This repo is not meant to be a production app repo; it’s a workflow/tools repo.

## Layout

- `codex-home/`: versioned sources for selected files that Codex reads from
  `~/.codex/`
- `skills/`: Codex skills intended to live under `~/.codex/skills/`

## Global Codex instructions

The versioned source for workstation-wide guidance is
[`codex-home/AGENTS.md`](codex-home/AGENTS.md). This repository does not activate
that file automatically or modify `~/.codex`.

[Codex natively discovers global guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
from `$CODEX_HOME/AGENTS.override.md` or `$CODEX_HOME/AGENTS.md` when a session
starts. There is no native instruction for one `AGENTS.md` file to include
another.

### Activation options

#### Symlink (recommended)

Replace `~/.codex/AGENTS.md` with a symlink to the versioned source:

Move or remove any existing file at that path first, then create the link:

```bash
ln -s "$HOME/.codex/workspaces/default/codex-home/AGENTS.md" \
  "$HOME/.codex/AGENTS.md"
```

This uses Codex's native discovery directly and makes repository updates take
effect in new sessions. It depends on this repository remaining at the same
absolute path.

#### Pointer file

Keep `~/.codex/AGENTS.md` as a regular file containing a pointer such as:

```md
Before beginning work, read
`/Users/tonym/.codex/workspaces/default/codex-home/AGENTS.md` completely and
treat it as global guidance.
```

This avoids a filesystem symlink, but Codex natively loads only the pointer. A
second file read and instruction-following step is required, and the pointer
itself remains outside version control unless it is installed from a versioned
template.

Do not use
[`model_instructions_file`](https://learn.chatgpt.com/docs/config-file/reference)
for this purpose. That setting replaces Codex's built-in instructions instead
of adding global `AGENTS.md` guidance.

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
