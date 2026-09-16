# Kademeli Vergi \& Kredi Taksit Hesaplayıcı

Gelir dilimlerine göre artan oranlı vergi hesabı + annüite formülüyle eşit aylık taksit.

## Çalıştırma

```bash
python main.py          # etkileşimli
python main.py --demo   # hazır örnekler
pytest -v               # 25 test
```

## Dosya yapısı ve neden böyle bölündü

|Dosya|Sorumluluk|Kural|
|-|-|-|
|`modeller.py`|Veri tipleri|Hesap yapmaz|
|`vergi.py`|Kademeli vergi|Ekrana yazmaz|
|`kredi.py`|Annüite + ödeme planı|Ekrana yazmaz|
|`rapor.py`|Metne çevirme|Hesap yapmaz, `print` etmez — string döndürür|
|`main.py`|Kullanıcı etkileşimi|Tek `print` yeri|

Bu ayrıma **katman ayrımı** denir. Faydası: `rapor.py` string döndürdüğü için çıktıyı da test edebiliyoruz (`test\_kriter3\_\*`). `print` etseydi test edemezdik.

## Kabul kriterleri ve kanıtları

|Kriter|Test|Kanıt|
|-|-|-|
|Dilim dilim vergi|`test\_kriter1\_dilim\_dilim\_hesaplanir`|300.000 → 58.500 (tek oranla 81.000 olurdu)|
|Sıfır faizde çökmüyor|`test\_kriter2\_sifir\_faiz\_cokmuyor`|120.000 / %0 / 12 ay → tam 10.000|
|Her ara sonuç ayrı satırda|`test\_kriter3\_her\_dilim\_ayri\_satirda`|Her dilim + her ay kendi satırında|

## Formüller

**Kademeli vergi** — her dilim için gelirin o dilime düşen kısmı:

```
matrah = max(0, min(gelir, dilim\_üst) - dilim\_alt)
vergi  = matrah × oran
```

300.000 TL örneği:

```
min(300k, 100k) -   0  = 100.000 × %15 = 15.000
min(300k, 250k) - 100k = 150.000 × %20 = 30.000
min(300k, inf)  - 250k =  50.000 × %27 = 13.500
                          Toplam        = 58.500  (efektif %19,5)
```

**Annüite:**

```
taksit = P × i / (1 - (1 + i)^-n)
```

`i` **aylık** orandır: `yıllık\_yüzde / 100 / 12`. Bu bölmeyi unutmak en sık yapılan hata.

`i = 0` iken payda `1 - 1 = 0` olur → `ZeroDivisionError`. Doğru davranış hata fırlatmak değil, `P / n` döndürmek.
