
# Changelog

## v0.3.1 (2025-10-11)

Öne çıkanlar:

- Universal LM Studio config ve import patch ile tüm çalışma modlarında sorunsuz başlatma.
- Tüm dokümantasyonlarda (TR/EN) config örnekleri ve migration rehberi güncellendi.
- MCP server artık modül veya script olarak çalıştırıldığında otomatik import path çözümü yapıyor.
- API, MCP tools ve hata şeması dokümanları senkronize edildi.

---

## v0.3.0 (2025-10-11)

Öne çıkanlar:

- Tüm kod tabanı modern Python standartlarına göre yeniden yazıldı.
- Global MCPException handler ile tüm HTTP hataları standard error block (docs/ERROR_SCHEMA.md) formatında.
- Unit, integration, contract ve edge-case testleri güncellendi; coverage yüksek.
- Dokümantasyon: Migration rehberi ve API hata örnekleri eklendi (docs/README.md, docs/API.md).
- CI/CD: Curated test set, coverage raporu ve OpenAPI artifact üretimi stabilize edildi.

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

## v0.2.3 (2025-10-11)

- Paket içindeki top-level modülün kesin olarak dahil edilmesi için yapılandırma düzeltildi ve sürüm 0.2.3 yapıldı.

## v0.2.4 (2025-10-11)

- Düzeltme: console script entry point `octave-mcp` artık doğru modul yolunu kullanır
  (önceden `src.mcp_server:main` idi); paket kurulduktan sonra script artık
  ModuleNotFoundError vermez.

## v0.2.5 (2025-10-11)

- Düzeltme: console script artık CLI modülünü (`cli.cli:main`) kullanır. Bu
  sayede `octave-mcp` yüklendikten sonra komut satırı arayüzü doğrudan çalışır.

## v0.1.0 (ilk sürüm)

- Proje iskeleti, model, servis, test ve API/CLI uç noktaları oluşturuldu.
