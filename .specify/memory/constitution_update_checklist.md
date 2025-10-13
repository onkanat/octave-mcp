
# Constitution Update Checklist (Octave MCP)

Anayasa (`/memory/constitution.md`) güncellendiğinde, tüm bağlı dokümanların ve şablonların tutarlılığı sağlanmalıdır.

## Güncellenecek Şablonlar

### Herhangi bir madde eklenirse/değişirse:
- [ ] `/templates/plan-template.md` – Anayasa kontrol bölümü güncellenmeli
- [ ] `/templates/spec-template.md` – Gereksinim/kapsam değiştiyse güncellenmeli
- [ ] `/templates/tasks-template.md` – Yeni görev türleri gerekiyorsa güncellenmeli
- [ ] `/.claude/commands/plan.md` – Planlama süreci değiştiyse güncellenmeli
- [ ] `/.claude/commands/tasks.md` – Görev üretimi etkileniyorsa güncellenmeli
- [ ] `/CLAUDE.md` – Çalışma zamanı geliştirme rehberi güncellenmeli

### Maddeye özel güncellemeler:

#### I. Modülerlik ve Bağımsızlık
- [ ] Şablonlarda modül/araç ayrımı vurgulanmalı
- [ ] Ortak yardımcılar ve kod tekrarları için örnekler eklenmeli

#### II. CLI ve API Arayüzü
- [ ] CLI ve HTTP API örnekleri güncellenmeli
- [ ] Giriş/çıkış protokolü (stdin/stdout, JSON, hata yönetimi) şablonlara eklenmeli

#### III. Test-First (TDD)
- [ ] Test sırası ve zorunluluğu tüm şablonlarda vurgulanmalı
- [ ] smoke_test.py ve entegrasyon testleri örneklenmeli

#### IV. Entegrasyon ve Uçtan Uca Test
- [ ] Entegrasyon testi tetikleyicileri listelenmeli
- [ ] Test tipleri ve öncelikleri güncellenmeli

#### V. Gözlemlenebilirlik, Sürümleme, Sadelik
- [ ] Loglama ve hata izleme gereksinimleri şablonlara eklenmeli
- [ ] Sürüm formatı ve değişiklik özeti zorunluluğu belirtilmeli
- [ ] YAGNI ve sadelik ilkeleri örneklenmeli
- [ ] Structured logging örnekleri güncellenmiş mi?
- [ ] Semantic versioning kuralları tüm dokümanlarda tutarlı mı?

#### VI. MCP Protocol Integration (v1.1.0'da eklendi)

- [ ] FastMCP ile tool tanımlama örnekleri şablonlara eklenmeli
- [ ] MCP tool naming convention (snake_case) vurgulanmalı
- [ ] LM Studio universal config örnekleri güncellenmiş mi?
- [ ] Her MCP tool için contract test gereksinimleri belirtilmeli
- [ ] MCP transport modes (STDIO, SSE) dokümante edilmeli
- [ ] Tool parameter types ve descriptions standartları eklenmeli

#### VII. Standardized Error Handling (v1.1.0'da eklendi)

- [ ] ERROR_SCHEMA.md referansları tüm şablonlara eklenmeli
- [ ] Error block format örnekleri güncellenmiş mi?
- [ ] Resource violation tracking örnekleri eklenmiş mi?
- [ ] HTTP 4xx/5xx ve MCP tool error handling tutarlı mı?
- [ ] Error type enum değerleri dokümante edilmiş mi?
- [ ] MCPException kullanımı örneklenmiş mi?

#### VIII. Bilingual Documentation (v1.1.0'da eklendi)

- [ ] Tüm yeni özellik dokümantasyonu TR/EN olarak planlanmış mı?
- [ ] API dokümantasyonu her iki dilde senkronize mi?
- [ ] Migration guide'lar çift dilde hazırlanmış mı?
- [ ] GitHub Pages yapılandırması güncel mi?
- [ ] Dokümantasyon şablonları bilingual requirement içeriyor mu?
- [ ] Çapraz referanslar her iki dilde çalışıyor mu?

#### IX. Import Path Resolution (v1.1.0'da eklendi)

- [ ] Module ve script execution mode örnekleri eklenmiş mi?
- [ ] pyproject.toml entry points dokümante edilmiş mi?
- [ ] LM Studio compatibility notları güncel mi?
- [ ] Import path resolution stratejisi açıklanmış mı?
- [ ] Development ve production execution mode'ları belgelenmiş mi?
- [ ] sys.path manipulation'dan kaçınma örnekleri verilmiş mi?

#### Güvenlik ve Performans

- [ ] Resource limit, sandbox, rate limit ve otomatik temizlik kuralları şablonlara eklenmeli
- [ ] Vektörizasyon, grafik optimizasyonu ve paket yönetimi örnekleri güncellenmeli
- [ ] Resource violation error reporting örnekleri eklenmiş mi?
- [ ] MCP_* environment variables dokümante edilmiş mi?

## Doğrulama Adımları

1. **Anayasa değişikliği öncesi:**
   - [ ] Tüm şablonlar yeni gereksinimleri referans alıyor mu?
   - [ ] Örnekler yeni kurallara uygun mu?
   - [ ] Dokümanlar arasında çelişki yok mu?

2. **Şablonlar güncellendikten sonra:**
   - [ ] Örnek bir uygulama planı ile test et
   - [ ] Tüm anayasa gereksinimleri karşılanıyor mu?
   - [ ] Şablonlar bağımsız okunabilir mi (anayasa olmadan)?

3. **Sürüm takibi:**
   - [ ] Anayasa sürüm numarası güncellendi mi?
   - [ ] Şablon dipnotlarında sürüm belirtildi mi?
   - [ ] Anayasa değişiklik geçmişine eklendi mi?

## Sık Atlananlar

- Komut dokümantasyonu (`/commands/*.md`)
- Şablonlardaki kontrol listeleri
- Örnek kod/komutlar
- Alan/ortam varyasyonları (web, CLI, API)
- Dokümanlar arası çapraz referanslar

## Şablon Senkronizasyon Durumu

Son kontrol: 2025-10-13

- Anayasa sürümü: 1.1.0
- Şablonlar uyumlu: ⚠️ VI-IX ilkeleri için güncelleme gerekli

### Değişiklik Geçmişi

#### v1.1.0 (2025-10-13)

- ✅ Yeni ilkeler VI-IX eklendi
- ✅ Checklist güncellemesi tamamlandı
- ⚠️ Template örnekleri güncellenmeli
- ⚠️ MCP tool validation checklist oluşturulmalı

#### v1.0.1 (2025-10-11)

- ✅ İlk anayasa placeholder'lar dolduruldu
- ✅ Şablonlar temel ilkelerle uyumlu

---

*Bu kontrol listesi, anayasa ilkelerinin tüm proje dokümantasyonunda tutarlı şekilde uygulanmasını sağlar.*
