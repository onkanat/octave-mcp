# OctaveMCP (English) v0.3.1

{% seo %}

[Türkçe](../index.md) · English

Welcome! This is the English documentation for OctaveMCP.

- Project version: 0.3.1

## LM Studio Universal Config Example

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

This config works for both script and module execution. All import and path issues are handled automatically.
- Tech stack: FastMCP + FastAPI + GNU Octave

## Overview

OctaveMCP provides:

- MCP STDIO tools: `octave_run`, `octave_publish`, `octave_grabcode`, `admin_cleanup`
- HTTP REST API: `/run`, `/publish`, `/grabcode`, `/cleanup`

See also:

- [API Reference (EN)](./API.md)
- [API Reference (TR)](../API.md)
- [MCP Tools](../MCP_TOOLS.md)
- [Error Schema](../ERROR_SCHEMA.md)
- [Turkish Docs (Ana Sayfa)](../index.md)
