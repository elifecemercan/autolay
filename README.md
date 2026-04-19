# AutoLay

Python ile AutoCAD entegrasyonu ile Türkiye mevzuatına uygun mimari ruhsat projesi üretimi.

## Proje Durumu

**Aşama 1 - Temel Altyapı** (Devam ediyor)

## Kurulum

1. Python 3.14 kurulu olmalıdır.

2. Sanal ortam oluştur ve etkinleştir:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Gerekli paketleri kur:
   ```bash
   pip install pywin32
   ```

4. AutoCAD 2026'nın açık olduğundan emin ol.

5. Projeyi çalıştır:
   ```bash
   python -m autolay
   ```

## Klasör Yapısı

```
Autolay/
├── autolay/          # Ana Python paketi
│   ├── core/         # Çekirdek modüller (AutoCAD bağlantısı vb.)
│   ├── drawing/      # Çizim modülleri
│   └── utils/        # Yardımcı araçlar
├── docs/             # Dokümantasyon
├── tests/            # Test dosyaları
├── eski_denemeler/   # İlk deneme scriptleri (arşiv)
└── venv/             # Sanal ortam
```

## Teknolojiler

- Python 3.14
- pywin32 (AutoCAD COM bağlantısı için)
- AutoCAD 2026
