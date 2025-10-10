# Contracts: Octave MCP Server

**Kaynak:** specify.txt, plan.md, spec.md
**Tarih:** 2025-09-17

---

## 1. API Sözleşmeleri

### 1.1 /run_octave (POST)

- Girdi: code, [session_id]
- Çıktı: success, stdout, stderr, exit_code, runtime_seconds, images[]
- Kurallar:
  - Kod Octave veya Python ortamında çalıştırılır (mod: `OCTAVE_RUNNER_MODE`).
  - Resource limitler env üzerinden enforce edilir (CPU, bellek, timeout, çıktı boyutu).
  - input fonksiyonu yasak (uygulama düzeyinde; [NEEDS CLARIFICATION]).
  - Vektörizasyon uyarısı henüz uygulanmadı ([NEEDS CLARIFICATION]).

### 1.2 /publish (POST)

- Girdi: code, [session_id]
- Çıktı: html_b64, html_truncated, html_original_size, publish_dir, html_name, images[], warnings[]
- Kurallar:
  - Koddan HTML üretilir; son çalıştırmadan bulunan `fig*.png` görselleri `published/images/` altına kopyalanır ve HTML’e `<img>` olarak gömülür.
  - Truncation bilgisi döner; veri bütünlüğü uyarıları opsiyonel.
  - Persistent mod önerilir; session_id verilmemişse `anonymous` vb. kullanılabilir.

### 1.3 /grabcode (POST)

- Girdi: session_id
- Çıktı: code, b64, lines
- Kurallar:
  - Son publish edilen HTML’den kod çıkarılır; base64 karşılığı da döner.

### 1.4 /admin/cleanup (POST)

- Girdi: dry_run (bool), [force] (bool), [max_age_hours] (int), [max_age_days] (int), [session_id] (str)
- Çıktı: deleted_runs, deleted_sessions, dry_run, errors[]
- Kurallar:
  - Eski oturum/run klasörleri veya hedefli oturum temizlenir.
  - Force işlemi politika ile korunur; yalnız `MCP_ALLOW_FORCE_DELETE=true` iken etkin.

---

## 2. Hata Blok Sözleşmesi

- Her endpoint hata durumunda standart blok döndürür:
  - identifier
  - message
  - stack (file:line func)
  - ipucu (otomatik)
- Hata mesajı referans ID ile loglanır, detaylar gizlenir.

---

## 3. Güvenlik ve Limitler

- CPU süresi, bellek, çıktı boyutu, dosya boyutu, timeout enforce edilir.
- Persistent modda sandbox yoksa devre dışı.
- input fonksiyonu yasak.
- API rate limit ve veri saklama politikası dokümante edilir.
