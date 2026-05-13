"""
TEFAS Fon Analiz Motoru — v11
==============================
v11 GÜNCELLEMELERİ:
- Tüm magic number'lar config.py'ye taşındı
- EVDS API entegrasyonu (risksiz faiz dinamik çekiliyor, fallback hardcoded liste)
- Backtest'te tarihsel enflasyon beklentisi (lookahead bias düzeltildi)
- tam_analiz `df` parametresi alabiliyor (cache zinciri için)

v10 GÜNCELLEMELERİ:
- rolling_beta_alpha NumPy ile vektörize edildi (10x+ hız)
- rolling_sharpe NumPy ile vektörize edildi
- YFinance verisi ffill ile tatil uyuşmazlığı düzeltildi
- _hizala_fon_endeks: merge_asof ile fon-endeks hizalama
- walk_forward_backtest progress_callback parametresi aldı
- Bütün analiz fonksiyonları hala saf (UI'dan bağımsız)
"""
import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from tefas import Crawler

import config as C

try:
    import yfinance as yf
    YF_VAR = True
except ImportError:
    YF_VAR = False

try:
    import requests
    REQUESTS_VAR = True
except ImportError:
    REQUESTS_VAR = False


# ================= 1. VERİ ÇEKME =================
def fon_verisi_getir(fon_kodu, gun_sayisi=1000, columns=None):
    if columns is None:
        columns = ["date", "price", "title"]
    bitis = datetime.now().strftime("%Y-%m-%d")
    bas = (datetime.now() - timedelta(days=gun_sayisi)).strftime("%Y-%m-%d")
    crawler = Crawler()
    veri = crawler.fetch(start=bas, end=bitis, name=fon_kodu, columns=columns)
    if veri is None or veri.empty:
        raise ValueError(f"{fon_kodu} kodlu fon bulunamadı veya verisi boş.")
    df = pd.DataFrame(veri)
    df['date'] = pd.to_datetime(df['date']).astype('datetime64[us]')
    df = df.sort_values('date').drop_duplicates('date').reset_index(drop=True)
    df['getiri'] = df['price'].pct_change()
    return df


def gunluk_istatistik(df):
    return (df['price'].iloc[-1], df['getiri'].mean(), df['getiri'].std())


# ================= 2. RİSKSİZ FAİZ =================
# EVDS API ile dinamik çekme — fallback: config.RISKSIZ_FAIZ_TARIHCE

# Modül seviyesinde cache — bir Python oturumunda 1 kez çekilir
_EVDS_FAIZ_CACHE = None
_EVDS_FAIZ_CACHE_TARIH = None


def _evds_faiz_serisi_cek():
    """
    TCMB EVDS API'sinden TP.AOFOD2 (gecelik repo faizi) haftalık tarihçesini çeker.

    API key gerekli — `EVDS_API_KEY` ortam değişkeninden veya Streamlit
    secrets'tan okunur. Yoksa None döner, çağıran fallback'e geçer.

    Cache: 24 saatlik in-memory (modül seviyesi). Streamlit @st.cache_data
    ile sarılmadığı için her cache miss'te yeniden çağrılmaz.
    """
    global _EVDS_FAIZ_CACHE, _EVDS_FAIZ_CACHE_TARIH

    # 24 saatlik cache kontrolü
    if _EVDS_FAIZ_CACHE is not None and _EVDS_FAIZ_CACHE_TARIH is not None:
        if (datetime.now() - _EVDS_FAIZ_CACHE_TARIH).total_seconds() < C.CACHE_TTL_GUNLUK:
            return _EVDS_FAIZ_CACHE

    if not REQUESTS_VAR:
        return None

    api_key = os.environ.get('EVDS_API_KEY')
    if not api_key:
        # Streamlit secrets — sadece runtime'da varsa
        try:
            import streamlit as st
            api_key = st.secrets.get('EVDS_API_KEY')
        except Exception:
            api_key = None

    if not api_key:
        return None

    try:
        # TP.AOFOD2: TCMB ağırlıklı ortalama fonlama maliyeti (politika faizi proxy)
        bas = "01-01-2018"
        bit = datetime.now().strftime("%d-%m-%Y")
        url = (
            f"https://evds2.tcmb.gov.tr/service/evds/series=TP.AOFOD2"
            f"&startDate={bas}&endDate={bit}"
            f"&type=json&aggregationTypes=avg&frequency=8"  # frequency=8: aylık
        )
        headers = {'key': api_key}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        if 'items' not in data or not data['items']:
            return None

        rows = []
        for item in data['items']:
            tarih_str = item.get('Tarih')  # "2018-1" formatı
            deger = item.get('TP_AOFOD2')
            if not tarih_str or deger is None:
                continue
            try:
                # "2018-1" → "2018-01-01"
                yil, ay = tarih_str.split('-')
                tarih = pd.Timestamp(f"{yil}-{int(ay):02d}-01")
                # API yıllık % olarak veriyor → ondalığa çevir
                faiz = float(deger) / 100
                rows.append((tarih, faiz))
            except (ValueError, AttributeError):
                continue

        if len(rows) < 5:
            return None

        df = pd.DataFrame(rows, columns=['date', 'faiz'])
        df['date'] = df['date'].astype('datetime64[us]')
        df = df.sort_values('date').drop_duplicates('date').reset_index(drop=True)

        _EVDS_FAIZ_CACHE = df
        _EVDS_FAIZ_CACHE_TARIH = datetime.now()
        return df
    except Exception:
        return None


def dinamik_risksiz_faiz_serisi(tarih_indeksi):
    """
    Önce EVDS'den çekmeyi dener, başarısızsa config.RISKSIZ_FAIZ_TARIHCE fallback.
    """
    df_faiz = _evds_faiz_serisi_cek()

    if df_faiz is None:
        # Fallback: hardcoded liste
        df_faiz = pd.DataFrame(C.RISKSIZ_FAIZ_TARIHCE, columns=['date', 'faiz'])
        df_faiz['date'] = pd.to_datetime(df_faiz['date']).astype('datetime64[us]')
        df_faiz = df_faiz.sort_values('date')

    df_tarih = pd.DataFrame({'date': tarih_indeksi})
    df_tarih_sorted = df_tarih.sort_values('date')
    merged = pd.merge_asof(df_tarih_sorted, df_faiz, on='date', direction='backward')
    merged['faiz'] = merged['faiz'].bfill().fillna(df_faiz['faiz'].iloc[0])
    merged.index = df_tarih_sorted.index
    return df_tarih.join(merged['faiz'])['faiz']


