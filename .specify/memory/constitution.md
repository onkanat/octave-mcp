<!--
============================================================================
SYNC IMPACT REPORT - Constitution v1.1.0
============================================================================

VERSION CHANGE: 1.0.1 → 1.1.0

BUMP RATIONALE: MINOR version bump
- Added 4 new principle sections (VI-IX)
- Materially expanded testing and error handling guidance
- Added MCP protocol integration requirements
- Added bilingual documentation requirements
- No breaking changes to existing principles

MODIFIED PRINCIPLES:
- Principle III: Expanded with contract test requirements and coverage tracking
- Principle IV: Added MCP tool contract test requirements
- Principle V: Split into V (Observability & Versioning) and VII (Error Handling)

ADDED PRINCIPLES:
- Principle VI: MCP Protocol Integration (FastMCP tooling standards)
- Principle VII: Standardized Error Handling (ERROR_SCHEMA.md compliance)
- Principle VIII: Bilingual Documentation (TR/EN requirement)
- Principle IX: Import Path Resolution (module/script execution modes)

REMOVED SECTIONS: None

TEMPLATES REQUIRING UPDATES:
- ✅ plan-template.md: Already includes constitution check section
- ✅ spec-template.md: Functional requirements align with new principles
- ✅ tasks-template.md: Test phases align with expanded testing requirements
- ⚠️  constitution_update_checklist.md: Should add new principles VI-IX

FOLLOW-UP ACTIONS:
- Update constitution_update_checklist.md to include new principles VI-IX
- Consider adding MCP tool validation checklist to templates
- Add bilingual documentation checklist for new features

DEFERRED ITEMS: None - all placeholders resolved

============================================================================
-->

# OctaveMCP Constitution

**Project**: OctaveMCP - Secure GNU Octave code execution via Model Context Protocol  
**Version**: 1.1.0  
**Ratified**: 2025-09-17  
**Last Amended**: 2025-10-13  
**Status**: Active

---

## Preamble

This constitution establishes the non-negotiable principles, practices, and governance
for the OctaveMCP project. All development, documentation, testing, and deployment
activities MUST comply with these principles. This document supersedes all other
practice guidelines and serves as the ultimate authority for technical decisions.

---

## Core Principles

### I. Modülerlik ve Bağımsızlık (Modularity and Independence)

**Principle**: Her özellik bağımsız bir modül olarak tasarlanır ve geliştirilir.

**Requirements**:

- Her modül bağımsız olarak test edilebilir olmalıdır
- Modüller kendi dokümantasyonuna sahip olmalıdır
- Modül arayüzleri açık ve tekrar kullanılabilir olmalıdır
- Ortak yardımcı fonksiyonlar `utils/` altında merkezi olarak tutulur
- Kod tekrarı (DRY prensibi) minimize edilmelidir

**Rationale**: Bağımsız modüller, paralel geliştirme, izole test etme ve özellik bazlı
deployment'a olanak tanır. Sistem karmaşıklığı arttıkça, bağımsızlık bakım maliyetini
düşürür.

**Examples**:

- `services/octave_runner.py` - Kod çalıştırma
- `services/publish_service.py` - HTML yayınlama
- `services/cleanup_service.py` - Kaynak temizleme

---

### II. CLI ve API Arayüzü (CLI and API Interface)

**Principle**: Tüm core özellikler hem CLI hem HTTP API üzerinden erişilebilir olmalıdır.

**Requirements**:

- HTTP API: FastAPI ile RESTful endpoint'ler (`/api/v1/*`)
- CLI: `octave-mcp` konsol komutu ile erişim
- Giriş: JSON formatında standartlaşmış request modelleri
- Çıkış: JSON formatında standartlaşmış response modelleri
- Hata yönetimi: Standart error block (ERROR_SCHEMA.md) formatında

**Rationale**: Çoklu arayüz desteği, farklı kullanım senaryolarını (automation, manual,
integration) destekler ve esneklik sağlar. Standart formatlar entegrasyon maliyetini
azaltır.

**Implementation**:

- `src/api/endpoints.py` - HTTP API endpoint'leri
- `src/cli/cli.py` - CLI komut arayüzü
- `src/models/requests.py` - Standart request modelleri
- `src/models/responses.py` - Standart response modelleri

---

### III. Test-First Development (TDD)

**Principle**: Testler her zaman implementasyondan önce yazılır.

**Requirements**:

- Yeni özellik için önce testler yazılır
- Testler başarısız olur (RED)
- Kod implementasyonu yapılır
- Testler başarılı olur (GREEN)
- Kod refactor edilir (REFACTOR)
- Test coverage izlenir ve CI/CD'de raporlanır
- Minimum coverage hedefi: %80 (core modüller için)

