import sys

from kredi import odeme_plani
from rapor import kredi_ozeti , odeme_plani_raporu , vergi_raporu
from vergi import vergi_hesapla

def sayi_iste(mesaj:str , en_az : float = 0.0 , tam_sayi : bool = False) ->float:

    while True:
        ham = input(mesaj).strip().replace(",",".")

        try:
            deger = float(ham)
        except ValueError:
            print("-> Lutfen sayi girin (ornek: 250000 veya 24.5)")
            continue

        if deger < en_az:
            print(f" -> Deger en az {en_az:g} olmalı.")
            continue
        if tam_sayi and deger != int(deger):
            print("  -> Bu alan tam sayi olmali (ornek: 12)")
            continue

        return deger


def vergi_akisi() -> None:
    gelir = sayi_iste("Yillik brut gelir (TL): ")
    print()
    print(vergi_raporu(vergi_hesapla(gelir)))


def kredi_akisi() -> None:
    anapara = sayi_iste("Kredi tutari (TL): ", en_az=0.01)
    oran = sayi_iste("Yillik faiz orani (%) [faizsiz icin 0]: ", en_az=0.0)
    vade = int(sayi_iste("Vade (ay): ", en_az=1, tam_sayi=True))

    sonuc = odeme_plani(anapara, oran, vade)
    print()
    print(kredi_ozeti(sonuc))
    print()
    print(odeme_plani_raporu(sonuc))


def demo() -> None:
    """Kabul kriterlerini gosteren hazir ornekler."""
    print(vergi_raporu(vergi_hesapla(300_000)))
    print()
    faizli = odeme_plani(100_000, 24, 12)
    print(kredi_ozeti(faizli))
    print()
    print(odeme_plani_raporu(faizli))
    print()
    faizsiz = odeme_plani(120_000, 0, 12)
    print(kredi_ozeti(faizsiz))


def main() -> None:
    if "--demo" in sys.argv:
        demo()
        return

    print("Kademeli Vergi & Kredi Taksit Hesaplayici")
    print("1) Vergi hesapla")
    print("2) Kredi taksiti hesapla")
    print("3) Ikisi de")

    secim = input("Seciminiz [1/2/3]: ").strip()
    if secim == "1":
        vergi_akisi()
    elif secim == "2":
        kredi_akisi()
    elif secim == "3":
        vergi_akisi()
        print()
        kredi_akisi()
    else:
        print("Gecersiz secim.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nIptal edildi.")

