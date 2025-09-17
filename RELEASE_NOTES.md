# Release Notes

## v0.2.0 (2025-09-17)

Öne çıkanlar:

- Publish: HTML çıktısı figür PNG’lerini gömülü olarak içerir; son çalıştırmadaki `fig*.png` dosyaları `runs/<session>/published/images/` altına kopyalanır ve HTML’de `<img>` olarak gösterilir.
- MCP STDIO köprüsü: `octave_run` (opsiyonel `images_b64`, `max_image_bytes`), `octave_publish`, `octave_grabcode`, `admin_cleanup` araçları; LM Studio entegrasyon örneği.
- Cleanup: `admin_cleanup` parametreleri genişletildi (`session_id`, `max_age_hours`, `max_age_days`, `force`); `force` politika ile korunur (`MCP_ALLOW_FORCE_DELETE`).
- Kalıcılık: publish çıktıları `runs/<session>/published/` altında kalıcıdır; figürler `images/` klasöründe.
- Dokümantasyon: README, API ve MCP Tools referansı güncellendi; yeni `ERROR_SCHEMA.md` ile standart hata şeması tanımlandı.
- Orta katman: Rate limit middleware IP tespiti iyileştirildi; `Retry-After` ve `X-RateLimit-*` başlıkları eklendi.

Teknik notlar:

- Vectorization: Python modunda for/while tespiti yapan hafif analizör iskeleti eklendi; entegrasyon bilgi amaçlı.
- Hata bloğu üretimi için `build_error_block` yardımcı fonksiyonu eklendi; HTTP `/run_octave` başarısızlıklarında `error` alanı döner.

Uyumluluk:

- Var olan sözleşmeleri bozmaz; yeni alanlar opsiyonel olarak eklendi.
