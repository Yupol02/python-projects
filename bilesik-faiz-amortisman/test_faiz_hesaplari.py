"""Bileşik faiz ve amortisman hesaplarının testleri.

Çalıştırmak için: pytest -v
"""

import subprocess
import sys
from pathlib import Path

import pytest

from amortisman import amortisman_tablosu, donemsel_taksit, yil_sonu_taksitleri
from bilesik_faiz import (
    bilesik_faiz_tablosu,
    gelecek_deger,
    yil_sonu_satirlari,
)
from faiz_modelleri import BirikimSatiri
from faiz_raporu import (
    amortisman_ozeti,
    amortisman_tablosu_raporu,
    birikim_ozeti,
    birikim_tablosu,
)
from girdi import metni_sayiya_cevir
from oranlar import (
    donem_adi,
    donem_sayisi_dogrula,
    donemsel_oran,
    efektif_yillik_oran,
    toplam_donem,
)

PROJE = Path(__file__).parent


def _veri_satirlari(satirlar: list[str]) -> list[str]:
    """Başlık/çizgi satırlarını eleyip sadece veri satırlarını bırakır.

    DÖNEM sütunu her iki tabloda da sabit 6 karakter. İlk 6 karaktere
    bakmak, yanındaki sütun taşıp yapışsa bile satırı doğru sayar;
    `s.split()[0].isdigit()` bu durumda satırı sessizce düşürürdü.
    """
    return [s for s in satirlar if s[:6].strip().isdigit()]


# --- Kabul kriterleri ---

def test_kriter1_tablo_ve_kapali_formul_ayni_sonucu_verir():
    """Birikim iki bağımsız yoldan hesaplanıp karşılaştırılıyor.

    Döngü ile kapalı formül birbirinin kontrolü: biri bozulursa test düşer.
    """
    ornekler = [
        (1_000, 10, 3, 1, 0),
        (10_000, 30, 2, 12, 500),
        (50_000, 7.5, 10, 4, 1_250),
        (0, 20, 5, 12, 1_000),
        (10_000, 0, 2, 12, 500),      # sıfır faiz dalı
        (100_000, 1.0, 1, 12, 0),     # küçük ama gerçek faiz
    ]

    for anapara, oran, yil, donem, katki in ornekler:
        tablo = bilesik_faiz_tablosu(anapara, oran, yil, donem, katki)
        formul = gelecek_deger(anapara, oran, yil, donem, katki)

        assert tablo.son_bakiye == pytest.approx(formul, rel=1e-9)


def test_kriter2_amortismanda_borc_tam_kapanir():
    sonuc = amortisman_tablosu(100_000, 24, 5, 12)
    toplam_anapara = sum(satir.anapara_payi for satir in sonuc.plan)

    assert sonuc.plan[-1].kalan_borc == 0.0
    assert toplam_anapara == pytest.approx(100_000.0, abs=0.01)
    assert sonuc.toplam_odeme == pytest.approx(
        sum(satir.taksit for satir in sonuc.plan)
    )


def test_kriter3_sifir_faizde_cokmuyor():
    kredi = amortisman_tablosu(120_000, 0, 1, 12)
    birikim = bilesik_faiz_tablosu(10_000, 0, 2, 12, 500)

    assert kredi.donemsel_taksit == pytest.approx(10_000.0)
    assert kredi.toplam_faiz == pytest.approx(0.0)
    assert birikim.son_bakiye == pytest.approx(10_000 + 500 * 24)
    assert birikim.toplam_faiz == pytest.approx(0.0)
    assert gelecek_deger(10_000, 0, 2, 12, 500) == pytest.approx(22_000.0)


def test_kriter4_her_donem_ayri_satirda():
    kredi_satirlari = amortisman_tablosu_raporu(
        amortisman_tablosu(100_000, 24, 1, 12)
    ).splitlines()
    birikim_satirlari = birikim_tablosu(
        bilesik_faiz_tablosu(1_000, 10, 2, 4)
    ).splitlines()

    assert len(_veri_satirlari(kredi_satirlari)) == 12
    assert len(_veri_satirlari(birikim_satirlari)) == 8


# --- Oran dönüşümleri ---

def test_donemsel_oran_yuzdeyi_ve_donemi_boler():
    assert donemsel_oran(24, 12) == pytest.approx(0.02)
    assert donemsel_oran(24, 1) == pytest.approx(0.24)


def test_efektif_oran_bilesiklemeyi_yansitir():
    assert efektif_yillik_oran(24, 1) == pytest.approx(0.24)
    assert efektif_yillik_oran(24, 12) == pytest.approx(0.2682417946, abs=1e-9)


