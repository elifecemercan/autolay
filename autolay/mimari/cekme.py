"""
cekme.py — CekmeCizici modülü

Türkiye yapı mevzuatında tanımlanan ön, arka ve yan bahçe çekme
mesafelerini arsa sınırından içeri doğru ofset alarak AutoCAD'de çizer.

Bağımlılıklar:
    - AutoCADConnector: AutoCAD COM bağlantısını yönetir
    - GeometryDrawer: Geometrik şekilleri çizer
    - LayerManager: Katman oluşturma ve yönetimi
    - GeometryUtils: Poligon ofset ve alan hesaplamaları
"""

from autolay.core.baglanti import AutoCADConnector
from autolay.drawing.shapes import GeometryDrawer
from autolay.drawing.layers import LayerManager
from autolay.utils.geometri import GeometryUtils
from autolay.utils.logger import logger_olustur
from autolay.core.hatalar import YetersizKoseHatasi
from autolay.config.sabitler import MIN_POLIGON_KOSE_SAYISI


class CekmeCizici:
    """
    Arsa sınırından belirtilen mesafe kadar içeri çekilerek oluşan
    yapı yaklaşma sınırını AutoCAD'de çizen sınıf.

    Kullanım sırası:
        1. CekmeCizici(connector) ile nesne oluştur
        2. arsa_koseleri_ayarla(koseler) ile arsa köşelerini ver
        3. cekme_mesafesi_ayarla(mesafe) ile çekme mesafesini belirle
        4. ciz() ile AutoCAD'e çiz
        5. İsteğe bağlı: cekme_koseleri() ile hesaplanan köşeleri al
    """

    def __init__(self, connector: AutoCADConnector):
        """
        CekmeCizici nesnesini başlatır.

        Parametreler:
            connector (AutoCADConnector): Aktif AutoCAD COM bağlantısı.
        """
        self.connector = connector
        self.layer_mgr = LayerManager(connector)
        self.drawer = GeometryDrawer(connector)
        self.geo = GeometryUtils()
        self.log = logger_olustur(__name__)
        self.arsa_koseleri = None
        self.mesafe = None
        self._cekme_koseleri = None
        self.KATMAN_ADI = "AUTOLAY_CEKME"
        self.KATMAN_RENGI = "sari"

    def arsa_koseleri_ayarla(self, koseler: list):
        """
        Çekme hesabının yapılacağı arsa köşe koordinatlarını ayarlar.

        Parametreler:
            koseler (list): (x, y) veya (x, y, z) tuple'larından oluşan liste.
                            En az MIN_POLIGON_KOSE_SAYISI kadar köşe olmalıdır.

        Hata:
            YetersizKoseHatasi: Köşe sayısı minimumun altındaysa fırlatılır.
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(kose_sayisi=len(koseler))
        self.arsa_koseleri = koseler
        self.log.info(f"{len(koseler)} arsa köşe noktası alındı.")

    def cekme_mesafesi_ayarla(self, mesafe: float):
        """
        Arsa sınırından içeri uygulanacak çekme mesafesini ayarlar.

        Parametreler:
            mesafe (float): Metre cinsinden pozitif çekme mesafesi.
                            Pozitif değer her zaman içeri yönde ofset uygular.

        Hata:
            ValueError: Mesafe sıfır veya negatifse fırlatılır.
        """
        if mesafe <= 0:
            raise ValueError("Çekme mesafesi pozitif olmalı.")
        self.mesafe = mesafe
        self.log.info(f"Çekme mesafesi ayarlandı: {mesafe} m")

    def ciz(self):
        """
        Çekme sınırı poligonunu hesaplar ve AutoCAD'e çizer.

        Arsa köşelerinden self.mesafe kadar içeri ofset alır,
        AUTOLAY_CEKME katmanında sarı renkte çizer.

        Hata:
            ValueError: arsa_koseleri_ayarla veya cekme_mesafesi_ayarla
                        daha önce çağrılmamışsa fırlatılır.
        """
        if self.arsa_koseleri is None:
            raise ValueError("Önce arsa_koseleri_ayarla çağır.")
        if self.mesafe is None:
            raise ValueError("Önce cekme_mesafesi_ayarla çağır.")

        self._cekme_koseleri = self.geo.poligon_offset(self.arsa_koseleri, self.mesafe)

        self.layer_mgr.katman_olustur(self.KATMAN_ADI, renk=self.KATMAN_RENGI)
        self.layer_mgr.aktif_katman_yap(self.KATMAN_ADI)
        self.drawer.poligon_ciz(self._cekme_koseleri)

        self.log.info(
            f"Çekme çizildi. Mesafe: {self.mesafe}m, "
            f"Alan: {self.geo.poligon_alani(self._cekme_koseleri):.2f} m²"
        )

    def cekme_koseleri(self) -> list:
        """
        Hesaplanan çekme sınırı köşe koordinatlarını döndürür.

        Dönüş:
            list: Çekme poligonunun (x, y) köşe listesi.

        Hata:
            ValueError: ciz() henüz çağrılmamışsa fırlatılır.
        """
        if self._cekme_koseleri is None:
            raise ValueError("Önce ciz() çağır.")
        return self._cekme_koseleri
