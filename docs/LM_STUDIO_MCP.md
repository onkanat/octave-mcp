# LM Studio — MCP integration with OctaveMCP

Bu rehber LM Studio'nun MCP (Model Context Protocol) sunucularını nasıl ekleyeceğinizi ve
OctaveMCP (bu repo) ile nasıl entegre edeceğinizi gösterir. Ayrıca LM Studio'ya tek-tıkla
ekleme (deeplink) nasıl oluşturulur örnekleri içerir.

## Önemli güvenlik notu

- MCP sunucuları uzaktan kod çalıştırma yetkisine sahip olabilir. Bilinmeyen/şüpheli kaynaklardan
  MCP kurmayın.

## 1) `mcp.json` ile manuel ekleme

LM Studio program sekmesinde `Install > Edit mcp.json` ile uygulama içi editörde `mcp.json`
dosyasına yeni MCP sunucuları ekleyebilirsiniz. `mcp.json` içinde sadece `"mcpServers": { ... }`
içeriğini kopyalayıp yapıştırın.

Örnek OctaveMCP girişi:

```json
{
  "mcpServers": {
    "octave-mcp-local": {
      "url": "http://127.0.0.1:8000",
      "headers": {
        "Authorization": "Bearer <OPTIONAL_TOKEN_IF_USED>"
      }
    }
  }
}
```

Notlar:

- `url` alanı OctaveMCP sunucunuzun base URL'sidir (ör. `http://127.0.0.1:8000`).
- Eğer OctaveMCP'niz erişim kontrolü (API token) kullanıyorsa `headers.Authorization` içine
  `Bearer <TOKEN>` ekleyin.

## 2) Deeplink (tek-tıkla ekleme)

LM Studio `lmstudio://add_mcp` deeplink protokolünü destekler. Deeplink şu formattadır:

```
lmstudio://add_mcp?name=<NAME>&config=<BASE64_JSON>
```

Örnek: OctaveMCP için JSON kısmı şöyle olsun (yalnızca `mcpServers` içeriğini verin):

```json
{
  "octave-mcp-local": {
    "url": "http://127.0.0.1:8000",
    "headers": {}
  }
}
```

Bu JSON'u base64 encode edip deeplink oluşturabilirsiniz. Terminal örneği (macOS / Linux):

```bash
python3 - <<'PY'
import base64, json
cfg = {
  "octave-mcp-local": {
    "url": "http://127.0.0.1:8000",
    "headers": {}
  }
}
encoded = base64.urlsafe_b64encode(json.dumps(cfg).encode()).decode()
print(f"lmstudio://add_mcp?name=octave-mcp-local&config={encoded}")
PY
```

Bu bağlantıyı tarayıcıda açarsanız (ve LM Studio yüklü ise) uygulama açılır ve server eklenir.

## 3) LM Studio içinde test çağrıları (örnek)

OctaveMCP yerelde çalışıyorsa (`http://127.0.0.1:8000`) LM Studio üzerinden ekledikten sonra
modelden veya Tools bölümünden HTTP isteği tetikleyebilirsiniz. Doğrudan curl ile test:

```bash
curl -X POST "http://127.0.0.1:8000/run_octave" \
  -H "Content-Type: application/json" \
  -d '{"code":"disp(2+2)","session_id":"test-session-1"}'
```

Başka örnek endpoint'ler:

- `/publish`  — kodu HTML'e dönüştürüp kaydeder
- `/grabcode` — bir session için son yayınlanan kodu getirir

## 4) LM Studio Tool konfigurasyonu (özet)

- Tool name: OctaveMCP Run
- Method: POST
- URL: `http://127.0.0.1:8000/run_octave`
- Body (JSON): `{"code":"{{user_input}}","session_id":"{{session_id}}"}`

## 5) Komut-tabanlı MCP örneği ve deeplink yardımcıları

Bu repoya, LM Studio'nun komut-tabanlı MCP başlatma modu için hazır bir örnek JSON dosyası
ekledim: `mcp_command.json` (repo kökünde). Dosya, bu projenin tipik çalışma dizinlerine göre
ayarlandı — lütfen kendi çalışma dizininize göre `command` ve `args` içindeki absolute yolları
güncelleyin.

Özellikle kontrol etmeniz gerekenler (manuel düzenleme gerekirse):

- `command` — virtualenv içindeki Python yürütülebilirinin tam yolu veya pip'in yüklediği `octave-mcp` console-script adı.
- `args` — `src/mcp_server.py` dosyasının absolute yolu (yalnızca `python` yerine -m kullanmıyorsanız).
- `env` — `MCP_RUNS_ROOT`, `TMPDIR`, zaman aşımı ve resource limitleri gibi ortam değişkenleri.

Önerilen akış (taşınabilir kullanım):

1. Eğer kullanıcılar paketi `pip install octave-mcp` ile kuruyorsa, LM Studio komut olarak doğrudan
  `octave-mcp` console-script'ini çağırabilir. Bu durum için repo kökünde `mcp_command.json` taşınabilir bir
  örnek içerir (komut: `octave-mcp`).

2. LM Studio GUI ortamı console-script'i PATH'te bulamayabilir. Bu durumda repo'daki yardımcı script'i
  çalıştırın: `scripts/generate_mcp_command.py` — script console-script'i tespit ederse onu kullanır, aksi halde
  `python -m octave_mcp.mcp_server` tarzı absolute çalıştırma komutu üretir ve `mcp_command.generated.json`
  dosyasına yazar.

3. Üretilen `mcp_command.generated.json`'ı LM Studio'ya yapıştırın ya da base64 encode edip deeplink ile ekleyin.

Örnek: generator kullanımı

```bash
python3 scripts/generate_mcp_command.py --out mcp_command.generated.json
```

Ve deeplink oluşturmak için:

```bash
python3 - <<'PY'
import base64, json
with open('mcp_command.generated.json','rb') as f:
  encoded = base64.urlsafe_b64encode(f.read()).decode()
print(f"lmstudio://add_mcp?name=octave-mcp-command&config={encoded}")
PY
```

Deeplink (komut-tabanlı config'i encode etmek için örnek):

```bash
python3 - <<'PY'
import base64, json
with open('mcp_command.json','rb') as f:
  encoded = base64.urlsafe_b64encode(f.read()).decode()
print(f"lmstudio://add_mcp?name=octave-mcp-command&config={encoded}")
PY
```

Not: LM Studio, başlattığı komutu kendi process olarak çalıştırır. Bu nedenle `command`'un
LM Studio tarafından erişilebilir ve yürütülebilir olması gerekir. macOS'te GUI uygulamaları
(ör. LM Studio) farklı PATH/permission ortamına sahip olabilir; tam absolute path kullanmak en güvenli yoldur.

## 6) Troubleshooting

- Eğer LM Studio deeplink açılmazsa: LM Studio sürümünüz 0.3.17 veya üstü olduğundan emin olun.
- Eğer MCP ekleniyor fakat çağrı başarısız oluyorsa: OctaveMCP erişim URL'sinin LM Studio ortamından
  erişilebilir olup olmadığını kontrol edin (localhost vs. container vs. WSL vs. port yönlendirmeleri).

---
