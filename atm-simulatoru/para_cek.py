
def para_cekme(bakiye: int):
    try:
        tutar = int(input("Çekmek İstediğiniz Tutarı Giriniz: "))
    except ValueError:
        print("Lütfen sadece rakam giriniz.")
        return 0

    if tutar <= 0:
        print("Geçersiz tutar: sıfır veya negatif bir miktar çekilemez.")
        return 0

    if tutar > bakiye:
        print(f"Yetersiz bakiye! İstenen: {tutar} TL, mevcut bakiye: {bakiye} TL")
        return 0

    print(f"{tutar} TL çekildi.")
    return tutar