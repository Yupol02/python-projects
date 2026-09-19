"""Kullanıcı etkileşimi: girdi alma ve ekrana yazma.

Projedeki tek `print` ve `input` yeri burası. Hesap, biçimlendirme ve
metni sayıya çevirme diğer modüllerde durduğu için bu dosya yalnızca
akışı yönetir.

Çalıştırma:
    python3 main.py          # etkileşimli
    python3 main.py --demo   # hazır örnekler
"""

import sys

from amortisman import amortisman_tablosu
from bilesik_faiz import bilesik_faiz_tablosu
from faiz_raporu import (
    amortisman_ozeti,
    amortisman_tablosu_raporu,
    birikim_ozeti,
    birikim_tablosu,
)
from girdi import metni_sayiya_cevir
from oranlar import DONEM_ADLARI, toplam_donem

# Menüde gösterilecek bileşikleme sıklıkları
SIKLIKLAR: list[int] = [1, 2, 4, 12]

# Süre üst sınırı. Fazladan bir sıfır (100000 yıl, aylık) milyonlarca satır
# üretip belleği tüketirdi; hesap katmanının böyle bir sınırı yok, olması da
# gerekmiyor — sınır kullanıcı arayüzüne ait bir karar.
EN_UZUN_SURE_YIL = 100

# Faiz oranı üst sınırı. Astronomik bir oran (%1e30) `(1 + i) ** n` ifadesini
# taşırıp OverflowError verirdi; bu da ValueError olmadığı için kullanıcıya
# ham traceback olarak yansıyordu.
EN_YUKSEK_ORAN_YUZDE = 1_000

# Tablonun tamamı yerine yıl sonlarını göstermeye geçilen satır sayısı
UZUN_TABLO_SINIRI = 36


def sayi_iste(
    mesaj: str,
    en_az: float = 0.0,
    en_cok: float | None = None,
    tam_sayi: bool = False,
) -> float:
    """Geçerli bir sayı girilene kadar sorar."""
    while True:
        try:
            deger = metni_sayiya_cevir(input(mesaj))
        except ValueError as hata:
            print(f"  -> {hata}")
            continue

        if deger < en_az:
            print(f"  -> Değer en az {en_az:g} olmalı.")
            continue
        if en_cok is not None and deger > en_cok:
            print(f"  -> Değer en çok {en_cok:g} olabilir.")
            continue
        if tam_sayi and deger != int(deger):
            print("  -> Bu alan tam sayı olmalı (örnek: 12)")
            continue

        return deger


def siklik_iste() -> int:
    """Yıldaki dönem sayısını menüden seçtirir."""
    print("Bileşikleme / taksit sıklığı:")
    for sira, adet in enumerate(SIKLIKLAR, start=1):
        print(f"  {sira}) {DONEM_ADLARI[adet]} (yılda {adet})")

    secim = int(
        sayi_iste(
            f"Seçiminiz [1-{len(SIKLIKLAR)}]: ",
            en_az=1,
            en_cok=len(SIKLIKLAR),
            tam_sayi=True,
        )
    )
    return SIKLIKLAR[secim - 1]


def sure_iste(mesaj: str, donem_sayisi: int) -> float:
    """Seçilen sıklığa tam bölünen bir süre girilene kadar sorar.

    "Yıl, dönemlere tam bölünmeli" kuralı `toplam_donem()` içinde ve ancak
    hesap çağrıldığında devreye giriyor. Burada yakalanmasaydı, kullanıcı
    bütün soruları yanıtladıktan sonra program tek bir girdi yüzünden
    kapanırdı; oysa doğrusu aynı soruyu tekrar sormak.
    """
    while True:
        yil = sayi_iste(mesaj, en_az=0.01, en_cok=EN_UZUN_SURE_YIL)

        try:
            toplam_donem(yil, donem_sayisi)
        except ValueError as hata:
            print(f"  -> {hata}")
            continue

        return yil


