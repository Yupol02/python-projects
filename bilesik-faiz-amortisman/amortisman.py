"""Amortisman: sabit taksitli bir borcun dönem dönem eritilmesi.

Bileşik faizin ters yüzü. Orada bakiye faizle büyüyordu; burada bakiye
her dönem faiz kadar büyüyüp taksit kadar küçülüyor, sonunda sıfırlanıyor.

Bu modül de ekrana hiçbir şey yazmaz.
"""

from faiz_modelleri import AmortismanSonucu, TaksitSatiri
from oranlar import EPSILON, donemsel_oran, sonlu_ve_en_az, toplam_donem


def anapara_dogrula(anapara: float) -> None:
    if not sonlu_ve_en_az(anapara, 0) or anapara == 0:
        raise ValueError(
            f"Kredi tutarı pozitif ve sonlu bir sayı olmalı, gelen: {anapara}"
        )


def donemsel_taksit(
    anapara: float,
    yillik_oran_yuzde: float,
    yil: float,
    donem_sayisi: int = 12,
) -> float:
    """Annüite formülüyle sabit taksit tutarı.

        taksit = P × i / (1 - (1 + i)^-n)

    `i = 0` iken payda `1 - 1 = 0` olur ve `ZeroDivisionError` fırlar.
    Doğru davranış hata vermek değil: faizsiz kredide taksit `P / n`.
    """
    anapara_dogrula(anapara)

    i = donemsel_oran(yillik_oran_yuzde, donem_sayisi)
    n = toplam_donem(yil, donem_sayisi)

    if abs(i) < EPSILON:
        return anapara / n

    return anapara * i / (1 - (1 + i) ** -n)


def kalan_bakiye(
    anapara: float, taksit: float, i: float, n: int, odenen_donem: int
) -> float:
    """`odenen_donem` taksit ödendikten sonra geriye kalan borç.

        kalan = taksit × (1 - (1 + i)^-(n - k)) / i

    Bakiyeyi her dönem `kalan -= anapara_payı` diye biriktirmek yerine
    doğrudan formülden okumanın nedeni **birikimli hata**: yüksek oran ile
    uzun vade birleştiğinde `taksit` ile `faiz_payı` birbirine öyle yaklaşır
    ki farkları kayan noktalı aritmetikte tamamen kaybolur (bu olaya
    *catastrophic cancellation* deniyor). O noktadan sonra bakiye hiç
    azalmaz ve tablo, hata vermeden tamamen yanlış sayılar gösterir.
    Formülden okunan bakiyede böyle bir birikim olmuyor.
    """
    if odenen_donem >= n:
        return 0.0

    if abs(i) < EPSILON:
        return anapara * (1 - odenen_donem / n)

    return taksit * (1 - (1 + i) ** -(n - odenen_donem)) / i


def amortisman_tablosu(
    anapara: float,
    yillik_oran_yuzde: float,
    yil: float,
    donem_sayisi: int = 12,
) -> AmortismanSonucu:
    """Her dönem için faiz payı, anapara payı ve kalan borcu hesaplar.

    Her dönemde önce faiz işler, taksitin artanı anaparadan düşülür:

        faiz_payı    = kalan_borç × i
        anapara_payı = taksit - faiz_payı
        kalan_borç  -= anapara_payı

    Kod bunu birebir böyle yazmıyor: kalan borç `kalan_bakiye()` ile
    formülden okunuyor, anapara payı da iki bakiyenin farkı olarak
    çıkarılıyor. Sonuç aynı, ama birikimli yuvarlama hatası olmuyor.

    Satırdaki `taksit` de `faiz_payı + anapara_payı` toplamından yazılıyor,
    sabit `donemsel_taksit` değerinden değil. Böylece her satır kendi içinde
    tam tutuyor; aksi hâlde anapara payı bakiye farkından, taksit ise
    formülden geldiği için ikisi kuruş düzeyinde ayrışabiliyordu. Aradaki
    fark gerçekçi girdilerde kuruşun çok altında kalır — özetteki
    `donemsel_taksit` yine sabit annüite taksitidir.
    """
    taksit = donemsel_taksit(anapara, yillik_oran_yuzde, yil, donem_sayisi)

    i = donemsel_oran(yillik_oran_yuzde, donem_sayisi)
    n = toplam_donem(yil, donem_sayisi)

    plan: list[TaksitSatiri] = []
    kalan = float(anapara)

    for donem in range(1, n + 1):
        faiz_payi = kalan * i
        yeni_kalan = kalan_bakiye(anapara, taksit, i, n, donem)
        anapara_payi = kalan - yeni_kalan

        plan.append(
            TaksitSatiri(
                donem=donem,
                taksit=faiz_payi + anapara_payi,
                faiz_payi=faiz_payi,
                anapara_payi=anapara_payi,
                kalan_borc=yeni_kalan,
            )
        )

        kalan = yeni_kalan

    return AmortismanSonucu(
        anapara=anapara,
        yillik_oran_yuzde=yillik_oran_yuzde,
        yil=yil,
        donem_sayisi=donem_sayisi,
        donemsel_taksit=taksit,
        plan=tuple(plan),
    )


def yil_sonu_taksitleri(sonuc: AmortismanSonucu) -> tuple[TaksitSatiri, ...]:
    """Sadece yıl kapanışlarına denk gelen taksitler.

    `bilesik_faiz.yil_sonu_satirlari()` ile aynı işi görür: 30 yıllık aylık
    bir kredide plan 360 satır olur, ekrana 30 satır basmak için bu süzgeç
    kullanılır. Vade tam yıl değilse son taksit her hâlükârda listeye girer,
    yoksa tablonun sonu görünmez.
    """
    satirlar = [
        satir for satir in sonuc.plan if satir.donem % sonuc.donem_sayisi == 0
    ]

    if sonuc.plan and (not satirlar or satirlar[-1] is not sonuc.plan[-1]):
        satirlar.append(sonuc.plan[-1])

    return tuple(satirlar)
