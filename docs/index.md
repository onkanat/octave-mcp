# OctaveMCP

{% seo %}

[Türkçe Dokümantasyon](./README.md) · [English](./en/index.md)

**Version**: 0.3.1 | **Tech Stack**: FastMCP + FastAPI + GNU Octave

## Overview

OctaveMCP is a secure Octave code execution service with dual interfaces:

- **MCP STDIO**: For LLM/MCP clients via `mcp_server.py`
- **HTTP REST API**: For web applications via `api/endpoints.py`

## Key Features

- ✅ **Secure Execution**: Resource limits, timeouts, sandboxing
- ✅ **Session Management**: Persistent workspaces with cleanup
- ✅ **Publish/Grabcode**: HTML output generation and source extraction
- ✅ **Image Capture**: Automatic PNG collection and embedding
- ✅ **Rate Limiting**: Token bucket for API protection
- ✅ **Error Reporting**: Structured error blocks with hints

## Quick Start

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### GNU Octave Setup

macOS:

```bash
brew install octave
```

Ubuntu/Debian:

```bash
sudo apt-get install octave
```

### Running the Services

**MCP STDIO Server** (for LLM clients):

```bash
python src/mcp_server.py
```

**HTTP API Server** (for web clients):

```bash
uvicorn src/api/endpoints:app --reload
```

Note: As a convenience `python src/mcp_server.py` now starts both the MCP STDIO
server and the HTTP API (uvicorn) in the same process. If you only want the
STDIO server, run:

```bash
python src/mcp_server.py --no-http
```

## Documentation

- 📖 [**README**](./README.md) - Detailed setup and usage
- 🔧 [**MCP Tools**](./MCP_TOOLS.md) - STDIO tool reference
- 🌐 [**API Reference**](./API.md) - HTTP endpoint documentation
- ❌ [**Error Schema**](./ERROR_SCHEMA.md) - Standard error format

## Architecture

```text
src/
├── mcp_server.py          # FastMCP STDIO interface
├── api/endpoints.py       # FastAPI HTTP interface
├── services/              # Core business logic
├── models/                # Data models
└── utils/                 # Utilities and config
```

## Example Usage

### MCP Tool Call

```json
{
  "tool": "octave_run",
  "arguments": {
    "code": "x = 1:10; y = x.^2; plot(x, y); print('-dpng', 'result.png');",
    "session_id": "demo_session"
  }
}
```

### HTTP API Call

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "disp(\"Hello Octave!\");"}'
```

## License

Educational and local use. Please comply with third-party licenses (GNU Octave, etc.).
