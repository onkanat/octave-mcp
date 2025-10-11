# OctaveMCP API v0.2.5

[Türkçe](./README.md) · [English](./en/API.md)

FastAPI tabanlı HTTP REST API endpoint'leri.

## Base URL

```text
http://localhost:8000
```

## Endpoints

### POST /run

Octave kodu çalıştırır ve sonuçları döndürür.

**Request Body:**

```json
{
  "code": "disp('Hello World');",
  "session_id": "optional_session",
  "timeout": 30,
  "cpu_time_limit": 10,
  "memory_limit_mb": 512
}
```

**Response:**

```json
{
  "success": true,
  "stdout": "Hello World\n",
  "stderr": "",
  "exit_code": 0,
  "runtime_seconds": 0.123,
  "images": []
}
```

### POST /publish

Koddan HTML çıktı ve figürler üretir.

**Request Body:**

```json
{
  "code": "x=1:10; y=x.^2; plot(x,y); title('Demo');",
  "session_id": "demo_session",
  "show_code": true,
  "include_images": true
}
```

**Response:**

```json
{
  "success": true,
  "html_b64": "base64_encoded_html",
  "html_truncated": false,
  "html_original_size": 1234,
  "publish_dir": "/path/to/runs/demo_session/run_123/published",
  "html_name": "script_publish.html",
  "images": ["images/figure_01.png"],
  "warnings": []
}
```

### POST /grabcode

Publish edilmiş HTML'den kaynak kodu çıkarır.

**Request Body:**

```json
{
  "session_id": "demo_session",
  "html_relpath": "run_123/published/script_publish.html"
}
```

**Response:**

```json
{
  "success": true,
  "code_b64": "base64_encoded_source",
  "line_count": 15,
  "warnings": []
}
```

### POST /cleanup

Eski session'ları ve run klasörlerini temizler.

**Request Body:**

```json
{
  "dry_run": true,
  "max_age_hours": 48,
  "session_id": "specific_session"
}
```

**Response:**

```json
{
  "success": true,
  "deleted_runs": 5,
  "deleted_sessions": 2,
  "dry_run": true,
  "errors": []
}
```

## Rate Limiting

- Default: 100 requests / 60 seconds
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Environment: `MCP_RATE_LIMIT_MAX`, `MCP_RATE_LIMIT_WINDOW`


## v0.3.0 Migration Notları & Hata Yanıtı Örnekleri

### Yeni Hata Yanıtı Formatı

Tüm endpoint’ler artık aşağıdaki gibi standard error block ile dönüyor:

```json
{
  "success": false,
  "error": {
    "id": "uuid",
    "type": "timeout|resource_violation|validation_error|service_error|execution_error|not_found_error|resource_error|security_error",
    "message": "Error description",
    "hint": "Suggested fix",
    "timestamp": "2025-10-10T12:00:00Z",
    "details": {
      "exit_code": 1,
      "stdout": "",
      "stderr": "Error details",
      "timeout_seconds": 10,
      "resource_type": "memory",
      "resource_id": "session_123"
    },
    "resource_violation": {
      "limit_type": "memory",
      "limit_value": 512,
      "observed_value": 1024
    }
  }
}
```

Detaylı şema için: [ERROR_SCHEMA.md](./ERROR_SCHEMA.md)

### Legacy Client Dönüştürücü Snippet

Eski client’lar için örnek hata yanıtı dönüştürücü:

```python
def convert_error_block(error):
    # v0.2.x formatından v0.3.0 standard error block'a dönüştürme
    return {
        "id": error.get("id"),
        "type": error.get("type"),
        "message": error.get("message"),
        "hint": error.get("hint"),
        "timestamp": error.get("timestamp"),
        "details": error.get("details", {}),
        "resource_violation": error.get("resource_violation", {})
    }
```

### Migration Notları

v0.3.0 ile gelen tüm endpoint ve parametre değişiklikleri docs/README.md ve bu dosyada güncellenmiştir.

