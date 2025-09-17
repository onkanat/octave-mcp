# Octave MCP Server

Yerel Octave kurulumunuz üzerinde güvenli komut çalıştıran bir MCP sunucusu.

## Özellikler
- STDIO ve HTTP API ile Octave/Python kodu çalıştırma
- publish/grabcode ile HTML çıktı ve kaynak kod geri alma
- Figür yakalama: Oluşan `fig_*.png` görsellerini kalıcı olarak saklama ve publish HTML’e gömme
- MCP (STDIO) köprüsü: `octave_run`, `octave_publish`, `octave_grabcode`, `admin_cleanup` araçları
- Kaynak limiti, hata raporu, persistent session desteği

## Kurulum
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Octave ile Devreye Alma
Sunucunun Octave ile çalışabilmesi için sisteminizde GNU Octave kurulu olmalıdır. Aşağıdaki komutla yükleyebilirsiniz:

macOS:
```sh
brew install octave
```
Ubuntu/Debian:
```sh
sudo apt-get install octave
```

## Kullanım

- Komut satırından Octave kodu çalıştırmak için:

```sh
python src/cli/cli.py run --code 'disp(1+1);'
```

- HTTP API sunucusunu başlatmak için:

```sh
uvicorn src/api/endpoints:app --reload
```

- CLI ile çalışırken HTTP sunucusunun çalıştığından emin olun ve gerekiyorsa URL'yi belirtin:

```sh
export MCP_SERVER_URL="http://127.0.0.1:8000"
python src/cli/cli.py publish --code "disp(42);" --session_id s1
python src/cli/cli.py grabcode --session_id s1
```

### Publish: HTML’de Figür Gömme

- `publish` çağrısı, `runs/<session_id>/published/` altında `script_publish.html` dosyasını üretir.
- Son çalıştırmadan bulunan `fig*.png` görselleri `runs/<session_id>/published/images/` dizinine kopyalanır ve HTML içine `<img>` olarak eklenir.
- Publish yanıtında `images` alanı göreli yolları içerir (ör. `images/fig_1.png`).

```sh
python src/cli/cli.py publish --code "plot(1:10);" --session_id demo
open runs/demo/published/script_publish.html
```

### Ortam Değişkenleri (.env)

Aşağıdaki ayarları `.env` dosyasına koyabilir veya kabukta export edebilirsiniz:

- `MCP_RATE_LIMIT_MAX`: Bir pencere içinde izin verilen maksimum istek (varsayılan: 100)
- `MCP_RATE_LIMIT_WINDOW`: Pencere süresi saniye cinsinden (varsayılan: 60)
- `MCP_MAX_OUTPUT_CHARS`: `stdout/stderr` için maksimum karakter (varsayılan: 20000)
- `MCP_TIMEOUT_SECONDS`: Alt süreç zaman aşımı (varsayılan: 10)
- `MCP_CPU_LIMIT`: CPU süresi limiti saniye (yoksa 0/None)
- `MCP_MEMORY_MB`: Bellek limiti MB (yoksa 0/None)
- `MCP_RUNS_ROOT`: Kalıcı çıktıların yazılacağı kök dizin (varsayılan: `runs`)
- `MCP_RUNS_RETENTION_DAYS`: Temizlik için gün cinsinden saklama süresi (0: saatlik varsayılanı kullan)
- `MCP_IS_VISION_MODEL`: Vision modu (true/false)
- `MCP_ALLOW_FORCE_DELETE`: Force temizliği (tümünü hedefleme) politikasını açar (true/false)
- `OCTAVE_RUNNER_MODE`: `python` veya `octave`
- `OCTAVE_FIG_WIDTH` / `OCTAVE_FIG_HEIGHT`: Figür boyutları

Örnek `.env`:

```env
MCP_RATE_LIMIT_MAX=100
MCP_RATE_LIMIT_WINDOW=60
MCP_MAX_OUTPUT_CHARS=20000
MCP_TIMEOUT_SECONDS=10
MCP_CPU_LIMIT=0
MCP_MEMORY_MB=0
MCP_RUNS_ROOT=runs
MCP_IS_VISION_MODEL=false
OCTAVE_RUNNER_MODE=python
OCTAVE_FIG_WIDTH=620
OCTAVE_FIG_HEIGHT=480
MCP_RUNS_RETENTION_DAYS=0
MCP_ALLOW_FORCE_DELETE=false
```

