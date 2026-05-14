"""
TEFAS Fon Analiz Aracı — Konfigürasyon Sabitleri
=================================================
Tüm eşik değerleri, ağırlıklar ve sihirli sayılar burada toplandı.
İleride strateji ayarı yapmak için sadece bu dosyayı değiştirmek yeterli.

Kurallar:
- Hiçbir hesaplama yok, sadece sabitler
- Yüzdeler ondalık olarak (0.45 = %45)
- Pencereler ve gün sayıları int
- Grup başlıkları içinde mantıksal olarak sıralı

DEĞİŞİKLİK NOTU (v12):
- Backtest oranları yeniden dengelendi. Önceki 2/3 - 1/3 ayarı 800 gün
  gibi yaygın bir veri uzunluğunda yalnızca 1 test noktası üretiyordu;
  bu da `BACKTEST_MIN_TEST_NOKTASI=3` eşiğinin altında kaldığı için
  backtest sessizce iptal oluyordu. Yeni oranlar (3/5 eğitim, 1/5
  tahmin, tahmin ufku 60-180 iş günü) 500+ gün için en az 4 test
  noktası üretiyor.
"""

# ============================================================
# VERİ / PERFORMANS
# ============================================================
CACHE_TTL_SANIYE = 3600              # Streamlit cache geçerlilik süresi (1 saat)
CACHE_TTL_GUNLUK = 86400             # Risksiz faiz gibi günde 1 değişen veriler (24 saat)
CACHE_MAX_ENTRIES = 5                # Bellek sınırı — kaç farklı analiz aynı anda cache'te tutulsun

