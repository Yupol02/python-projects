import os
from para_yatir import para_yatirma
from bakiye_ekrani import kullanici_bakiyesi
from para_cek import para_cekme

def clean_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[H\033[J",end ="",flush=True)

def karsilama():
    print("\n")
    print("="*40)
    print("Lütfen yapmak istediğiniz işlemi seçiniz")

def menu():
    bakiye = 0
    islem_gecmisi = []


    while True :
        print("1. Bakiye Görüntüle")
        print("2. Para Yatır")
        print("3. Para Çek")
        print("4. İşlem Geçmişi")
        print("5. Çıkış")

        try:
            option = int(input("Yapacağınız işlemi seçiniz: "))
        except ValueError:
            print("Geçersiz seçim! Lütfen 1-5 arasında bir rakam giriniz.")
            continue

        match option:
            case 1:
                kullanici_bakiyesi(bakiye)
                print("\n")
            case 2:
                yatirilan = para_yatirma()
                bakiye = bakiye + yatirilan
                if yatirilan > 0:
                    islem_gecmisi.append(f"Para Yatırma : +{yatirilan} TL")
                kullanici_bakiyesi(bakiye)
            case 3:
                cekilen = para_cekme(bakiye)
                bakiye = bakiye - cekilen
                if cekilen > 0:
                    islem_gecmisi.append(f"Para Çekme   : -{cekilen} TL")
                kullanici_bakiyesi(bakiye)
            case 4:
                if not islem_gecmisi:
                    print("Henüz işlem yapılmadı.")
                else:
                    print("===== İŞLEM GEÇMİŞİ =====")
                    for kayit in islem_gecmisi:
                        print(kayit)
                    print("=" * 25)
            case 5:
                print("Çıkış Yapılıyor...")
                break
            case _:
                print("Geçersiz seçim! Lütfen 1-5 arasında bir rakam giriniz.")

