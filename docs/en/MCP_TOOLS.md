# OctaveMCP Tools Reference (English)

English · [Türkçe](../MCP_TOOLS.md)

This document describes the tools exposed via the MCP stdio bridge:
parameters, return shapes, and short examples.

## General

- Server: `src/mcp_server.py`
- Run:

  ```bash
  source .venv/bin/activate
  python src/mcp_server.py
  ```

### LM Studio Universal Config (v0.3.1)

This configuration works in both script and module modes; the server automatically
handles import/path issues:

```json
{
  "mcpServers": {
    "octave_execute": {
      "command": "/path/to/octave-mcp/.venv/bin/python",
      "args": [
        "/path/to/octave-mcp/src/mcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PATH": "/opt/homebrew/bin:/usr/local/bin:${PATH}",
        "MCP_RUNS_ROOT": "/path/to/octave-mcp/runs",
        "TMPDIR": "/path/to/octave-mcp/runs",
        "OCTAVE_RUNNER_MODE": "python",
        "MCP_IS_VISION_MODEL": "false",
        "MCP_RATE_LIMIT_MAX": "100",
        "MCP_RATE_LIMIT_WINDOW": "60",
        "MCP_MAX_OUTPUT_CHARS": "20000",
        "MCP_TIMEOUT_SECONDS": "10",
        "MCP_CPU_LIMIT": "0",
        "MCP_MEMORY_MB": "0",
        "MCP_RUNS_RETENTION_DAYS": "0"
      }
    }
  }
}
```

## Tool: `octave_run`

- Description: Execute code with Octave or Python; returns stdout/stderr and images.
- Parameters:
  - `code` (str, required): The Python/Octave code to run
  - `session_id` (str, optional): Session identifier
  - `images_b64` (bool, optional, default: false): Return images as base64
  - `max_image_bytes` (int, optional, default: 200000): Max bytes per image
- Return:
  - `success` (bool), `stdout` (str), `stderr` (str),
    `exit_code` (int), `runtime_seconds` (float)
  - `images`: Array. Each item:
    `{ name, path?, b64?, size? }`
- Example (pseudocode):

  ```json
  {
    "code": "plot(1:10); disp('ok');",
    "images_b64": true,
    "max_image_bytes": 200000
  }
  ```

## Tool: `octave_publish`

- Description: Converts code to HTML and stores under
  `runs/<session_id>/published/`.
- Parameters:
  - `code` (str, required)
  - `session_id` (str, optional)
- Return:
  - `html_b64`, `html_truncated`, `html_original_size`,
    `publish_dir`, `html_name`, `images`, `warnings`
- Notes:
  - Figures from the last run (e.g., `fig*.png`) are copied into `images/` and
    embedded into HTML via `<img>`.

## Tool: `octave_grabcode`

- Description: Retrieves the last published code for a given session.
- Parameters:
  - `session_id` (str, required)
- Return:
  - `code`, `b64`, `lines`

## Tool: `admin_cleanup`

- Description: Cleans old runs according to retention settings.
- Parameters:
  - `dry_run` (bool, default: true): Report only, do not delete
  - `force` (bool, default: false): Skip age checks and target all (guarded by policy)
  - `max_age_hours` (int, optional)
  - `max_age_days` (int, optional)
  - `session_id` (str, optional): Target only this session
- Return:
  - `deleted_runs`, `deleted_sessions`, `dry_run`, `errors`
- Policy:
  - `force: true` is allowed only when `MCP_ALLOW_FORCE_DELETE=true`;
    otherwise the operation is blocked and returns an error.

## Tips

- To capture figures with Octave mode:

  ```bash
  export OCTAVE_RUNNER_MODE=octave
  ```

- If you don't want large images as base64, use `images_b64=false` or reduce `max_image_bytes`.