**Rationale**: TDD, requirement'ların netleşmesini, daha az bug, daha iyi API tasarımı
ve refactoring güveni sağlar. Test-first yaklaşımı, over-engineering'i engeller.

**Test Types**:

- Unit tests: `tests/unit/` - Modül seviyesi, mocked dependencies
- Integration tests: `tests/integration/` - Modüller arası etkileşim
- Contract tests: `tests/contract/` - API/MCP tool sözleşmeleri

**CI/CD Integration**:

- Coverage raporu pytest-cov ile üretilir
- CI pipeline'da coverage threshold kontrolü yapılır
- Curated test sets ile CI süresi optimize edilir

---

### IV. Entegrasyon ve Contract Test (Integration and Contract Testing)

**Principle**: Modül sözleşmeleri, servisler arası iletişim ve ortak şemalar contract
testleri ile garanti edilir.

**Requirements**:

- Yeni HTTP endpoint: Contract test zorunlu (`tests/contract/test_*_post.py`)
- Yeni MCP tool: Contract test zorunlu (araç parametreleri, dönüş şeması)
- Değişen sözleşme: Geriye dönük uyumluluk kontrolü
- Entegrasyon testleri: Kritik akışlar için zorunlu (örn: publish → grabcode)
- Ortak şemalar: `ERROR_SCHEMA.md`, request/response modelleri contract ile korunur

**Rationale**: Contract testler, API breaking change'lerini erken yakalar, bağımlı
sistemlerin güvenle entegre olmasını sağlar ve dokümantasyon-kod uyumunu garantiler.

**Examples**:

- `tests/contract/test_run_octave_post.py` - /run endpoint contract
- `tests/contract/test_publish_post.py` - /publish endpoint contract
- `tests/integration/test_api_basic.py` - HTTP API akış testi

---

### V. Gözlemlenebilirlik ve Sürümleme (Observability and Versioning)

**Principle**: Sistemin davranışı, text I/O ve yapılandırılmış loglar ile izlenebilir
olmalıdır. Sürümler semantik versioning ile yönetilir.

**Requirements**:

**Gözlemlenebilirlik**:

- Tüm servisler yapılandırılmış logging kullanır (`logging` modülü)
- Kritik operasyonlar (kod çalıştırma, kaynak limiti, hata) loglanır
- Log seviyeleri: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Stdout/stderr çıktıları preserve edilir ve yanıtlarda döndürülür
- Resource violation durumları açıkça loglanır ve error block'ta raporlanır

**Sürümleme** (Semantic Versioning: MAJOR.MINOR.PATCH):

- MAJOR: Breaking API/MCP tool değişiklikleri, uyumsuz değişiklikler
- MINOR: Yeni özellik, yeni MCP tool, geriye dönük uyumlu eklentiler
- PATCH: Bug fix, dokümantasyon, performans iyileştirmeleri
- `pyproject.toml` version alanı tek kaynak olarak kullanılır
- `CHANGELOG.md` tüm sürümler için detaylı notlar içerir

