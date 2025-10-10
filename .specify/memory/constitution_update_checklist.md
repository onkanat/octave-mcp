
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

#### Güvenlik ve Performans
- [ ] Resource limit, sandbox, rate limit ve otomatik temizlik kuralları şablonlara eklenmeli
- [ ] Vektörizasyon, grafik optimizasyonu ve paket yönetimi örnekleri güncellenmeli

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

Son kontrol: 2025-09-17
- Anayasa sürümü: 1.0.0
- Şablonlar uyumlu: ✅

---

*Bu kontrol listesi, anayasa ilkelerinin tüm proje dokümantasyonunda tutarlı şekilde uygulanmasını sağlar.*