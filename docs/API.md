# Octave MCP Server API

## /run_octave (POST)

- Octave kodu çalıştırır

## /publish (POST)

- Koddan HTML ve figür üretir
- Çıktı: `runs/<session_id>/published/script_publish.html` ve `images/` altında figür PNG’leri; HTML içinde `<img>` olarak gömülüdür
- Yanıt alanları: `html_b64`, `html_truncated`, `html_original_size`, `publish_dir`, `html_name`, `images` (göreli yollar), `warnings`

## /grabcode (POST)

- HTML'den kaynak kodu çıkarır

## /admin/cleanup (POST)

- Eski veya hedefli `runs/` oturumlarını temizler
- Body alanları:
  - `dry_run` (bool, vars: true)
  - `force` (bool, vars: false) — Politikaya tabidir; yalnız `MCP_ALLOW_FORCE_DELETE=true` iken etkin
  - `max_age_hours` (int, opsiyonel)
  - `max_age_days` (int, opsiyonel)
  - `session_id` (str, opsiyonel) — Tek bir oturumu hedeflemek için
- Yanıt alanları: `deleted_runs`, `deleted_sessions`, `dry_run`, `errors` (silinemeyen yollar ve mesajları)

Tüm endpointler için detaylı sözleşmeler ve örnekler için contracts.md dosyasına bakınız.

Standart hata bloğu şeması için bkz: [ERROR_SCHEMA.md](./ERROR_SCHEMA.md)
