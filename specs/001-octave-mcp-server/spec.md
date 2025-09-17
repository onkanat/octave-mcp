# Feature Specification: Octave MCP Server (FastAPI + STDIO MCP)

**Feature Branch**: `001-octave-mcp-server`  
**Created**: 2025-09-17  
**Status**: Implemented (v0.2.0)  
**Input**: User description: "Octave MCP Server (FastAPI + STDIO MCP): Octave'i yerel olarak çalıştıran, hem STDIO hem HTTP API ile çalışan, publish ve grabcode özellikli, kaynak sınırları ve hata raporlaması olan bir sunucu. Persistent mod, vektörizasyon zorunluluğu, test ve güvenlik öncelikli. Python 3.11+, FastAPI, GNU Octave ile çalışır. Kurulum ve kullanım akışı, #file:specify.txt özetine ve yukarıdaki özet açıklamaya uygun olmalı."

## Execution Flow (main)
```
1. Parse user description from Input
2. Extract key concepts: Octave MCP sunucusu, STDIO ve HTTP API, publish/grabcode, kaynak sınırları, hata raporu, persistent mod, vektörizasyon, test, güvenlik, kurulum/kullanım akışı
3. Kullanıcı türü ve erişim kontrolü yok
4. Hata raporlama formatı en azından identifier, message, stack trace, ipucu içermeli
5. API rate limit ve veri saklama politikası yok
6. Fill User Scenarios & Testing section
7. Generate Functional Requirements
8. Identify Key Entities (Session, Run, Publish, Grabcode, User?)
9. Run Review Checklist
```

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
Bir kullanıcı, Octave kodunu yerel olarak çalıştırmak, çıktısını almak, HTML olarak yayınlamak ve yayınlanan HTML'den kaynak kodu geri almak ister. Kullanıcı, kaynak ve güvenlik sınırlarının aşıldığı durumlarda anlamlı hata mesajları bekler.

### Acceptance Scenarios
1. **Given** Octave kurulu ve sunucu başlatılmış, **When** kullanıcı bir kodu `run_octave` ile gönderirse, **Then** kod çalışır, stdout/stderr ve varsa figürler döner.
2. **Given** bir kod başarıyla çalıştırılmış ve publish edilmiş, **When** kullanıcı grabcode ile HTML'den kaynak kodu isterse, **Then** orijinal kod base64 olarak döner.
3. **Given** kaynak sınırları (CPU, bellek, çıktı boyutu) aşılırsa, **When** kullanıcı kod gönderirse, **Then** sistem anlamlı bir hata mesajı döner. [Pending: standart hata blok formatı]
4. **Given** persistent mod aktif, **When** aynı session_id ile tekrar kod gönderilirse, **Then** çalışma dizini korunur ve grabcode yapılabilir.

### Edge Cases
- Kaynak sınırları (CPU, bellek, çıktı) aşıldığında sistemin davranışı nedir?
- Hatalı Octave kodu gönderildiğinde kullanıcıya ne tür hata mesajı döner?
- Aynı anda birden fazla publish/grabcode işlemi yapılırsa sistem nasıl davranır?
- Octave veya bağımlılıklar eksikse sistem ne yanıt verir?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Sistem MUST Octave kodunu STDIO ve HTTP API üzerinden çalıştırabilmeli.
- **FR-002**: Sistem MUST publish komutu ile kodun HTML çıktısını ve figürleri üretebilmeli.
- **FR-003**: Sistem MUST grabcode komutu ile publish edilmiş HTML'den orijinal kodu base64 olarak döndürebilmeli.
- **FR-004**: Sistem MUST kaynak sınırlarını (CPU süresi, bellek, çıktı boyutu, timeout) enforce etmeli ve aşıldığında anlamlı hata mesajı döndürmeli.
- **FR-005**: Sistem MUST persistent modda session_id ile çalışma dizinlerini koruyabilmeli.
- **FR-006**: Sistem SHOULD vektörizasyon zorunluluğu ve kod üretim kurallarını enforce etmeli (gereksiz döngü uyarısı, çarpma işareti, grafik kaydetme, input kullanmama). [Pending]
- **FR-007**: Sistem SHOULD hata raporlarını standart blok formatında (identifier, message, stack trace, ipucu) döndürmeli. [Pending]
- **FR-008**: Sistem MUST publish ve grabcode işlemlerinde truncation ve veri bütünlüğü uyarılarını döndürmeli.
- **FR-009**: Sistem MUST test ve smoke testlerini otomatik olarak çalıştırabilmeli.
- **FR-010**: Sistem MUST güvenlik ve erişim sınırlarını enforce etmeli (ör. persistent modda sandbox yoksa devre dışı).
- **FR-011**: Sistem MUST kurulum ve kullanım adımlarını dokümante etmeli.
- **FR-012**: Sistem MUST API rate limit ve veri saklama politikasını belirtmeli. [NEEDS CLARIFICATION: Limitler ve retention süresi]

### Key Entities
- **Session**: Her oturumun kimliği, çalışma dizini, süresi, persistent olup olmadığı.
- **Run**: Çalıştırılan kod, stdout, stderr, figürler, kaynak sınırları, exit_code.
- **Publish**: HTML çıktısı, figürler, truncation durumu, publish_dir, html_name.
  - Not: HTML figürleri `<img>` olarak gömülür; `images/` altına kopyalanır.
- **Grabcode**: HTML'den çıkarılan orijinal kod, line_count, warnings.
- **User**: Çoklu kullanıcı desteği yok.

---

## Review & Acceptance Checklist

GATE: Automated checks run during main() execution

### Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain (bazıları Pending olarak tutuldu)
- [ ] Requirements are testable and unambiguous  
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status

Updated by main() during processing

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed (Pending items var)

---