def test_efektif_oran_property_ve_rapor_ayni_sayiyi_verir():
    birikim = bilesik_faiz_tablosu(10_000, 30, 2, 12, 500)
    kredi = amortisman_tablosu(100_000, 24, 2, 12)

    assert birikim.efektif_yillik_oran == pytest.approx(0.3448888242, abs=1e-9)
    assert kredi.efektif_yillik_oran == pytest.approx(0.2682417946, abs=1e-9)
    assert "34.49 %" in birikim_ozeti(birikim)
    assert "26.82 %" in amortisman_ozeti(kredi)


def test_sik_bilesikleme_daha_cok_kazandirir():
    bakiyeler = [
        bilesik_faiz_tablosu(10_000, 30, 1, donem).son_bakiye
        for donem in (1, 2, 4, 12)
    ]

    assert bakiyeler == sorted(bakiyeler)
    assert bakiyeler[0] < bakiyeler[-1]


def test_kucuk_oran_faizsiz_sayilmiyor():
    """%1 gibi küçük ama gerçek bir faiz EPSILON eşiğine takılıp yutulmamalı."""
    assert donemsel_taksit(100_000, 1.0, 1, 12) == pytest.approx(8_378.54, abs=0.01)
    assert gelecek_deger(100_000, 1.0, 1, 12) == pytest.approx(101_004.60, abs=0.01)


def test_donem_etiketi_raporlara_dogru_yansiyor():
    aylik = bilesik_faiz_tablosu(1_000, 10, 1, 12)
    yillik = amortisman_tablosu(1_000, 10, 3, 1)

    assert aylik.donem_etiketi == "aylık"
    assert yillik.donem_etiketi == "yıllık"
    assert "aylık" in birikim_ozeti(aylik)
    assert "yıllık" in amortisman_ozeti(yillik)


def test_donem_adlari_dogru_etiket_veriyor():
    assert donem_adi(1) == "yıllık"
    assert donem_adi(4) == "üç aylık"
    assert donem_adi(12) == "aylık"
    assert donem_adi(52) == "haftalık"
    assert donem_adi(7) == "yılda 7 dönem"


def test_yil_donemlere_tam_bolunmezse_hata_verir():
    assert toplam_donem(1.5, 12) == 18
    # 1.4 * 365 = 510.99999999999994 -> round() + tolerans burada devreye girer
    assert toplam_donem(1.4, 365) == 511

    with pytest.raises(ValueError):
        toplam_donem(1.5, 1)


def test_sure_en_az_bir_donem_olmali():
    """Çok küçük süre 0 döneme yuvarlanıp ZeroDivisionError'a yol açmamalı."""
    with pytest.raises(ValueError):
        toplam_donem(1e-10, 1)

    with pytest.raises(ValueError):
        amortisman_tablosu(1_000, 24, 1e-10, 1)


def test_sonsuz_ve_nan_girdiler_reddedilir():
    for bozuk in (float("inf"), float("nan")):
        with pytest.raises(ValueError):
            toplam_donem(bozuk, 12)

        with pytest.raises(ValueError):
            bilesik_faiz_tablosu(bozuk, 10, 1, 12)

        with pytest.raises(ValueError):
            amortisman_tablosu(100_000, bozuk, 1, 12)


def test_gecersiz_donem_sayisi_reddedilir():
    with pytest.raises(ValueError):
        donemsel_oran(10, 0)

    with pytest.raises(ValueError):
        donemsel_oran(10, 12.5)

    # Python'da bool, int'in alt sınıfı: `isinstance(True, int)` True döner.
    # Ayrıca elenmeseydi donemsel_oran(10, True) sessizce 0.1 dönerdi.
    with pytest.raises(ValueError):
        donem_sayisi_dogrula(True)


# --- Bileşik faiz ---

def test_katkisiz_birikim_basit_bilesik_formule_uyar():
    sonuc = bilesik_faiz_tablosu(1_000, 10, 3, 1)

    assert sonuc.son_bakiye == pytest.approx(1_331.0)
    assert sonuc.toplam_faiz == pytest.approx(331.0)
    assert sonuc.toplam_katki == 0.0


def test_katkilar_donem_sonunda_eklenir():
    """İlk dönemin katkısı o döneme faiz kazandırmamalı."""
    sonuc = bilesik_faiz_tablosu(1_000, 10, 1, 1, donemsel_katki=100)
    ilk = sonuc.tablo[0]

    assert ilk.faiz == pytest.approx(100.0)  # 1000 x %10, katkı hariç
    assert ilk.kapanis_bakiye == pytest.approx(1_200.0)


