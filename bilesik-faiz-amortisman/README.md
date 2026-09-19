# Bileşik Faiz & Amortisman Tablosu

Aynı madalyonun iki yüzü: bileşik faizle **büyüyen** bir birikim ve annüite
taksitleriyle **eriyen** bir borç. İkisi de dönem dönem tablo hâlinde çıkarılıyor.

## Gereksinimler

- Python 3.10 veya üzeri (`float | None` tip yazımı kullanıldığı için)
- Testler için: `pip install pytest`

## Çalıştırma

```bash
python3 main.py          # etkileşimli
python3 main.py --demo   # hazır örnekler
pytest -v                # 44 test
```

## Dosya yapısı ve neden böyle bölündü

| Dosya | Sorumluluk | Kural |
|---|---|---|
| `oranlar.py` | Oran dönüşümleri, ortak doğrulamalar | İki hesap modülünün de dayandığı temel |
| `faiz_modelleri.py` | Veri tipleri | Hesap yapmaz |
| `bilesik_faiz.py` | Birikim tablosu + kapalı formül | Ekrana yazmaz |
| `amortisman.py` | Annüite taksiti + ödeme planı | Ekrana yazmaz |
| `girdi.py` | Metni sayıya çevirme kuralları | `input` almaz, `print` etmez |
| `faiz_raporu.py` | Metne çevirme | Hesap yapmaz, `print` etmez — string döndürür |
| `main.py` | Kullanıcı etkileşimi, arayüz sınırları | Tek `print` ve `input` yeri |
| `test_faiz_hesaplari.py` | Testler | Sadece hesap, girdi ve rapor katmanlarını çağırır |

Bu ayrıma **katman ayrımı** deniyor. `faiz_raporu.py` string döndürdüğü için
çıktının kendisi de test edilebiliyor (`test_kriter4_*`, `test_tablo_sutunlari_*`);
`print` etseydi edemezdik. Aynı gerekçeyle metni sayıya çeviren kurallar
`girdi.py`ye ayrıldı: arayüzü taklit etmeden sınanabiliyorlar.

Oran dönüşümü ve süre doğrulaması `oranlar.py`de tek bir yerde duruyor. İki
modülde ayrı ayrı yazılsaydı biri düzeltilip diğeri unutulabilirdi.

Dosya adlarındaki `faiz_` öneki tesadüf değil: bu depodaki
[vergi-kredi-hesaplayici](../vergi-kredi-hesaplayici) projesinde de `modeller.py`
ve `rapor.py` var. `pytest` depo kökünden çalıştırıldığında her iki klasör de
`sys.path`e ekleniyor, aynı adlı modüller çakışıyor ve toplama aşaması hata
veriyor. Benzersiz adlar bu çakışmayı önlüyor.

## Kabul kriterleri ve kanıtları

| Kriter | Test | Kanıt |
|---|---|---|
| Tablo ile formül aynı sonucu verir | `test_kriter1_tablo_ve_kapali_formul_ayni_sonucu_verir` | 6 farklı senaryoda döngü ve kapalı formül karşılaştırılıyor |
| Borç tam kapanır | `test_kriter2_amortismanda_borc_tam_kapanir` | Son kalan borç tam `0.0`, anapara payları toplamı tam anaparaya eşit |
| Sıfır faizde çökmüyor | `test_kriter3_sifir_faizde_cokmuyor` | 120.000 / %0 / 12 taksit → tam 10.000; birikimde faiz tam 0 |
| Her dönem ayrı satırda | `test_kriter4_her_donem_ayri_satirda` | 12 taksit → 12 satır, 8 dönem → 8 satır |

## Formüller

### Dönemsel oran

Yıllık yüzde, önce dönemsel ondalık orana çevrilir:

```
i = yıllık_yüzde / 100 / yıldaki_dönem_sayısı
```

%24 yıllık, aylık bileşiklemede `i = 24 / 100 / 12 = 0,02`. Yüzdeyi 100'e
bölmeyi ya da yıllık oranı döneme bölmeyi unutmak bu hesaplarda en sık
yapılan hata.

### Efektif yıllık oran

Bileşikleme sıklaştıkça yıl sonundaki gerçek getiri, yazan orandan büyür:

