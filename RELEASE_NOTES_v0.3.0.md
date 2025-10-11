# Release Notes - v0.3.0 (2025-10-11)

Öne çıkanlar:

- Tüm kod tabanı modern Python standartlarına göre yeniden yazıldı.
- Global MCPException handler: HTTP hata yanıtları standard error block (docs/ERROR_SCHEMA.md).
- Testler: Unit, integration, contract ve edge-case kapsamı artırıldı; coverage yüksek.
- Dokümantasyon: Migration rehberi ve API hata örnekleri eklendi (docs/README.md, docs/API.md).
- CI/CD: Curated test set + coverage raporu + OpenAPI artifact üretimi stabilize edildi.

Uyumluluk ve Migration:

- Hata yanıtı formatı değişti: Client’lar error block şemasına göre güncellenmeli.
- Endpoint parametreleri büyük oranda geriye dönük uyumlu; yeni alanlar opsiyonel.
- Ortam değişkenleri v0.2.x ile uyumlu; yeni parametreler docs’ta belirtilmiştir.

Notlar:

- MCP STDIO araçları: `octave_run`, `octave_publish`, `octave_grabcode`, `admin_cleanup`.
- Kaynak limit ihlalleri ve timeout durumları error block içinde açıkça işaretlenir.