def test_toplam_faiz_yatirilan_parayi_asan_kisimdir():
    sonuc = bilesik_faiz_tablosu(10_000, 30, 2, 12, 500)

    assert sonuc.toplam_yatirilan == pytest.approx(22_000.0)
    assert sonuc.toplam_faiz == pytest.approx(
        sonuc.son_bakiye - sonuc.toplam_yatirilan
    )


def test_tablo_satir_sayisi_donem_sayisi_kadardir():
    sonuc = bilesik_faiz_tablosu(1_000, 10, 2.5, 12)

    assert sonuc.toplam_donem == 30
    assert [satir.donem for satir in sonuc.tablo] == list(range(1, 31))


def test_sonuc_nesneleri_degistirilemez():
    """frozen dataclass + tuple: türev değerler sonradan bozulamamalı."""
    birikim = bilesik_faiz_tablosu(1_000, 10, 2, 1)
    kredi = amortisman_tablosu(1_000, 10, 2, 1)

    assert hash(birikim) is not None
    assert hash(kredi) is not None
    assert isinstance(birikim.tablo, tuple)
    assert isinstance(kredi.plan, tuple)

    with pytest.raises(AttributeError):
        birikim.tablo.append(BirikimSatiri(99, 0, 0, 0, 0))


def test_yil_sonu_suzgeci_son_donemi_her_zaman_icerir():
    tam = yil_sonu_satirlari(bilesik_faiz_tablosu(1_000, 10, 3, 12))
    kusuratli = yil_sonu_satirlari(bilesik_faiz_tablosu(1_000, 10, 2.5, 12))

    assert [s.donem for s in tam] == [12, 24, 36]
    assert [s.donem for s in kusuratli] == [12, 24, 30]


def test_bilesik_faizde_gecersiz_girdiler_hata_verir():
    with pytest.raises(ValueError):
        bilesik_faiz_tablosu(-1, 10, 1)

    with pytest.raises(ValueError):
        bilesik_faiz_tablosu(1_000, -10, 1)

    with pytest.raises(ValueError):
        bilesik_faiz_tablosu(1_000, 10, 0)

    with pytest.raises(ValueError):
        bilesik_faiz_tablosu(1_000, 10, 1, donemsel_katki=-50)


# --- Amortisman ---

def test_taksit_annuite_formulune_uyar():
    assert donemsel_taksit(100_000, 24, 1, 12) == pytest.approx(9_455.96, abs=0.01)
    assert donemsel_taksit(1_000, 10, 3, 1) == pytest.approx(402.11, abs=0.01)


def test_yuksek_oran_uzun_vadede_toplam_odeme_sapmiyor():
    """Bakiye birikimli çıkarmayla tutulsaydı burada anapara kadar sapardı.

    %200 / 20 yıl / aylık: taksit x dönem = 166.666,67 x 240 = 40.000.000.
    Eski (birikimli) hesapta toplam 41.000.000 çıkıyor, yani 1.000.000 TL
    fazla faiz raporlanıyordu.
    """
    sonuc = amortisman_tablosu(1_000_000, 200, 20, 12)

    assert sonuc.donemsel_taksit == pytest.approx(166_666.67, abs=0.01)
    assert sonuc.toplam_odeme == pytest.approx(40_000_000.0, abs=0.05)
    assert sum(s.anapara_payi for s in sonuc.plan) == pytest.approx(
        1_000_000.0, abs=0.01
    )


def test_faiz_payi_azalirken_anapara_payi_artar():
    plan = amortisman_tablosu(100_000, 24, 2, 12).plan

    faizler = [satir.faiz_payi for satir in plan]
    anaparalar = [satir.anapara_payi for satir in plan]

    assert faizler == sorted(faizler, reverse=True)
    assert anaparalar == sorted(anaparalar)


def test_kalan_borc_her_donem_azalir():
    plan = amortisman_tablosu(100_000, 24, 2, 12).plan
    bakiyeler = [satir.kalan_borc for satir in plan]

    assert bakiyeler == sorted(bakiyeler, reverse=True)
    assert bakiyeler[-1] == 0.0


def test_satirdaki_taksit_sabit_annuite_taksitiyle_ayni():
    """Satır taksiti faiz + anapara toplamından yazılıyor; bu toplam sabit
    annüite taksitinden kuruşun altında bile sapmamalı."""
    sonuc = amortisman_tablosu(100_000, 24, 2, 12)

    for satir in sonuc.plan:
        assert satir.taksit == pytest.approx(satir.faiz_payi + satir.anapara_payi)
        assert satir.taksit == pytest.approx(sonuc.donemsel_taksit, abs=0.001)


