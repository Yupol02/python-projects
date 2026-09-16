def para_yatirma():
    try:
        tutar = int(input("Yatırmak istediğiniz tutarı giriniz: "))
    except ValueError:
        print("Lütfen sadece rakam giriniz.")
        return 0

    if tutar <= 0:
        print("Geçersiz tutar: sıfır veya negatif bir miktar yatırılamaz.")
        return 0

    print(f"{tutar} TL yatırıldı.")
    return tutar