def guncel_risksiz_faiz():
    return dinamik_risksiz_faiz_serisi(pd.DatetimeIndex([pd.Timestamp.now()])).iloc[0]


def tarihsel_enflasyon_beklentisi(tarih_indeksi):
    """
    O tarihte geçerli olan 12-ay ileri enflasyon beklentisini döner.
    Backtest'te lookahead bias'ı önlemek için kullanılır.

    Kaynak: TCMB Piyasa Katılımcıları Anketi (config'de hardcoded fallback).
    İlerideki bir geliştirmede EVDS'den TP.BEK.S02.A.B12 serisi çekilebilir.
    """
    df_enf = pd.DataFrame(C.ENFLASYON_BEKLENTI_TARIHCE, columns=['date', 'enf'])
    df_enf['date'] = pd.to_datetime(df_enf['date']).astype('datetime64[us]')
    df_enf = df_enf.sort_values('date')

    df_tarih = pd.DataFrame({'date': tarih_indeksi})
    df_tarih_sorted = df_tarih.sort_values('date')
    merged = pd.merge_asof(df_tarih_sorted, df_enf, on='date', direction='backward')
    merged['enf'] = merged['enf'].bfill().fillna(df_enf['enf'].iloc[0])
    merged.index = df_tarih_sorted.index
    return df_tarih.join(merged['enf'])['enf']


# ================= 3. KATEGORİ =================
def fon_kategorisi_belirle(df):
    if 'title' not in df.columns or df['title'].isna().all():
        return "BİLİNMİYOR", "Fon adı çekilemedi"
    isim = str(df['title'].iloc[-1]).upper()
    if 'PARA PİYASASI' in isim or 'LİKİT' in isim:
        return "PARA_PIYASASI", "Para Piyasası / Likit"
    if 'KIYMETLİ MADEN' in isim or 'ALTIN' in isim or 'GÜMÜŞ' in isim:
        return "ALTIN", "Kıymetli Maden / Altın"
    if 'EUROBOND' in isim or 'YABANCI BORÇLANMA' in isim:
        return "EUROBOND", "Eurobond"
    if 'BORÇLANMA' in isim or 'KAMU' in isim or 'TAHVIL' in isim:
        return "BORCLANMA", "Borçlanma Araçları"
    if 'KATILIM' in isim:
        return "KATILIM", "Katılım Fonu"
    if 'YABANCI HİSSE' in isim or 'NASDAQ' in isim or 'S&P' in isim:
        return "YABANCI_HISSE", "Yabancı Hisse"
    if 'TEKNOLOJİ' in isim or 'BİLİŞİM' in isim:
        return "TEKNOLOJI", "Teknoloji"
    if 'BANKA' in isim or 'BANKACILIK' in isim:
        return "BANKACILIK", "Bankacılık"
    if 'HİSSE' in isim:
        return "HISSE", "Hisse Senedi Yoğun"
    if 'DEĞIŞKEN' in isim or 'KARMA' in isim or 'ÇOKLU VARLIK' in isim:
        return "DEGISKEN", "Değişken / Karma"
    if 'FON SEPETİ' in isim:
        return "FON_SEPETI", "Fon Sepeti"
    if 'ENDEKS' in isim or 'BIST' in isim:
        return "ENDEKS", "Endeks"
    return "DIGER", f"Diğer ({isim[:50]})"


def kategoriye_gore_endeks_kodu(kategori):
    haritasi = {
        "HISSE":         ("BIST100",   "BIST 100"),
        "ENDEKS":        ("BIST100",   "BIST 100"),
        "TEKNOLOJI":     ("BIST_TEKNO","BIST Teknoloji"),
        "BANKACILIK":    ("BIST_BANKA","BIST Bankacılık"),
        "DEGISKEN":      ("BIST100",   "BIST 100"),
        "FON_SEPETI":    ("BIST100",   "BIST 100"),
        "ALTIN":         ("ALTIN_TRY", "Altın TL (XAU×USDTRY)"),
        "YABANCI_HISSE": ("SP500",     "S&P 500"),
        "EUROBOND":      ("USDTRY",    "USD/TRY"),
    }
    return haritasi.get(kategori, (None, "Mevduat / Risksiz"))


# ================= 4. MAKRO VERİ (FFILL ile tatil hizalama) =================
def makro_verileri_getir(baslangic_tarihi, bitis_tarihi):
    if not YF_VAR:
        return {}
    semboller = {
        'BIST100':     'XU100.IS',
        'BIST_BANKA':  'XBANK.IS',
        'BIST_TEKNO':  'XUTEK.IS',
        'USDTRY':      'USDTRY=X',
        'ALTIN_USD':   'GC=F',
        'SP500':       '^GSPC',
    }
    sonuclar = {}
    for isim, sembol in semboller.items():
        try:
            data = yf.download(sembol, start=baslangic_tarihi, end=bitis_tarihi,
                              progress=False, auto_adjust=True)
            if data.empty or len(data) < 30:
                continue
            d = data[['Close']].reset_index()
            d.columns = ['date', 'price']
            d['date'] = pd.to_datetime(d['date']).dt.tz_localize(None).astype('datetime64[us]')
            d = d.sort_values('date').reset_index(drop=True)
            # YENİ: ffill ile boş günleri doldur (tatil uyuşmazlıkları için)
            d['price'] = d['price'].ffill()
            d['getiri'] = d['price'].pct_change()
            sonuclar[isim] = d
        except Exception:
            continue

    if 'ALTIN_USD' in sonuclar and 'USDTRY' in sonuclar:
        au = sonuclar['ALTIN_USD'][['date', 'price']].rename(columns={'price': 'au'})
        ut = sonuclar['USDTRY'][['date', 'price']].rename(columns={'price': 'ut'})
        # YENİ: outer join + ffill — ABD ve TR tatilleri çakışmadığında veri kaybı önlenir
        m = au.merge(ut, on='date', how='outer').sort_values('date').reset_index(drop=True)
        m['au'] = m['au'].ffill()
        m['ut'] = m['ut'].ffill()
        m = m.dropna()
        m['price'] = m['au'] * m['ut']
        m['getiri'] = m['price'].pct_change()
        sonuclar['ALTIN_TRY'] = m[['date', 'price', 'getiri']].reset_index(drop=True)
    return sonuclar