def test_tek_taksitli_kredi():
    sonuc = amortisman_tablosu(1_000, 12, 1, 1)

    assert sonuc.vade_donem == 1
    assert sonuc.donemsel_taksit == pytest.approx(1_120.0)
    assert sonuc.plan[0].kalan_borc == 0.0


def test_yil_sonu_taksitleri_son_taksiti_her_zaman_icerir():
    tam = yil_sonu_taksitleri(amortisman_tablosu(100_000, 24, 3, 12))
    kusuratli = yil_sonu_taksitleri(amortisman_tablosu(100_000, 24, 2.5, 12))

    assert [s.donem for s in tam] == [12, 24, 36]
    assert [s.donem for s in kusuratli] == [12, 24, 30]


def test_amortismanda_gecersiz_girdiler_hata_verir():
    with pytest.raises(ValueError):
        amortisman_tablosu(0, 24, 1)

    with pytest.raises(ValueError):
        amortisman_tablosu(100_000, -1, 1)

    with pytest.raises(ValueError):
        amortisman_tablosu(100_000, 24, 0)


# --- Girdi ayrıştırma ---

def test_ondalik_ayraci_virgul_de_nokta_da_olabilir():
    assert metni_sayiya_cevir("250000") == 250_000.0
    assert metni_sayiya_cevir("24,5") == 24.5
    assert metni_sayiya_cevir("24.5") == 24.5
    assert metni_sayiya_cevir(" -3,75 ") == -3.75
    assert metni_sayiya_cevir("250 000") == 250_000.0


def test_uc_haneli_ondalik_bastaki_rakama_gore_ayirt_edilir():
    """Binlik grubu ne "0" ile başlar ne de 3 haneyi aşar.

    Bu yüzden "0,125" ve "1234,567" belirsiz değil — ancak ondalık
    olabilirler. Bunları da reddetmek, %0,125'lik bir oranı arayüzden
    hiç girilemez hâle getirirdi.
    """
    assert metni_sayiya_cevir("0,125") == 0.125
    assert metni_sayiya_cevir("-0,125") == -0.125
    assert metni_sayiya_cevir("1234,567") == 1234.567


def test_belirsiz_binlik_ayraci_sessizce_kabul_edilmez():
    """'120,000' hem 120 bin hem 120,0 olabilir; tahmin etmek yerine sorulur."""
    for belirsiz in ("120,000", "120.000", "1.234.567", "1,234,567"):
        with pytest.raises(ValueError):
            metni_sayiya_cevir(belirsiz)


def test_sonsuz_ve_anlamsiz_metinler_reddedilir():
    for bozuk in ("inf", "-inf", "nan", "1e400", "abc", ""):
        with pytest.raises(ValueError):
            metni_sayiya_cevir(bozuk)


# --- Rapor katmanı ---

def test_faizsiz_ozette_etiket_gorunur():
    assert "0 (faizsiz)" in amortisman_ozeti(amortisman_tablosu(120_000, 0, 1, 12))
    assert "0 (faizsiz)" in birikim_ozeti(bilesik_faiz_tablosu(1_000, 0, 1, 12))


def test_ozet_tabloyla_ayni_sayilari_gosterir():
    sonuc = bilesik_faiz_tablosu(10_000, 30, 2, 12, 500)
    ozet = birikim_ozeti(sonuc)

    assert f"{sonuc.son_bakiye:,.2f}" in ozet
    assert f"{sonuc.toplam_faiz:,.2f}" in ozet


def test_amortisman_ozeti_sonuctaki_sayilari_gosterir():
    sonuc = amortisman_tablosu(100_000, 24, 5, 12)
    ozet = amortisman_ozeti(sonuc)

    def _satir(etiket: str) -> str:
        return next(s for s in ozet.splitlines() if s.startswith(etiket))

    # Satır satır bakılıyor: "72,607.79" dizgisi "172,607.79" satırının
    # içinde de geçtiği için özetin tamamında aramak yanıltıcı olurdu.
    assert f"{sonuc.donemsel_taksit:,.2f}" in _satir("Dönemsel taksit")
    assert f"{sonuc.toplam_odeme:,.2f}" in _satir("Toplam geri ödeme")
    assert f"{sonuc.toplam_faiz:,.2f}" in _satir("Toplam faiz")


