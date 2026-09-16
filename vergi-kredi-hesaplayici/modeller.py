from dataclasses import dataclass , field

@dataclass(frozen=True)
class Dilim:
    alt : float
    ust : float | None
    oran : float

    @property
    def ust_sinir(self) -> float:
        return float("inf") if self.ust is None else self.ust

    @property
    def etiket(self) ->str:
        ust = "ve üzeri" if self.ust is None else f"- {self.ust:>11,.0f}"
        return f"{self.alt:11,.0f} {ust} "


@dataclass(frozen=True)
class DilimSonucu:

    dilim: Dilim
    matrah : float
    vergi : float


@dataclass(frozen=True)
class VergiSonucu:

    gelir : float
    dokum : list[DilimSonucu]
    toplam_vergi : float

    @property
    def efektif_oran(self)->float:
        if self.gelir == 0:
            return 0.0
        return self.toplam_vergi / self.gelir

    @property
    def net_gelir(self)->float:
        return self.gelir - self.toplam_vergi

@dataclass(frozen=True)
class TaksitSatiri:

    ay :  int
    taksit : float
    faiz_payi : float
    anapara_payi : float
    kalan_borc : float


@dataclass(frozen=True)
class KrediSonucu:
    anapara : float
    yillik_oran_yuzde: float
    vade_ay : int
    aylik_taksit : float
    plan : list[TaksitSatiri] = field(default_factory=list)

    @property
    def toplam_odeme(self) -> float:
        return self.aylik_taksit * self.vade_ay

    @property
    def toplam_faiz(self) -> float:
        return self.toplam_odeme - self.anapara

VARSAYILAN_DILIMLER : list[Dilim] = [
    Dilim(alt=0 , ust=100_000 , oran=0.15),
    Dilim(alt=100_000 , ust=250_000 , oran=0.20),
    Dilim(alt=250_000, ust=None, oran=0.27)
]