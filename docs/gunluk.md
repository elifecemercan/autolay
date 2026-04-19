# AutoLay Geliştirme Günlüğü

## 18 Nisan 2026

- Python 3.14 kurulumu yapıldı, sanal ortam (venv) oluşturuldu
- pywin32 paketi kurularak AutoCAD COM bağlantısı için altyapı hazırlandı
- AutoCAD 2026 ile Python arasında bağlantı testi gerçekleştirildi (`baglanti_testi.py`)
- İlk çizim denemesi: 60x60 boyutunda kare çizildi (`kare_ciz.py`)
- Daire çizimi denemesi yapıldı, koordinat formatı (VARIANT) öğrenildi (`daire_ciz.py`)
- Proje mimarisi kuruldu: paket klasörleri, `__init__.py` dosyaları ve dokümantasyon oluşturuldu

## 18 Nisan 2026 - Tam Gün Özeti

### Sabah Yapılanlar
- Python 3.14 + pywin32 311 kurulumu
- venv sanal ortam
- UTF-8 karakter desteği (utf8_aktif_et fonksiyonu)
- AutoCAD 2026 ile canlı bağlantı kuruldu
- İlk 60x60 kare ve daire çizildi (eski_denemeler/)

### Öğleden Sonra - Altyapı Kurulumu
- autolay/ paketi profesyonel mimariyle kuruldu (core, drawing, utils, config alt paketleri)
- autolay/core/baglanti.py — AutoCADConnector sınıfı
- autolay/drawing/shapes.py — GeometryDrawer (cizgi, kare, dikdortgen, daire, poligon)
- autolay/drawing/layers.py — LayerManager (katman_olustur, aktif_katman_yap, tum_katmanlar, katman_sil)
- RENK_ADLARI sözlüğü (Türkçe renk isimleri → ACI değerleri)
- autolay/utils/konsol.py — utf8_aktif_et
- Dokümantasyon: README.md, CLAUDE.md, docs/gunluk.md

### Akşam - Altyapı Tamamlama
- autolay/core/hatalar.py — 11 özel hata sınıfı (AutoLayError, BaglantiHatasi, GeometriHatasi, KatmanHatasi ve alt sınıfları)
- autolay/config/sabitler.py — tarafsız altyapı sabitleri (KATMAN_ONEKI, GEOMETRI_TOLERANSI, MIN_POLIGON_KOSE_SAYISI, VARSAYILAN_Z)
- autolay/utils/logger.py — merkezi loglama (konsol + logs/autolay.log)
- autolay/utils/input_yoneticisi.py — InputManager (sayi_al, koordinat_al, evet_hayir)
- Entegrasyon: Tüm mevcut sınıflar yeni hata sınıflarına, sabitlere, logger'a geçirildi
- baglanti.py'ye fail-fast eklendi: aktif çizim yoksa başta hata verir

### Test Dosyaları (hepsi başarılı)
- tests/test_baglanti.py
- tests/test_geometry.py (5 şekil çizildi)
- tests/test_layers.py (3 katman, renkli)
- tests/test_input_yoneticisi.py (canlı terminal → AutoCAD etkileşimi)

### Öğrenilen Kavramlar
- Sınıf, nesne, self, __init__, docstring
- try/except, raise, return, f-string
- Dependency Injection (AutoCADConnector üzerinden)
- DRY prensibi, idempotent davranış
- Paket/modül yapısı, PEP 8
- Exception hiyerarşisi
- Python logging modülü
- Sabit dosyalar ve config yönetimi
- Fail fast prensibi
- Regression testing
- isinstance, tuple unpacking, for + range

### Sonraki Seans İçin Kritik Bilgi
- Altyapı %90 bitti. KALAN: autolay/utils/geometri.py (GeometryUtils sınıfı)
- GeometryUtils içeriği:
  - iki_nokta_arasi_mesafe
  - poligon_alani (shoelace formülü)
  - poligon_merkezi (centroid)
  - nokta_poligon_icinde_mi
  - poligon_offset (içeri/dışarı daraltma — çekme mesafesi için KRİTİK)
- GeometryUtils bittikten sonra: autolay/mimari/ klasörü açılacak, ilk modül ArsaCizici olacak.

### Önemli Proje Kararları
- Altyapı tarafsız kalacak (mimari, elektrik, mekanik alanlarına özel şeyler altyapıya girmeyecek)
- Gelecekte aynı altyapı hem mimari ruhsat hem elektrik iç tesisat projesi için kullanılabilir olacak
- Mimari sabitler autolay/mimari/ klasöründe tanımlanacak (ileride)

## 18 Nisan 2026 - Tüm Gün

**Yapılan Sınıflar:**
- autolay/core/baglanti.py (AutoCADConnector)
- autolay/core/hatalar.py (11 hata sınıfı)
- autolay/drawing/shapes.py (GeometryDrawer)
- autolay/drawing/layers.py (LayerManager, RENK_ADLARI)
- autolay/config/sabitler.py (tarafsız altyapı sabitleri)
- autolay/utils/konsol.py (utf8_aktif_et)
- autolay/utils/logger.py (merkezi loglama)
- autolay/utils/input_yoneticisi.py (InputManager)

**Yapılan Testler (hepsi başarılı):**
- test_baglanti.py, test_geometry.py, test_layers.py, test_input_yoneticisi.py

**Entegrasyonlar:**
- Tüm sınıflar yeni hata sınıflarına geçirildi
- shapes.py config sabitlerini kullanıyor
- baglanti.py logger ve fail-fast eklendi

**Sonraki Adım:** autolay/utils/geometri.py (GeometryUtils) — mesafe, alan, poligon offset, merkez, nokta içinde mi.

**Sonra:** autolay/mimari/ klasörü ile ArsaCizici.
