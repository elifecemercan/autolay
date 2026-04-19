"""
tests/test_cekme.py

CekmeCizici sınıfını AutoCAD üzerinde test eder.
25x20 metrelik arsa üzerine 3 metrelik çekme mesafesi uygulanır.
Beklenen sonuç: 19x14 = 266 m² yapı yaklaşma alanı.

Çalıştırma:
    cd C:/Projeler/Autolay
    python tests/test_cekme.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.mimari.arsa import ArsaCizici
from autolay.mimari.cekme import CekmeCizici
from autolay.utils.logger import logger_olustur

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()

log = logger_olustur(__name__)


def test_cekme():
    """ArsaCizici + CekmeCizici birlikte çalışmasını uçtan uca test eder."""

    print("=" * 40)
    print("AutoLay — CekmeCizici Testi")
    print("=" * 40)

    # 1. AutoCAD bağlantısını kur
    connector = AutoCADConnector()
    try:
        basarili = connector.baglan()
    except AktifCizimYokHatasi as hata:
        print(f"HATA: {hata}")
        print("Çözüm: AutoCAD'de bir .dwg dosyası açın ve tekrar deneyin.")
        return

    if not basarili:
        print("HATA: AutoCAD'e bağlanılamadı. Test durduruluyor.")
        print("Çözüm: AutoCAD 2026'yı açın ve tekrar deneyin.")
        return

    # 2. Arsayı çiz
    koseler = [(0, 0), (25, 0), (25, 20), (0, 20)]
    arsa = ArsaCizici(connector)
    arsa.koseleri_ayarla(koseler)
    arsa.ciz()
    print(f"✓ Arsa çizildi        → {koseler}")
    print(f"  Alan: {arsa.alan():.2f} m²  (beklenen: 500.00)")

    # 3. CekmeCizici nesnesi oluştur
    cekme = CekmeCizici(connector)

    # 4. Arsa köşelerini ayarla
    cekme.arsa_koseleri_ayarla(koseler)
    print(f"✓ Arsa köşeleri ayarlandı → {len(koseler)} köşe")

    # 5. Çekme mesafesini ayarla: 3 metre içeri
    cekme.cekme_mesafesi_ayarla(3)
    print("✓ Çekme mesafesi ayarlandı → 3 m")

    # 6. Çekme sınırını çiz
    cekme.ciz()
    print("✓ Çekme çizildi       → AUTOLAY_CEKME katmanı, sarı")

    # 7. Hesaplanan çekme köşelerini göster
    kose_listesi = cekme.cekme_koseleri()
    print(f"✓ Çekme köşeleri      → {kose_listesi}")
    log.info(f"Çekme köşeleri: {kose_listesi}")

    # 8. Beklenen: 19x14 = 266 m² (her kenarda 3m çekilince 25-6=19, 20-6=14)
    from autolay.utils.geometri import GeometryUtils
    geo = GeometryUtils()
    cekme_alani = geo.poligon_alani(kose_listesi)
    log.info(f"Çekme alanı: {cekme_alani:.2f} m²  (beklenen: 266.00 m²)")
    print(f"  Çekme alanı: {cekme_alani:.2f} m²  (beklenen: 266.00)")

    # 9. Tüm çizimin ekranda görünmesi için ZoomExtents uygula
    connector.acad.ZoomExtents()
    print("✓ ZoomExtents uygulandı — arsa ve çekme ekranda görünüyor")

    print("=" * 40)
    print("Test tamamlandı.")


if __name__ == "__main__":
    test_cekme()