def _hizala_fon_endeks(fon_df, endeks_df):
    """
    Fon ve endeks tarihlerini merge_asof ile hizalar.
    Fonun her gününe en yakın endeks değerini eşler (tolerans 3 gün).
    Hem ABD tatili (S&P 500) hem TR tatili durumlarını çözer.
    """
    fon_sorted = fon_df[['date', 'getiri']].sort_values('date').reset_index(drop=True)
    endeks_sorted = endeks_df[['date', 'getiri']].sort_values('date').reset_index(drop=True)
    birlesik = pd.merge_asof(
        fon_sorted.rename(columns={'getiri': 'fon_g'}),
        endeks_sorted.rename(columns={'getiri': 'bench_g'}),
        on='date', direction='backward',
        tolerance=pd.Timedelta(days=3)
    ).dropna()
    return birlesik


# ================= 5. Z-SKOR =================
def rolling_z_skor(df, pencere=None):
    if pencere is None:
        pencere = C.Z_SKOR_PENCERE
    son = df['price'].tail(pencere).dropna().values
    if len(son) < C.Z_SKOR_MIN_GUN:
        return 0.0, 50.0, "Veri yetersiz"
    log_p = np.log(son)
    x = np.arange(len(log_p))
    slope, intercept, _, _, _ = stats.linregress(x, log_p)
    sapma = log_p - (slope * x + intercept)
    std_s = sapma.std()
    if std_s == 0:
        return 0.0, 50.0, "Sabit fiyat"
    z = (sapma[-1] - sapma.mean()) / std_s
    skor = float(np.clip(50 - z * 25, 0, 100))
    if z > C.Z_ZIRVE:    yorum = "Zirve bölgesi"
    elif z > C.Z_PAHALI: yorum = "Pahalı"
    elif z > C.Z_UCUZ:   yorum = "Adil değer"
    elif z > C.Z_DIP:    yorum = "Ucuz"
    else:                yorum = "Dip bölgesi"
    return float(z), skor, yorum


# ================= 6. TREND =================
def trend_rejimi(df, rf_yillik):
    df = df.copy()
    df['SMA_50']  = df['price'].rolling(C.SMA_KISA).mean()
    df['SMA_200'] = df['price'].rolling(C.SMA_UZUN).mean()
    son_fiyat = df['price'].iloc[-1]
    sma_50, sma_200 = df['SMA_50'].iloc[-1], df['SMA_200'].iloc[-1]

    if pd.isna(sma_50) or pd.isna(sma_200):
        sma_sinyali, sma_skor = "Veri yetersiz", 50
    elif sma_50 > sma_200 and son_fiyat > sma_50:
        sma_sinyali, sma_skor = "Yükseliş trendi", 80
    elif sma_50 > sma_200:
        sma_sinyali, sma_skor = "Yükselişte geri çekilme", 70
    elif sma_50 < sma_200 and son_fiyat < sma_50:
        sma_sinyali, sma_skor = "Düşüş trendi", 20
    else:
        sma_sinyali, sma_skor = "Düşüşte toparlanma", 40

    son_90 = df['price'].tail(C.TREND_KISA_PENCERE).dropna().values
    if len(son_90) >= C.TREND_MIN_GUN:
        slope, _, r_value, _, _ = stats.linregress(np.arange(len(son_90)), np.log(son_90))
        yillik_egim = slope * 252 * 100
        trend_gucu = r_value ** 2
    else:
        yillik_egim, trend_gucu = 0, 0

    rf_pct = rf_yillik * 100
    if yillik_egim > rf_pct + C.TREND_YUKSELIS_ESIK_PUAN:
        rejim = "YÜKSELİŞ"
    elif yillik_egim > rf_pct + C.TREND_DUSUS_ESIK_PUAN:
        rejim = "YATAY"
    else:
        rejim = "DÜŞÜŞ"

    return {'rejim': rejim, 'sma_sinyali': sma_sinyali, 'sma_skor': sma_skor,
            'yillik_egim_yuzde': yillik_egim, 'trend_gucu_r2': trend_gucu}


def rejim_mu_sigma(df, rf_yillik):
    df = df.copy()
    n = len(df)
    etiketler = ["YETERSİZ"] * n
    fiyatlar = df['price'].values
    rf_pct = rf_yillik * 100

    for i in range(C.REJIM_BASLANGIC_GUN, n):
        pencere = fiyatlar[max(0, i - C.REJIM_GERIYE_PENCERE):i]
        pencere = pencere[~np.isnan(pencere)]
        if len(pencere) < C.TREND_MIN_GUN:
            continue
        x = np.arange(len(pencere))
        slope, _, _, _, _ = stats.linregress(x, np.log(pencere))
        yil_egim = slope * 252 * 100
        if yil_egim > rf_pct + C.TREND_YUKSELIS_ESIK_PUAN:
            etiketler[i] = "YÜKSELİŞ"
        elif yil_egim > rf_pct + C.TREND_DUSUS_ESIK_PUAN:
            etiketler[i] = "YATAY"
        else:
            etiketler[i] = "DÜŞÜŞ"

    df['rejim'] = etiketler
    rejim_stat = {}
    for r in ["YÜKSELİŞ", "YATAY", "DÜŞÜŞ"]:
        f = df[df['rejim'] == r]['getiri'].dropna()
        if len(f) >= C.REJIM_MIN_GOZLEM:
            rejim_stat[r] = {'mu': f.mean(), 'sigma': f.std(), 'n': len(f)}
        else:
            rejim_stat[r] = {'mu': df['getiri'].mean(),
                            'sigma': df['getiri'].std(), 'n': 0}
    return rejim_stat


# ================= 7. REJİM UYARI =================
def rejim_degisim_uyarisi(df, kisa=None, uzun=None):
    if kisa is None:
        kisa = C.REJIM_KISA_PENCERE
    if uzun is None:
        uzun = C.REJIM_UZUN_PENCERE
    g = df['getiri'].dropna()
    if len(g) < uzun:
        return {'siddet': 0, 'karar': "Veri yok", 'vol_orani': 1, 'mu_fark': 0,
                'son_vol': 0, 'tar_vol': 0, 'uyarilar': []}
    son_vol  = g.tail(kisa).std() * np.sqrt(252) * 100
    tar_vol  = g.tail(uzun).std() * np.sqrt(252) * 100
    vol_oran = son_vol / tar_vol if tar_vol > 0 else 1
    mu_fark  = (g.tail(kisa).mean() - g.tail(uzun).mean()) * 252 * 100

    siddet = 0
    uyarilar = []
    if vol_oran > C.VOL_PATLAMA_ESIK:
        siddet += 2; uyarilar.append(f"Volatilite patlaması: {vol_oran:.1f}x")
    elif vol_oran > C.VOL_ARTIS_ESIK:
        siddet += 1; uyarilar.append(f"Volatilite artışı: {vol_oran:.1f}x")
    if abs(mu_fark) > C.MU_KIRILMA_ESIK_PUAN:
        siddet += 2; uyarilar.append(f"Trend kırılması: {mu_fark:+.0f} puan")

    if siddet >= C.SIDDET_KRITIK:   karar = "Rejim değişimi muhtemel"
    elif siddet >= C.SIDDET_ORTA:   karar = "Anormal davranış"
    else:                            karar = "Normal"

    return {'siddet': siddet, 'son_vol': son_vol, 'tar_vol': tar_vol,
            'vol_orani': vol_oran, 'mu_fark': mu_fark,
            'uyarilar': uyarilar, 'karar': karar}


