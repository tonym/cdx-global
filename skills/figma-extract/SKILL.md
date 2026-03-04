---
name: figma-extract
description: Extract Figma variables through figma_console MCP (read-only), normalize deterministically, and write snapshot JSON artifacts using optional repo config (no CLI dependency).
---

# Figma extract

## Purpose

Use this skill when you need to pull design tokens/variables from Figma through `figma_console` and write deterministic snapshot artifacts directly from the agent flow.

This skill is intentionally repo-agnostic:

- one Figma read call (`figma_get_variables`)
- no Figma write/mutate calls
- no dependence on a repo-specific extraction helper or CLI wrapper

## Read-only rules

Allowed Figma tools:

- `figma_get_status` (preflight)
- `figma_get_variables` (extraction)

Do not call Figma mutate tools (`create`, `set`, `update`, `delete`, `instantiate`, etc.).

## Optional Repo Config

If present, read config from one of these paths (first match wins):

1. user-provided path
2. `.codex/figma-extract.json`
3. `figma-extract.config.json`

Config schema (example file: `references/repo-config.example.json`):

```json
{
  "collectionName": "Prism UI Core Tokens",
  "outputDir": "domains/ui-core/authoring/snapshots/figma",
  "latestFile": "domains/ui-core/authoring/snapshots/figma/latest.json",
  "source": {
    "serverName": "figma_console",
    "toolName": "figma_get_variables"
  },
  "mcp": {
    "format": "full",
    "verbosity": "standard",
    "refreshCache": true,
    "useConsoleFallback": false
  }
}
```

Defaults when config is absent:

- `collectionName`: not enforced unless provided; if multiple collections exist, stop and ask user to disambiguate
- `outputDir`: `authoring/snapshots/figma` if that directory exists, otherwise `.codex/artifacts/figma/snapshots`
- `latestFile`: `<outputDir>/latest.json`
- `source.serverName`: `figma_console`
- `source.toolName`: `figma_get_variables`
- MCP payload:
  - `format: "full"`
  - `verbosity: "standard"`
  - `refreshCache: true`
  - `useConsoleFallback: false`

## Workflow

1. Resolve file URL:
- If user provided a URL, use it.
- Otherwise call `figma_get_status` and use `monitoredPageUrl`.

2. Preflight connection:
- Call `figma_get_status`.
- If no active transport (`websocket`/`cdp`) and no monitored page, stop and report a blocking condition.

3. Fetch variables once:
- Call `figma_get_variables` with configured/default MCP payload.
- This is the only Figma data call in this skill.

4. Normalize payload deterministically in-agent (no repo helper):
- Support both payload shapes:
  - `payload.data.variableCollections` + `payload.data.variables`
  - `payload.data.collections` + nested collection variables
- Build normalized snapshot object:
  - `schemaVersion: 1`
  - `source`: `{ transport: "mcp", serverName, toolName, collectionName }`
  - `collection`:
    - `id`, `name`, `defaultModeId`
    - `modes`: sort by `name`, then `id`
    - `variables`: sort by `name`, then `id`
      - keep only stable fields:
        - `id`, `name`, `resolvedType`
        - `description` (or `null`)
        - `hiddenFromPublishing` (boolean)
        - `scopes` (sorted array of strings)
        - `valuesByMode` (mode IDs sorted)
      - recursively sort keys in nested objects
- Strip/ignore volatile fields (timestamps, session IDs, runtime metadata).

5. Validate collection scope:
- If `collectionName` is configured, require exact match and fail otherwise.
- If not configured and there is exactly one collection, use it.
- If not configured and multiple collections exist, stop and ask for `collectionName`.

6. Compute content hash:
- Compute SHA-256 on stable-stringified snapshot object *before* `contentHash` is added.
- Add `contentHash` to the snapshot.

7. Generate snapshot ID:
- `snapshotId = YYYYMMDDTHHmmssZ-<hash8>` (UTC time + first 8 hash chars).

8. Write artifacts deterministically:
- Write `<outputDir>/<snapshotId>.json`.
- Write `latestFile`.
- JSON must be stable key ordered and pretty-printed with trailing newline.

9. Report summary:
- file URL
- collection name
- variable count
- content hash
- snapshot path
- latest path

## Blocking conditions

Stop and escalate to the user when:

- Figma transport is not connected
- collection disambiguation is required
- output path cannot be written
- extracted payload is missing collections/variables

## Notes

- Never shell out to repo extraction CLIs as part of this skill.
- If a repo offers its own normalizer/writer library, prefer this skill's portable normalization path unless the user explicitly asks to use repo helpers.
- Repeated runs over unchanged Figma data should produce byte-stable JSON content (hash identical; filename may differ due timestamp).
