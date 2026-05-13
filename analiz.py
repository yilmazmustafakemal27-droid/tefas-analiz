"""
TEFAS Fon Analiz Motoru
========================
Streamlit UI'dan bağımsız, import edilebilir analiz modülü.
Tüm fonksiyonlar saf — yan etki yok, print yok.

v9 GÜNCELLEMELERİ:
- walk_forward_backtest düzeltildi (işlem günü tabanlı, anlamlı hata mesajları)
- Backtest neden çalışmadığını söyleyen 'hata' alanı eklendi
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from tefas import Crawler

try:
    import yfinance as yf
    YF_VAR = True
except ImportError:
    YF_VAR = False


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
def dinamik_risksiz_faiz_serisi(tarih_indeksi):
    tarihsel = [
        ("2018-01-01", 0.08),  ("2018-06-01", 0.175),
        ("2019-01-01", 0.24),  ("2019-07-01", 0.195),
        ("2020-01-01", 0.115), ("2020-09-01", 0.105),
        ("2021-01-01", 0.17),  ("2021-09-01", 0.18),  ("2021-12-01", 0.14),
        ("2022-06-01", 0.14),  ("2022-12-01", 0.09),
        ("2023-06-01", 0.15),  ("2023-09-01", 0.30),  ("2023-12-01", 0.425),
        ("2024-04-01", 0.50),  ("2024-12-01", 0.475),
        ("2025-04-01", 0.46),  ("2025-12-01", 0.40),
        ("2026-04-01", 0.36),
    ]
    df_faiz = pd.DataFrame(tarihsel, columns=['date', 'faiz'])
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


# ================= 3. KATEGORİ + BENCHMARK =================
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


# ================= 4. MAKRO VERİ =================
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
            d['getiri'] = d['price'].pct_change()
            sonuclar[isim] = d
        except Exception:
            continue

    if 'ALTIN_USD' in sonuclar and 'USDTRY' in sonuclar:
        au = sonuclar['ALTIN_USD'][['date', 'price']].rename(columns={'price': 'au'})
        ut = sonuclar['USDTRY'][['date', 'price']].rename(columns={'price': 'ut'})
        m = au.merge(ut, on='date', how='inner').dropna()
        m['price'] = m['au'] * m['ut']
        m['getiri'] = m['price'].pct_change()
        sonuclar['ALTIN_TRY'] = m[['date', 'price', 'getiri']]
    return sonuclar

# ================= 5. ROLLING Z-SKOR =================
def rolling_z_skor(df, pencere=252):
    son = df['price'].tail(pencere).dropna().values
    if len(son) < 60:
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
    if z > 2:    yorum = "Zirve bölgesi"
    elif z > 1:  yorum = "Pahalı"
    elif z > -1: yorum = "Adil değer"
    elif z > -2: yorum = "Ucuz"
    else:        yorum = "Dip bölgesi"
    return float(z), skor, yorum


# ================= 6. TREND =================
def trend_rejimi(df, rf_yillik):
    df = df.copy()
    df['SMA_50']  = df['price'].rolling(50).mean()
    df['SMA_200'] = df['price'].rolling(200).mean()
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

    son_90 = df['price'].tail(90).dropna().values
    if len(son_90) >= 30:
        slope, _, r_value, _, _ = stats.linregress(np.arange(len(son_90)), np.log(son_90))
        yillik_egim = slope * 252 * 100
        trend_gucu = r_value ** 2
    else:
        yillik_egim, trend_gucu = 0, 0

    rf_pct = rf_yillik * 100
    if yillik_egim > rf_pct + 15:    rejim = "YÜKSELİŞ"
    elif yillik_egim > rf_pct - 10:  rejim = "YATAY"
    else:                            rejim = "DÜŞÜŞ"

    return {'rejim': rejim, 'sma_sinyali': sma_sinyali, 'sma_skor': sma_skor,
            'yillik_egim_yuzde': yillik_egim, 'trend_gucu_r2': trend_gucu}


def rejim_mu_sigma(df, rf_yillik):
    df = df.copy()
    n = len(df)
    etiketler = ["YETERSİZ"] * n
    fiyatlar = df['price'].values
    rf_pct = rf_yillik * 100

    for i in range(60, n):
        pencere = fiyatlar[max(0, i-90):i]
        pencere = pencere[~np.isnan(pencere)]
        if len(pencere) < 30:
            continue
        x = np.arange(len(pencere))
        slope, _, _, _, _ = stats.linregress(x, np.log(pencere))
        yil_egim = slope * 252 * 100
        if yil_egim > rf_pct + 15:    etiketler[i] = "YÜKSELİŞ"
        elif yil_egim > rf_pct - 10:  etiketler[i] = "YATAY"
        else:                          etiketler[i] = "DÜŞÜŞ"

    df['rejim'] = etiketler
    rejim_stat = {}
    for r in ["YÜKSELİŞ", "YATAY", "DÜŞÜŞ"]:
        f = df[df['rejim'] == r]['getiri'].dropna()
        if len(f) >= 20:
            rejim_stat[r] = {'mu': f.mean(), 'sigma': f.std(), 'n': len(f)}
        else:
            rejim_stat[r] = {'mu': df['getiri'].mean(),
                            'sigma': df['getiri'].std(), 'n': 0}
    return rejim_stat


# ================= 7. REJİM UYARI =================
def rejim_degisim_uyarisi(df, kisa=30, uzun=252):
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
    if vol_oran > 2.0:
        siddet += 2; uyarilar.append(f"Volatilite patlaması: {vol_oran:.1f}x")
    elif vol_oran > 1.5:
        siddet += 1; uyarilar.append(f"Volatilite artışı: {vol_oran:.1f}x")
    if abs(mu_fark) > 30:
        siddet += 2; uyarilar.append(f"Trend kırılması: {mu_fark:+.0f} puan")

    if siddet >= 3:   karar = "Rejim değişimi muhtemel"
    elif siddet >= 1: karar = "Anormal davranış"
    else:             karar = "Normal"

    return {'siddet': siddet, 'son_vol': son_vol, 'tar_vol': tar_vol,
            'vol_orani': vol_oran, 'mu_fark': mu_fark,
            'uyarilar': uyarilar, 'karar': karar}


# ================= 8. RSI + RİSK =================
def rsi_skoru(df):
    delta = df['price'].diff()
    kazanc = delta.where(delta > 0, 0).rolling(14).mean()
    kayip  = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = kazanc / kayip
    rsi = (100 - 100 / (1 + rs)).iloc[-1]
    if pd.isna(rsi):
        return {'rsi': None, 'skor': 50, 'yorum': "N/A"}
    if rsi > 80:   s, y = 15, "Aşırı alım (yüksek)"
    elif rsi > 70: s, y = 35, "Aşırı alım"
    elif rsi > 50: s, y = 65, "Pozitif"
    elif rsi > 30: s, y = 50, "Negatif"
    elif rsi > 20: s, y = 75, "Aşırı satım"
    else:          s, y = 90, "Aşırı satım (düşük)"
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
        neg = fazla[fazla < 0]
        downside = neg.std() if len(neg) > 0 else np.std(fazla)
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
    birlesik = fon_df[['date', 'getiri']].rename(columns={'getiri': 'fon_g'}).merge(
        endeks_df[['date', 'getiri']].rename(columns={'getiri': 'bench_g'}),
        on='date', how='inner'
    ).dropna()
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


def rolling_beta_alpha(fon_df, endeks_df, pencere=126):
    birlesik = fon_df[['date', 'getiri']].rename(columns={'getiri': 'fon_g'}).merge(
        endeks_df[['date', 'getiri']].rename(columns={'getiri': 'bench_g'}),
        on='date', how='inner'
    ).dropna().reset_index(drop=True)
    if len(birlesik) < pencere + 30:
        return None
    rb, ra, ri, t = [], [], [], []
    for i in range(pencere, len(birlesik)):
        p = birlesik.iloc[i-pencere:i]
        slope, intercept, _, _, _ = stats.linregress(p['bench_g'], p['fon_g'])
        rb.append(slope)
        ra.append(((1 + intercept) ** 252 - 1) * 100)
        a = p['fon_g'] - p['bench_g']
        ri.append((a.mean() * 252) / (a.std() * np.sqrt(252)) if a.std() > 0 else 0)
        t.append(birlesik['date'].iloc[i])
    return pd.DataFrame({'date': t, 'beta': rb, 'alpha_yillik': ra, 'info_ratio': ri})


def rolling_sharpe(fon_df, pencere=126):
    df = fon_df.copy().dropna(subset=['getiri'])
    if len(df) < pencere + 30:
        return None
    rf_serisi = dinamik_risksiz_faiz_serisi(df['date'])
    rf_gunluk = (1 + rf_serisi) ** (1/252) - 1
    fazla = df['getiri'].values - rf_gunluk.values
    rs, t = [], []
    for i in range(pencere, len(df)):
        f = fazla[i-pencere:i]
        s = np.std(f)
        rs.append(np.mean(f) / s * np.sqrt(252) if s > 0 else 0)
        t.append(df['date'].iloc[i])
    return pd.DataFrame({'date': t, 'sharpe': rs})


# ================= 10. MONTE CARLO =================
def monte_carlo_motoru(baslangic_fiyati, mu_genel, sigma_genel,
                      rejim_mu, rejim_sigma,
                      enflasyon_orani, enflasyon_sigma_yillik=0.13,
                      gun_sayisi=252, senaryo_sayisi=10000, df_t=6):
    duzeltilmis_mu    = mu_genel * 0.30 + rejim_mu * 0.70
    duzeltilmis_sigma = sigma_genel * 0.40 + rejim_sigma * 0.60
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

    if sharpe > 2:    sh = 100
    elif sharpe > 1:  sh = 75
    elif sharpe > 0.5:sh = 60
    elif sharpe > 0:  sh = 45
    else:             sh = 25
    if drawdown_guncel > -5:    dd = 50
    elif drawdown_guncel > -10: dd = 60
    elif drawdown_guncel > -20: dd = 70
    else:                       dd = 80
    grup_risk = (sh + dd) / 2

    if alpha_yillik is None: alpha_skor = 50
    elif alpha_yillik > 10:  alpha_skor = 90
    elif alpha_yillik > 5:   alpha_skor = 75
    elif alpha_yillik > 0:   alpha_skor = 60
    elif alpha_yillik > -5:  alpha_skor = 40
    elif alpha_yillik > -10: alpha_skor = 25
    else:                    alpha_skor = 10
    if info_ratio is None:   ir_skor = 50
    elif info_ratio > 0.75:  ir_skor = 90
    elif info_ratio > 0.5:   ir_skor = 75
    elif info_ratio > 0.25:  ir_skor = 60
    elif info_ratio > 0:     ir_skor = 50
    elif info_ratio > -0.25: ir_skor = 35
    else:                    ir_skor = 20
    grup_aktif = (alpha_skor + ir_skor) / 2

    gruplar = {
        'Değerleme': float(grup_degerleme),
        'Trend':     float(grup_trend),
        'Risk':      float(grup_risk),
        'Aktif Yön.': float(grup_aktif),
    }
    skor_ham = float(np.mean(list(gruplar.values())))

    if rejim_uyari_siddet >= 3:
        skor = skor_ham * 0.5 + 50 * 0.5
        guven = "Düşük (rejim değişimi sinyali)"
    elif rejim_uyari_siddet >= 1:
        skor = skor_ham * 0.75 + 50 * 0.25
        guven = "Orta"
    else:
        skor = skor_ham
        guven = "Normal"
    skor = float(np.clip(skor, 0, 100))

    if skor >= 70:   etiket = "Çok güçlü göstergeler"
    elif skor >= 58: etiket = "Güçlü göstergeler"
    elif skor >= 45: etiket = "Karışık göstergeler"
    elif skor >= 32: etiket = "Zayıf göstergeler"
    else:            etiket = "Çok zayıf göstergeler"

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


# ================= 13. WALK-FORWARD BACKTEST (DÜZELTİLDİ — İŞLEM GÜNÜ TABANLI) =================
def walk_forward_backtest(df_tam, enflasyon, gecmis_gun_sayisi,
                          adim_is_gunu=None, senaryo_sayisi=3000):
    """
    DÜZELTİLDİ: Artık tamamen İŞLEM GÜNÜ tabanında çalışır.
    Önceki sürümde takvim günü/işlem günü karışıklığı vardı.

    Mantık:
    - Mevcut veri satır sayısı (n) üzerinden hesaplanır
    - Eğitim penceresi:  n * 2/3 işlem günü
    - Tahmin ufku:       n * 1/3 işlem günü (en fazla 252 = 1 yıl)
    - Test adımı:        n / 25 (minimum 10 işlem günü)

    Her test noktasında SADECE o satıra kadarki veri kullanılır.

    Return:
        dict (başarılı) veya {'hata': '...'} (başarısız neden bilgisiyle)
    """
    n = len(df_tam)

    # Minimum veri kontrolü — çok agresif değil
    if n < 250:
        return {'hata': f"Geçmiş veri çok kısa: {n} işlem günü. Backtest için en az 250 işlem günü gerekli. "
                        f"Sidebar'dan 'Geçmiş veri' değerini artırın (en az 500 gün önerilir)."}

    # İşlem günü tabanlı pencereler
    egitim_is_gun = int(n * 2/3)
    tahmin_ufku_is = min(252, max(20, int(n * 1/3)))  # 1 yılla sınırla

    if adim_is_gunu is None:
        adim_is_gunu = max(10, n // 25)

    # Test edilecek başlangıç indeksleri (satır numaraları)
    # Eğitim sonrası başla, son test noktası + tahmin ufku < n olsun
    ilk_idx = egitim_is_gun
    son_idx = n - tahmin_ufku_is - 1

    if ilk_idx >= son_idx:
        return {'hata': f"Veri pencereye sığmıyor. n={n}, eğitim={egitim_is_gun}, tahmin ufku={tahmin_ufku_is}. "
                        f"Sidebar'dan daha uzun 'Geçmiş veri' seçin."}

    test_indeksleri = list(range(ilk_idx, son_idx + 1, adim_is_gunu))
    if len(test_indeksleri) < 3:
        return {'hata': f"Test noktası sayısı çok az ({len(test_indeksleri)}). Daha uzun 'Geçmiş veri' seçin."}

    sonuclar = []
    hata_sayaci = 0
    son_hata = None

    for idx in test_indeksleri:
        df_gecmis = df_tam.iloc[:idx + 1].copy()
        if len(df_gecmis) < 200:
            continue

        tarih = df_gecmis['date'].iloc[-1]
        rf_o_tarih = dinamik_risksiz_faiz_serisi(pd.DatetimeIndex([tarih])).iloc[0]

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
                enflasyon, gun_sayisi=tahmin_ufku_is,
                senaryo_sayisi=senaryo_sayisi
            )
        except Exception as e:
            hata_sayaci += 1
            son_hata = str(e)
            continue

        son_gun = senaryolar[-1, :]
        p5, p50, p95 = np.percentile(son_gun, [5, 50, 95])

        # Gerçek değer — tahmin ufku kadar ileri git (işlem günü cinsinden)
        hedef_idx = idx + tahmin_ufku_is
        if hedef_idx >= n:
            continue

        gercek_satir = df_tam.iloc[hedef_idx]
        gun_farki = (gercek_satir['date'] - tarih).days
        if gun_farki <= 0:
            continue

        enf_kayip = (1 + enflasyon) ** (gun_farki / 365) - 1
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
        })

    if not sonuclar:
        msg = f"Hiçbir test noktası tamamlanamadı (denenmiş: {len(test_indeksleri)}, hata: {hata_sayaci})."
        if son_hata:
            msg += f" Son hata: {son_hata}"
        return {'hata': msg}

    return {
        'sonuclar': pd.DataFrame(sonuclar),
        'egitim_gun': egitim_is_gun,
        'tahmin_ufku_takvim': int(tahmin_ufku_is * 365/252),
        'tahmin_ufku_is': tahmin_ufku_is,
        'test_sayisi': len(sonuclar),
        'denenen_test': len(test_indeksleri),
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

    bant_skoru = min(100, (ham_bant / 90) * 100)
    yon_skoru = max(0, (ham_yon - 50) * 2)
    sapma_skoru = max(0, min(100, 100 - yillik_esdeger_sapma * 1.5))

    standart_skor = float(bant_skoru * 0.5 + yon_skoru * 0.3 + sapma_skoru * 0.2)

    if standart_skor >= 75:   kalite = "Çok iyi"
    elif standart_skor >= 60: kalite = "İyi"
    elif standart_skor >= 45: kalite = "Vasat"
    elif standart_skor >= 30: kalite = "Zayıf"
    else:                     kalite = "Çok zayıf"

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
               enflasyon_sigma=0.13, makro_kullan=True, senaryo_sayisi=5000,
               backtest_calistir=True, backtest_senaryo=3000):
    # 1. Veri
    df = fon_verisi_getir(fon_kodu, gun_sayisi=gun_sayisi)
    son_fiyat, mu, sigma = gunluk_istatistik(df)
    fon_adi = df['title'].iloc[-1] if 'title' in df.columns else "Bilinmiyor"
    kategori, kategori_ad = fon_kategorisi_belirle(df)
    guncel_rf = guncel_risksiz_faiz()

    # 2. Makro
    makro_dict = {}
    if makro_kullan and YF_VAR:
        bas_str = df['date'].iloc[0].strftime("%Y-%m-%d")
        bit_str = df['date'].iloc[-1].strftime("%Y-%m-%d")
        makro_dict = makro_verileri_getir(bas_str, bit_str)

    # 3. Benchmark
    bench_sonuc, endeks_df = benchmark_karsilastir(df, kategori, beklenen_enflasyon, makro_dict)

    # 4. Beta / Alpha
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

    # 8. Walk-forward backtest
    backtest = None
    backtest_skor = None
    backtest_hata = None
    if backtest_calistir:
        try:
            backtest_raw = walk_forward_backtest(
                df, beklenen_enflasyon, gun_sayisi,
                senaryo_sayisi=backtest_senaryo
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