# ================= 8. RSI + RİSK =================
def rsi_skoru(df):
    delta = df['price'].diff()
    
    # --- DÜZELTİLEN RSI (ÜSTEL HAREKETLİ ORTALAMA) ---
    kazanc = delta.where(delta > 0, 0).ewm(alpha=1/C.RSI_PENCERE, adjust=False).mean()
    kayip  = -delta.where(delta < 0, 0).ewm(alpha=1/C.RSI_PENCERE, adjust=False).mean()
    # -------------------------------------------------
    rs = kazanc / kayip
    rsi = (100 - 100 / (1 + rs)).iloc[-1]
    if pd.isna(rsi):
        return {'rsi': None, 'skor': 50, 'yorum': "N/A"}
    if rsi > C.RSI_ASIRI_ALIM_YUKSEK:   s, y = 15, "Aşırı alım (yüksek)"
    elif rsi > C.RSI_ASIRI_ALIM:        s, y = 35, "Aşırı alım"
    elif rsi > C.RSI_NOTR_UST:          s, y = 65, "Pozitif"
    elif rsi > C.RSI_NOTR_ALT:          s, y = 50, "Negatif"
    elif rsi > C.RSI_ASIRI_SATIM_DUSUK: s, y = 75, "Aşırı satım"
    else:                                s, y = 90, "Aşırı satım (düşük)"
    return {'rsi': float(rsi), 'skor': s, 'yorum': y}


def risk_metrikleri(df):
    fiyat = df['price'].values
    zirve = np.maximum.accumulate(fiyat)
    drawdown = (fiyat - zirve) / zirve
    yillik_oynak = df['getiri'].std() * np.sqrt(252) * 100

    rf_serisi = dinamik_risksiz_faiz_serisi(df['date'])
    rf_gunluk = (1 + rf_serisi) ** (1/252) - 1
    fazla = df['getiri'].values - rf_gunluk.values
    fazla = fazla[~np.isnan(fazla)]

   if len(fazla) > 0 and np.std(fazla) > 0:
        sharpe = (np.mean(fazla) / np.std(fazla)) * np.sqrt(252)
        downside = np.sqrt(np.mean(np.minimum(0, fazla)**2))
        sortino = (np.mean(fazla) / downside) * np.sqrt(252) if downside > 0 else 0
    else:
        sharpe, sortino = 0, 0

    return {'max_drawdown': float(drawdown.min() * 100),
            'guncel_drawdown': float(drawdown[-1] * 100),
            'yillik_oynaklik': float(yillik_oynak),
            'sharpe': float(sharpe), 'sortino': float(sortino),
            'guncel_rf_yillik': float(rf_serisi.iloc[-1] * 100)}


# ================= 9. BETA / ALPHA =================
def beta_alpha_endekse_karsi(fon_df, endeks_df):
    birlesik = _hizala_fon_endeks(fon_df, endeks_df)
    if len(birlesik) < 60:
        return None
    bench = birlesik['bench_g'].values
    fon   = birlesik['fon_g'].values
    slope, intercept, r, p, _ = stats.linregress(bench, fon)
    alpha_yillik = ((1 + intercept) ** 252 - 1) * 100
    aktif = fon - bench
    te = aktif.std() * np.sqrt(252) * 100
    ir = (aktif.mean() * 252) / (aktif.std() * np.sqrt(252)) if aktif.std() > 0 else 0

    if alpha_yillik > 5 and p < 0.05:
        alpha_yorum = f"Pozitif ve istatistiksel olarak anlamlı (%{alpha_yillik:+.1f}/yıl, p={p:.3f})"
    elif alpha_yillik > 0:
        alpha_yorum = f"Hafif pozitif (%{alpha_yillik:+.1f}/yıl, p={p:.3f})"
    elif alpha_yillik > -5:
        alpha_yorum = f"Hafif negatif (%{alpha_yillik:+.1f}/yıl)"
    else:
        alpha_yorum = f"Negatif (%{alpha_yillik:+.1f}/yıl)"

    return {'beta': float(slope), 'alpha_yillik_yuzde': float(alpha_yillik),
            'p_value': float(p), 'r_squared': float(r**2),
            'tracking_error': float(te), 'information_ratio': float(ir),
            'alpha_yorum': alpha_yorum, 'gozlem_sayisi': len(birlesik)}


