# Standard Error Block Schema (English)

English · [Türkçe](../ERROR_SCHEMA.md)

This document defines the standard error block returned by the HTTP API and MCP tools.
The schema aims to improve diagnosis, observability, and clarity around resource
limit violations.

## Purpose

- Consistent error structure so UIs/clients can parse uniformly
- Explicitly surfaces resource limit violations
- Carries short hints to speed up user actions when applicable

## JSON Schema (logical)

```json
{
  "id": "string (uuid)",
  "type": "string (enum: runtime_error|timeout|resource_violation|validation_error|rate_limited|internal)",
  "message": "string",
  "hint": "string?",
  "timestamp": "ISO-8601",
  "session_id": "string?",
  "run_id": "string?",
  "stdout_truncated": "boolean?",
  "stderr_truncated": "boolean?",
  "resource_violation": {
    "limit_type": "string (cpu|memory|timeout|output_chars)",
    "limit_value": "number|string",
    "observed_value": "number|string"
  },
  "details": {"...": "any"}
}
```

Notes:

- `id`: Unique correlation id (uuid4 recommended)
- `type`: Helps clients map to user-facing messages
- `hint`: Short suggestion to accelerate user action
- `resource_violation`: Present only when a limit is violated

## Usage Guidelines

- Every error should at least include `id`, `type`, `message`, `timestamp`
- For limit violations, `resource_violation` is required
- When truncation occurs, set `stdout_truncated`/`stderr_truncated` to true

## Integration

- HTTP: 4xx/5xx bodies should carry this block
- MCP: `toolError` or `toolResult.error` may return this block

## Future Work

- More specific types (e.g., `file_system_error`) and a `code` field
- Localization fields such as `localized_message`
