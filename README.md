# Octave MCP Server

Bu depo hakkında hızlı bakış ve yönlendirmeler:

- Ayrıntılı kurulum ve kullanım: `docs/README.md`
- MCP araçlarının tam referansı: `docs/MCP_TOOLS.md`
- API ayrıntıları: `docs/API.md`
- Değişiklik günlüğü: `CHANGELOG.md`

Hızlı başlatma (macOS):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src/api/endpoints:app --reload
```

STDIO MCP sunucusu:

```sh
source .venv/bin/activate
python src/mcp_server.py
```

Testler:

```sh
pytest -q
```