def rolling_beta_alpha(fon_df, endeks_df, pencere=None):
    """
    VEKTÖRİZE: NumPy ile rolling OLS, O(n) karmaşıklık.
    Eski for-döngüsü scipy.linregress versiyonundan ~15-30x hızlı.

    Matematik:
        beta = (n*Σxy - Σx*Σy) / (n*Σxx - (Σx)^2)
        alpha = mean(y) - beta * mean(x)
    Kümülatif toplamlarla rolling sum'ları O(n)'de hesaplıyoruz.
    """
    if pencere is None:
        pencere = C.ROLLING_BETA_PENCERE
    birlesik = _hizala_fon_endeks(fon_df, endeks_df).reset_index(drop=True)
    if len(birlesik) < pencere + C.ROLLING_MIN_EK_GUN:
        return None

    x = birlesik['bench_g'].values
    y = birlesik['fon_g'].values
    tarihler = birlesik['date'].values
    n = len(x)

    # Kümülatif toplamlar
    cumx = np.concatenate([[0.0], np.cumsum(x)])
    cumy = np.concatenate([[0.0], np.cumsum(y)])
    cumxx = np.concatenate([[0.0], np.cumsum(x * x)])
    cumxy = np.concatenate([[0.0], np.cumsum(x * y)])
    cumyy = np.concatenate([[0.0], np.cumsum(y * y)])

    idx = np.arange(pencere, n + 1)  # her i için pencere = [i-pencere, i)
    sx = cumx[idx] - cumx[idx - pencere]
    sy = cumy[idx] - cumy[idx - pencere]
    sxx = cumxx[idx] - cumxx[idx - pencere]
    sxy = cumxy[idx] - cumxy[idx - pencere]
    syy = cumyy[idx] - cumyy[idx - pencere]
    p = float(pencere)

    pay = p * sxy - sx * sy
    payda = p * sxx - sx * sx
    payda_safe = np.where(np.abs(payda) > 1e-15, payda, np.nan)
    beta = pay / payda_safe

    mean_x = sx / p
    mean_y = sy / p
    alpha_gunluk = mean_y - beta * mean_x
    alpha_yillik = ((1 + alpha_gunluk) ** 252 - 1) * 100

    # Information Ratio: aktif getiri (y - x) için
    aktif_mean = mean_y - mean_x
    var_y = (syy - p * mean_y * mean_y) / (p - 1)
    var_x = (sxx - p * mean_x * mean_x) / (p - 1)
    cov_xy = (sxy - p * mean_x * mean_y) / (p - 1)
    var_aktif = np.maximum(var_y + var_x - 2 * cov_xy, 0)
    std_aktif = np.sqrt(var_aktif)
    std_aktif_safe = np.where(std_aktif > 1e-15, std_aktif, np.nan)
    info_ratio = (aktif_mean * 252) / (std_aktif_safe * np.sqrt(252))

    # NaN'leri temizle
    beta = np.nan_to_num(beta, nan=0.0)
    alpha_yillik = np.nan_to_num(alpha_yillik, nan=0.0)
    info_ratio = np.nan_to_num(info_ratio, nan=0.0)

    # Tarih hizalama: her i. pencere [i-pencere, i)'nin SON noktası tarihler[i-1]
    son_tarihler = tarihler[idx - 1]

    return pd.DataFrame({
        'date': son_tarihler,
        'beta': beta,
        'alpha_yillik': alpha_yillik,
        'info_ratio': info_ratio
    })


def rolling_sharpe(fon_df, pencere=None):
    """VEKTÖRİZE: O(n) kümülatif toplam yöntemi."""
    if pencere is None:
        pencere = C.ROLLING_SHARPE_PENCERE
    df = fon_df.copy().dropna(subset=['getiri']).reset_index(drop=True)
    if len(df) < pencere + C.ROLLING_MIN_EK_GUN:
        return None
    rf_serisi = dinamik_risksiz_faiz_serisi(df['date'])
    rf_gunluk = (1 + rf_serisi) ** (1/252) - 1
    fazla = df['getiri'].values - rf_gunluk.values

    n = len(fazla)
    cumf = np.concatenate([[0.0], np.cumsum(fazla)])
    cumff = np.concatenate([[0.0], np.cumsum(fazla * fazla)])

    idx = np.arange(pencere, n + 1)
    sf = cumf[idx] - cumf[idx - pencere]
    sff = cumff[idx] - cumff[idx - pencere]
    p = float(pencere)

    mean_f = sf / p
    var_f = np.maximum((sff - p * mean_f * mean_f) / (p - 1), 0)
    std_f = np.sqrt(var_f)
    std_f_safe = np.where(std_f > 1e-15, std_f, np.nan)
    sharpe = (mean_f / std_f_safe) * np.sqrt(252)
    sharpe = np.nan_to_num(sharpe, nan=0.0)

    tarihler = df['date'].values
    son_tarihler = tarihler[idx - 1]

    return pd.DataFrame({'date': son_tarihler, 'sharpe': sharpe})


# ================= 10. MONTE CARLO =================
def monte_carlo_motoru(baslangic_fiyati, mu_genel, sigma_genel,
                      rejim_mu, rejim_sigma,
                      enflasyon_orani, enflasyon_sigma_yillik=0.13,
                      gun_sayisi=252, senaryo_sayisi=None, df_t=None):
    if senaryo_sayisi is None:
        senaryo_sayisi = C.MC_VARSAYILAN_SENARYO
    if df_t is None:
        df_t = C.MC_T_DAGILIM_DF
    duzeltilmis_mu    = mu_genel * (1 - C.MC_REJIM_AGIRLIK_MU) + rejim_mu * C.MC_REJIM_AGIRLIK_MU
    duzeltilmis_sigma = sigma_genel * (1 - C.MC_REJIM_AGIRLIK_SIGMA) + rejim_sigma * C.MC_REJIM_AGIRLIK_SIGMA
    varyans_t = df_t / (df_t - 2)
    t_norm = np.random.standard_t(df_t,
                                  size=(gun_sayisi - 1, senaryo_sayisi)) / np.sqrt(varyans_t)
    nominal_soklar = duzeltilmis_mu + duzeltilmis_sigma * t_norm
    gunluk_enf_mu    = (1 + enflasyon_orani) ** (1/252) - 1
    gunluk_enf_sigma = enflasyon_sigma_yillik / np.sqrt(252)
    enf_soklari = np.random.normal(gunluk_enf_mu, gunluk_enf_sigma,
                                  size=(gun_sayisi - 1, senaryo_sayisi))
    reel_soklar = (1 + nominal_soklar) / (1 + enf_soklari)
    yollar = baslangic_fiyati * np.cumprod(reel_soklar, axis=0)
    return np.vstack([np.full(senaryo_sayisi, baslangic_fiyati), yollar])


