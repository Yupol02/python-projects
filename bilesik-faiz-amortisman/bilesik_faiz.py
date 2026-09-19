"""Bileşik faiz: paranın dönem dönem büyümesi.

Bu modül ekrana hiçbir şey yazmaz; sadece hesaplar ve sonuç nesnesi döndürür.
Yazdırma işi `faiz_raporu.py` ile `main.py`ye ait.

Katkılar **dönem sonunda** yatırılır (finansta "ordinary annuity"). Yani bir
dönemde yatırılan para o döneme faiz kazandırmaz, faizi bir sonraki dönemde
işlemeye başlar.
"""

from faiz_modelleri import BirikimSatiri, BirikimSonucu
from oranlar import EPSILON, donemsel_oran, sonlu_ve_en_az, toplam_donem


def anapara_dogrula(anapara: float) -> None:
    if not sonlu_ve_en_az(anapara, 0):
        raise ValueError(
            f"Anapara 0 veya daha büyük sonlu bir sayı olmalı, gelen: {anapara}"
        )


def katki_dogrula(donemsel_katki: float) -> None:
    if not sonlu_ve_en_az(donemsel_katki, 0):
        raise ValueError(
            f"Dönemsel katkı 0 veya daha büyük sonlu bir sayı olmalı, "
            f"gelen: {donemsel_katki}"
        )


def gelecek_deger(
    anapara: float,
    yillik_oran_yuzde: float,
    yil: float,
    donem_sayisi: int = 12,
    donemsel_katki: float = 0.0,
) -> float:
    """Kapalı formülle son bakiye — tablo kurmadan, tek satırda.

        GD = P × (1 + i)^n  +  K × ((1 + i)^n - 1) / i

    `i = 0` iken ikinci terimin paydası sıfır olur. Doğru davranış hata
    fırlatmak değil: faiz yoksa para sadece birikir, yani `P + K × n`.

    Bu fonksiyon `bilesik_faiz_tablosu` ile aynı sonucu vermek zorunda.
    Testlerde ikisi karşılaştırılıyor: biri bozulursa diğeri yakalar.
    """
    anapara_dogrula(anapara)
    katki_dogrula(donemsel_katki)

    i = donemsel_oran(yillik_oran_yuzde, donem_sayisi)
    n = toplam_donem(yil, donem_sayisi)

    if abs(i) < EPSILON:
        return anapara + donemsel_katki * n

    buyume = (1 + i) ** n
    return anapara * buyume + donemsel_katki * (buyume - 1) / i


def bilesik_faiz_tablosu(
    anapara: float,
    yillik_oran_yuzde: float,
    yil: float,
    donem_sayisi: int = 12,
    donemsel_katki: float = 0.0,
) -> BirikimSonucu:
    """Dönem dönem ilerleyerek birikim tablosunu kurar."""
    anapara_dogrula(anapara)
    katki_dogrula(donemsel_katki)

    i = donemsel_oran(yillik_oran_yuzde, donem_sayisi)
    n = toplam_donem(yil, donem_sayisi)

    tablo: list[BirikimSatiri] = []
    bakiye = float(anapara)

    for donem in range(1, n + 1):
        acilis = bakiye
        faiz = acilis * i
        bakiye = acilis + faiz + donemsel_katki

        tablo.append(
            BirikimSatiri(
                donem=donem,
                acilis_bakiye=acilis,
                katki=donemsel_katki,
                faiz=faiz,
                kapanis_bakiye=bakiye,
            )
        )

    return BirikimSonucu(
        anapara=anapara,
        yillik_oran_yuzde=yillik_oran_yuzde,
        yil=yil,
        donem_sayisi=donem_sayisi,
        donemsel_katki=donemsel_katki,
        tablo=tuple(tablo),
    )


def yil_sonu_satirlari(sonuc: BirikimSonucu) -> list[BirikimSatiri]:
    """Sadece yıl kapanışlarına denk gelen satırlar.

    30 yıllık aylık bir birikimde tablo 360 satır olur; ekrana 30 satır
    basmak için bu süzgeç kullanılıyor. Süre tam yıl değilse son dönem
    her hâlükârda listeye girer, yoksa tablonun sonu görünmez.
    """
    satirlar = [
        satir
        for satir in sonuc.tablo
        if satir.donem % sonuc.donem_sayisi == 0
    ]

    if sonuc.tablo and (not satirlar or satirlar[-1] is not sonuc.tablo[-1]):
        satirlar.append(sonuc.tablo[-1])

    return satirlar
