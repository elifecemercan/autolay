"""
autolay/utils/geometri.py

Mimari hesaplamalar için matematiksel yardımcı araçlar.

Bu modül AutoCAD'e hiç dokunmaz; yalnızca saf Python matematiği içerir.
Çekme mesafesi, alan hesabı, ağırlık merkezi gibi tüm geometrik
işlemler buraya yönlendirilir.

Kullanım:
    from autolay.utils.geometri import GeometryUtils

    gu = GeometryUtils()
    alan = gu.poligon_alani([(0,0),(10,0),(10,10),(0,10)])
    iceri = gu.poligon_offset(koseler, mesafe=3000)
"""

import math

from autolay.config.sabitler import MIN_POLIGON_KOSE_SAYISI
from autolay.core.hatalar import YetersizKoseHatasi
from autolay.utils.logger import logger_olustur


class GeometryUtils:
    """
    Matematiksel geometri yardımcıları.

    Tüm metodlar örnekten çağrılabilir (self alır) ama dışarıdan
    bağımlılık gerektirmez — sadece sayısal girdi alır, sayısal çıktı verir.
    AutoCAD bağlantısı veya çizim nesnesi gerektirmez.
    """

    def __init__(self):
        """
        GeometryUtils nesnesini başlatır.

        Yalnızca logger hazırlanır; başka bağımlılık yoktur.
        """
        self.log = logger_olustur(__name__)

    # -----------------------------------------------------------------------
    # METOT 1: İki Nokta Arası Mesafe
    # -----------------------------------------------------------------------

    def mesafe(self, nokta1: tuple, nokta2: tuple) -> float:
        """
        İki nokta arasındaki Öklid (düz hat) mesafesini hesaplar.

        Formül: sqrt((x2 - x1)^2 + (y2 - y1)^2)

        Parametreler:
            nokta1 (tuple): Başlangıç noktası (x, y)
            nokta2 (tuple): Bitiş noktası (x, y)

        Dönüş değeri:
            float — iki nokta arasındaki mesafe (girdi birimiyle aynı)

        Örnek:
            gu.mesafe((0, 0), (3, 4))  → 5.0
        """
        x1, y1 = nokta1
        x2, y2 = nokta2

        # Öklid uzaklık formülü
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # -----------------------------------------------------------------------
    # METOT 2: Poligon Alanı (Shoelace Formülü)
    # -----------------------------------------------------------------------

    def poligon_alani(self, koseler: list) -> float:
        """
        Kapalı bir poligonun alanını Shoelace (Gauss) formülüyle hesaplar.

        Shoelace formülü:
            Alan = |Σ (xi * y(i+1) - x(i+1) * yi)| / 2
        Son köşe ile ilk köşe otomatik olarak kapatılır.

        Parametreler:
            koseler (list): [(x1,y1), (x2,y2), ...] biçiminde köşe listesi.
                            En az MIN_POLIGON_KOSE_SAYISI (3) köşe olmalıdır.

        Dönüş değeri:
            float — poligon alanı (her zaman pozitif; köşe sırasından bağımsız)

        Hatalar:
            YetersizKoseHatasi — 3'ten az köşe verilirse

        Örnek:
            gu.poligon_alani([(0,0),(10,0),(10,10),(0,10)])  → 100.0
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(len(koseler))

        n = len(koseler)
        toplam = 0.0

        for i in range(n):
            xi, yi = koseler[i]
            # Bir sonraki köşe; son köşede başa dön (kapalı poligon)
            xi1, yi1 = koseler[(i + 1) % n]

            # Shoelace: xi * yi+1 - xi+1 * yi
            toplam += xi * yi1 - xi1 * yi

        # Mutlak değer: köşe yönüne (saat/saat-karşıtı) bağımsız pozitif alan
        return abs(toplam) / 2.0

    # -----------------------------------------------------------------------
    # METOT 3: Poligon Merkezi (Basit Centroid)
    # -----------------------------------------------------------------------

    def poligon_merkezi(self, koseler: list) -> tuple:
        """
        Poligon köşelerinin aritmetik ortalamasını (basit centroid) döndürür.

        NOT: Bu hesap gerçek alan ağırlık merkezini (geometric centroid) değil,
        köşe noktalarının basit ortalamasını verir. Düzgün (regular) ve
        yaklaşık simetrik poligonlarda yeterince doğrudur.
        Çarpık veya çok girintili şekillerde alan merkezi gerekiyorsa
        daha gelişmiş bir algoritma kullanılmalıdır.

        Parametreler:
            koseler (list): [(x1,y1), (x2,y2), ...] biçiminde köşe listesi.
                            En az 1 köşe olmalıdır.

        Dönüş değeri:
            tuple — (ortalama_x, ortalama_y) biçiminde merkez noktası

        Hatalar:
            YetersizKoseHatasi — boş liste verilirse

        Örnek:
            gu.poligon_merkezi([(0,0),(10,0),(10,10),(0,10)])  → (5.0, 5.0)
        """
        if len(koseler) < 1:
            raise YetersizKoseHatasi(
                kose_sayisi=0,
                mesaj="Merkez hesaplamak için en az 1 köşe gereklidir."
            )

        n = len(koseler)

        # Tüm x ve y değerlerinin aritmetik ortalaması
        ortalama_x = sum(k[0] for k in koseler) / n
        ortalama_y = sum(k[1] for k in koseler) / n

        return (ortalama_x, ortalama_y)

    # -----------------------------------------------------------------------
    # METOT 4: Nokta Poligon İçinde Mi? (Ray Casting)
    # -----------------------------------------------------------------------

    def nokta_poligon_icinde_mi(self, nokta: tuple, koseler: list) -> bool:
        """
        Bir noktanın poligonun içinde olup olmadığını Ray Casting algoritmasıyla
        belirler.

        Algoritma:
            Noktadan yatay olarak sağa doğru sonsuz bir ışın gönderilir.
            Bu ışının poligon kenarlarıyla kaç kez kesiştiği sayılır.
            - Tek sayı → nokta içeride
            - Çift sayı → nokta dışarıda

        Parametreler:
            nokta  (tuple): Sınanacak nokta (x, y)
            koseler (list): Poligon köşeleri [(x1,y1), (x2,y2), ...]

        Dönüş değeri:
            bool — True: nokta içeride, False: dışarıda veya kenar üzerinde

        Örnek:
            gu.nokta_poligon_icinde_mi((5,5), [(0,0),(10,0),(10,10),(0,10)])
            → True
        """
        x, y = nokta
        n = len(koseler)
        icerde = False

        for i in range(n):
            xi, yi = koseler[i]
            xj, yj = koseler[(i + 1) % n]  # Bir sonraki köşe (kapalı döngü)

            # Kenar y aralığında mı ve ışın bu kenarla kesişiyor mu?
            y_araliginda = (yi > y) != (yj > y)
            if not y_araliginda:
                continue

            # Kesişim noktasının x değeri (kenarın doğru denkleminden)
            kesisim_x = (xj - xi) * (y - yi) / (yj - yi) + xi

            # Işın noktanın sağına gidiyorsa (x < kesisim_x) kesişim var
            if x < kesisim_x:
                icerde = not icerde  # Her kesişimde iç/dış durumu değişir

        return icerde

    # -----------------------------------------------------------------------
    # METOT 5: Poligon Offset (İçe/Dışa Daraltma-Genişletme)
    # -----------------------------------------------------------------------

    def poligon_offset(self, koseler: list, mesafe: float) -> list:
        """
        Poligonu her kenara dik yönde kaydırarak içe (büzer) veya dışa
        (şişirir) doğru yeni bir poligon üretir.

        Algoritma (köşe açıortay yöntemi):
            1. Poligonun yönü imzalı alan ile tespit edilir (CCW mu CW mi).
            2. Yöne göre normal vektör yönü ayarlanır; böylece pozitif mesafe
               HER ZAMAN içeri, negatif mesafe HER ZAMAN dışarı anlamına gelir.
            3. Her kenar için birim normal vektör hesaplanır.
            4. Her köşe için iki komşu kenarın normalleri toplanıp
               normalize edilir (açıortay yönü).
            5. Açıortay yönünde "mesafe / cos(yarı_açı)" kadar gidilir.
               Bu düzeltme köşenin gerçekten "mesafe" uzakta kalmasını sağlar.
            6. Yeni köşe listesi döndürülür.

        Parametreler:
            koseler (list): Poligon köşeleri [(x1,y1), ...].
                            Saat yönü (CW) veya saat karşıtı (CCW) — her ikisi
                            de desteklenir; yön otomatik tespit edilir.
            mesafe  (float): Pozitif → içe büzme (küçültme),
                             negatif → dışa şişirme (büyütme).
                             Birim, girdi koordinatlarıyla aynıdır.

        Dönüş değeri:
            list — Yeni köşe listesi [(x,y), ...], orijinalle aynı uzunlukta.

        Hatalar:
            YetersizKoseHatasi — 3'ten az köşe verilirse

        UYARI:
            Konveks (dışbükey) poligonlar için güvenilir sonuç üretir.
            Konkav (içbükey / girintili) poligonlarda kenarlar çakışabilir
            veya ters dönebilir. Bu durum log.warning ile bildirilir ama
            hata fırlatılmaz; çıktı yine de döndürülür.

        Örnek:
            gu.poligon_offset([(0,0),(10,0),(10,10),(0,10)], 2)
            → [(2,2),(8,2),(8,8),(2,8)]   # 10x10 → 6x6
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(len(koseler))

        n = len(koseler)

        # --- Adım 1: Poligonun yönünü tespit et (imzalı alan) ---
        # İmzalı alan pozitif → CCW (saat karşıtı)
        # İmzalı alan negatif → CW  (saat yönü)
        # CCW poligonda "sola dik normal" içeriye bakar.
        # CW  poligonda "sola dik normal" dışarıya bakar → mesafeyi ters çevir.

        imzali_alan = sum(
            koseler[i][0] * koseler[(i + 1) % n][1] -
            koseler[(i + 1) % n][0] * koseler[i][1]
            for i in range(n)
        ) / 2.0

        if imzali_alan < 0:
            # CW poligon: normaller dışarı bakıyor, işareti ters çevirerek düzelt
            dahili_mesafe = -mesafe
            self.log.debug("Poligon yönü: CW (saat yönü) — mesafe işareti ters çevriliyor.")
        else:
            dahili_mesafe = mesafe
            self.log.debug("Poligon yönü: CCW (saat karşıtı).")

        # --- Adım 2: Her kenar için birim normal vektörü hesapla ---
        # Kenar vektörü: (dx, dy)
        # Sola dik normal: (-dy, dx) — CCW poligon için içeriye bakar
        # Normalize edilir (uzunluk = 1).

        normaller = []
        for i in range(n):
            xi, yi = koseler[i]
            xj, yj = koseler[(i + 1) % n]

            dx = xj - xi
            dy = yj - yi
            uzunluk = math.sqrt(dx * dx + dy * dy)

            if uzunluk < 1e-10:
                # Sıfır uzunluklu kenar (iki özdeş köşe) — normal tanımsız
                normaller.append((0.0, 0.0))
                self.log.warning(
                    f"Sıfır uzunluklu kenar tespit edildi (köşe {i} ve {(i+1) % n}). "
                    "Bu köşe offset hesabında atlanacak."
                )
                continue

            # Sola dik birim normal: (-dy/len, dx/len)
            normaller.append((-dy / uzunluk, dx / uzunluk))

        # --- Adım 3: Her köşe için açıortay yönünü ve ölçek faktörünü hesapla ---

        yeni_koseler = []
        konkav_uyari_verildi = False

        for i in range(n):
            # Bu köşeye gelen iki kenar: önceki kenar (i-1 → i) ve sonraki (i → i+1)
            onceki_normal = normaller[(i - 1) % n]
            sonraki_normal = normaller[i]

            # Açıortay: iki normalin toplamı
            bx = onceki_normal[0] + sonraki_normal[0]
            by = onceki_normal[1] + sonraki_normal[1]
            b_uzunluk = math.sqrt(bx * bx + by * by)

            if b_uzunluk < 1e-10:
                # İki normal tam zıt → 180° dönüş noktası (düz çizgi üzerinde köşe)
                # Bu köşeyi sadece normal yönünde kaydır
                bx, by = onceki_normal
                olcek = dahili_mesafe
            else:
                # Normalize et
                bx /= b_uzunluk
                by /= b_uzunluk

                # cos(yarı_açı) = açıortay · kenar_normali
                # 1 / cos ile ölçekle: köşe gerçekten "mesafe" uzakta kalır
                cos_yari_aci = onceki_normal[0] * bx + onceki_normal[1] * by

                if abs(cos_yari_aci) < 1e-6:
                    # Neredeyse 90° açı — sonsuz uzama, uyarı ver
                    olcek = dahili_mesafe
                    if not konkav_uyari_verildi:
                        self.log.warning(
                            "Poligonda çok keskin köşe veya konkav bölge tespit edildi. "
                            "Offset sonucu güvenilir olmayabilir."
                        )
                        konkav_uyari_verildi = True
                else:
                    olcek = dahili_mesafe / cos_yari_aci

            # Köşeyi açıortay yönünde kaydır
            xi, yi = koseler[i]
            yeni_koseler.append((xi + bx * olcek, yi + by * olcek))

        # --- Adım 4: Sonucu doğrula (konkavlık uyarısı) ---
        # Offset sonrası alan orijinalden büyükse "içe büzme" ters gitti —
        # poligon muhtemelen konkavdı veya köşe sırası tutarsızdı.

        try:
            orijinal_alan = self.poligon_alani(koseler)
            yeni_alan = self.poligon_alani(yeni_koseler)

            if mesafe > 0 and yeni_alan > orijinal_alan + 1e-6:
                self.log.warning(
                    f"Offset sonrası alan arttı ({orijinal_alan:.1f} → {yeni_alan:.1f}). "
                    "Poligon konkav olabilir; sonucu görsel olarak doğrulayın."
                )
        except YetersizKoseHatasi:
            pass  # Doğrulama isteğe bağlı; hata fırlatma

        return yeni_koseler