**Sadelik (YAGNI - You Aren't Gonna Need It)**:

- Speculative feature'lar eklenmez
- Gereksiz abstraction katmanlarından kaçınılır
- Configuration yalnızca kullanılan parametreler için yapılır

**Rationale**: İyi gözlemlenebilirlik, production sorunlarının hızlı tanısını sağlar.
Semantik versioning, dependency yönetimini kolaylaştırır ve breaking change'leri açık
hale getirir. Sadelik, bakım maliyetini düşürür.

---

### VI. MCP Protocol Integration

**Principle**: Tüm core özellikler Model Context Protocol (MCP) üzerinden FastMCP ile
expose edilir.

**Requirements**:

- MCP server: `src/mcp_server.py` üzerinden FastMCP ile yayınlanır
- Tool naming: snake_case konvansiyonu (`octave_run`, `octave_publish`, vb.)
- Tool documentation: Her araç için parameter tipleri, açıklamalar ve örnekler
- LM Studio integration: Universal config örnekleri sağlanır ve test edilir
- Transport modes: STDIO (default), SSE desteklenir
- Tool contract: Her tool için contract test yazılır

**Core MCP Tools**:

- `octave_run`: Kod çalıştırma, stdout/stderr/images döndürme
- `octave_publish`: HTML yayınlama, figürleri embedded görsel olarak ekleme
- `octave_grabcode`: Yayınlanmış kodları geri getirme
- `admin_cleanup`: Session temizleme (policy ile korunan)

**LM Studio Configuration**:

- Universal config hem script hem module modunda çalışır
- Import path resolution otomatik olarak yapılır
- Environment variables dokümante edilir (`MCP_TOOLS.md`)

**Rationale**: MCP protocol, AI assistant'ların kod çalıştırma yeteneklerini standart
bir arayüz üzerinden kazanmasını sağlar. FastMCP, boilerplate'i azaltır ve type-safe
tool tanımları sunar.

---

### VII. Standardized Error Handling

**Principle**: Tüm hatalar `ERROR_SCHEMA.md` standardına uygun olarak raporlanır.

**Requirements**:

**Error Block Format** (required fields):

- `id`: UUID4 formatında unique identifier
- `type`: Enum (runtime_error, timeout, resource_violation, validation_error,
  rate_limited, internal)
- `message`: User-friendly hata açıklaması
- `timestamp`: ISO-8601 formatında zaman damgası

**Optional Fields**:

- `hint`: Kullanıcıya düzeltme önerisi
- `session_id`, `run_id`: İlgili context bilgileri
- `stdout_truncated`, `stderr_truncated`: Truncation flag'leri
- `resource_violation`: Limit ihlali detayları (limit_type, limit_value, observed_value)
- `details`: Ek debug bilgileri

**Implementation**:

- Tüm HTTP 4xx/5xx yanıtları error block içerir
- MCP tool errors error block ile dönülür
- Global exception handler: `MCPException` sınıfı (`src/exceptions.py`)
- Resource limit ihlalleri `resource_violation` bloğu ile raporlanır

**Rationale**: Standart error format, client-side error handling'i kolaylaştırır,
user experience'i iyileştirir ve debugging'i hızlandırır. Resource violation tracking,
kullanıcıların limit sorunlarını anlamasını sağlar.

---

### VIII. Bilingual Documentation

**Principle**: Tüm kullanıcıya yönelik dokümantasyon Türkçe ve İngilizce olarak
sağlanır.

**Requirements**:

- API documentation: `docs/API.md` (TR), `docs/en/API.md` (EN)
- MCP tools reference: `docs/MCP_TOOLS.md` (TR), `docs/en/MCP_TOOLS.md` (EN)
- Error schema: `docs/ERROR_SCHEMA.md` (TR), `docs/en/ERROR_SCHEMA.md` (EN)
- README: `README.md` (TR), `docs/en/README.md` (EN)
- Code comments: Türkçe veya İngilizce (internal, team preference)
- Public API docstrings: İngilizce (Python convention)

**Synchronization**:

- Dokümantasyon değişiklikleri her iki dilde yapılır
- Breaking change'ler migration guide ile açıklanır (both languages)
- GitHub Pages: Jekyll ile otomatik yayınlanır (`docs/_config.yml`)

**Rationale**: Bilingual documentation, hem yerel hem uluslararası kullanıcı kitlesine
hizmet verir. Türkçe dokümantasyon, local adoption'ı artırırken İngilizce global
visibility sağlar.

---

### IX. Import Path Resolution

**Principle**: Paket hem module hem script execution mode'unda sorunsuz çalışmalıdır.

**Requirements**:

- Package structure: `src/` altında organize edilmiş modüller
- Entry points: `pyproject.toml` içinde console_scripts tanımları
- Import resolution: Otomatik, manuel `sys.path` manipülasyonu gerektirmez
- Execution modes:
  - Module mode: `python -m mcp_server`
  - Script mode: `python src/mcp_server.py`
  - Console script: `octave-mcp` (installed package)
- LM Studio compatibility: Universal config hem script hem module mode'unda çalışır

**Implementation**:

- `src/mcp_server.py`: Import path otomatik çözümü
- `pyproject.toml`: Entry point tanımları (`octave-mcp = "cli.cli:main"`)
- `src/__init__.py`: Package root initialization

**Rationale**: Flexible execution modes, development ve production deployment
senaryolarına uyum sağlar. Otomatik import resolution, setup complexity'sini azaltır
ve user experience'i iyileştirir.

---

## Güvenlik ve Performans (Security and Performance)

**Sandbox Execution**:

- Tüm Octave/Python kodları izole ortamda çalıştırılır
- Resource limits uygulanır: CPU time, memory, output size, timeout
- Malicious code'a karşı koruma: Process sandboxing

**Resource Limits**:

- `MCP_CPU_LIMIT`: CPU time limit (seconds)
- `MCP_MEMORY_MB`: Memory limit (MB)
- `MCP_TIMEOUT_SECONDS`: Execution timeout
- `MCP_MAX_OUTPUT_CHARS`: Stdout/stderr character limit
- Resource violations: `resource_violation` block ile raporlanır

**Rate Limiting**:

- HTTP API: Request rate limiting (configurable)
- `MCP_RATE_LIMIT_MAX`: Max requests
- `MCP_RATE_LIMIT_WINDOW`: Time window (seconds)

**Automatic Cleanup**:

- Session directories: `runs/<session_id>/`
- Retention policy: `MCP_RUNS_RETENTION_DAYS`
- `admin_cleanup` tool: Policy-protected force cleanup

---

## Teknoloji Yığını (Technology Stack)

**Core Technologies**:

- Python 3.11+ (type hints, modern syntax)
- FastAPI 0.100+ (HTTP REST API)
- FastMCP (mcp>=1.8.0) (Model Context Protocol)
- GNU Octave (scientific computing)
- pytest (testing framework)

**Dependencies**:

- uvicorn, gunicorn (ASGI servers)
- httpx, requests (HTTP clients)
- python-dotenv (environment management)
- Pydantic (data validation)

**Project Structure**:

```
src/
├── api/             # FastAPI endpoints
├── cli/             # CLI interface
├── models/          # Pydantic models (requests, responses, entities)
├── services/        # Business logic (octave_runner, publish, cleanup, etc.)
├── utils/           # Shared utilities (config, logging, security, etc.)
├── mcp_server.py    # MCP protocol server (FastMCP)
└── app.py           # FastAPI application

tests/
├── unit/            # Unit tests (mocked dependencies)
├── integration/     # Integration tests (real interactions)
└── contract/        # Contract tests (API/MCP schemas)
```

---

## Geliştirme Süreci (Development Process)

**Code Review**:

- Tüm değişiklikler Pull Request (PR) ile yapılır
- PR review zorunludur (en az 1 reviewer)
- Automated checks: Tests, linting, coverage

**Test Gates**:

- Unit tests MUST pass
- Integration tests MUST pass (critical flows)
- Contract tests MUST pass (API/MCP tools)
- Coverage threshold: ≥80% (core modules)

**CI/CD Pipeline**:

- Automated testing on push
- Coverage reporting
- OpenAPI artifact generation
- GitHub Pages deployment (documentation)

**Compliance Review**:

- Constitution alignment check
- Breaking change impact analysis
- Migration guide requirement (for breaking changes)

**Deployment**:

- PyPI package: `pip install octave-mcp`
- GitHub releases: Tagged versions
- Documentation: Auto-deployed to GitHub Pages

---

## Governance

**Authority**: Bu anayasa tüm uygulama, dokümantasyon ve süreç pratiklerinin
üstündedir. Çelişki durumunda anayasa hükümleri geçerlidir.

**Amendment Process**:

1. Constitution değişikliği PR ile önerilir
2. Impact analysis yapılır (etkilenen bileşenler, breaking changes)
3. Template ve dokümantasyon güncellemeleri belirlenir
4. Review ve onay (maintainer approval)
5. Version bump (semantic versioning rules)
6. Migration plan (if breaking changes)
7. Merge ve deployment

**Version Control**:

- Constitution version: Semantic versioning
- Sync Impact Report: Her değişiklikte üretilir (HTML comment)
- Last Amended Date: ISO-8601 format

**Compliance Enforcement**:

- Tüm PR'larda constitution compliance kontrolü yapılır
- Breaking principle violations: PR reject
- Minor violations: Review comment ile düzeltme istenir
- Checklist: `.specify/memory/constitution_update_checklist.md`

**Document Hierarchy**:

1. Constitution (this document) - Supreme authority
2. Specification templates (`.specify/templates/`)
3. Feature specifications (`specs/*/spec.md`)
4. Implementation plans (`specs/*/plan.md`)
5. Task lists (`specs/*/tasks.md`)

---

## Revision History

**v1.1.0** (2025-10-13):

- Added Principle VI: MCP Protocol Integration
- Added Principle VII: Standardized Error Handling
- Added Principle VIII: Bilingual Documentation
- Added Principle IX: Import Path Resolution
- Expanded Principle III: Test coverage and CI/CD integration
- Expanded Principle IV: MCP tool contract tests
- Expanded Principle V: Split observability from error handling

**v1.0.1** (2025-10-11):

- Initial constitution with core principles
- Placeholder resolution for project-specific details

**v1.0.0** (2025-09-17):

- Constitution ratified
- Core principles established

---

**END OF CONSTITUTION**