### Octave Çalıştırma Modu

- Varsayılan olarak `run_octave` uç noktası test kolaylığı için Python ile çalışır.
- Gerçek Octave çalıştırmak için ortam değişkenini ayarlayın (Octave kurulu olmalı):

```sh
export OCTAVE_RUNNER_MODE=octave
uvicorn src/api/endpoints:app --reload
```

### Görsel Çıktılar ve Boyutlar

- Görsellerin modele gönderilip gönderilmeyeceği `MCP_IS_VISION_MODEL` ile kontrol edilir.
  - Vision değilse: Görseller dosya sistemine kaydedilir, yanıt içinde sadece isimler döner.
  - Vision ise: Görsellerin dosya yolları da yanıt içinde döner.

```sh
# Vision modeli değil (varsayılan):
export MCP_IS_VISION_MODEL=false

# Vision modeli:
export MCP_IS_VISION_MODEL=true
```

- Figür boyutları ayarlanabilir. Varsayılan: 620x480

```sh
export OCTAVE_FIG_WIDTH=620
export OCTAVE_FIG_HEIGHT=480
```

### Cleanup (Temizlik)

- HTTP: `POST /admin/cleanup` gövdesi örnekleri:
  - Sadece rapor: `{ "dry_run": true }`
  - 72 saatten eski: `{ "dry_run": false, "max_age_hours": 72 }`
  - 7 günden eski: `{ "dry_run": false, "max_age_days": 7 }`
  - Belirli oturum: `{ "dry_run": false, "session_id": "demo" }`
  - Force (tümünü hedefler, dikkat): `{ "dry_run": false, "force": true }` (yalnızca `MCP_ALLOW_FORCE_DELETE=true` iken uygulanır)

- MCP aracı `admin_cleanup` da aynı parametreleri destekler:
  - `dry_run` (bool), `force` (bool), `max_age_hours` (int), `max_age_days` (int), `session_id` (str)

Politika uyarısı: `force: true` isteği, ortamda `MCP_ALLOW_FORCE_DELETE=true` değilse engellenir ve anlamlı bir hata yanıtı döner.

Standart hata bloğu şeması için bkz: [ERROR_SCHEMA.md](./ERROR_SCHEMA.md)

## Testler

Projedeki sözleşme ve entegrasyon testleri doğrulanmıştır.

```sh
source .venv/bin/activate
pytest -q
```

Hızlı bir duman testi için:

```sh
pytest -q tests/smoke_test.py
```

Sunucu devredeyken, HTTP API üzerinden Octave kodu gönderebilir, publish/grabcode ile kod ve HTML çıktısı alabilirsiniz.

Daha fazla bilgi için specify.txt ve docs klasörüne bakınız.

### MCP (STDIO) Köprüsü ve LM Studio

Bu repoda MCP stdio köprüsü mevcuttur (`src/mcp_server.py`). Böylece LM Studio gibi MCP istemcileriyle doğrudan entegre olabilirsiniz.

Çalıştırma:

```sh
source .venv/bin/activate
python src/mcp_server.py
```

LM Studio `mcpServers` yapılandırma örneği:

