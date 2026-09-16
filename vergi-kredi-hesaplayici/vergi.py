from modeller import VARSAYILAN_DILIMLER , Dilim , DilimSonucu , VergiSonucu

def dilimleri_dogrula(dilimler : list[Dilim]) -> None:

    if not dilimler:
        raise ValueError("Vergi Dilimi Listesi Boş Olamaz.")

    for i,d in enumerate(dilimler):
        if d.oran < 0 or d.oran > 1:
            raise ValueError(
                f"{i}. dilimin oranı 0 ile 1 arasında olmalı, gelen: {d.oran}"
            )
        if d.ust is not None and d.ust <= d.alt :
            raise ValueError(
                f"{i}. diliminin üst sınırı ({d.ust}) alt sinirindan ({d.alt}) büyük olmalı "
            )


    for onceki,sonraki in zip(dilimler,dilimler[1:]):
        if onceki.ust is None:
            raise ValueError("Ucu acik dilim (ust=None) sadece en sonda olabilir.")
        if onceki.ust != sonraki.alt:
            raise  ValueError(
                f"Dilimler surekli degil: {onceki.ust} bitiyor, {sonraki.alt} basliyor "
            )

    if dilimler[0].alt !=0:
        raise ValueError("Ilk dilim 0'dan baslamali.")

def vergi_hesapla(
        gelir : float, dilimler : list[Dilim] | None = None
) -> VergiSonucu:
    if dilimler is None :
        dilimler = VARSAYILAN_DILIMLER

    if gelir < 0 :
        raise ValueError(f"Gelir negatif olamaz, gelen: {gelir}")

    dilimleri_dogrula(dilimler)

    dokum: list[DilimSonucu] = []
    toplam = 0.0

    for dilim  in dilimler :
        matrah =max(0.0,min(gelir,dilim.ust_sinir) - dilim.alt )

        if matrah == 0 :
            break

        dilim_vergisi = matrah * dilim.oran
        dokum.append(DilimSonucu(dilim = dilim , matrah = matrah , vergi = dilim_vergisi ))
        toplam += dilim_vergisi

    return VergiSonucu(gelir=gelir, dokum=dokum, toplam_vergi=toplam)