```
efektif = (1 + i)^m - 1        # m = yıldaki dönem sayısı
```

10.000 TL, %30 nominal, 1 yıl:

| Bileşikleme | Son bakiye | Efektif oran |
|---|---:|---:|
| yıllık | 13.000,00 | %30,00 |
| altı aylık | 13.225,00 | %32,25 |
| üç aylık | 13.354,69 | %33,55 |
| aylık | 13.448,89 | %34,49 |

### Bileşik faiz (gelecek değer)

```
GD = P × (1 + i)^n  +  K × ((1 + i)^n - 1) / i
```

`P` anapara, `K` her dönem eklenen tutar, `n` toplam dönem sayısı. Katkılar
**dönem sonunda** yatırılır; yani bir dönemde eklenen para o döneme faiz
kazandırmaz.

`i = 0` iken ikinci terimin paydası sıfır olur. Doğru davranış hata fırlatmak
değil, `P + K × n` döndürmek — faiz yoksa para sadece birikir.

10.000 TL başlangıç + ayda 500 TL, %30, 2 yıl:

```
Toplam yatırılan :  22.000,00 TL   (10.000 + 24 × 500)
Toplam faiz      :  12.261,78 TL
Son bakiye       :  34.261,78 TL
```

Aynı sonuç iki bağımsız yoldan üretiliyor: `gelecek_deger()` yukarıdaki
formülü tek satırda uygularken `bilesik_faiz_tablosu()` dönem dönem ilerliyor.
Testte ikisi karşılaştırılıyor, biri bozulursa diğeri yakalıyor.

### Annüite taksiti

```
taksit = P × i / (1 - (1 + i)^-n)
```

`i = 0` iken payda `1 - 1 = 0` olur → `ZeroDivisionError`. Burada da doğru
davranış hata vermek değil, `P / n` döndürmek.

### Amortisman tablosu

Her dönemde önce faiz işler, taksitin artanı anaparadan düşülür:

```
faiz_payı    = kalan_borç × i
anapara_payı = taksit - faiz_payı
kalan_borç  -= anapara_payı
```

1.000 TL, %10, 3 yıl, yıllık taksit (taksit = 402,11 TL):

| Dönem | Taksit | Faiz | Anapara | Kalan borç |
|---:|---:|---:|---:|---:|
| 1 | 402,11 | 100,00 | 302,11 | 697,89 |
| 2 | 402,11 | 69,79 | 332,33 | 365,56 |
| 3 | 402,11 | 36,56 | 365,56 | 0,00 |

Taksit sabit kalırken faiz payı düşüyor, anapara payı artıyor — çünkü faiz
her dönem küçülen bakiyeden hesaplanıyor.

### Kalan borç neden formülden okunuyor?

Yukarıdaki üç satır, tabloyu kurmanın en doğal yolu gibi görünüyor: bakiyeyi
her dönem `kalan -= anapara_payı` diye azalt. Ama bu **birikimli bir hataya**
açık. Faiz oranı yükselip vade uzadıkça `taksit` ile `faiz_payı` birbirine
öyle yaklaşır ki farkları kayan noktalı aritmetikte tamamen kaybolur — buna
*catastrophic cancellation* deniyor. O noktadan sonra `anapara_payı` sıfıra
yuvarlanır, bakiye hiç azalmaz ve tablo hata vermeden tamamen yanlış sayılar
gösterir.

Somut örnek — 1.000.000 TL, %200, 20 yıl, aylık:

| | Toplam geri ödeme |
|---|---:|
| Birikimli çıkarmayla | 41.000.000,00 |
| Doğrusu (`Decimal` ile kontrol edildi) | 40.000.000,00 |

Bir milyon TL fazla faiz, hiçbir uyarı olmadan. Bu yüzden `kalan_bakiye()`
bakiyeyi doğrudan formülden okuyor:

```
kalan_k = taksit × (1 - (1 + i)^-(n - k)) / i
```

Anapara payı da iki bakiyenin farkı olarak çıkarılıyor. Sonuç matematiksel
olarak aynı, ama hata birikmiyor. `test_yuksek_oran_uzun_vadede_toplam_odeme_sapmiyor`
bu durumu sabitliyor.