# ================= 11. SİNYAL GRUPLARI =================
def sinyal_gruplari_uret(z_skor, sma_skor, rsi_skor,
                         sharpe, drawdown_guncel,
                         alpha_yillik, info_ratio,
                         rejim_uyari_siddet=0):
    grup_degerleme = float(np.clip(50 - z_skor * 25, 0, 100))
    grup_trend = (sma_skor + rsi_skor) / 2

    if sharpe > C.SHARPE_MUKEMMEL:  sh = 100
    elif sharpe > C.SHARPE_IYI:     sh = 75
    elif sharpe > C.SHARPE_ORTA:    sh = 60
    elif sharpe > C.SHARPE_POZITIF: sh = 45
    else:                            sh = 25
    if drawdown_guncel > C.DD_HAFIF:    dd = 50
    elif drawdown_guncel > C.DD_ORTA:   dd = 60
    elif drawdown_guncel > C.DD_AGIR:   dd = 70
    else:                                dd = 80
    grup_risk = (sh + dd) / 2

    if alpha_yillik is None:                alpha_skor = 50
    elif alpha_yillik > C.ALPHA_MUKEMMEL:   alpha_skor = 90
    elif alpha_yillik > C.ALPHA_IYI:        alpha_skor = 75
    elif alpha_yillik > C.ALPHA_POZITIF:    alpha_skor = 60
    elif alpha_yillik > C.ALPHA_HAFIF_NEG:  alpha_skor = 40
    elif alpha_yillik > C.ALPHA_NEGATIF:    alpha_skor = 25
    else:                                    alpha_skor = 10
    if info_ratio is None:                  ir_skor = 50
    elif info_ratio > C.IR_MUKEMMEL:        ir_skor = 90
    elif info_ratio > C.IR_IYI:             ir_skor = 75
    elif info_ratio > C.IR_ORTA:            ir_skor = 60
    elif info_ratio > C.IR_POZITIF:         ir_skor = 50
    elif info_ratio > C.IR_HAFIF_NEG:       ir_skor = 35
    else:                                    ir_skor = 20
    grup_aktif = (alpha_skor + ir_skor) / 2

    gruplar = {
        'Değerleme': float(grup_degerleme),
        'Trend':     float(grup_trend),
        'Risk':      float(grup_risk),
        'Aktif Yön.': float(grup_aktif),
    }
    skor_ham = float(np.mean(list(gruplar.values())))

    if rejim_uyari_siddet >= C.SIDDET_KRITIK:
        skor = skor_ham * 0.5 + 50 * 0.5
        guven = "Düşük (rejim değişimi sinyali)"
    elif rejim_uyari_siddet >= C.SIDDET_ORTA:
        skor = skor_ham * 0.75 + 50 * 0.25
        guven = "Orta"
    else:
        skor = skor_ham
        guven = "Normal"
    skor = float(np.clip(skor, 0, 100))

    if skor >= C.SKOR_COK_GUCLU:   etiket = "Çok güçlü göstergeler"
    elif skor >= C.SKOR_GUCLU:     etiket = "Güçlü göstergeler"
    elif skor >= C.SKOR_KARISIK:   etiket = "Karışık göstergeler"
    elif skor >= C.SKOR_ZAYIF:     etiket = "Zayıf göstergeler"
    else:                           etiket = "Çok zayıf göstergeler"

    return {'toplam_skor': skor, 'etiket': etiket, 'guven': guven, 'gruplar': gruplar}


# ================= 12. BENCHMARK =================
def benchmark_karsilastir(fon_df, kategori, enflasyon_yillik, makro_dict):
    fon_bas = fon_df['price'].iloc[0]
    fon_son = fon_df['price'].iloc[-1]
    yil = (fon_df['date'].iloc[-1] - fon_df['date'].iloc[0]).days / 365
    fon_top = (fon_son / fon_bas - 1) * 100
    fon_yil = ((fon_son / fon_bas) ** (1 / yil) - 1) * 100 if yil > 0 else 0

    sonuc = {'fon_toplam': fon_top, 'fon_yillik': fon_yil,
             'sure_yil': yil, 'karsilastirmalar': []}

    rf_serisi = dinamik_risksiz_faiz_serisi(fon_df['date'])
    rf_gunluk = (1 + rf_serisi) ** (1/252) - 1
    mevduat_carpan = (1 + rf_gunluk).cumprod().iloc[-1]
    mevduat_top = (mevduat_carpan - 1) * 100
    sonuc['karsilastirmalar'].append({
        'isim': 'Mevduat (dinamik RF)',
        'toplam': mevduat_top, 'avantaj': fon_top - mevduat_top
    })

    enf_top = ((1 + enflasyon_yillik) ** yil - 1) * 100
    sonuc['karsilastirmalar'].append({
        'isim': 'Enflasyon', 'toplam': enf_top, 'avantaj': fon_top - enf_top
    })

    endeks_kod, endeks_isim = kategoriye_gore_endeks_kodu(kategori)
    endeks_df = None
    if endeks_kod and endeks_kod in makro_dict:
        edf = makro_dict[endeks_kod].copy()
        edf = edf[edf['date'] >= fon_df['date'].iloc[0]]
        if len(edf) >= 30:
            e_top = (edf['price'].iloc[-1] / edf['price'].iloc[0] - 1) * 100
            sonuc['karsilastirmalar'].append({
                'isim': endeks_isim, 'toplam': e_top,
                'avantaj': fon_top - e_top, 'endeks_df': edf
            })
            endeks_df = edf
    return sonuc, endeks_df


