# Research: Octave MCP Server

**Kaynak:** specify.txt, plan.md, spec.md
**Tarih:** 2025-09-17

---

## 1. Bilinmeyenler & Açık Sorular
- Hata raporu formatı: Stack trace ve ipucu zorunlu, ancak formatın son hali (ör. JSON blok, metin blok) kesinleşmeli.
- API rate limit ve veri saklama politikası: Limitler ve retention süresi netleştirilmeli.
- Persistent modda sandbox zorunluluğu: macOS ve Linux’ta farklılıklar, güvenlik fallback’ı nasıl olmalı?
- Vektörizasyon zorunluluğu: Uyarı eşiği (ör. 15+ satırlık loop) ve örnek bloklar prompt’a nasıl entegre edilmeli?
- Paket kontrol akışı: list/find araçlarının hata akışına entegrasyonu nasıl optimize edilmeli?

---

## 2. Literatür ve Referanslar
- GNU Octave dokümantasyonu
- FastAPI resmi dokümantasyonu
- Python resource ve subprocess modülleri
- Firejail (Linux sandbox)
- Octave MCP örnek projeleri

---

## 3. Karar ve Notlar
- Hata blok formatı için hem JSON hem metin blok desteği önerildi.
- Persistent modda güvenlik riskine karşı varsayılan spawn (yeni süreç) önerildi.
- Vektörizasyon prompt örnekleri specify.txt’den alınarak sistem mesajına eklenecek.
- API rate limit için basit token bucket algoritması uygun.
- Kod üretiminde input fonksiyonu kesinlikle yasaklanacak.