def test_tablo_sutunlari_dogru_degerleri_gosterir():
    """Satır sayısı değil, hangi değerin hangi sütuna bastığı kontrol edilir."""
    birikim = bilesik_faiz_tablosu(10_000, 30, 1, 12, donemsel_katki=500)
    ilk = birikim.tablo[0]
    birikim_satiri = _veri_satirlari(birikim_tablosu(birikim).splitlines())[0]

    assert birikim_satiri.split() == [
        "1",
        f"{ilk.acilis_bakiye:,.2f}",
        f"{ilk.katki:,.2f}",
        f"{ilk.faiz:,.2f}",
        f"{ilk.kapanis_bakiye:,.2f}",
    ]

    kredi = amortisman_tablosu(100_000, 24, 1, 12)
    ilk_taksit = kredi.plan[0]
    kredi_satiri = _veri_satirlari(
        amortisman_tablosu_raporu(kredi).splitlines()
    )[0]

    assert kredi_satiri.split() == [
        "1",
        f"{ilk_taksit.taksit:,.2f}",
        f"{ilk_taksit.faiz_payi:,.2f}",
        f"{ilk_taksit.anapara_payi:,.2f}",
        f"{ilk_taksit.kalan_borc:,.2f}",
    ]


def test_yil_sonu_raporu_daha_kisa_olur():
    sonuc = bilesik_faiz_tablosu(1_000, 10, 5, 12)

    tam = _veri_satirlari(birikim_tablosu(sonuc).splitlines())
    kisa = _veri_satirlari(birikim_tablosu(sonuc, sadece_yil_sonu=True).splitlines())

    assert len(tam) == 60
    assert len(kisa) == 5


# --- Kullanıcı arayüzü (main.py) ---

def _cli_calistir(girdiler: str) -> subprocess.CompletedProcess:
    """main.py'yi ayrı bir süreçte çalıştırır.

    `import main` demek yerine alt süreç kullanılıyor: bu depodaki
    vergi-kredi-hesaplayici projesinde de bir `main.py` var ve `pytest`
    depo kökünden çalıştırıldığında hangisinin içeri alınacağı
    `sys.path` sırasına kalırdı.
    """
    return subprocess.run(
        [sys.executable, "main.py"],
        input=girdiler,
        capture_output=True,
        text=True,
        cwd=PROJE,
        timeout=60,
    )


def test_demo_akisi_hatasiz_calisir():
    sonuc = subprocess.run(
        [sys.executable, "main.py", "--demo"],
        capture_output=True,
        text=True,
        cwd=PROJE,
        timeout=60,
    )

    assert sonuc.returncode == 0
    assert "Traceback" not in sonuc.stderr
    assert "402.11" in sonuc.stdout      # 1.000 TL / %10 / 3 yıl taksiti
    assert "34,261.78" in sonuc.stdout   # birikim örneğinin son bakiyesi


def test_sikliga_bolunmeyen_sure_programi_dusurmez():
    """1,5 yıl + yıllık taksit: hata gösterilip aynı soru tekrar sorulmalı."""
    sonuc = _cli_calistir("2\n100000\n24\n1\n1.5\n3\n")

    assert "tam bölünmüyor" in sonuc.stdout
    assert "AMORTİSMAN TABLOSU" in sonuc.stdout
    assert "Traceback" not in sonuc.stderr


def test_sure_ve_oran_ust_sinirlari_uygulanir():
    sonuc = _cli_calistir("2\n100000\n1e30\n24\n4\n500\n1\n")

    assert "en çok 1000 olabilir" in sonuc.stdout   # faiz oranı sınırı
    assert "en çok 100 olabilir" in sonuc.stdout    # süre sınırı
    assert "Traceback" not in sonuc.stderr


def test_uzun_tablo_yil_sonlarina_kisaltilir():
    """50 yıl x 12 = 600 taksit ekrana satır satır basılmamalı."""
    sonuc = _cli_calistir("2\n100000\n24\n4\n50\n")
    satirlar = _veri_satirlari(sonuc.stdout.splitlines())

    assert "yıl sonları gösterildi" in sonuc.stdout
    assert len(satirlar) == 50
    assert "Traceback" not in sonuc.stderr


def test_bozuk_girdiler_traceback_dokmez():
    for girdi in (
        "2\n100000\n24\n2\ninf\n1\n",
        "1\nnan\n1000\n10\n1\n1\n0\n",
        "2\n120,000\n120000\n0\n1\n1\n",
        "1\n1000\n10\n1\n1e400\n1\n0\n",
        "abc\n",
    ):
        sonuc = _cli_calistir(girdi)

        assert "Traceback" not in sonuc.stderr, girdi
        assert sonuc.returncode == 0, girdi
