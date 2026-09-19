"""Oran dönüşümleri ve iki hesap modülünün ortak doğrulamaları.

Bileşik faiz ve amortisman aynı temel üzerine kurulu: yıllık oran önce
dönemsel orana çevrilir, sonra dönem sayısı kadar uygulanır. Bu ortak
kısım tek yerde toplandı ki iki modül birbirinden sapmasın.
"""

import math

# Kayan noktalı sayılarda "sıfır mı?" karşılaştırması için tolerans.
# `oran == 0` yazmak 1e-18 gibi bir değeri sıfır saymaz ve payda patlar.
EPSILON = 1e-12

# Bir yıldaki dönem sayısı -> o dönemin adı
DONEM_ADLARI: dict[int, str] = {
    1: "yıllık",
    2: "altı aylık",
    4: "üç aylık",
    12: "aylık",
    52: "haftalık",
    365: "günlük",
}


def donem_adi(donem_sayisi: int) -> str:
    """Yıldaki dönem sayısını okunabilir bir ada çevirir."""
    return DONEM_ADLARI.get(donem_sayisi, f"yılda {donem_sayisi} dönem")


def donem_sayisi_dogrula(donem_sayisi: int) -> None:
    if not isinstance(donem_sayisi, int) or isinstance(donem_sayisi, bool):
        raise ValueError(
            f"Yıldaki dönem sayısı tam sayı olmalı, gelen: {donem_sayisi!r}"
        )
    if donem_sayisi < 1:
        raise ValueError(
            f"Yıldaki dönem sayısı en az 1 olmalı, gelen: {donem_sayisi}"
        )


def sonlu_ve_en_az(deger: float, en_az: float) -> bool:
    """`deger` sonlu bir sayı ve `en_az`dan küçük değil mi?

    Sadece `deger < en_az` sorulsaydı `nan` ve `inf` doğrulamalardan
    geçerdi: NaN ile yapılan her karşılaştırma False döner, `inf` de
    her alt sınırı aşar. İkisi de hesabı sessizce bozar, o yüzden
    doğrulamalar bu yardımcıdan geçiyor.
    """
    return math.isfinite(deger) and deger >= en_az


def oran_dogrula(yillik_oran_yuzde: float) -> None:
    if not sonlu_ve_en_az(yillik_oran_yuzde, 0):
        raise ValueError(
            f"Faiz oranı 0 veya daha büyük sonlu bir sayı olmalı, gelen: "
            f"{yillik_oran_yuzde}"
        )


def donemsel_oran(yillik_oran_yuzde: float, donem_sayisi: int) -> float:
    """Yıllık yüzdeyi dönemsel ondalık orana çevirir.

    %24 yıllık, ayda bir bileşikleme -> 24 / 100 / 12 = 0.02
    Yüzdeyi 100'e bölmeyi ya da yıllık oranı döneme bölmeyi unutmak
    bu hesaplarda en sık yapılan hata.
    """
    donem_sayisi_dogrula(donem_sayisi)
    oran_dogrula(yillik_oran_yuzde)
    return yillik_oran_yuzde / 100 / donem_sayisi


def efektif_yillik_oran(yillik_oran_yuzde: float, donem_sayisi: int) -> float:
    """Bileşiklemeyi de hesaba katan gerçek yıllık getiri.

    %24 yıllık ama aylık bileşiklenirse yıl sonundaki gerçek artış
    %24 değil (1 + 0.02) ** 12 - 1 = %26,82'dir.
    """
    i = donemsel_oran(yillik_oran_yuzde, donem_sayisi)
    return (1 + i) ** donem_sayisi - 1


def toplam_donem(yil: float, donem_sayisi: int) -> int:
    """Yıl sayısını tam dönem sayısına çevirir.

    `yil` ondalıklı olabilir (0.5 yıl = 6 ay) ama sonuç tam sayı
    olmak zorunda: 1.5 yıl yıllık bileşiklemeyle 1.5 dönem etmez.
    """
    donem_sayisi_dogrula(donem_sayisi)

    if not math.isfinite(yil) or yil <= 0:
        raise ValueError(f"Süre sonlu ve pozitif olmalı, gelen: {yil}")

    ham = yil * donem_sayisi
    # round(), 1.4 * 365 = 510.99999999999994 gibi "tam sayının bir tık
    # altına düşen" çarpımları doğru tarafa yuvarlar; int() kesip atardı.
    yuvarlanmis = round(ham)

    if yuvarlanmis < 1:
        raise ValueError(
            f"Süre en az 1 dönem olmalı, gelen: {yil} yıl ({ham:.6g} dönem)."
        )

    if abs(ham - yuvarlanmis) > 1e-9:
        raise ValueError(
            f"{yil} yıl, {donem_adi(donem_sayisi)} dönemlere tam bölünmüyor "
            f"({ham:.4f} dönem çıkıyor). Süreyi ya da dönem sayısını değiştirin."
        )

    return yuvarlanmis