# ================= 13. WALK-FORWARD BACKTEST (PROGRESS DESTEKLİ) =================
def walk_forward_backtest(df_tam, enflasyon, gecmis_gun_sayisi,
                          adim_is_gunu=None, senaryo_sayisi=None,
                          progress_callback=None,
                          tarihsel_enf_kullan=True):
    """
    İşlem günü tabanlı walk-forward backtest.

    progress_callback: opsiyonel callable. (current, total, mesaj) ile çağrılır.
    UI'da progress bar göstermek için kullanılır. None ise sessiz çalışır.

    tarihsel_enf_kullan: True ise (varsayılan), her test noktasında O TARİHTEKİ
    enflasyon beklentisi kullanılır (lookahead bias'sız). False ise üst seviyede
    geçilen `enflasyon` parametresi tüm test noktalarında sabit uygulanır
    (eski v10 davranışı — karşılaştırma için bırakıldı).

    `enflasyon` parametresi tarihsel mod kapalıyken (veya beklenti serisi
    eksikse) fallback olarak kullanılır.
    """
    if senaryo_sayisi is None:
        senaryo_sayisi = C.MC_BACKTEST_SENARYO
    n = len(df_tam)

    if n < C.BACKTEST_MIN_GUN:
        return {'hata': f"Geçmiş veri çok kısa: {n} işlem günü. Backtest için en az "
                        f"{C.BACKTEST_MIN_GUN} işlem günü gerekli. Sidebar'dan 'Geçmiş veri' "
                        f"değerini artırın (en az 500 gün önerilir)."}

    egitim_is_gun = int(n * C.BACKTEST_EGITIM_ORANI)
    tahmin_ufku_is = min(C.BACKTEST_TAHMIN_MAX,
                         max(C.BACKTEST_TAHMIN_MIN, int(n * C.BACKTEST_TAHMIN_ORANI)))

    if adim_is_gunu is None:
        adim_is_gunu = max(C.BACKTEST_ADIM_MIN, n // C.BACKTEST_ADIM_BOLEN)

    ilk_idx = egitim_is_gun
    son_idx = n - tahmin_ufku_is - 1

    if ilk_idx >= son_idx:
        return {'hata': f"Veri pencereye sığmıyor. n={n}, eğitim={egitim_is_gun}, tahmin ufku={tahmin_ufku_is}."}

    test_indeksleri = list(range(ilk_idx, son_idx + 1, adim_is_gunu))
    if len(test_indeksleri) < C.BACKTEST_MIN_TEST_NOKTASI:
        return {'hata': f"Test noktası sayısı çok az ({len(test_indeksleri)}). Daha uzun 'Geçmiş veri' seçin."}

    # YENİ: Tarihsel enflasyon beklentisi serisini bir kerede hazırla
    if tarihsel_enf_kullan:
        enf_serisi = tarihsel_enflasyon_beklentisi(df_tam['date'])
    else:
        enf_serisi = None

    sonuclar = []
    hata_sayaci = 0
    son_hata = None
    toplam = len(test_indeksleri)

    for sira, idx in enumerate(test_indeksleri):
        if progress_callback is not None:
            try:
                progress_callback(sira + 1, toplam, f"Test {sira+1}/{toplam}")
            except Exception:
                pass

        df_gecmis = df_tam.iloc[:idx + 1].copy()
        if len(df_gecmis) < C.BACKTEST_MIN_VERI_GUN:
            continue

        tarih = df_gecmis['date'].iloc[-1]
        rf_o_tarih = dinamik_risksiz_faiz_serisi(pd.DatetimeIndex([tarih])).iloc[0]

        # YENİ: O tarihte geçerli olan enflasyon beklentisi (lookahead bias düzeltmesi)
        if enf_serisi is not None:
            enf_o_tarih = float(enf_serisi.iloc[idx])
        else:
            enf_o_tarih = enflasyon

        try:
            son_fiyat, mu, sigma = gunluk_istatistik(df_gecmis)
            if pd.isna(mu) or pd.isna(sigma) or sigma == 0:
                continue

            rejim_stat = rejim_mu_sigma(df_gecmis, rf_o_tarih)
            trend = trend_rejimi(df_gecmis, rf_o_tarih)
            rejim_mu_v = rejim_stat[trend['rejim']]['mu']
            rejim_sigma_v = rejim_stat[trend['rejim']]['sigma']

            if pd.isna(rejim_mu_v) or pd.isna(rejim_sigma_v) or rejim_sigma_v == 0:
                rejim_mu_v = mu
                rejim_sigma_v = sigma

            senaryolar = monte_carlo_motoru(
                son_fiyat, mu, sigma, rejim_mu_v, rejim_sigma_v,
                enf_o_tarih, gun_sayisi=tahmin_ufku_is,
                senaryo_sayisi=senaryo_sayisi
            )
        except Exception as e:
            hata_sayaci += 1
            son_hata = str(e)
            continue

        son_gun = senaryolar[-1, :]
        p5, p50, p95 = np.percentile(son_gun, [5, 50, 95])

        hedef_idx = idx + tahmin_ufku_is
        if hedef_idx >= n:
            continue

        gercek_satir = df_tam.iloc[hedef_idx]
        gun_farki = (gercek_satir['date'] - tarih).days
        if gun_farki <= 0:
            continue

        # Reel gerçek: o dönemin enflasyon beklentisi ile deflate edilir
        # (gerçekleşen enflasyon kullanılsa lookahead bias olurdu)
        enf_kayip = (1 + enf_o_tarih) ** (gun_farki / 365) - 1
        reel_gercek = gercek_satir['price'] / (1 + enf_kayip)

        sonuclar.append({
            'test_tarihi': tarih,
            'p5': float(p5), 'p50': float(p50), 'p95': float(p95),
            'reel_gercek': float(reel_gercek),
            'baslangic': float(son_fiyat),
            'bant_ici': bool(p5 <= reel_gercek <= p95),
            'yon_dogru': bool((p50 > son_fiyat) == (reel_gercek > son_fiyat)),
            'sapma_yuzde': float((reel_gercek - p50) / p50 * 100),
            'rejim': trend['rejim'],
            'enf_o_tarih': float(enf_o_tarih),  # Şeffaflık için kaydet
        })

    if progress_callback is not None:
        try:
            progress_callback(toplam, toplam, "Tamamlandı")
        except Exception:
            pass

    if not sonuclar:
        msg = f"Hiçbir test noktası tamamlanamadı (denenmiş: {toplam}, hata: {hata_sayaci})."
        if son_hata:
            msg += f" Son hata: {son_hata}"
        return {'hata': msg}

    return {
        'sonuclar': pd.DataFrame(sonuclar),
        'egitim_gun': egitim_is_gun,
        'tahmin_ufku_takvim': int(tahmin_ufku_is * 365/252),
        'tahmin_ufku_is': tahmin_ufku_is,
        'test_sayisi': len(sonuclar),
        'denenen_test': toplam,
        'hata_sayisi': hata_sayaci,
    }


# ================= 14. STANDART BACKTEST SKORU =================
def standart_backtest_skoru(backtest_dict):
    if backtest_dict is None or 'sonuclar' not in backtest_dict or backtest_dict['sonuclar'].empty:
        return None

    df = backtest_dict['sonuclar']
    tahmin_ufku_is = backtest_dict['tahmin_ufku_is']

    ham_bant = float(df['bant_ici'].mean() * 100)
    ham_yon = float(df['yon_dogru'].mean() * 100)
    medyan_sapma = float(df['sapma_yuzde'].abs().median())

    yillik_esdeger_sapma = medyan_sapma / np.sqrt(tahmin_ufku_is / 252) if tahmin_ufku_is > 0 else medyan_sapma

    bant_skoru = min(100, (ham_bant / C.BACKTEST_BANT_HEDEF_PCT) * 100)
    yon_skoru = max(0, (ham_yon - 50) * 2)
    sapma_skoru = max(0, min(100, 100 - yillik_esdeger_sapma * C.BACKTEST_SAPMA_CARPAN))

    standart_skor = float(
        bant_skoru * C.BACKTEST_BANT_AGIRLIK
        + yon_skoru * C.BACKTEST_YON_AGIRLIK
        + sapma_skoru * C.BACKTEST_SAPMA_AGIRLIK
    )

    if standart_skor >= C.KALITE_COK_IYI:   kalite = "Çok iyi"
    elif standart_skor >= C.KALITE_IYI:     kalite = "İyi"
    elif standart_skor >= C.KALITE_VASAT:   kalite = "Vasat"
    elif standart_skor >= C.KALITE_ZAYIF:   kalite = "Zayıf"
    else:                                    kalite = "Çok zayıf"

    return {
        'ham_bant': ham_bant,
        'ham_yon': ham_yon,
        'medyan_sapma': medyan_sapma,
        'yillik_esdeger_sapma': yillik_esdeger_sapma,
        'bant_skoru': float(bant_skoru),
        'yon_skoru': float(yon_skoru),
        'sapma_skoru': float(sapma_skoru),
        'standart_skor': standart_skor,
        'kalite': kalite,
    }


# ================= ANA ANALİZ FONKSİYONU =================
def tam_analiz(fon_kodu, gun_sayisi=1000, beklenen_enflasyon=0.45,
               enflasyon_sigma=0.13, makro_kullan=True, senaryo_sayisi=None,
               backtest_calistir=True, backtest_senaryo=None,
               backtest_progress_callback=None,
               df=None, makro_dict=None):
    """
    Tam analiz akışı.

    `df` parametresi: önceden çekilmiş fon verisi. Verilirse TEFAS'a tekrar
    gidilmez (cache zincirini bağlamak için). None ise içeride fon_verisi_getir
    çağrılır.

    `makro_dict` parametresi: önceden çekilmiş Yahoo Finance verileri. Benzer
    şekilde çift çağrıyı önler.
    """
    if senaryo_sayisi is None:
        senaryo_sayisi = C.MC_VARSAYILAN_SENARYO
    if backtest_senaryo is None:
        backtest_senaryo = C.MC_BACKTEST_SENARYO

    # 1. Veri — verilmediyse çek
    if df is None:
        df = fon_verisi_getir(fon_kodu, gun_sayisi=gun_sayisi)
    son_fiyat, mu, sigma = gunluk_istatistik(df)
    fon_adi = df['title'].iloc[-1] if 'title' in df.columns else "Bilinmiyor"
    kategori, kategori_ad = fon_kategorisi_belirle(df)
    guncel_rf = guncel_risksiz_faiz()

    # 2. Makro — verilmediyse çek
    if makro_dict is None:
        makro_dict = {}
        if makro_kullan and YF_VAR:
            bas_str = df['date'].iloc[0].strftime("%Y-%m-%d")
            bit_str = df['date'].iloc[-1].strftime("%Y-%m-%d")
            makro_dict = makro_verileri_getir(bas_str, bit_str)

    # 3. Benchmark
    bench_sonuc, endeks_df = benchmark_karsilastir(df, kategori, beklenen_enflasyon, makro_dict)

    # 4. Beta / Alpha (vektörize)
    beta_alpha = None
    rolling_ba = None
    if endeks_df is not None and len(endeks_df) >= 60:
        beta_alpha = beta_alpha_endekse_karsi(df, endeks_df)
        rolling_ba = rolling_beta_alpha(df, endeks_df)
    rolling_sh = rolling_sharpe(df)

    # 5. Sinyaller
    z_skor, konum_skor, konum_yorum = rolling_z_skor(df, pencere=252)
    trend = trend_rejimi(df, guncel_rf)
    rejim_stat = rejim_mu_sigma(df, guncel_rf)
    guncel_rejim_mu    = rejim_stat[trend['rejim']]['mu']
    guncel_rejim_sigma = rejim_stat[trend['rejim']]['sigma']
    rejim_uyari = rejim_degisim_uyarisi(df)
    rsi = rsi_skoru(df)
    risk = risk_metrikleri(df)

    # 6. Monte Carlo
    senaryolar = monte_carlo_motoru(
        son_fiyat, mu, sigma, guncel_rejim_mu, guncel_rejim_sigma,
        beklenen_enflasyon, enflasyon_sigma,
        senaryo_sayisi=senaryo_sayisi
    )
    son_gun = senaryolar[-1, :]
    p5, p50, p95 = np.percentile(son_gun, [5, 50, 95])
    zarar_ihtimal = float((son_gun < son_fiyat).mean() * 100)

    # 7. Sinyal grupları
    alpha_yil = beta_alpha['alpha_yillik_yuzde'] if beta_alpha else None
    info_r    = beta_alpha['information_ratio'] if beta_alpha else None
    sinyal = sinyal_gruplari_uret(
        z_skor, trend['sma_skor'], rsi['skor'],
        risk['sharpe'], risk['guncel_drawdown'],
        alpha_yil, info_r,
        rejim_uyari_siddet=rejim_uyari['siddet']
    )

    # 8. Backtest
    backtest = None
    backtest_skor = None
    backtest_hata = None
    if backtest_calistir:
        try:
            backtest_raw = walk_forward_backtest(
                df, beklenen_enflasyon, gun_sayisi,
                senaryo_sayisi=backtest_senaryo,
                progress_callback=backtest_progress_callback
            )
            if backtest_raw is not None and 'hata' in backtest_raw:
                backtest_hata = backtest_raw['hata']
            elif backtest_raw is not None:
                backtest = backtest_raw
                backtest_skor = standart_backtest_skoru(backtest)
        except Exception as e:
            backtest_hata = f"Beklenmeyen hata: {e}"

    return {
        'fon_kodu': fon_kodu,
        'fon_adi': fon_adi,
        'kategori': kategori,
        'kategori_ad': kategori_ad,
        'guncel_rf': guncel_rf,
        'son_fiyat': float(son_fiyat),
        'gun_sayisi': len(df),
        'baslangic_tarih': df['date'].iloc[0],
        'bitis_tarih': df['date'].iloc[-1],
        'df': df,
        'makro_dict': makro_dict,
        'endeks_df': endeks_df,
        'bench_sonuc': bench_sonuc,
        'beta_alpha': beta_alpha,
        'rolling_ba': rolling_ba,
        'rolling_sh': rolling_sh,
        'z_skor': z_skor,
        'konum_yorum': konum_yorum,
        'trend': trend,
        'rejim_stat': rejim_stat,
        'rejim_uyari': rejim_uyari,
        'rsi': rsi,
        'risk': risk,
        'senaryolar': senaryolar,
        'p5': float(p5), 'p50': float(p50), 'p95': float(p95),
        'zarar_ihtimal': zarar_ihtimal,
        'sinyal': sinyal,
        'backtest': backtest,
        'backtest_skor': backtest_skor,
        'backtest_hata': backtest_hata,
    }
