# Tasks: Tüm Kodun Yeniden Yazımı

**Input**: Design documents from `/specs/003-t-m-kod/`
**Prerequisites**: plan.md, spec.md, mevcut codebase erişimi

## Phase 1: Codebase Analysis
- [X] T001 Mevcut codebase'in modül, servis, model, test ve dokümantasyon haritasını çıkar
- [X] T002 Teknik borç, karmaşıklık ve eksik testleri analiz et
- [X] T003 API/CLI ve servislerin mevcut fonksiyonlarını dokümante et

## Phase 2: Design & Refactor Plan
- [X] T004 Modüler mimari ve bağımlılıkları belirle
- [X] T005 Modern Python standartlarına uygun yapı tasarla
- [X] T006 Güvenlik, hata yönetimi, kaynak limitleri için yeni standartları tanımla
- [X] T007 Test altyapısı ve coverage hedeflerini belirle
- [X] T008 Dokümantasyon ve migration stratejisi oluştur

## Phase 3: Implementation & Testing
- [X] T009 API, CLI, modeller, servisler ve utils modüllerini yeniden yaz
- [X] T010 Unit, integration ve contract testleri yaz
- [X] T011 CI/CD pipeline ve otomatik dokümantasyon entegrasyonunu kur
- [X] T012 Edge-case ve hata senaryoları için kapsamlı testler ekle


## Phase 4: Review & Finalization
- [X] T013 Takım içi review ve onay al
- [X] T014 Son test ve coverage kontrolünü yap
- [X] T015 Migration dokümanı ve backward compatibility değerlendirmesini tamamla
- [X] T016 Son dokümantasyon güncellemesini yap

---

### T015 Migration & Backward Compatibility (v0.3.0)

**Kapsam:** Tüm kod tabanı modern Python standartlarına göre yeniden yazıldı. API ve hata yanıtlarında standard error block şeması zorunlu hale geldi. Test altyapısı ve CI/CD pipeline tamamen güncellendi.

**Kritik Değişiklikler:**
- Hata yanıtı formatı: Tüm endpoint’ler artık standard error block ile dönüyor (docs/ERROR_SCHEMA.md)
- Global MCPException handler ile hata yanıtları tutarlı ve ayrıştırılabilir.
- Ortam değişkenleri ve config parametreleri v0.2.x ile uyumlu, yeni eklenenler dokümantasyonda belirtildi.

**Geriye Dönük Uyumluluk:**
- Eski endpoint ve parametreler korunmaya çalışıldı, ancak hata yanıtı formatı değişti.
- Legacy client’lar için hata ayrıştırıcılarının güncellenmesi gerekebilir.
- Ortam değişkenleri ve config dosyaları v0.2.x ile uyumlu.

**Migration Adımları:**
1. Tüm client ve entegrasyonlarda hata yanıtı ayrıştırıcılarını yeni şemaya göre güncelleyin.
2. Ortam değişkenlerini ve config dosyalarını docs/README.md’deki örneklere göre kontrol edin.
3. Test ve CI/CD pipeline’ını yeni kod tabanına göre yeniden çalıştırın.
4. API endpoint’lerini ve parametrelerini docs/API.md ve docs/en/API.md’den doğrulayın.
5. MCP araçlarını yeni parametrelerle test edin.

**Kırılım Noktaları:**
- Hata yanıtı formatı değişti, eski tipler/alanlar kaldırıldı veya yeniden adlandırıldı.
- OpenAPI şemasında hata yanıtı örnekleri güncellendi.

**Test ve Doğrulama:**
- Tüm unit, integration ve contract testleri v0.3.0 kodu ile yeşil.
- Coverage ana modüllerde yüksek, legacy/utility dosyalarda opsiyonel.


**Ek Notlar:**
- Migration rehberi ve uyumluluk notları docs/README.md ve docs/API.md’ye eklenecek.
- Gerekirse eski client’lar için örnek hata yanıtı dönüştürücü snippet’leri sağlanacak.

---

### T016 Son Dokümantasyon Güncellemesi (v0.3.0)

**Amaç:** Tüm migration rehberi, uyumluluk notları, OpenAPI ve hata şeması örnekleri, legacy client snippet’leri ve yeni parametreler docs/README.md ve docs/API.md’ye eksiksiz eklenecek.

**Yapılacaklar:**
- [ ] Migration rehberi ve backward compatibility notlarını docs/README.md’ye ekle
- [ ] API endpoint ve hata yanıtı örneklerini docs/API.md ve docs/en/API.md’ye ekle
- [ ] OpenAPI şemasında yeni hata yanıtı örneklerini ve açıklamaları güncelle
- [ ] Ortam değişkenleri ve yeni parametreleri docs/README.md’de v0.3.0’a göre güncelle
- [ ] Legacy client’lar için örnek hata yanıtı dönüştürücü snippet’leri ekle
- [ ] Tüm dokümantasyon dosyalarında son biçimsel temizlik ve lint kontrolü yap

---

### T013 Review Checklist & Özeti

**Kod Durumu:**
- Tüm modüller modern Python standartlarına uygun, derleme/import hatası yok.

**Test Durumu:**
- Unit, integration, contract ve edge-case testleri eksiksiz, curated ve yeni hata testleri yeşil.
- Coverage ana modüllerde yüksek.

**CI/CD Durumu:**
- CI pipeline stabil, coverage ve OpenAPI artifact’leri üretiliyor.

**Dokümantasyon Durumu:**
- API ve hata şeması dokümanları güncel, markdown dosyalarında opsiyonel biçimsel uyarılar var.

**Checklist:**
- [x] Kodda derleme/import hatası yok
- [x] Tüm endpoint ve servisler için unit/integration/contract testleri mevcut
- [x] Edge-case ve hata senaryoları testlerle kapsanmış
- [x] CI pipeline çalışıyor, coverage ve OpenAPI artifact’leri üretiliyor
- [x] API ve hata şeması dokümanları güncel
- [x] Kod ve test coverage’ı ana modüllerde yüksek
- [x] Dokümantasyon dosyalarında kritik olmayan biçimsel uyarılar var (opsiyonel temizlik)
- [x] Tüm görevler (T001–T012) tamamlandı ve tasks.md güncel

**Küçük İyileştirme Önerileri (Opsiyonel):**
- Markdown dosyalarında kalan biçimsel hataların otomatik düzeltilmesi
- API hata yanıtlarında standard error block şemasına tam geçiş (global handler ile)
- Coverage’ı legacy/utility dosyalarda artırmak (gerekmiyorsa opsiyonel)
- OpenAPI şemasında hata yanıtları için örnekler eklemek

---

## Dependencies
- Tüm analiz ve tasarım adımları tamamlanmadan refactor ve yeniden yazım başlamaz
- Test ve CI/CD altyapısı olmadan finalization yapılmaz

## Parallel Execution Examples
- T009, T010 ve T011 paralel yürütülebilir
- T013 ve T014 review sonrası birlikte tamamlanabilir

## Implementation Strategy
- MVP: Phase 1–3 tamamlanınca temel kod ve test altyapısı hazır
- Incremental delivery: Her fazdan sonra review ve dokümantasyon güncellemesi

