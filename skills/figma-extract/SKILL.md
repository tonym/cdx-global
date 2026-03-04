---
name: figma-extract
description: Extract Prism UI Core Figma variables via Figma Console MCP (read-only) and write deterministic snapshot artifacts matching the ui-core authoring snapshot contract.
---

# Figma extract

## Purpose

Use this skill when you need agent-driven extraction of UI Core Figma variables through `figma_console` MCP (without relying on REST API scopes), while producing the same deterministic snapshot artifacts as `figma:extract`.

The outcome should match CLI behavior:

- write `domains/ui-core/authoring/snapshots/figma/<snapshotId>.json`
- write `domains/ui-core/authoring/snapshots/figma/latest.json`
- preserve deterministic snapshot normalization and hashing

## Defaults

- Snapshot directory: `domains/ui-core/authoring/snapshots/figma/`
- Output files:
  - `<snapshotId>.json`
  - `latest.json`
- Snapshot ID format: `YYYYMMDDTHHmmssZ-<hash8>`
- Figma collection must be exactly: `Prism UI Core Tokens`
- MCP tool payload defaults:
  - `format: "full"`
  - `verbosity: "standard"`
  - `refreshCache: true`
  - `useConsoleFallback: false`

## Read-only rules

- Allowed Figma tools for extraction:
  - `figma_get_variables`
  - `figma_get_status` (optional preflight)
- Do not call write/mutate tools (`create`, `update`, `delete`, `set`, `instantiate`, etc.).

## Workflow

1. Resolve file URL:
   - If user provides `fileUrl`, validate/normalize to `https://www.figma.com/design/<fileKey>/<fileName>`.
   - If omitted, call `figma_get_status` and use `monitoredPageUrl` or current file URL from status.
2. Preflight transport with `figma_get_status`:
   - If no active transport (`websocket` or `cdp`), stop and report a blocking condition.
3. Call `figma_get_variables` using the defaults above.
4. Normalize using the repo’s canonical normalizer:
   - Use `domains/ui-core/authoring/lib/snapshot-schema.js` (`buildNormalizedSnapshot`)
   - Do not introduce a duplicate schema implementation.
5. Generate snapshot id exactly like CLI:
   - use content hash from normalized snapshot
   - snapshot id = `YYYYMMDDTHHmmssZ-<hash8>`
6. Write deterministic artifacts using stable JSON writer:
   - `domains/ui-core/authoring/lib/file-io.js` (`writeStableJson`)
7. Confirm output with:
   - collection name
   - variable count
   - content hash
   - snapshot path

## Implementation notes

- Prefer reusing ui-core authoring libraries over re-implementing sorting/hashing.
- Prefer reusing the repo extraction helpers directly where possible:
  - `domains/ui-core/authoring/lib/figma-extract.js`
  - `domains/ui-core/authoring/lib/snapshot-schema.js`
  - `domains/ui-core/authoring/lib/file-io.js`
- If `figma_get_variables` fails and status shows no active transport, surface a blocking message that bridge transport is not attached to this MCP instance.
- Keep extraction idempotent: repeated unchanged runs should produce byte-stable JSON.
