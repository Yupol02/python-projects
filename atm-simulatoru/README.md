# ATM Simülatörü

Python öğrenirken geliştirdiğim, terminal üzerinde çalışan basit bir ATM uygulaması. Bakiye görüntüleme, para yatırma, para çekme ve işlem geçmişi özelliklerini içerir.

## Özellikler

- Bakiye görüntüleme
- Para yatırma
- Para çekme (yetersiz bakiye kontrolü ile)
- İşlem geçmişi (yalnızca başarılı işlemler kaydedilir)
- Girdi doğrulama: harf/sembol girişleri, negatif ve sıfır tutarlar reddedilir

## Gereksinimler

- Python 3.10 veya üzeri (`match-case` yapısı kullanıldığı için)

## Çalıştırma

```bash
python3 main.py
```

## Örnek Kullanım

```
========================================
ATM SİMÜLATÖRÜNE HOŞ GELDİNİZ
========================================

Lütfen yapmak istediğiniz işlemi seçiniz
========================================
1. Bakiye Görüntüle
2. Para Yatır
3. Para Çek
4. İşlem Geçmişi
5. Çıkış
Yapacağınız işlemi seçiniz: 2
Yatırmak istediğiniz tutarı giriniz: 1000
1000 TL yatırıldı.
Güncel bakiyeniz: 1000 TL

Yapacağınız işlemi seçiniz: 3
Çekmek İstediğiniz Tutarı Giriniz: 1500
Yetersiz bakiye! İstenen: 1500 TL, mevcut bakiye: 1000 TL
Güncel bakiyeniz: 1000 TL

Yapacağınız işlemi seçiniz: 3
Çekmek İstediğiniz Tutarı Giriniz: 400
400 TL çekildi.
Güncel bakiyeniz: 600 TL

Yapacağınız işlemi seçiniz: 4
===== İŞLEM GEÇMİŞİ =====
Para Yatırma : +1000 TL
Para Çekme   : -400 TL
=========================
```

## Proje Yapısı

| Dosya | Görevi |
|---|---|
| `main.py` | Programın giriş noktası; karşılama ekranını gösterir ve menüyü başlatır |
| `islemler.py` | Menü döngüsü; bakiye ile işlem geçmişini tutar ve seçimleri ilgili fonksiyona yönlendirir |
| `para_yatir.py` | Para yatırma işlemi ve tutar doğrulaması |
| `para_cek.py` | Para çekme işlemi; tutar doğrulaması ve bakiye yeterlilik kontrolü |
| `bakiye_ekrani.py` | Bakiyeyi ekrana yazdırır |

## Bu Projede Öğrendiklerim

- Fonksiyonlarda `print` (kullanıcıya göstermek) ile `return` (koda değer vermek) arasındaki fark
- Değişken kapsamı (scope): verinin işlemler arasında hayatta kalması için nerede tanımlanması gerektiği
- Döngüsel import (circular import) sorunu ve bağımlılıkların tek yönlü akması gerektiği
- Girdi doğrulama ve "guard clause" (bekçi kontrolü) deseni: işlemden önce kontrol etmek
- `try/except` bloğunu geniş değil, yakalanacak hataya özel (`ValueError`) yazmak
- Listeler ve `for` döngüsüyle koleksiyon üzerinde gezinmek

## Yapılacaklar

- [ ] Bakiye ve işlem geçmişinin dosyaya kaydedilmesi (kalıcılık)
- [ ] İşlem kayıtlarına tarih/saat bilgisi eklenmesi
- [ ] Hesap yapısının sınıf (class) ile modellenmesi
- [ ] PIN doğrulaması ve çoklu kullanıcı desteği
