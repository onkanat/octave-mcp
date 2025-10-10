# Data Model: Octave MCP Server

**Kaynak:** specify.txt, plan.md, spec.md
**Tarih:** 2025-09-17

---

## 1. Varlıklar (Entities)

### Session
- session_id: str
- persistent: bool
- start_time: datetime
- last_active: datetime
- work_dir: str

### Run
- code: str (veya code_b64: str)
- stdout: str
- stderr: str
- exit_code: int
- runtime_seconds: float
- images: List[ImageResult]
- resource_limits: ResourceLimits

### Publish
- html_b64: str
- html_truncated: bool
- html_original_size: int
- publish_dir: str
- html_name: str
- images: List[str] (publish edilen HTML için göreli yollar; ör. `images/fig_1.png`)
- warnings: List[str]

### Grabcode
- code_b64: str
- line_count: int
- warnings: List[str]

### ImageResult
- name: str
- mime: str (opsiyonel)
- b64: str (opsiyonel)
- size: int (opsiyonel)
- path: str (opsiyonel)

### ResourceLimits

- cpu_time_limit: int
- memory_limit_mb: int
- max_output_chars: int
- max_image_size_bytes: int
- timeout: int

---

## 2. İlişkiler (Relations)

- Session 1:N Run
- Session 1:N Publish
- Session 1:N Grabcode
- Run 1:N ImageResult
- Publish 1:N ImageResult (HTTP publish yanıtında görüntüler göreli yol listesi olarak basitleştirilmiştir)

---

## 3. Notlar

- Tüm alanlar specify.txt ve spec.md ile uyumlu tutuldu.
- Kod ve çıktı alanları base64 destekli.
- Persistent modda session_id zorunlu.
- Resource limitler hem global hem istek bazında ayarlanabilir.
- Hata ve uyarı alanları standart blok formatında.
