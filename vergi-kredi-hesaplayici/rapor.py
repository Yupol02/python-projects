from modeller import KrediSonucu , VergiSonucu

GENISLIK = 74

def _baslik(metin:str)-> list[str]:
    return ["=" * GENISLIK, metin.center(GENISLIK), "=" * GENISLIK]

def vergi_raporu(sonuc:VergiSonucu) ->str:
    satirlar = _baslik("GELİR VERGİSİ DOKUMU")
    satirlar.append(f"brut gelir :  {sonuc.gelir:>15,.2f} TL")
    satirlar.append("-" * GENISLIK )

    if not sonuc.dokum:
        satirlar.append("(vergilendirilecek gelir yok)")

    else :
        satirlar.append(
            f"{'DILIM':<28}{'MATRAH':>16}{'ORAN':>8}{'VERGI':>16}"
        )

        for kalem in sonuc.dokum:
            satirlar.append(
                f"{kalem.dilim.etiket:<28}"
                f"{kalem.matrah:>16,.2f}"
                f"{kalem.dilim.oran * 100:>7.0f}%"
                f"{kalem.vergi:>16,.2f}"
            )

    satirlar.append("-" * GENISLIK)
    satirlar.append(f"Toplam vergi          : {sonuc.toplam_vergi:>15,.2f} TL")
    satirlar.append(f"Efektif vergi orani   : {sonuc.efektif_oran * 100:>15.2f} %")
    satirlar.append(f"Net gelir             : {sonuc.net_gelir:>15,.2f} TL")
    return "\n".join(satirlar)


def kredi_ozeti(sonuc: KrediSonucu) -> str:
    faiz_etiketi = (
        "0 (faizsiz)"
        if sonuc.yillik_oran_yuzde == 0
        else f"{sonuc.yillik_oran_yuzde:,.2f} %"
    )
    satirlar = _baslik("KREDI OZETI")
    satirlar.append(f"Anapara               : {sonuc.anapara:>15,.2f} TL")
    satirlar.append(f"Yillik faiz           : {faiz_etiketi:>15}")
    satirlar.append(f"Vade                  : {sonuc.vade_ay:>15} ay")
    satirlar.append("-" * GENISLIK)
    satirlar.append(f"Aylik taksit          : {sonuc.aylik_taksit:>15,.2f} TL")
    satirlar.append(f"Toplam geri odeme     : {sonuc.toplam_odeme:>15,.2f} TL")
    satirlar.append(f"Toplam faiz           : {sonuc.toplam_faiz:>15,.2f} TL")
    return "\n".join(satirlar)


def odeme_plani_raporu(sonuc: KrediSonucu) -> str:
    satirlar = _baslik("ODEME PLANI")
    satirlar.append(
        f"{'AY':>4}{'TAKSIT':>16}{'FAIZ':>16}{'ANAPARA':>16}{'KALAN':>16}"
    )
    satirlar.append("-" * GENISLIK)
    for s in sonuc.plan:
        satirlar.append(
            f"{s.ay:>4}"
            f"{s.taksit:>16,.2f}"
            f"{s.faiz_payi:>16,.2f}"
            f"{s.anapara_payi:>16,.2f}"
            f"{s.kalan_borc:>16,.2f}"
        )
    return "\n".join(satirlar)