```json
{
  "mcpServers": {
    "octave_execute": {
      "command": "/Users/hakankilicaslan/Prompts/mcp_new/.venv/bin/python",
      "args": [
        "/Users/hakankilicaslan/Prompts/mcp_new/src/mcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PATH": "/opt/homebrew/bin:/usr/local/bin:${PATH}",
        "MCP_RUNS_ROOT": "/Users/hakankilicaslan/Prompts/mcp_new/runs",
        "TMPDIR": "/Users/hakankilicaslan/Prompts/mcp_new/runs",
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

MCP Araçları ve Parametreler:

- `octave_run`:
  - `code` (str), `session_id` (opsiyonel), `images_b64` (bool), `max_image_bytes` (int)
  - `images_b64` true ise, boyut limiti altındaki görseller base64 olarak döner.
- `octave_publish`:
  - `code` (str), `session_id` (opsiyonel)
  - Üretilen HTML figürleri gömülü `<img>` olarak içerir.
- `octave_grabcode`:
  - `session_id` (str)
- `admin_cleanup`:
  - `dry_run` (bool), `force` (bool), `max_age_hours` (int), `max_age_days` (int), `session_id` (str)
  - Force işlemleri policy ile korunur: `MCP_ALLOW_FORCE_DELETE=true` değilse engellenir.

MCP araçları (tools): `octave_run`, `octave_publish`, `octave_grabcode`, `admin_cleanup`.
`OCTAVE_RUNNER_MODE=octave` ile Octave kurulu olduğunda gerçek Octave çalıştırma aktiftir.

Tam araç parametreleri ve dönüş şemaları için ayrıntılı referans: [MCP Tools Reference](./MCP_TOOLS.md)

## Sorun Giderme

- Octave PATH: Octave komutuna erişilemiyorsa, PATH’e Homebrew dizinlerini ekleyin veya tam yolu kullanın.

```sh
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH}"
which octave
```

- İzin hataları (temizlik): `admin_cleanup` force işlemleri politika ile korunur. Force gerekli ise ortamı açın.

```sh
export MCP_ALLOW_FORCE_DELETE=true
```

- Figür görünmüyor: Kod gerçekten bir figür üretiyor mu? Octave modunda çalıştırmayı deneyin ve `runs/<session>/published/images/` altında `fig_*.png` oluştuğunu doğrulayın.

```sh
export OCTAVE_RUNNER_MODE=octave
python src/cli/cli.py publish --code "plot(1:10);" --session_id demo
open runs/demo/published/script_publish.html
```

- Bellek/Zaman aşımı: `MCP_MEMORY_MB`, `MCP_TIMEOUT_SECONDS`, `MCP_MAX_OUTPUT_CHARS` değişkenleriyle sınırları ayarlayın.

## CLI Örnekleri

- Çalıştırma (run):

```sh
python src/cli/cli.py run --code 'disp(1+1);' --session_id s1
```

- Yayınla (publish):

```sh
python src/cli/cli.py publish --code "plot(1:10);" --session_id s1
open runs/s1/published/script_publish.html
```

- Kodu geri al (grabcode):

```sh
python src/cli/cli.py grabcode --session_id s1
```

### MCP Demo Akışı (publish → grabcode → run)

Hızlı bir uçtan uca demo için hazır betiği çalıştırabilirsiniz:

```sh
source .venv/bin/activate
python scripts/mcp_demo_flow.py
```
 
Bu betik örnek kodu publish eder, ardından grabcode ile geri alır ve `octave_run` aracını `images_b64=true` ile çağırıp görsel çıktıları base64 olarak da gösterir.

Alternatif olarak hızlı bir kontrol betiği:

```sh
python scripts/mcp_client_quicktest.py
```

Her iki betik de `src/mcp_server.py`’yi stdio üzerinden başlatıp araçları sırasıyla kullanır.

### admin_cleanup için curl Örnekleri

HTTP API çalışırken aşağıdaki örneklerle temizlik yapabilirsiniz:

Sadece rapor (dry run):

```sh
curl -s -X POST http://127.0.0.1:8000/admin/cleanup \
  -H 'Content-Type: application/json' \
  -d '{"dry_run": true}' | jq
```

72 saatten eski klasörleri sil:

```sh
curl -s -X POST http://127.0.0.1:8000/admin/cleanup \
  -H 'Content-Type: application/json' \
  -d '{"dry_run": false, "max_age_hours": 72}' | jq
```

Belirli oturumu hedefle:

```sh
curl -s -X POST http://127.0.0.1:8000/admin/cleanup \
  -H 'Content-Type: application/json' \
  -d '{"dry_run": false, "session_id": "demo"}' | jq
```

Force (dikkat — tümünü hedefleyebilir):

```sh
export MCP_ALLOW_FORCE_DELETE=true
curl -s -X POST http://127.0.0.1:8000/admin/cleanup \
  -H 'Content-Type: application/json' \
  -d '{"dry_run": false, "force": true}' | jq
```
