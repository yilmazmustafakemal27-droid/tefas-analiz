# TEFAS Fon Analiz Aracı

TEFAS'ta listelenen yatırım fonlarını istatistiksel olarak analiz eden web tabanlı eğitim aracı.

## ⚠️ Yasal Uyarı

Bu uygulama **eğitim ve araştırma amaçlıdır**. **Yatırım tavsiyesi DEĞİLDİR.** SPK lisanslı bir yatırım danışmanına başvurmadan yatırım kararı vermeyin.

## Özellikler

- **Fon analizi**: TEFAS'tan canlı fiyat verisi çekme
- **Risk metrikleri**: Sharpe, Sortino, drawdown, volatilite
- **Endeks karşılaştırması**: BIST100, S&P 500, USD/TRY, Altın'a karşı alpha/beta
- **Monte Carlo**: 1 yıl reel getiri simülasyonu (10K senaryo, stokastik enflasyon)
- **Sinyal grupları**: Değerleme, Trend, Risk, Aktif Yönetim (4 grup, eşit ağırlık)
- **Rolling metrikler**: 6 aylık beta/alpha/IR/Sharpe değişimleri

## Yerel Kurulum

```bash
# 1. Sanal ortam (opsiyonel ama tavsiye edilir)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Çalıştır
streamlit run app.py
```

Uygulama `http://localhost:8501` adresinde açılır.

## Streamlit Cloud'a Yayınlama (Ücretsiz)

1. Bu klasörü bir GitHub reposuna push edin (public veya private fark etmez)
2. [share.streamlit.io](https://share.streamlit.io) adresine girin
3. GitHub ile bağlanın → "New app" → reponuzu seçin
4. Main file path: `app.py`
5. Deploy

5 dakikada canlıya alabilirsiniz. Ücretsiz tier yeterli (~1000 saatlik aylık kullanım).

## Dosya Yapısı

```
tefas_app/
├── app.py              # Streamlit UI (frontend)
├── analiz.py           # Analiz motoru (backend, UI'dan bağımsız)
├── requirements.txt    # Python bağımlılıkları
├── .streamlit/
│   └── config.toml     # Tema ayarları
└── README.md
```

## Mimari Notlar

- `analiz.py` UI'dan tamamen ayrıdır. Herhangi bir CLI veya başka frontend'den de import edilebilir.
- TEFAS-crawler ve yfinance kullanılır.
- Streamlit'in cache mekanizması kullanılmadı (her analiz baştan yapılır). Trafik artarsa `@st.cache_data` ile cache eklenebilir.

## Yol Haritası

- [x] Yol 1: Eğitim aracı (mevcut)
- [ ] Kullanıcı oturumu (favori fonlar, izleme listesi)
- [ ] Veritabanı cache (Postgres / SQLite) — TEFAS gecikmesini azaltmak için
- [ ] Çoklu fon karşılaştırması (portföy analizi)
- [ ] Lisanslı sürüm (SPK uyumu sonrası premium özellikler)

## Lisans ve Sorumluluk

Bu yazılım "olduğu gibi" sunulur. Kullanımından doğacak finansal kayıplardan yazılım yazarı sorumlu değildir.
