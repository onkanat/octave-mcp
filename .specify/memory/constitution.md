
# Octave MCP Constitution


## Core Principles

### I. Modülerlik ve Bağımsızlık
Her ana özellik ayrı, bağımsız ve test edilebilir modül (örn. MCP STDIO, HTTP API, yürütücü, modeller, yardımcılar) olarak tasarlanır. Kod tekrarları ortak yardımcı dosyalara taşınır. Her modülün amacı ve kapsamı nettir.

### II. CLI ve API Arayüzü
Her modül hem CLI hem de HTTP API üzerinden erişilebilir olmalıdır. Tüm giriş/çıkışlar metin tabanlıdır (stdin/args → stdout, hatalar stderr). JSON ve insan okunabilir formatlar desteklenir. API endpointleri açıkça dokümante edilir.

### III. Test-First (TDD Zorunlu)
Tüm yeni özellikler ve hata düzeltmeleri için önce test yazılır. Testler kullanıcı tarafından onaylanır, başarısız olur, ardından implementasyon yapılır. Red-Green-Refactor döngüsü zorunludur. smoke_test.py ile temel işlevler sürekli doğrulanır.

### IV. Entegrasyon ve Uçtan Uca Test
Her yeni modül, API veya önemli değişiklikte entegrasyon ve uçtan uca testler zorunludur. Özellikle publish/grabcode zinciri, hata raporlama ve kaynak yönetimi için kapsamlı testler uygulanır.

### V. Gözlemlenebilirlik, Sürümleme, Sadelik
Tüm çıktılar ve hatalar izlenebilir, loglanabilir ve referans ID ile takip edilebilir olmalıdır. Sürümleme MAJOR.MINOR.BUILD formatında yapılır. Her değişiklikte sürüm ve dokümantasyon güncellenir. Gereksiz karmaşıklıktan kaçınılır, YAGNI ilkesi uygulanır.


## Ek Kısıtlar, Güvenlik ve Performans Standartları

- Tüm kodlar yalnızca GNU Octave uyumlu olmalı, MATLAB özel API kullanılmaz.
- Her yürütme izole edilir; persistent mod opsiyoneldir ve güvenlik riski varsa devre dışı bırakılır.
- CPU süresi, bellek, çıktı ve dosya boyutu limitleri zorunludur (resource limit).
- Hata mesajları ve stack trace zorunlu, otomatik ipucu üretimi teşvik edilir.
- Kodda vektörizasyon zorunludur; gereksiz döngü kullanımı uyarı üretir.
- Grafik çıktılarında downsampling ve DPI kuralları uygulanır.
- Paket yönetimi: Fonksiyon bulunamazsa otomatik paket kontrolü yapılır.
- Tüm endpointler ve araçlar için rate limit ve otomatik temizlik mekanizması bulunur.


## Geliştirme Akışı, İnceleme ve Kalite Kapıları

- Tüm kod değişiklikleri test ile başlar (TDD).
- Kod gözden geçirme zorunludur; her PR/merge öncesi test ve dokümantasyon kontrol edilir.
- Sürüm geçişlerinde checklist uygulanır: testler, dokümantasyon, roadmap, güvenlik limitleri, yeni araçlar.
- Her sürümde değişiklik özeti ve geriye dönük uyumluluk notu eklenir.
- Öncelik sırası: Güvenlik & tutarlılık > Hata raporu > Performans > Kullanıcı deneyimi > Ek özellikler.


## Governance

Bu anayasa, tüm proje uygulamalarının üzerinde yer alır. Her değişiklikte dokümantasyon, onay ve geçiş planı zorunludur. Tüm PR ve incelemelerde anayasaya uyum kontrol edilir. Karmaşıklık gerekçelendirilmelidir. Geliştirme sırasında specify.txt ve CLAUDE.md rehberleri referans alınır.

**Version**: 1.0.0 | **Ratified**: 2025-09-17 | **Last Amended**: 2025-09-17