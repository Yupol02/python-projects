"""Hesap sonuçlarını taşıyan veri tipleri.

Bu dosya hesap yapmaz; sadece sonucun neye benzediğini tarif eder.
Türetilmiş değerler (toplam faiz, efektif oran ...) `@property` olarak
burada duruyor, böylece aynı çıkarım birden çok yerde tekrarlanmıyor.
"""

from dataclasses import dataclass

from oranlar import donem_adi, efektif_yillik_oran


# --- Bileşik faiz ---

@dataclass(frozen=True)
class BirikimSatiri:
    """Bileşik faiz tablosunun tek bir dönemi."""

    donem: int
    acilis_bakiye: float
    katki: float
    faiz: float
    kapanis_bakiye: float


@dataclass(frozen=True)
class BirikimSonucu:
    anapara: float
    yillik_oran_yuzde: float
    yil: float
    donem_sayisi: int
    donemsel_katki: float
    # tuple, list degil: frozen dataclass'in korumasi ancak boyle tamamlanir
    # (liste alani kalsaydi sonuc.tablo.append(...) turev degerleri bozardi)
    tablo: tuple[BirikimSatiri, ...] = ()

    @property
    def donem_etiketi(self) -> str:
        return donem_adi(self.donem_sayisi)

    @property
    def toplam_donem(self) -> int:
        return len(self.tablo)

    @property
    def son_bakiye(self) -> float:
        return self.tablo[-1].kapanis_bakiye if self.tablo else self.anapara

    @property
    def toplam_katki(self) -> float:
        return self.donemsel_katki * self.toplam_donem

    @property
    def toplam_yatirilan(self) -> float:
        """Cepten çıkan para: başlangıç anaparası + tüm katkılar."""
        return self.anapara + self.toplam_katki

    @property
    def toplam_faiz(self) -> float:
        """Faizin kazandırdığı kısım: bakiyenin yatırılan parayı aşan bölümü."""
        return self.son_bakiye - self.toplam_yatirilan

    @property
    def efektif_yillik_oran(self) -> float:
        return efektif_yillik_oran(self.yillik_oran_yuzde, self.donem_sayisi)


# --- Amortisman ---

@dataclass(frozen=True)
class TaksitSatiri:
    """Amortisman tablosunun tek bir dönemi."""

    donem: int
    taksit: float
    faiz_payi: float
    anapara_payi: float
    kalan_borc: float


@dataclass(frozen=True)
class AmortismanSonucu:
    anapara: float
    yillik_oran_yuzde: float
    yil: float
    donem_sayisi: int
    donemsel_taksit: float
    plan: tuple[TaksitSatiri, ...] = ()

    @property
    def donem_etiketi(self) -> str:
        return donem_adi(self.donem_sayisi)

    @property
    def vade_donem(self) -> int:
        return len(self.plan)

    @property
    def toplam_odeme(self) -> float:
        """Plandaki taksitlerin toplamı.

        `donemsel_taksit * vade_donem` demiyoruz: satırdaki taksit
        `faiz_payı + anapara_payı` toplamından yazıldığı için sabit
        annüite taksitinden kıl payı sapabilir. Toplamı satırlardan
        okumak, özet ile tablonun aynı sayıyı göstermesini garanti eder.
        """
        return sum(satir.taksit for satir in self.plan)

    @property
    def toplam_faiz(self) -> float:
        return self.toplam_odeme - self.anapara

    @property
    def efektif_yillik_oran(self) -> float:
        return efektif_yillik_oran(self.yillik_oran_yuzde, self.donem_sayisi)
