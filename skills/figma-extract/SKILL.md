---
name: figma-extract
description: Extract Prism UI Core Figma variables via Figma Console MCP (read-only) and write deterministic snapshot artifacts matching the ui-core authoring snapshot contract.
---

# Figma extract

## Purpose

Use this skill when you need agent-driven extraction of UI Core Figma variables through `figma_console` MCP (without relying on REST API scopes), while producing the same deterministic snapshot artifacts as `figma:extract`.

## Defaults

- Snapshot directory: `domains/ui-core/authoring/snapshots/figma/`
- Output files:
  - `<snapshotId>.json`
  - `latest.json`
- Snapshot ID format: `YYYYMMDDTHHmmssZ-<hash8>`
- Figma collection must be exactly: `Prism UI Core Tokens`

## Read-only rules

- Allowed Figma tools for extraction:
  - `figma_get_variables`
  - `figma_get_status` (optional preflight)
- Do not call write/mutate tools (`create`, `update`, `delete`, `set`, `instantiate`, etc.).

## Workflow

1. Validate or normalize the provided Figma file URL (`https://www.figma.com/design/<fileKey>/<fileName>`).
2. Optional preflight: call `figma_get_status` to verify bridge transport is active.
3. Call `figma_get_variables` with:
   - `fileUrl`
   - `format: "full"`
   - `verbosity: "standard"`
   - `refreshCache: true`
   - `useConsoleFallback: false`
4. Normalize using the repo’s canonical normalizer:
   - Use `domains/ui-core/authoring/lib/snapshot-schema.js` (`buildNormalizedSnapshot`)
   - Do not introduce a duplicate schema implementation.
5. Write deterministic artifacts using stable JSON writer:
   - `domains/ui-core/authoring/lib/file-io.js` (`writeStableJson`)
6. Confirm output with:
   - collection name
   - variable count
   - content hash
   - snapshot path

## Implementation notes

- Prefer reusing ui-core authoring libraries over re-implementing sorting/hashing.
- If `figma_get_variables` fails and status shows no active transport, surface a blocking message that bridge transport is not attached to this MCP instance.
- Keep extraction idempotent: repeated unchanged runs should produce byte-stable JSON.