# ============================================================
# RİSKSİZ FAİZ (TÜRKİYE — TCMB politika faizi tarihçesi)
# ============================================================
# Kaynak: TCMB EVDS, "TP.AOFOD2" haftalık repo faizi.
# Bu liste EVDS API'si erişilemediğinde fallback olarak kullanılır.
RISKSIZ_FAIZ_TARIHCE = [
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

# ============================================================
# TARİHSEL ENFLASYON BEKLENTİSİ (BACKTEST İÇİN)
# ============================================================
# Backtest'te o tarihte geçerli olan enflasyon BEKLENTİSİ kullanılmalı,
# bugünkü beklenti değil (lookahead bias). TCMB Piyasa Katılımcıları
# Anketi'nden 12-ay ileri TÜFE beklentisi yıllık ortalama olarak alındı.
# Kaynak: TCMB Beklenti Anketi (TP.BEK.S02.A.B12)
ENFLASYON_BEKLENTI_TARIHCE = [
    ("2018-01-01", 0.090), ("2018-07-01", 0.115), ("2018-12-01", 0.155),
    ("2019-06-01", 0.140), ("2019-12-01", 0.105),
    ("2020-06-01", 0.095), ("2020-12-01", 0.110),
    ("2021-06-01", 0.135), ("2021-12-01", 0.215),
    ("2022-06-01", 0.355), ("2022-12-01", 0.245),
    ("2023-06-01", 0.295), ("2023-12-01", 0.420),
    ("2024-06-01", 0.380), ("2024-12-01", 0.275),
    ("2025-06-01", 0.225), ("2025-12-01", 0.205),
    ("2026-04-01", 0.185),
]

# ============================================================
# REJİM TESPİTİ (trend_rejimi, rejim_mu_sigma)
# ============================================================
TREND_KISA_PENCERE = 90              # 90 işlem günü (~4.5 ay) eğim regresyonu
TREND_MIN_GUN = 30                   # Minimum veri gereği
TREND_YUKSELIS_ESIK_PUAN = 15        # rf + 15 puan üstü → YÜKSELİŞ
TREND_DUSUS_ESIK_PUAN = -10          # rf - 10 puan altı → DÜŞÜŞ
SMA_KISA = 50                        # Kısa hareketli ortalama
SMA_UZUN = 200                       # Uzun hareketli ortalama

# Rejim mu/sigma penceresi
REJIM_GERIYE_PENCERE = 90
REJIM_BASLANGIC_GUN = 60             # İlk 60 gün YETERSİZ kalır
REJIM_MIN_GOZLEM = 20                # Rejim bazlı istatistik için min gün

# ============================================================
# REJİM DEĞİŞİM UYARISI (rejim_degisim_uyarisi)
# ============================================================
REJIM_KISA_PENCERE = 30              # Son 30 gün volatilite
REJIM_UZUN_PENCERE = 252             # Tarihsel 1 yıl
VOL_PATLAMA_ESIK = 2.0               # 2x volatilite → kritik uyarı
VOL_ARTIS_ESIK = 1.5                 # 1.5x → orta uyarı
MU_KIRILMA_ESIK_PUAN = 30            # Yıllık getiri kırılması, mutlak puan
SIDDET_KRITIK = 3                    # >= 3 → "Rejim değişimi muhtemel"
SIDDET_ORTA = 1                      # >= 1 → "Anormal davranış"

# ============================================================
# RSI EŞİKLERİ
# ============================================================
RSI_PENCERE = 14
RSI_ASIRI_ALIM_YUKSEK = 80
RSI_ASIRI_ALIM = 70
RSI_NOTR_UST = 50
RSI_NOTR_ALT = 30
RSI_ASIRI_SATIM_DUSUK = 20

# ============================================================
# MONTE CARLO
# ============================================================
MC_VARSAYILAN_SENARYO = 5000
MC_BACKTEST_SENARYO = 3000
MC_T_DAGILIM_DF = 6                  # Student-t serbestlik derecesi (kalın kuyruk)
MC_REJIM_AGIRLIK_MU = 0.70           # mu'da rejim ağırlığı (genel mu için 0.30)
MC_REJIM_AGIRLIK_SIGMA = 0.60        # sigma'da rejim ağırlığı (genel için 0.40)

# ============================================================
# Z-SKOR / TREND DEĞERLEME
# ============================================================
Z_SKOR_PENCERE = 252                 # 1 yıl
Z_SKOR_MIN_GUN = 60

# Skor → konum yorumu eşikleri (z değerinde)
Z_ZIRVE = 2.0
Z_PAHALI = 1.0
Z_UCUZ = -1.0
Z_DIP = -2.0

# ============================================================
# SHARPE / SİNYAL EŞİKLERİ
# ============================================================
SHARPE_MUKEMMEL = 2.0                # > 2 → 100 puan
SHARPE_IYI = 1.0                     # > 1 → 75
SHARPE_ORTA = 0.5                    # > 0.5 → 60
SHARPE_POZITIF = 0.0                 # > 0 → 45

# Drawdown sinyali (negatif yüzdeler — gerçek drawdown değerleri)
DD_HAFIF = -5.0
DD_ORTA = -10.0
DD_AGIR = -20.0

# Alpha eşikleri (yıllık %)
ALPHA_MUKEMMEL = 10.0
ALPHA_IYI = 5.0
ALPHA_POZITIF = 0.0
ALPHA_HAFIF_NEG = -5.0
ALPHA_NEGATIF = -10.0

# Information Ratio eşikleri
IR_MUKEMMEL = 0.75
IR_IYI = 0.50
IR_ORTA = 0.25
IR_POZITIF = 0.0
IR_HAFIF_NEG = -0.25

# ============================================================
# ROLLING PENCERELER
# ============================================================
ROLLING_BETA_PENCERE = 126           # ~6 ay
ROLLING_SHARPE_PENCERE = 126
ROLLING_MIN_EK_GUN = 30              # pencere + 30 minimum gözlem

# ============================================================
# BACKTEST PARAMETRELERİ
# ============================================================
# v12 dengelemesi: 500+ gün için en az 4 test noktası garantilenir.
# Önceki ayar (2/3 eğitim, 1/3 tahmin, tahmin_max=252) tahmin ufkunu
# 252'ye sıkıştırıp test aralığını çok daraltıyordu. Yeni ayar daha
# kısa tahmin ufku ile daha çok pencere üretiyor.
#
# Beklenen test noktası sayısı:
#   n=500  → 4
#   n=800  → 4
#   n=1000 → 5
#   n=1500 → 6
#   n=2000 → 7
BACKTEST_MIN_GUN = 250
BACKTEST_EGITIM_ORANI = 3/5          # %60 eğitim (önce 2/3)
BACKTEST_TAHMIN_ORANI = 1/5          # %20 tahmin ufku (önce 1/3)
BACKTEST_TAHMIN_MIN = 60             # En az 3 ay iş günü (önce 20 — çok gürültülü)
BACKTEST_TAHMIN_MAX = 180            # En fazla ~9 ay iş günü (önce 252)
BACKTEST_ADIM_BOLEN = 20             # n // 20 → kaç adımda bir test (önce 25)
BACKTEST_ADIM_MIN = 15               # Çok sık örnekleme → otokorelasyon (önce 10)
BACKTEST_MIN_TEST_NOKTASI = 3
BACKTEST_MIN_VERI_GUN = 200          # df_gecmis için minimum

# Standart backtest skoru ağırlıkları (toplam = 1.0)
BACKTEST_BANT_AGIRLIK = 0.50
BACKTEST_YON_AGIRLIK = 0.30
BACKTEST_SAPMA_AGIRLIK = 0.20

# Skor hedefleri
BACKTEST_BANT_HEDEF_PCT = 90         # %90 bant kapsama tam puan
BACKTEST_SAPMA_CARPAN = 1.5          # Yıllık sapma * 1.5 puan kaybı

# Kalite eşikleri
KALITE_COK_IYI = 75
KALITE_IYI = 60
KALITE_VASAT = 45
KALITE_ZAYIF = 30

# ============================================================
# GENEL SİNYAL SKOR EŞİKLERİ
# ============================================================
SKOR_COK_GUCLU = 70
SKOR_GUCLU = 58
SKOR_KARISIK = 45
SKOR_ZAYIF = 32
