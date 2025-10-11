
# OctaveMCP Constitution

## Core Principles

### I. Modülerlik ve Bağımsızlık

Her özellik bağımsız bir modül olarak başlar; modüller kendi başına test edilebilir,
belgelenmiş ve tekrar kullanılabilir olmalıdır. Ortak yardımcılar ve kod tekrarları
minimize edilmelidir.

### II. CLI ve API Arayüzü

Her modül CLI ve/veya HTTP API üzerinden erişilebilir olmalıdır. Giriş/çıkış protokolü
(stdin/stdout, JSON, hata yönetimi) standartlaştırılmıştır.

### III. Test-First (TDD)

TDD zorunludur: Testler önce yazılır, kullanıcı onaylar, testler başarısız olur,
ardından implementasyon yapılır. Red-Green-Refactor döngüsü sıkı şekilde uygulanır.

### IV. Entegrasyon ve Uçtan Uca Test

Yeni modül sözleşmeleri, sözleşme değişiklikleri, servisler arası iletişim ve ortak
şemalar için entegrasyon testleri zorunludur.

### V. Gözlemlenebilirlik, Sürümleme, Sadelik

Text I/O ve yapılandırılmış loglama ile hata ayıklanabilirlik sağlanır. Sürümleme
MAJOR.MINOR.PATCH formatında yapılır. Sadelik ve YAGNI ilkeleri önceliklidir.

## Güvenlik, Performans ve Teknoloji Yığını

Tüm kodlar sandbox ortamında çalıştırılır, kaynak limitleri ve rate limiting uygulanır.
Otomatik temizlik ve hata blokları zorunludur. Teknoloji yığını: Python 3.11+,
FastAPI, GNU Octave.

## Geliştirme Süreci ve Kalite Kontrol

Kod incelemesi, test kapıları ve deployment onayı zorunludur. Tüm değişiklikler PR
ile yapılır, compliance review gereklidir.

## Governance

Bu anayasa tüm diğer uygulama ve dokümantasyon pratiklerinin üstündedir.
Değişiklikler PR ile yapılır, onay ve migration planı gerektirir. Sürüm değişiklikleri
semantik kurallara göre yapılır. Tüm PR/review'larda compliance kontrolü zorunludur.

<!--
Sync Impact Report:
Version change: 1.0.0 → 1.0.1
Modified principles: placeholder → gerçek ilke metinleri
Added sections: Güvenlik, Performans ve Teknoloji Yığını; Geliştirme Süreci ve Kalite Kontrol
Templates requiring updates: plan-template.md ✅, spec-template.md ✅, tasks-template.md ✅
Follow-up TODOs: TODO(RATIFICATION_DATE): İlk onay tarihi bilinmiyor, eklenmeli
-->

**Version**: 1.0.1 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-10-11
