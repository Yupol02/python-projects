"""Kademeli vergi ve kredi taksit hesaplarının testleri.

Çalıştırmak için: pytest -v
"""

import pytest

from kredi import aylik_oran, aylik_taksit, odeme_plani
from modeller import Dilim
from rapor import kredi_ozeti, odeme_plani_raporu, vergi_raporu
from vergi import dilimleri_dogrula, vergi_hesapla


# --- Kabul kriterleri ---

def test_kriter1_dilim_dilim_hesaplanir():
    sonuc = vergi_hesapla(300_000)

    assert sonuc.toplam_vergi == pytest.approx(58_500.0)
    assert [kalem.vergi for kalem in sonuc.dokum] == pytest.approx(
        [15_000.0, 30_000.0, 13_500.0]
    )


def test_kriter2_sifir_faiz_cokmuyor():
    sonuc = odeme_plani(120_000, 0, 12)

    assert sonuc.aylik_taksit == pytest.approx(10_000.0)
    assert sonuc.toplam_faiz == pytest.approx(0.0)


def test_kriter3_her_dilim_ayri_satirda():
    satirlar = vergi_raporu(vergi_hesapla(300_000)).splitlines()
    beklenen = [
        ("100,000.00", "15,000.00"),
        ("150,000.00", "30,000.00"),
        ("50,000.00", "13,500.00"),
    ]

    for matrah, vergi in beklenen:
        eslesen = [s for s in satirlar if matrah in s and vergi in s]
        assert len(eslesen) == 1


def test_odeme_plani_her_ay_ayri_satirda():
    satirlar = odeme_plani_raporu(odeme_plani(120_000, 0, 12)).splitlines()
    ay_satirlari = [s for s in satirlar if s.split() and s.split()[0].isdigit()]

    assert len(ay_satirlari) == 12


# --- Vergi hesabı ---

def test_gelir_sifirken_dokum_bos_olur():
    sonuc = vergi_hesapla(0)

    assert sonuc.dokum == []
    assert sonuc.toplam_vergi == 0.0
    assert sonuc.efektif_oran == 0.0


def test_ilk_dilimde_kalan_gelir_tek_satir_uretir():
    sonuc = vergi_hesapla(50_000)

    assert len(sonuc.dokum) == 1
    assert sonuc.toplam_vergi == pytest.approx(7_500.0)


def test_negatif_gelir_hata_verir():
    with pytest.raises(ValueError):
        vergi_hesapla(-1)


def test_efektif_oran_ve_net_gelir():
    sonuc = vergi_hesapla(300_000)

    assert sonuc.efektif_oran == pytest.approx(0.195)
    assert sonuc.net_gelir == pytest.approx(241_500.0)


def test_araliksiz_olmayan_dilimler_reddedilir():
    dilimler = [
        Dilim(alt=0, ust=100_000, oran=0.15),
        Dilim(alt=150_000, ust=None, oran=0.20),
    ]

    with pytest.raises(ValueError):
        dilimleri_dogrula(dilimler)


def test_ucu_acik_dilim_sadece_sonda_olabilir():
    dilimler = [
        Dilim(alt=0, ust=None, oran=0.15),
        Dilim(alt=100_000, ust=None, oran=0.20),
    ]

    with pytest.raises(ValueError):
        dilimleri_dogrula(dilimler)


# --- Kredi hesabı ---

def test_aylik_oran_yillik_orandan_hesaplanir():
    assert aylik_oran(24) == pytest.approx(0.02)


def test_faizli_taksit_annuite_formulune_uyar():
    assert aylik_taksit(100_000, 24, 12) == pytest.approx(9_455.96, abs=0.01)


def test_odeme_plani_vade_kadar_satir_uretir():
    sonuc = odeme_plani(100_000, 24, 12)

    assert len(sonuc.plan) == 12
    assert [satir.ay for satir in sonuc.plan] == list(range(1, 13))


def test_son_taksitte_kalan_borc_sifirlanir():
    sonuc = odeme_plani(100_000, 24, 12)

    assert sonuc.plan[-1].kalan_borc == 0.0


def test_anapara_paylari_toplami_anaparaya_esittir():
    sonuc = odeme_plani(100_000, 24, 12)
    toplam_anapara = sum(satir.anapara_payi for satir in sonuc.plan)

    assert toplam_anapara == pytest.approx(100_000.0, abs=0.01)


def test_faizli_kredide_toplam_faiz_pozitiftir():
    sonuc = odeme_plani(100_000, 24, 12)

    assert sonuc.toplam_faiz > 0
    assert sonuc.toplam_odeme == pytest.approx(sonuc.aylik_taksit * 12)


def test_gecersiz_girdiler_hata_verir():
    with pytest.raises(ValueError):
        aylik_taksit(0, 24, 12)

    with pytest.raises(ValueError):
        aylik_taksit(100_000, 24, 0)

    with pytest.raises(ValueError):
        aylik_taksit(100_000, -1, 12)


def test_faizsiz_kredi_ozetinde_etiket_gorunur():
    assert "0 (faizsiz)" in kredi_ozeti(odeme_plani(120_000, 0, 12))
