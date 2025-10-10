
# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)


## Summary
Octave MCP Server, Octave kodunu yerel olarak çalıştırmak için hem STDIO hem HTTP API sunan, publish ve grabcode özellikli, kaynak sınırları ve detaylı hata raporlaması sağlayan bir sunucudur. Persistent mod ile oturumlar korunabilir, vektörizasyon zorunluluğu ve kod üretim kuralları enforce edilir. Kullanıcı, kodunu çalıştırır, çıktısını alır, HTML olarak yayınlar ve yayınlanan HTML'den kaynak kodunu geri alabilir. Sistem, güvenlik ve tutarlılığı önceliklendirir, test ve otomatik doğrulama içerir. Teknik yaklaşımda Python 3.11+, FastAPI ve GNU Octave kullanılır; kaynak limiti, hata blokları ve otomatik temizlik gibi optimizasyonlar uygulanır.


## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, GNU Octave (>=7.x), requests, base64, pytest
**Storage**: Dosya sistemi (geçici çalışma dizinleri, session klasörleri)
**Testing**: pytest, smoke_test.py, otomatik entegrasyon testleri
**Target Platform**: macOS (ilk hedef), Linux (sandbox opsiyonel), CLI ve HTTP API istemcileri
**Project Type**: single (backend CLI+API)
**Performance Goals**: <1s ortalama yanıt süresi (küçük kodlar), 100k+ veri noktasında downsampling uyarısı, kaynak limiti ihlallerinde hızlı hata
**Constraints**: CPU süresi, bellek, çıktı boyutu, dosya boyutu, timeout, persistent modda sandbox zorunluluğu yoksa devre dışı
**Scale/Scope**: Tek kullanıcı (çoklu session), paralel publish/grabcode desteği, 1-10 eşzamanlı işlem önerisi


## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Modülerlik: Tüm ana işlevler (run, publish, grabcode, temizlik) ayrı modüller ve yardımcılar ile ayrılmıştır.
- CLI ve API: Hem CLI (STDIO) hem HTTP API ile erişim, tüm giriş/çıkışlar metin tabanlı ve JSON destekli.
- Test-First: smoke_test.py ve otomatik testler zorunlu, TDD döngüsü uygulanacak.
- Entegrasyon Testi: publish/grabcode zinciri ve hata raporu için entegrasyon testleri zorunlu.
- Gözlemlenebilirlik: Tüm hata ve çıktılar loglanabilir, referans ID ile izlenebilir.
- Sürümleme: MAJOR.MINOR.BUILD, her değişiklikte dokümantasyon ve sürüm güncellemesi.
- Güvenlik: Kaynak limiti, persistent modda sandbox yoksa devre dışı, input fonksiyonu yasak.
- Vektörizasyon: Kod üretiminde vektörizasyon zorunlu, gereksiz döngü uyarısı.
- Rate limit ve otomatik temizlik: API ve çalışma dizinleri için uygulanacak.

Tüm anayasa gereksinimleri karşılanıyor, karmaşıklık gerekçesi gerekmiyor.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project, backend CLI+API)


## Phase 0: Outline & Research

### Araştırılacak Unknowns ve Sorular

- Hata raporlama formatı: Standart blokta hangi alanlar zorunlu? (identifier, message, stack trace, ipucu dışında ek gereksinim var mı?)
- API rate limit ve veri saklama politikası: Maksimum istek sayısı, rate limit algoritması, session ve çalışma dizini saklama süresi ne olmalı?
- Persistent modda güvenlik: Sandbox zorunluluğu olmayan persistent modda ek güvenlik önlemleri gerekir mi?
- Vektörizasyon enforcement: Otomatik döngü tespiti ve uyarı mekanizması için en iyi yöntem nedir?
- Büyük veri/figür optimizasyonu: Downsampling ve DPI ayarları için sınır değerler ve kullanıcıya uyarı mekanizması nasıl olmalı?
- Çoklu publish/grabcode işlemlerinde eşzamanlılık: Paralel işlemlerde veri bütünlüğü ve çakışma riskleri nasıl yönetilmeli?
- Test otomasyonu: smoke_test.py dışında hangi testler zorunlu olmalı, coverage hedefi nedir?
- Platform desteği: Linux sandbox opsiyonları ve macOS ile uyumlulukta ek gereksinim var mı?

### Research.md için Görevler

- Her unknown için: "Research {unknown} for Octave MCP Server"
- Her teknoloji için: "Find best practices for {tech} in CLI+API backend context"

**Output**: research.md ile tüm belirsizlikler ve teknik kararlar netleşmiş olacak


## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. Feature spec'ten ana varlıkları ve ilişkileri çıkar: Session, Run, Publish, Grabcode. Her biri için alanlar, ilişkiler ve validasyon kuralları data-model.md'ye yazılır.
2. Fonksiyonel gereksinimlerden kullanıcı aksiyonlarını belirle: run_octave, publish_octave, grabcode_octave, clean_octave. Her aksiyon için REST endpoint ve OpenAPI şeması /contracts/ klasörüne üretilir.
3. Her endpoint için birer contract test dosyası oluştur: request/response şemaları, hata durumları, kaynak limiti ihlali, publish/grabcode edge-case'leri. Tüm testler başta başarısız olmalı (TDD).
4. Kullanıcı hikayelerinden entegrasyon test senaryoları çıkar: Her ana akış için bir quickstart testi, edge-case'ler için ek entegrasyon testleri.
5. Agent dosyasını (copilot-instructions) güncelle: Yeni teknoloji ve kurallar eklenir, son 3 değişiklik tutulur, toplam uzunluk 150 satırı geçmez.

**Output**: data-model.md, /contracts/*, başarısız testler, quickstart.md, copilot-instructions.md


## Phase 2: Task Planning Approach
*Bu bölümde /tasks komutu ile üretilecek görevlerin yaklaşımı açıklanır; tasks.md bu aşamada oluşturulmaz.*

**Task Generation Strategy:**
- Phase 1'de üretilen contracts, data-model ve quickstart.md temel alınır.
- Her contract için: contract test taskı [P]
- Her entity için: model oluşturma taskı [P]
- Her user story için: entegrasyon test taskı
- Tüm testleri geçirecek şekilde uygulama taskları

**Ordering Strategy:**
- Önce TDD: Testler → implementasyon
- Bağımlılık sırası: Modeller → servisler → CLI/API
- [P] ile bağımsız dosyalar paralel işaretlenir

**Beklenen Çıktı:** tasks.md'de 25-30 numaralı, sıralı görev

**ÖNEMLİ:** Bu faz yalnızca /tasks komutu ile yürütülür, /plan aşamasında dosya oluşturulmaz.

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)


## Complexity Tracking
Bu plan anayasa ile tam uyumlu; ek karmaşıklık gerekçesi gerekmiyor.



## Progress Tracking
*This checklist güncellenmiştir.*

**Phase Status:**
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status:**
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved (research.md ile tamamlanacak)
- [x] Complexity deviations documented (yok)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
