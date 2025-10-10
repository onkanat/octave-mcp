
# Changelog

## v0.2.0 (2025-09-17)

- Publish: Üretilen HTML artık figür PNG’lerini gömülü olarak gösterir;
  son çalıştırmadan bulunan `fig*.png` dosyaları
  `runs/<session>/published/images/` altına kopyalanır ve sayfaya `<img>`
  olarak eklenir. Yanıtta `images` alanı göreli yollarla döner.
- MCP köprüsü: `octave_run` (opsiyonel `images_b64`, `max_image_bytes`),
  `octave_publish`, `octave_grabcode`, `admin_cleanup` araçları eklendi;
  LM Studio ile entegrasyon örneği dokümana eklendi.
- Cleanup: HTTP ve MCP üzerinden `admin_cleanup` parametreleri genişletildi
  (`session_id`, `max_age_hours`, `max_age_days`, `force`). `force` işlemleri
  politika ile korunur; yalnız `MCP_ALLOW_FORCE_DELETE=true` iken etkinleşir.
  Hata raporlaması için `errors` alanı eklendi.
- Kalıcılık: publish çıktıları kalıcı olarak `runs/<session>/published/`
  altına yazılır; figürler `images/` klasöründe tutulur.
- Dokümantasyon: README ve API dokümanları yeni bayraklar, ortam değişkenleri
  ve kullanım örnekleriyle güncellendi.

## v0.2.1 (2025-10-11)

- Küçük hata düzeltmeleri, formatlama ve CI yapılandırma iyileştirmeleri.

## v0.2.2 (2025-10-11)

- Küçük düzeltme: top-level import uyumluluğu için `octave_mcp` shim eklendi.

## v0.1.0 (ilk sürüm)

- Proje iskeleti, model, servis, test ve API/CLI uç noktaları oluşturuldu.
