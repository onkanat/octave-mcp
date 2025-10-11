# OctaveMCP

Secure GNU Octave code execution via MCP with FastMCP + FastAPI architecture.

[![Open in LM Studio](https://img.shields.io/badge/Open%20in-LM%20Studio-blue?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](lmstudio://install-model/octave-mcp)

## Quick Install

### Option 1: pip install (Recommended)

```sh
pip install octave-mcp
# MCP server için:
python -m src.mcp_server
# CLI kullanım için:
octave-mcp --help
```

### Option 2: One-line installer

```sh
curl -sSL https://raw.githubusercontent.com/onkanat/octave-mcp/master/
install.sh | bash
```

### Option 3: Development setup

```sh
git clone https://github.com/onkanat/octave-mcp.git
cd octave-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
# Start MCP server:
octave-mcp
# Or module approach:
python -m mcp_server
```

## Requirements

- Python 3.11+
- GNU Octave (for code execution)

## Documentation

- Detailed setup and usage: `docs/README.md`
- Complete MCP tools reference: `docs/MCP_TOOLS.md`
- API details: `docs/API.md`
- Change log: `CHANGELOG.md`

## Docs

GitHub Pages (yayınlandıktan sonra):

- Ana sayfa (TR): docs/index.md → <https://onkanat.github.io/octave-mcp/>
- Ana sayfa (EN): docs/en/index.md → <https://onkanat.github.io/octave-mcp/en/>

Hızlı linkler:

- API (TR): <https://onkanat.github.io/octave-mcp/API.html>
- API (EN): <https://onkanat.github.io/octave-mcp/en/API.html>
- MCP Tools (TR): <https://onkanat.github.io/octave-mcp/MCP_TOOLS.html>
- MCP Tools (EN): <https://onkanat.github.io/octave-mcp/en/MCP_TOOLS.html>
- Error Schema (TR): <https://onkanat.github.io/octave-mcp/ERROR_SCHEMA.html>
- Error Schema (EN): <https://onkanat.github.io/octave-mcp/en/ERROR_SCHEMA.html>