def bilesik_faiz_akisi() -> None:
    anapara = sayi_iste("Başlangıç anaparası (TL): ")
    oran = sayi_iste(
        "Yıllık faiz oranı (%) [faizsiz için 0]: ",
        en_cok=EN_YUKSEK_ORAN_YUZDE,
    )
    donem_sayisi = siklik_iste()
    yil = sure_iste("Süre (yıl): ", donem_sayisi)
    katki = sayi_iste("Her dönem eklenecek tutar (TL) [yoksa 0]: ")

    sonuc = bilesik_faiz_tablosu(anapara, oran, yil, donem_sayisi, katki)
    uzun = sonuc.toplam_donem > UZUN_TABLO_SINIRI

    print()
    print(birikim_ozeti(sonuc))
    print()
    print(birikim_tablosu(sonuc, sadece_yil_sonu=uzun))

    if uzun:
        print(f"\n({sonuc.toplam_donem} dönemin tamamı yerine yıl sonları gösterildi.)")


def amortisman_akisi() -> None:
    anapara = sayi_iste("Kredi tutarı (TL): ", en_az=0.01)
    oran = sayi_iste(
        "Yıllık faiz oranı (%) [faizsiz için 0]: ",
        en_cok=EN_YUKSEK_ORAN_YUZDE,
    )
    donem_sayisi = siklik_iste()
    yil = sure_iste("Vade (yıl): ", donem_sayisi)

    sonuc = amortisman_tablosu(anapara, oran, yil, donem_sayisi)
    uzun = sonuc.vade_donem > UZUN_TABLO_SINIRI

    print()
    print(amortisman_ozeti(sonuc))
    print()
    print(amortisman_tablosu_raporu(sonuc, sadece_yil_sonu=uzun))

    if uzun:
        print(f"\n({sonuc.vade_donem} taksitin tamamı yerine yıl sonları gösterildi.)")


def demo() -> None:
    """Kabul kriterlerini gösteren hazır örnekler."""
    print("--- 1) 1.000 TL, %10, 3 yıl, yıllık taksit ---\n")
    kredi = amortisman_tablosu(1_000, 10, 3, 1)
    print(amortisman_ozeti(kredi))
    print()
    print(amortisman_tablosu_raporu(kredi))

    print("\n\n--- 2) Faizsiz kredi: 120.000 TL, %0, 1 yıl, aylık ---\n")
    print(amortisman_ozeti(amortisman_tablosu(120_000, 0, 1, 12)))

    print("\n\n--- 3) Birikim: 10.000 TL + ayda 500 TL, %30, 2 yıl ---\n")
    birikim = bilesik_faiz_tablosu(10_000, 30, 2, 12, 500)
    print(birikim_ozeti(birikim))
    print()
    print(birikim_tablosu(birikim, sadece_yil_sonu=True))

    print("\n\n--- 4) Aynı oran, farklı bileşikleme sıklığı ---\n")
    print(f"{'SIKLIK':<12}{'SON BAKİYE':>16}{'EFEKTİF ORAN':>16}")
    print("-" * 44)
    for adet in SIKLIKLAR:
        sonuc = bilesik_faiz_tablosu(10_000, 30, 1, adet)
        print(
            f"{sonuc.donem_etiketi:<12}"
            f"{sonuc.son_bakiye:>16,.2f}"
            f"{sonuc.efektif_yillik_oran * 100:>15.2f}%"
        )


def main() -> None:
    if "--demo" in sys.argv:
        demo()
        return

    print("Bileşik Faiz & Amortisman Tablosu")
    print("1) Bileşik faiz (birikim) tablosu")
    print("2) Amortisman (kredi ödeme planı) tablosu")
    print("3) İkisi de")

    secim = input("Seçiminiz [1/2/3]: ").strip()

    if secim == "1":
        bilesik_faiz_akisi()
    elif secim == "2":
        amortisman_akisi()
    elif secim == "3":
        bilesik_faiz_akisi()
        print()
        amortisman_akisi()
    else:
        print("Geçersiz seçim.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nİptal edildi.")
    except (ValueError, OverflowError) as hata:
        # OverflowError da yakalanıyor: girdi katmanı sonsuz değerleri elese
        # de, çok büyük ama sonlu girdilerin çarpımı hesap sırasında taşabilir.
        print(f"\nHata: {hata}")
