from modeller import KrediSonucu, TaksitSatiri

EPSILON = 1e-12

def aylik_oran(yillik_oran_yuzde: float) -> float:

    return yillik_oran_yuzde / 100 / 12


def aylik_taksit(
        anapara: float, yillik_oran_yuzde: float, vade_ay: int
) -> float:

    if anapara <= 0:
        raise ValueError(f"Anapara pozitif olmali, gelen: {anapara}")
    if vade_ay <= 0:
        raise ValueError(f"Vade en az 1 ay olmali, gelen: {vade_ay}")
    if yillik_oran_yuzde < 0:
        raise ValueError(
            f"Faiz orani negatif olamaz, gelen: {yillik_oran_yuzde}"
        )

    i = aylik_oran(yillik_oran_yuzde)

    if abs(i) < EPSILON:
        return anapara / vade_ay

    payda = 1 - (1 + i) ** (-vade_ay)
    return anapara * i / payda


def odeme_plani(
        anapara: float, yillik_oran_yuzde: float, vade_ay: int
) -> KrediSonucu:
    taksit = aylik_taksit(anapara, yillik_oran_yuzde, vade_ay)
    i = aylik_oran(yillik_oran_yuzde)

    plan: list[TaksitSatiri] = []
    kalan = anapara

    for ay in range(1, vade_ay + 1):
        faiz_payi = kalan * i
        anapara_payi = taksit - faiz_payi
        kalan -= anapara_payi

        if ay == vade_ay:
            kalan = 0.0

        plan.append(
            TaksitSatiri(
                ay=ay,
                taksit=taksit,
                faiz_payi=faiz_payi,
                anapara_payi=anapara_payi,
                kalan_borc=kalan,
            )
        )

    return KrediSonucu(
        anapara=anapara,
        yillik_oran_yuzde=yillik_oran_yuzde,
        vade_ay=vade_ay,
        aylik_taksit=taksit,
        plan=plan,
    )