Satırdaki `TAKSİT` sütunu da sabit annüite taksitinden değil,
`faiz_payı + anapara_payı` toplamından yazılıyor. Aksi hâlde anapara payı
bakiye farkından, taksit ise formülden geldiği için ikisi kuruş düzeyinde
ayrışıp satırın kendi içinde tutmadığı durumlar çıkıyordu. Fark gerçekçi
girdilerde kuruşun çok altında kalır; özetteki `Dönemsel taksit` yine sabit
annüite taksitidir.

`toplam_odeme` de bu yüzden `taksit × dönem_sayısı` değil **plandaki
taksitlerin toplamı** olarak hesaplanıyor — özet ile tablo her zaman aynı
sayıyı gösteriyor.

### Yıl neden dönemlere tam bölünmeli?

1,5 yıl aylık bileşiklemede 18 dönem eder ama yıllık bileşiklemede 1,5 dönem
eder — böyle bir şey yok. `toplam_donem()` bu durumu sessizce yuvarlamak yerine
`ValueError` fırlatıyor:

```
1.5 yıl, yıllık dönemlere tam bölünmüyor (1.5000 dönem çıkıyor).
Süreyi ya da dönem sayısını değiştirin.
```

### Girdide belirsizlik: "120,000" ne demek?

Program Türkçe soru soruyor ama sayıları `1,234.56` biçiminde yazdırıyor.
Kullanıcının ekranda gördüğü tutarı geri yazması çok doğal — ve tam burada
bir tuzak var:

```python
ham = input(mesaj).replace(",", ".")   # "120,000" -> "120.000" -> 120.0
```

Uyarı yok, tekrar sorulmuyor: hesap 120.000 TL yerine 120 TL ile yapılıyor.
Bir finans hesaplayıcısında sessiz 1000 kat hata, hata mesajından çok daha
kötü.

`girdi.metni_sayiya_cevir()` bu yüzden tahmin etmiyor, **reddediyor**:

| Girdi | Sonuç |
|---|---|
| `250000`, `24,5`, `24.5`, `1e3` | kabul |
| `120,000`, `120.000` | reddedilir — ayraç binlik mi ondalık mı belli değil |
| `1.234.567` | reddedilir — binlik ayracı |
| `inf`, `nan`, `1e400` | reddedilir — sonlu değil |

Son satır ayrı bir tuzak: `float("nan")` başarıyla çalışır ve `nan` bütün
`<` / `>` karşılaştırmalarından geçer (NaN ile yapılan her karşılaştırma
`False` döner). Doğrulama ağından sızan bir `nan`, "kalan borç 0,00" yazan
ama diğer tüm sütunları `nan` olan bir tablo üretiyordu. Bu yüzden
doğrulamalar `deger < en_az` yerine `oranlar.sonlu_ve_en_az()` yardımcısından
geçiyor.

### Sınırlar neden hesap katmanında değil, `main.py`de?

`main.py` üç sabit tanımlıyor:

| Sabit | Değer | Neden var |
|---|---:|---|
| `EN_UZUN_SURE_YIL` | 100 | Fazladan bir sıfır (100000 yıl, aylık) milyonlarca satır üretip belleği tüketirdi |
| `EN_YUKSEK_ORAN_YUZDE` | 1.000 | Astronomik bir oran `(1 + i)^n` ifadesini taşırıp `OverflowError` verirdi — `ValueError` olmadığı için kullanıcıya ham traceback olarak yansıyordu |
| `UZUN_TABLO_SINIRI` | 36 | Bu sayıdan uzun tablolar satır satır değil, yıl sonları hâlinde gösterilir |

Hepsi **arayüz kararı**, hesap kuralı değil. `bilesik_faiz_tablosu()` ya da
`amortisman_tablosu()` doğrudan çağrıldığında bu sınırlar yok: kütüphane
katmanı ne kadar uzun bir tablo isterseniz onu üretir. Sınırlar, yanlışlıkla
fazladan basılan bir tuşun programı kullanılmaz hâle getirmesini engellemek
için arayüzde duruyor.

Uzun tablolarda hem birikim hem amortisman raporu aynı seçeneği sunuyor:

```python
birikim_tablosu(sonuc, sadece_yil_sonu=True)
amortisman_tablosu_raporu(sonuc, sadece_yil_sonu=True)
```
