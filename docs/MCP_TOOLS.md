# OctaveMCP Tools Reference

Bu belge MCP stdio köprüsündeki araçların (tools) parametrelerini, dönüşlerini ve kısa örnekleri içerir.

## Genel

- Sunucu: `src/mcp_server.py`
- Çalıştırma:

  ```sh
  source .venv/bin/activate
  python src/mcp_server.py
  ```

## Tool: `octave_run`

- Açıklama: Octave veya Python ile kod çalıştırır; stdout/stderr ve görselleri döndürür.
- Parametreler:
  - `code` (str, zorunlu): Çalıştırılacak Python/Octave kodu
  - `session_id` (str, opsiyonel): Oturum kimliği
  - `images_b64` (bool, opsiyonel, vars: false): Görselleri base64 olarak döndür
  - `max_image_bytes` (int, opsiyonel, vars: 200000): Görsel başına maksimum boyut
- Dönüş:
  - `success` (bool), `stdout` (str), `stderr` (str), `exit_code` (int), `runtime_seconds` (float)
  - `images`: Liste. Her biri: `{ name, path?, b64?, size? }`
- Örnek (pseudocode):

  ```json
  {
    "code": "plot(1:10); disp('ok');",
    "images_b64": true,
    "max_image_bytes": 200000
  }
  ```

## Tool: `octave_publish`

- Açıklama: Kodu HTML'e dönüştürüp `runs/<session_id>/published/` altına kaydeder.
- Parametreler:
  - `code` (str, zorunlu)
  - `session_id` (str, opsiyonel)
- Dönüş:
  - `html_b64`, `html_truncated`, `html_original_size`, `publish_dir`, `html_name`, `images`, `warnings`
- Notlar:
  - Son çalıştırmadan bulunan `fig*.png` görselleri `images/` klasörüne kopyalanır ve HTML'e `<img>` olarak gömülür.

## Tool: `octave_grabcode`

- Açıklama: Verilen oturum için son yayınlanan kodu getirir.
- Parametreler:
  - `session_id` (str, zorunlu)
- Dönüş:
  - `code`, `b64`, `lines`

## Tool: `admin_cleanup`

- Açıklama: Saklama ayarına göre eski runs klasörlerini temizler.
- Parametreler:
  - `dry_run` (bool, vars: true): Sadece raporla, silme
  - `force` (bool, vars: false): Yaş kontrolünü atla, hepsini hedefle (policy ile korunur)
  - `max_age_hours` (int, opsiyonel): Maksimum yaş (saat)
  - `max_age_days` (int, opsiyonel): Maksimum yaş (gün)
  - `session_id` (str, opsiyonel): Sadece bu oturumu hedefle
- Dönüş:
  - `deleted_runs`, `deleted_sessions`, `dry_run`, `errors`
- Politika:
  - `force: true` sadece `MCP_ALLOW_FORCE_DELETE=true` iken yürürlüğe girer, aksi halde işlem engellenir ve hata döner.

## İpuçları

- Görsellerin yakalanması için Octave modunu deneyin:

```sh
  export OCTAVE_RUNNER_MODE=octave
```

- Büyük görselleri base64 döndürmek istemiyorsanız `images_b64=false` kullanın veya `max_image_bytes` değerini küçültün.
