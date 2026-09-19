"""Kullanıcının yazdığı metni sayıya çevirme kuralları.

Bu modül `input` almaz, `print` etmez — sadece metin alıp sayı döndürür.
Ayrı bir dosyada durmasının nedeni test edilebilirlik: kuralların doğru
çalıştığını kullanıcı arayüzünü taklit etmeden sınayabiliyoruz.
"""

import math
import re

# "120,000" ya da "24.500" gibi girdiler belirsiz: ayraç binlik ayracı da
# olabilir ondalık ayracı da. Türkçe yazan biri 120.000 ile 120 bin, İngilizce
# yazan biri aynı metinle 120,0 kastediyor olabilir.
#
# Tam sayı kısmının 1-3 basamak olması ve sıfırla başlamaması şart: binlik
# grubu ne 3 basamağı aşar ne de "0" ile başlar. Bu sayede "0,125" ya da
# "1234,567" belirsiz sayılmıyor — onlar ancak ondalık olabilir.
BELIRSIZ = re.compile(r"[+-]?[1-9][0-9]{0,2}[.,][0-9]{3}")


def metni_sayiya_cevir(metin: str) -> float:
    """Metni sayıya çevirir; belirsiz ya da sonsuz değerleri reddeder.

    Kabul edilenler : "250000", "24.5", "24,5", "1e3", "-3,75"
    Reddedilenler   : "120,000" (belirsiz), "1.234.567" (binlik ayraçlı),
                      "inf", "nan", "1e400", "abc"

    Belirsiz girdiyi tahmin etmek yerine reddetmek bilinçli bir seçim:
    bir finans hesaplayıcısında sessizce 1000 kat yanlış çalışmaktansa
    kullanıcıya sayıyı ayraçsız yazdırmak daha doğru.
    """
    temiz = metin.strip().replace(" ", "")

    if not temiz:
        raise ValueError("Boş bırakmayın; bir sayı yazın (örnek: 250000).")

    if temiz.count(",") + temiz.count(".") > 1:
        raise ValueError(
            "Binlik ayracı kullanmayın; sayıyı ayraçsız yazın "
            "(örnek: 1250000 ya da ondalık için 1250000,5)."
        )

    if BELIRSIZ.fullmatch(temiz):
        raise ValueError(
            f"'{temiz}' belirsiz: ayraç binlik mi ondalık mı belli değil. "
            "Ayraçsız yazın (örnek: 120000)."
        )

    try:
        deger = float(temiz.replace(",", "."))
    except ValueError:
        raise ValueError(
            "Bunu sayı olarak okuyamadım (örnek: 250000 veya 24,5)."
        ) from None

    if not math.isfinite(deger):
        # float("inf"), float("nan") ve taşan "1e400" buraya düşer. Sonsuz
        # ya da NaN bir değer doğrulamalardan geçer (nan ile yapılan her
        # karşılaştırma False döner) ve tabloyu sessizce bozardı.
        raise ValueError("Sonlu bir sayı yazın (örnek: 250000 veya 24,5).")

    return deger
