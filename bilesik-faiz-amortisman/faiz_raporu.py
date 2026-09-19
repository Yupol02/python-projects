"""Sonuç nesnelerini okunabilir metne çevirir.

Buradaki fonksiyonlar hesap yapmaz ve `print` etmez — **string döndürür**.
Bu ayrımın nedeni test edilebilirlik: çıktı string olduğu için testler
satırların içeriğini doğrudan kontrol edebiliyor. `print` etseydik
çıktıyı yakalamak için uğraşmak gerekirdi.
"""

from amortisman import yil_sonu_taksitleri
from bilesik_faiz import yil_sonu_satirlari
from faiz_modelleri import AmortismanSonucu, BirikimSonucu

GENISLIK = 72


def _baslik(metin: str) -> list[str]:
    return ["=" * GENISLIK, metin.center(GENISLIK), "=" * GENISLIK]


def _oran_etiketi(yillik_oran_yuzde: float) -> str:
    if yillik_oran_yuzde == 0:
        return "0 (faizsiz)"
    return f"{yillik_oran_yuzde:,.2f} %"


# --- Bileşik faiz ---

def birikim_ozeti(sonuc: BirikimSonucu) -> str:
    satirlar = _baslik("BİLEŞİK FAİZ ÖZETİ")
    satirlar.append(f"Başlangıç anaparası   : {sonuc.anapara:>15,.2f} TL")
    satirlar.append(
        f"Yıllık faiz           : "
        f"{_oran_etiketi(sonuc.yillik_oran_yuzde):>15}"
    )
    satirlar.append(f"Bileşikleme           : {sonuc.donem_etiketi:>15}")
    satirlar.append(
        f"Süre                  : {sonuc.yil:>15,.2f} yıl "
        f"({sonuc.toplam_donem} dönem)"
    )
    satirlar.append(f"Dönemsel katkı        : {sonuc.donemsel_katki:>15,.2f} TL")
    satirlar.append("-" * GENISLIK)
    satirlar.append(f"Toplam yatırılan      : {sonuc.toplam_yatirilan:>15,.2f} TL")
    satirlar.append(f"Toplam faiz kazancı   : {sonuc.toplam_faiz:>15,.2f} TL")
    satirlar.append(f"Son bakiye            : {sonuc.son_bakiye:>15,.2f} TL")
    satirlar.append(f"Efektif yıllık oran   : {sonuc.efektif_yillik_oran * 100:>15.2f} %")
    return "\n".join(satirlar)


def birikim_tablosu(sonuc: BirikimSonucu, sadece_yil_sonu: bool = False) -> str:
    """Birikim tablosu. Uzun vadelerde `sadece_yil_sonu=True` işe yarar."""
    baslik = "BİRİKİM TABLOSU (yıl sonları)" if sadece_yil_sonu else "BİRİKİM TABLOSU"
    satirlar = _baslik(baslik)
    satirlar.append(
        f"{'DÖNEM':>5} {'AÇILIŞ':>16} {'KATKI':>13} {'FAİZ':>14} {'KAPANIŞ':>20}"
    )
    satirlar.append("-" * GENISLIK)

    gosterilecek = yil_sonu_satirlari(sonuc) if sadece_yil_sonu else sonuc.tablo

    for s in gosterilecek:
        # Sütunlar arasındaki tek boşluk bilinçli: alan genişliğine
        # sığmayan bir tutar, yandaki sütuna yapışıp satırı okunamaz
        # hâle getirmesin.
        satirlar.append(
            f"{s.donem:>5} "
            f"{s.acilis_bakiye:>16,.2f} "
            f"{s.katki:>13,.2f} "
            f"{s.faiz:>14,.2f} "
            f"{s.kapanis_bakiye:>20,.2f}"
        )

    return "\n".join(satirlar)


# --- Amortisman ---

def amortisman_ozeti(sonuc: AmortismanSonucu) -> str:
    satirlar = _baslik("KREDİ ÖZETİ")
    satirlar.append(f"Kredi tutarı          : {sonuc.anapara:>15,.2f} TL")
    satirlar.append(
        f"Yıllık faiz           : "
        f"{_oran_etiketi(sonuc.yillik_oran_yuzde):>15}"
    )
    satirlar.append(f"Taksit sıklığı        : {sonuc.donem_etiketi:>15}")
    satirlar.append(
        f"Vade                  : {sonuc.yil:>15,.2f} yıl "
        f"({sonuc.vade_donem} taksit)"
    )
    satirlar.append("-" * GENISLIK)
    satirlar.append(f"Dönemsel taksit       : {sonuc.donemsel_taksit:>15,.2f} TL")
    satirlar.append(f"Toplam geri ödeme     : {sonuc.toplam_odeme:>15,.2f} TL")
    satirlar.append(f"Toplam faiz           : {sonuc.toplam_faiz:>15,.2f} TL")
    satirlar.append(f"Efektif yıllık oran   : {sonuc.efektif_yillik_oran * 100:>15.2f} %")
    return "\n".join(satirlar)


def amortisman_tablosu_raporu(
    sonuc: AmortismanSonucu, sadece_yil_sonu: bool = False
) -> str:
    """Ödeme planı. Uzun vadelerde `sadece_yil_sonu=True` işe yarar."""
    baslik = (
        "AMORTİSMAN TABLOSU (yıl sonları)"
        if sadece_yil_sonu
        else "AMORTİSMAN TABLOSU"
    )
    satirlar = _baslik(baslik)
    satirlar.append(
        f"{'DÖNEM':>5} {'TAKSİT':>15} {'FAİZ':>15} {'ANAPARA':>15} "
        f"{'KALAN BORÇ':>18}"
    )
    satirlar.append("-" * GENISLIK)

    gosterilecek = yil_sonu_taksitleri(sonuc) if sadece_yil_sonu else sonuc.plan

    for s in gosterilecek:
        satirlar.append(
            f"{s.donem:>5} "
            f"{s.taksit:>15,.2f} "
            f"{s.faiz_payi:>15,.2f} "
            f"{s.anapara_payi:>15,.2f} "
            f"{s.kalan_borc:>18,.2f}"
        )

    return "\n".join(satirlar)
