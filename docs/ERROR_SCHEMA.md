# Standard Error Block Schema

Bu doküman, HTTP API ve MCP araçlarında dönebilecek standart hata bloğunu tanımlar. Şema; tanı, gözlemlenebilirlik ve kaynak limit ihlallerini açıkça iletmeyi amaçlar.

## Amaç

- Tutarlı hata yapısı: UI/istemciler tek şema ile ayrıştırır.
- Kaynak ihlallerini açıkça belirtir.
- Gerektiğinde kullanıcıya düzeltme ipuçları taşır.

## JSON Şeması (mantıksal)

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

Notlar:

- `id`: Korelasyon için tekil kimlik (uuid4 önerilir).
- `type`: İstemcide kullanıcı mesajları için uygun eşleştirme sağlar.
- `hint`: Kullanıcı aksiyonlarını hızlandıracak kısa öneri.
- `resource_violation`: Yalnızca limit ihlali varsa doldurulur.

## Kullanım İlkeleri

- Her hata yanıtında en azından `id`, `type`, `message`, `timestamp` alanları olmalı.
- Sınır ihlallerinde `resource_violation` zorunludur.
- Truncation yapıldıysa `stdout_truncated`/`stderr_truncated` true olmalı.

## Entegrasyon

- HTTP: 4xx/5xx gövdeleri bu bloğu taşımalı.
- MCP: toolError veya toolResult içi `error` alanında bu blok döndürülebilir.

## Gelecek Çalışmalar

- Ayrıntılı tipler (e.g., file_system_error) ve `code` alanı.
- Lokalizasyon için `localized_message` alanları.
