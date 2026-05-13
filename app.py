"""
TEFAS Fon Analiz Aracı — Web Uygulaması (v11)
==============================================
v11 GÜNCELLEMELERİ:
- Cache zinciri düzeltildi: fon verisi tekil çağrılıp tam_analiz'a paslanıyor
- session_state manuel cache takibi kaldırıldı (Streamlit @st.cache_data yeterli)
- max_entries=5 eklendi (bellek sınırı)
- Magic number'lar config.py'de
- EVDS API key Streamlit secrets'tan okunabilir
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

import analiz
import config as C
from aciklamalar import (
    aciklamali_metrik, popover_aciklama, aciklama_expander,
    aciklama_inline, dinamik_aciklama
)


# ================= SAYFA AYARLARI =================
st.set_page_config(
    page_title="TEFAS Fon Analiz Aracı",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "TEFAS verilerini analiz eden eğitim amaçlı araç. Yatırım tavsiyesi DEĞİLDİR."
    }
)


# ================= CSS =================
st.markdown("""
<style>
    h1 {
        font-family: Georgia, 'Times New Roman', serif;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1a1a1a;
    }
    h2, h3 {
        font-family: Georgia, serif;
        font-weight: 500;
        color: #2a2a2a;
    }
    .disclaimer-box {
        background: linear-gradient(90deg, #FFF8E7 0%, #FEF3D9 100%);
        border-left: 3px solid #C77D2A;
        padding: 14px 18px;
        margin: 12px 0;
        border-radius: 4px;
        font-size: 0.875rem;
        color: #5A4A1F;
    }
    [data-testid="metric-container"] {
        background: #FAFAF7;
        border: 1px solid #E8E5DD;
        padding: 16px;
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .footer-disclaimer {
        margin-top: 40px;
        padding: 20px;
        background: #FAF7F0;
        border-top: 2px solid #D4A574;
        font-size: 0.85rem;
        color: #4A5560;
        line-height: 1.6;
    }
    [data-testid="stSidebar"] {
        background: #FAFAF7;
    }
    .stTextInput input {
        font-family: 'Courier New', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stPopover"] button {
        padding: 4px 8px !important;
        min-height: 32px !important;
        font-size: 1rem !important;
    }
    .cache-info {
        background: #E8F4F8;
        border-left: 3px solid #0F4C81;
        padding: 8px 14px;
        font-size: 0.82rem;
        color: #2a4a5e;
        border-radius: 4px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ================= CACHE'LENMİŞ FONKSİYONLAR =================
# Strateji: analiz.py saf kalıyor (UI bağımlılığı yok).
# Cache app.py'de — fon verisi ve makro veriler bağımsız cache'leniyor,
# tam_analiz onları parametre olarak alıyor (cache zinciri korunur).

@st.cache_data(ttl=C.CACHE_TTL_SANIYE, show_spinner=False, max_entries=C.CACHE_MAX_ENTRIES)
def cache_fon_verisi(fon_kodu: str, gun_sayisi: int):
    """TEFAS fon verisini 1 saat cache'le."""
    return analiz.fon_verisi_getir(fon_kodu, gun_sayisi=gun_sayisi)


@st.cache_data(ttl=C.CACHE_TTL_SANIYE, show_spinner=False, max_entries=C.CACHE_MAX_ENTRIES)
def cache_makro_veriler(bas_str: str, bit_str: str):
    """Yahoo Finance makro verilerini 1 saat cache'le."""
    return analiz.makro_verileri_getir(bas_str, bit_str)


@st.cache_data(
    ttl=C.CACHE_TTL_SANIYE, show_spinner=False, max_entries=C.CACHE_MAX_ENTRIES,
    hash_funcs={pd.DataFrame: lambda df: (len(df), df['date'].iloc[0], df['date'].iloc[-1],
                                          df['price'].iloc[-1])}
)
def cache_tam_analiz_with_df(fon_kodu, gun_sayisi, beklenen_enflasyon, enflasyon_sigma,
                              senaryo_sayisi, backtest_calistir, backtest_senaryo,
                              df, makro_dict_kullan):
    """
    Tam analizi cache'le. df ve makro_dict üst seviyede ayrıca cache'lendiği için
    burada parametre olarak alınıp tam_analiz'a paslanır — çift TEFAS/YF çağrısı
    önlenir. df için custom hash: tarih aralığı + son fiyat (içerik tam karşılaştırması
    yerine yeterli imza).

    Backtest progress callback BURADA YOK — çünkü cache anahtarına UI nesnesi giremez.
    Backtest çalıştırılacaksa cache miss durumunda ayrı bir runner kullanılır.
    """
    # Makro verileri — aynı df aralığı için tekrar cache'lenmiş halini al
    if makro_dict_kullan:
        bas_str = df['date'].iloc[0].strftime("%Y-%m-%d")
        bit_str = df['date'].iloc[-1].strftime("%Y-%m-%d")
        makro_dict = cache_makro_veriler(bas_str, bit_str)
    else:
        makro_dict = {}

    return analiz.tam_analiz(
        fon_kodu=fon_kodu,
        gun_sayisi=gun_sayisi,
        beklenen_enflasyon=beklenen_enflasyon,
        enflasyon_sigma=enflasyon_sigma,
        makro_kullan=makro_dict_kullan,
        senaryo_sayisi=senaryo_sayisi,
        backtest_calistir=backtest_calistir,
        backtest_senaryo=backtest_senaryo,
        backtest_progress_callback=None,
        df=df,
        makro_dict=makro_dict,
    )


def calistir_analiz_progressli(fon_kodu, gun_sayisi, beklenen_enflasyon, enflasyon_sigma,
                                makro_kullan, senaryo_sayisi, backtest_calistir, backtest_senaryo):
    """
    Akış:
      1. Fon verisini cache'ten al (cache miss ise TEFAS'a tek sefer git)
      2. Backtest YOKSA → cache_tam_analiz_with_df çağır (tam cache hit/miss otomatik)
      3. Backtest VARSA → Streamlit cache anahtarına progress callback giremediği için
         doğrudan analiz.tam_analiz çağrılır (her seferinde hesaplanır). df ve makro
         hâlâ alt-seviye cache'lerden gelir, sadece backtest döngüsü tekrar koşar.
         Bu kabul edilebilir: kullanıcı zaten "yeni backtest" istemiş demektir.
    """
    # 1. Fon verisini çek (cache'li)
    df = cache_fon_verisi(fon_kodu, gun_sayisi)

    if not backtest_calistir:
        # Backtest yok → tam cache yolu
        return cache_tam_analiz_with_df(
            fon_kodu=fon_kodu,
            gun_sayisi=gun_sayisi,
            beklenen_enflasyon=beklenen_enflasyon,
            enflasyon_sigma=enflasyon_sigma,
            senaryo_sayisi=senaryo_sayisi,
            backtest_calistir=False,
            backtest_senaryo=backtest_senaryo,
            df=df,
            makro_dict_kullan=makro_kullan,
        )

    # 2. Backtest var → progress bar göster, alt-seviye cache'lerden faydalan
    if makro_kullan:
        bas_str = df['date'].iloc[0].strftime("%Y-%m-%d")
        bit_str = df['date'].iloc[-1].strftime("%Y-%m-%d")
        makro_dict = cache_makro_veriler(bas_str, bit_str)
    else:
        makro_dict = {}

    progress_alani = st.empty()
    progress_bar = progress_alani.progress(0.0, text="Backtest hazırlanıyor...")

    def progress_cb(current, total, mesaj):
        if total > 0:
            progress_bar.progress(min(current / total, 1.0),
                                  text=f"⏳ Backtest: {mesaj}")

    sonuc = analiz.tam_analiz(
        fon_kodu=fon_kodu, gun_sayisi=gun_sayisi,
        beklenen_enflasyon=beklenen_enflasyon,
        enflasyon_sigma=enflasyon_sigma,
        makro_kullan=makro_kullan,
        senaryo_sayisi=senaryo_sayisi,
        backtest_calistir=True,
        backtest_senaryo=backtest_senaryo,
        backtest_progress_callback=progress_cb,
        df=df,
        makro_dict=makro_dict,
    )
    progress_alani.empty()
    return sonuc


# ================= BAŞLIK + DİSCLAİMER =================
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("# TEFAS Fon Analiz Aracı")
    st.markdown(
        "<p style='color: #5A6A7A; font-size: 1.05rem; font-style: italic; margin-top: -10px;'>"
        "Türkiye'deki yatırım fonlarını istatistiksel olarak inceleyin"
        "</p>",
        unsafe_allow_html=True
    )
with col_t2:
    st.markdown(
        "<div style='text-align: right; padding-top: 20px;'>"
        f"<small style='color: #888;'>Veri kaynağı: TEFAS + Yahoo Finance<br>"
        f"Tarih: {datetime.now().strftime('%d.%m.%Y')}</small>"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown("""
<div class="disclaimer-box">
<strong>⚠️ Yasal Uyarı:</strong> Bu araç <strong>eğitim ve araştırma amaçlıdır</strong>.
Yatırım tavsiyesi, danışmanlığı veya öneri içermez.
Yatırım kararlarınız için <strong>SPK lisanslı bir yatırım danışmanına</strong> başvurunuz.
</div>
""", unsafe_allow_html=True)


# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### Analiz Parametreleri")

    fon_kodu = st.text_input(
        "Fon Kodu (3 harf)",
        value="THV",
        max_chars=3,
        help="Örn: THV, AFA, GPB."
    ).upper().strip()

    gun_sayisi = st.select_slider(
        "Geçmiş veri (gün)",
        options=[365, 500, 750, 1000, 1500, 1825],
        value=1000,
    )

    egt_g = int(gun_sayisi * 2/3)
    tah_g = int(gun_sayisi * 1/3)
    st.caption(f"📊 Backtest: **{egt_g}g** eğitim → **{tah_g}g** tahmin")

    st.markdown("---")
    st.markdown("### Beklentiler")

    enflasyon = st.slider("Beklenen yıllık enflasyon (%)",
        min_value=10.0, max_value=80.0, value=45.0, step=2.5) / 100
    enf_belirsizlik = st.slider("Enflasyon belirsizliği (σ, %)",
        min_value=5.0, max_value=25.0, value=13.0, step=1.0) / 100

    st.markdown("---")
    st.markdown("### Gelişmiş")

    senaryo_sayisi = st.select_slider("Monte Carlo senaryo sayısı",
        options=[1000, 2000, 5000, 10000], value=C.MC_VARSAYILAN_SENARYO)

    backtest_calistir = st.checkbox("Walk-forward backtest çalıştır", value=True)
    makro_kullan = st.checkbox("Makro veri kullan (Yahoo Finance)", value=True)

    st.markdown("---")
    analiz_basla = st.button("🔍 Analizi Başlat", type="primary", use_container_width=True)

    # Cache temizleme düğmesi
    if st.button("🔄 Cache'i Temizle", use_container_width=True,
                help="TEFAS ve Yahoo verilerini taze çek. Veri güncellendiyse kullanın."):
        st.cache_data.clear()
        st.success("✓ Cache temizlendi. Bir sonraki analizde veri taze çekilecek.")

    st.markdown("---")
    with st.expander("ℹ️ Bu araç ne yapar?"):
        st.markdown("""
        **Yapar:**
        - TEFAS'tan fon fiyat verisini çeker (1 saat cache)
        - Volatilite, Sharpe, drawdown hesaplar
        - Endeks ile karşılaştırır (alpha, beta)
        - Monte Carlo simülasyonu
        - Walk-forward backtest

        **Yapmaz:**
        - Yatırım tavsiyesi vermez
        - "AL/SAT" demez
        """)


# ================= ANA İÇERİK =================
if not analiz_basla:
    st.markdown("### Nasıl Kullanılır?")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**1. Fon kodu girin**\n\n3 harfli TEFAS fon kodu (örn: THV, AFA, IPB).")
    with col_b:
        st.markdown("**2. Parametreleri ayarlayın**\n\nEnflasyon beklentinizi ve veri uzunluğunu seçin.")
    with col_c:
        st.markdown("**3. Sonuçları yorumlayın**\n\nHer metriğin yanında **(?) ikonu** var.")

    st.markdown(
        '<div class="cache-info">💡 <strong>Hız ipucu:</strong> Analiz sonuçları 1 saat cache\'lenir. '
        'Aynı parametrelerle tekrar çalıştırırsanız anında gelir. Veriyi tazelemek için '
        'sidebar\'daki "Cache\'i Temizle" düğmesini kullanabilirsiniz.</div>',
        unsafe_allow_html=True
    )

else:
    if not fon_kodu or len(fon_kodu) != 3:
        st.error("Lütfen 3 harfli geçerli bir fon kodu girin (örn: THV).")
        st.stop()

    # Analizi başlat (cache veya progress'li gerçek hesaplama)
    bilgi_kutusu = st.empty()
    bilgi_kutusu.info(f"📡 {fon_kodu} analizi başlatılıyor...")

    try:
        sonuc = calistir_analiz_progressli(
            fon_kodu=fon_kodu,
            gun_sayisi=gun_sayisi,
            beklenen_enflasyon=enflasyon,
            enflasyon_sigma=enf_belirsizlik,
            makro_kullan=makro_kullan,
            senaryo_sayisi=senaryo_sayisi,
            backtest_calistir=backtest_calistir,
            backtest_senaryo=C.MC_BACKTEST_SENARYO,
        )
        bilgi_kutusu.empty()
    except ValueError as e:
        bilgi_kutusu.empty()
        st.error(f"❌ {e}")
        st.info("İpucu: Fon kodu büyük harf, 3 karakter olmalı.")
        st.stop()
    except Exception as e:
        bilgi_kutusu.empty()
        st.error(f"Beklenmeyen hata: {e}")
        st.stop()

    # ================= ÜST ÖZET =================
    st.markdown(f"## {sonuc['fon_kodu']} — {sonuc['fon_adi']}")
    st.markdown(
        f"<p style='color: #5A6A7A; margin-top: -10px;'>"
        f"<strong>{sonuc['kategori_ad']}</strong> • "
        f"{sonuc['gun_sayisi']} işlem günü • "
        f"{sonuc['baslangic_tarih'].strftime('%d.%m.%Y')} – {sonuc['bitis_tarih'].strftime('%d.%m.%Y')}"
        f"</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Son Fiyat", f"{sonuc['son_fiyat']:.4f}")
    with col2:
        aciklamali_metrik("Yıllık Getiri", f"{sonuc['bench_sonuc']['fon_yillik']:+.1f}%",
            "yillik_getiri", sonuc['bench_sonuc']['fon_yillik'],
            delta=f"Toplam: %{sonuc['bench_sonuc']['fon_toplam']:+.1f}")
    with col3:
        aciklamali_metrik("Sharpe Oranı", f"{sonuc['risk']['sharpe']:.2f}",
                          "sharpe", sonuc['risk']['sharpe'])
    with col4:
        aciklamali_metrik("Yıllık Volatilite", f"{sonuc['risk']['yillik_oynaklik']:.1f}%",
                          "volatilite", sonuc['risk']['yillik_oynaklik'])
    with col5:
        aciklamali_metrik("Güncel Düşüş", f"{sonuc['risk']['guncel_drawdown']:.1f}%",
                          "guncel_drawdown", sonuc['risk']['guncel_drawdown'])

    if sonuc['rejim_uyari']['siddet'] >= 1:
        renk = "#B83A3A" if sonuc['rejim_uyari']['siddet'] >= 3 else "#C77D2A"
        col_uy1, col_uy2 = st.columns([20, 1])
        with col_uy1:
            st.markdown(
                f"<div style='background: #FFF3E0; border-left: 3px solid {renk}; "
                f"padding: 10px 14px; margin: 10px 0; border-radius: 4px;'>"
                f"<strong style='color: {renk};'>📡 {sonuc['rejim_uyari']['karar']}</strong><br>"
                f"<small>{' • '.join(sonuc['rejim_uyari']['uyarilar'])}</small>"
                f"</div>", unsafe_allow_html=True)
        with col_uy2:
            st.markdown("<div style='padding-top: 18px;'></div>", unsafe_allow_html=True)
            popover_aciklama("rejim_uyarisi", sonuc['rejim_uyari']['siddet'],
                            karar=sonuc['rejim_uyari']['karar'])

    # ================= TABLAR =================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Genel Bakış", "🎯 Sinyaller", "📈 Karşılaştırma",
        "🎲 Monte Carlo", "🕰️ Backtest", "📋 Detay Tablo"
    ])

    # ----- TAB 1: GENEL BAKIŞ -----
    with tab1:
        st.markdown("### Fiyat Geçmişi ve Trend")
        df = sonuc['df']

        fig_fiyat = go.Figure()
        fig_fiyat.add_trace(go.Scatter(x=df['date'], y=df['price'], mode='lines',
            name='Fiyat', line=dict(color='#0F4C81', width=2)))
        if len(df) >= 252:
            son_252 = df.tail(252)
            log_p = np.log(son_252['price'].values)
            x_arr = np.arange(len(log_p))
            from scipy import stats as sp_stats
            slope, intercept, _, _, _ = sp_stats.linregress(x_arr, log_p)
            trend = np.exp(slope * x_arr + intercept)
            fig_fiyat.add_trace(go.Scatter(x=son_252['date'], y=trend, mode='lines',
                name='252g log-trend', line=dict(color='#D4A574', width=2, dash='dash')))
        fig_fiyat.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="", yaxis_title="Fiyat (TL)",
            plot_bgcolor='#FAFAF7', paper_bgcolor='white',
            legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1))
        st.plotly_chart(fig_fiyat, use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Trend & Konum**")
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Konum (Z-skor): **{sonuc['z_skor']:+.2f}** → {sonuc['konum_yorum']}")
            with col_b:
                popover_aciklama("konum_yorum", sonuc['z_skor'], sonuc['konum_yorum'])

            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Trend rejimi: **{sonuc['trend']['rejim']}**")
            with col_b:
                popover_aciklama("trend", sonuc['trend']['rejim'])

            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- 90g yıllık eğim: **%{sonuc['trend']['yillik_egim_yuzde']:+.1f}**")
            with col_b:
                popover_aciklama("yillik_egim", sonuc['trend']['yillik_egim_yuzde'])

            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Trend gücü (R²): **{sonuc['trend']['trend_gucu_r2']:.2f}**")
            with col_b:
                popover_aciklama("trend_gucu", sonuc['trend']['trend_gucu_r2'])

            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- SMA sinyali: **{sonuc['trend']['sma_sinyali']}**")
            with col_b:
                popover_aciklama("sma_sinyali", sonuc['trend']['sma_sinyali'])

            if sonuc['rsi']['rsi'] is not None:
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(f"- RSI(14): **{sonuc['rsi']['rsi']:.1f}** — {sonuc['rsi']['yorum']}")
                with col_b:
                    popover_aciklama("rsi", sonuc['rsi']['rsi'])

        with col_r:
            st.markdown("**Risk Profili**")
            for satir_etiket, deger_str, terim_id, terim_deger in [
                ("Sharpe", f"**{sonuc['risk']['sharpe']:.2f}**", "sharpe", sonuc['risk']['sharpe']),
                ("Sortino", f"**{sonuc['risk']['sortino']:.2f}**", "sortino", sonuc['risk']['sortino']),
                ("Yıllık volatilite", f"**%{sonuc['risk']['yillik_oynaklik']:.1f}**", "volatilite", sonuc['risk']['yillik_oynaklik']),
                ("Maks düşüş", f"**%{sonuc['risk']['max_drawdown']:.1f}**", "max_drawdown", sonuc['risk']['max_drawdown']),
            ]:
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(f"- {satir_etiket}: {deger_str}")
                with col_b:
                    popover_aciklama(terim_id, terim_deger)
            st.markdown(f"- Risksiz faiz (güncel): **%{sonuc['risk']['guncel_rf_yillik']:.1f}**")

        col_rs1, col_rs2 = st.columns([20, 1])
        with col_rs1:
            st.markdown("**Rejim İstatistikleri**")
        with col_rs2:
            popover_aciklama("rejim_stat")

        rejim_data = []
        for r, s in sonuc['rejim_stat'].items():
            yil_mu = ((1 + s['mu']) ** 252 - 1) * 100
            yil_sig = s['sigma'] * np.sqrt(252) * 100
            rejim_data.append({
                'Rejim': r, 'Yıllık μ (%)': f"{yil_mu:+.1f}",
                'Yıllık σ (%)': f"{yil_sig:.1f}", 'Gözlem (gün)': s['n']
            })
        st.dataframe(pd.DataFrame(rejim_data), use_container_width=True, hide_index=True)

    # ----- TAB 2: SİNYALLER -----
    with tab2:
        st.markdown("### Sinyal Grupları")
        st.caption("Skorlar 0-100 arası bilgilendiricidir.")

        gruplar = sonuc['sinyal']['gruplar']
        renkler = ['#2E7D5C' if v >= 60 else '#C77D2A' if v >= 40 else '#B83A3A' for v in gruplar.values()]

        fig_sinyal = go.Figure(go.Bar(
            x=list(gruplar.values()), y=list(gruplar.keys()),
            orientation='h', marker=dict(color=renkler),
            text=[f"{v:.0f}" for v in gruplar.values()],
            textposition='outside', textfont=dict(size=14, color='#1a1a1a')))
        fig_sinyal.update_layout(height=300, margin=dict(l=10, r=40, t=10, b=30),
            xaxis=dict(range=[0, 110], showgrid=True, gridcolor='#E8E5DD', title="Skor (0-100)"),
            yaxis=dict(showgrid=False), plot_bgcolor='#FAFAF7',
            paper_bgcolor='white', showlegend=False)
        fig_sinyal.add_vline(x=50, line_dash="dot", line_color="#888")
        st.plotly_chart(fig_sinyal, use_container_width=True)

        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            skor = sonuc['sinyal']['toplam_skor']
            renk_skor = '#2E7D5C' if skor >= 58 else '#C77D2A' if skor >= 45 else '#B83A3A'
            st.markdown(
                f"<div style='text-align: center; padding: 30px; "
                f"background: linear-gradient(135deg, #FAFAF7 0%, #F0EDE3 100%); "
                f"border-radius: 8px; border: 1px solid #E8E5DD;'>"
                f"<div style='font-size: 0.85rem; color: #888; text-transform: uppercase; "
                f"letter-spacing: 0.1em; margin-bottom: 8px;'>Birleşik Skor</div>"
                f"<div style='font-size: 3.5rem; font-weight: 600; color: {renk_skor}; "
                f"font-family: Georgia, serif; line-height: 1;'>{skor:.0f}</div>"
                f"<div style='font-size: 0.95rem; color: #4A5560; margin-top: 8px;'>{sonuc['sinyal']['etiket']}</div>"
                f"<div style='font-size: 0.8rem; color: #888; margin-top: 4px;'>Güven: {sonuc['sinyal']['guven']}</div>"
                f"</div>", unsafe_allow_html=True)
            aciklama_expander("genel_skor", skor, etiket=sonuc['sinyal']['etiket'])

        with col_s2:
            st.markdown("**Skor Nasıl Yorumlanır?**")
            st.markdown("""
            - **70+** : Çok güçlü göstergeler
            - **58-70**: Güçlü göstergeler
            - **45-58**: Karışık göstergeler
            - **32-45**: Zayıf göstergeler
            - **0-32**: Çok zayıf göstergeler

            **Önemli:** Yüksek skor "AL" anlamına gelmez. Düşük skor "SAT" anlamına gelmez.
            """)

        if sonuc['rolling_ba'] is not None:
            st.markdown("---")
            col_rt1, col_rt2 = st.columns([20, 1])
            with col_rt1:
                st.markdown("### Zamana Göre Performans")
            with col_rt2:
                with st.popover("❓", help="Rolling metrikler ne demek?"):
                    st.markdown("#### Rolling Metrikler")
                    st.markdown(
                        "**Rolling metrik**, bir göstergenin **zaman içinde nasıl değiştiğini** "
                        "gösteren versiyonudur. Burada 6 aylık kayar pencere kullanılıyor.\n\n"
                        "💡 *Düz çizgi = tutarlı yönetim. Çok dalgalanan çizgi = stratejide değişimler.*"
                    )

            col_rb1, col_rb2, col_rb3 = st.columns(3)
            with col_rb1:
                popover_aciklama("rolling_beta", label="❓ Rolling Beta")
            with col_rb2:
                popover_aciklama("rolling_alpha", label="❓ Rolling Alpha")
            with col_rb3:
                popover_aciklama("rolling_ir", label="❓ Rolling IR")

            rba = sonuc['rolling_ba']
            fig_roll = make_subplots(rows=1, cols=3,
                subplot_titles=("Rolling Beta", "Rolling Alpha (yıllık %)", "Rolling IR"))
            fig_roll.add_trace(go.Scatter(x=rba['date'], y=rba['beta'],
                line=dict(color='#0F4C81', width=1.5), showlegend=False), row=1, col=1)
            fig_roll.add_hline(y=1.0, line_dash="dot", line_color="#888", row=1, col=1)
            fig_roll.add_trace(go.Scatter(x=rba['date'], y=rba['alpha_yillik'],
                line=dict(color='#7B4B94', width=1.5), showlegend=False), row=1, col=2)
            fig_roll.add_hline(y=0, line_dash="dot", line_color="#888", row=1, col=2)
            fig_roll.add_trace(go.Scatter(x=rba['date'], y=rba['info_ratio'],
                line=dict(color='#1A8B9D', width=1.5), showlegend=False), row=1, col=3)
            fig_roll.add_hline(y=0, line_dash="dot", line_color="#888", row=1, col=3)
            fig_roll.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=30),
                plot_bgcolor='#FAFAF7', paper_bgcolor='white')
            st.plotly_chart(fig_roll, use_container_width=True)

        if sonuc['rolling_sh'] is not None:
            col_rsh1, col_rsh2 = st.columns([20, 1])
            with col_rsh1:
                st.markdown("#### Rolling Sharpe")
            with col_rsh2:
                popover_aciklama("rolling_sharpe")

            rsh = sonuc['rolling_sh']
            fig_rsh = go.Figure()
            fig_rsh.add_trace(go.Scatter(x=rsh['date'], y=rsh['sharpe'],
                line=dict(color='#2E7D5C', width=1.5), showlegend=False))
            fig_rsh.add_hline(y=1.0, line_dash="dot", line_color="#888",
                            annotation_text="Sharpe = 1")
            fig_rsh.add_hline(y=0, line_dash="dot", line_color="#B83A3A")
            fig_rsh.update_layout(height=250, margin=dict(l=10, r=10, t=20, b=30),
                plot_bgcolor='#FAFAF7', paper_bgcolor='white', yaxis_title="Sharpe")
            st.plotly_chart(fig_rsh, use_container_width=True)

    # ----- TAB 3: KARŞILAŞTIRMA -----
    with tab3:
        st.markdown("### Endeks ve Benchmark Karşılaştırması")

        comp_data = []
        for k in sonuc['bench_sonuc']['karsilastirmalar']:
            comp_data.append({
                'Karşılaştırma': k['isim'],
                'Toplam Getiri': f"{k['toplam']:+.1f}%",
                'Fon Avantajı': f"{k['avantaj']:+.1f}%",
                'Durum': '✓ Üstte' if k['avantaj'] > 0 else '✗ Altta'
            })
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        if sonuc['endeks_df'] is not None:
            st.markdown(f"#### Kümülatif Getiri: Fon vs Endeks")
            fon_df = sonuc['df'].copy()
            endeks_df = sonuc['endeks_df'].copy()
            fon_df['kum'] = (fon_df['price'] / fon_df['price'].iloc[0] - 1) * 100
            endeks_df['kum'] = (endeks_df['price'] / endeks_df['price'].iloc[0] - 1) * 100

            fig_kum = go.Figure()
            fig_kum.add_trace(go.Scatter(x=fon_df['date'], y=fon_df['kum'],
                mode='lines', name=f"Fon ({sonuc['fon_kodu']})",
                line=dict(color='#0F4C81', width=2)))
            endeks_isim = analiz.kategoriye_gore_endeks_kodu(sonuc['kategori'])[1]
            fig_kum.add_trace(go.Scatter(x=endeks_df['date'], y=endeks_df['kum'],
                mode='lines', name=endeks_isim, line=dict(color='#D4A574', width=2)))
            fig_kum.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=30),
                yaxis_title="Kümülatif Getiri (%)",
                plot_bgcolor='#FAFAF7', paper_bgcolor='white',
                legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1))
            st.plotly_chart(fig_kum, use_container_width=True)

        if sonuc['beta_alpha']:
            st.markdown("#### Beta / Alpha Analizi")
            ba = sonuc['beta_alpha']
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                aciklamali_metrik("Beta", f"{ba['beta']:+.2f}", "beta", ba['beta'])
            with col_b2:
                aciklamali_metrik("Alpha (yıllık)", f"{ba['alpha_yillik_yuzde']:+.1f}%",
                                 "alpha", ba['alpha_yillik_yuzde'], delta=f"p={ba['p_value']:.3f}")
            with col_b3:
                aciklamali_metrik("R²", f"{ba['r_squared']:.2f}", "r_squared", ba['r_squared'])
            with col_b4:
                aciklamali_metrik("Information Ratio", f"{ba['information_ratio']:+.2f}",
                                 "info_ratio", ba['information_ratio'])

            st.markdown("---")
            col_te1, col_te2 = st.columns(2)
            with col_te1:
                aciklamali_metrik("Tracking Error (yıllık)", f"%{ba['tracking_error']:.1f}",
                                 "tracking_error", ba['tracking_error'])
            with col_te2:
                st.metric("Gözlem sayısı", f"{ba['gozlem_sayisi']}")
            st.info(f"**Özet:** {ba['alpha_yorum']}")

    # ----- TAB 4: MONTE CARLO -----
    with tab4:
        st.markdown("### 1 Yıl Sonrası Reel Getiri Simülasyonu")
        st.caption(f"{senaryo_sayisi:,} senaryo simüle edildi.")

        senaryolar = sonuc['senaryolar']
        gun_aralik = np.arange(senaryolar.shape[0])
        p5_yol = np.percentile(senaryolar, 5, axis=1)
        p50_yol = np.percentile(senaryolar, 50, axis=1)
        p95_yol = np.percentile(senaryolar, 95, axis=1)

        fig_mc = go.Figure()
        fig_mc.add_trace(go.Scatter(x=gun_aralik, y=p95_yol, mode='lines',
            line=dict(color='rgba(46,125,92,0.3)', width=0),
            showlegend=False, hoverinfo='skip'))
        fig_mc.add_trace(go.Scatter(x=gun_aralik, y=p5_yol, mode='lines',
            line=dict(color='rgba(46,125,92,0.3)', width=0),
            fill='tonexty', fillcolor='rgba(46,125,92,0.15)', name='P5–P95 bandı'))
        fig_mc.add_trace(go.Scatter(x=gun_aralik, y=p5_yol, mode='lines',
            name='P5 (kötü)', line=dict(color='#B83A3A', width=1.5, dash='dash')))
        fig_mc.add_trace(go.Scatter(x=gun_aralik, y=p50_yol, mode='lines',
            name='P50 (medyan)', line=dict(color='#0F4C81', width=2.5)))
        fig_mc.add_trace(go.Scatter(x=gun_aralik, y=p95_yol, mode='lines',
            name='P95 (iyi)', line=dict(color='#2E7D5C', width=1.5, dash='dash')))
        fig_mc.add_hline(y=sonuc['son_fiyat'], line_dash="dot", line_color="#888",
                        annotation_text=f"Bugün: {sonuc['son_fiyat']:.4f}")
        fig_mc.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="İşlem günü", yaxis_title="Reel fiyat",
            plot_bgcolor='#FAFAF7', paper_bgcolor='white',
            legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1))
        st.plotly_chart(fig_mc, use_container_width=True)

        st.markdown("#### 1 Yıl Sonrası Olasılık Dağılımı")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            getiri_p5 = (sonuc['p5'] / sonuc['son_fiyat'] - 1) * 100
            st.metric("Kötü senaryo (P5)", f"{getiri_p5:+.1f}%")
        with col_p2:
            getiri_p50 = (sonuc['p50'] / sonuc['son_fiyat'] - 1) * 100
            aciklamali_metrik("Medyan (P50)", f"{getiri_p50:+.1f}%",
                "p50_reel", sonuc['p50'], baslangic=sonuc['son_fiyat'])
        with col_p3:
            getiri_p95 = (sonuc['p95'] / sonuc['son_fiyat'] - 1) * 100
            st.metric("İyi senaryo (P95)", f"{getiri_p95:+.1f}%")
        with col_p4:
            aciklamali_metrik("Reel Kayıp İhtimali", f"%{sonuc['zarar_ihtimal']:.0f}",
                "reel_kayip", sonuc['zarar_ihtimal'])

    # ----- TAB 5: BACKTEST -----
    with tab5:
        st.markdown("### Walk-Forward Backtest")
        st.caption("Sistemin geçmiş tahminlerini gerçek değerlerle karşılaştırır.")

        bt = sonuc['backtest']
        bs = sonuc['backtest_skor']
        bt_hata = sonuc.get('backtest_hata')

        if bt is None:
            if bt_hata:
                st.error(f"❌ **Backtest çalıştırılamadı:**\n\n{bt_hata}")
                aciklama_expander("backtest_hata", bt_hata)
            elif not backtest_calistir:
                st.info("ℹ️ Backtest kapalı. Sidebar'dan 'Walk-forward backtest çalıştır' kutusunu işaretle.")
            else:
                st.warning("⚠️ Backtest sonuç üretmedi.")
        else:
            st.success(f"✅ Backtest tamamlandı: **{bt['test_sayisi']} test noktası** "
                      f"(denenen: {bt.get('denenen_test', '?')}, atlanan: {bt.get('hata_sayisi', 0)})")

            st.markdown(f"""
            - Eğitim verisi: **{bt['egitim_gun']} işlem günü**
            - Tahmin ufku: **{bt['tahmin_ufku_is']} işlem günü**
            - Test sayısı: **{bt['test_sayisi']}**
            """)

            if bs is not None:
                col_st1, col_st2 = st.columns([1, 2])
                with col_st1:
                    skor_renk = ('#2E7D5C' if bs['standart_skor'] >= 60
                                else '#C77D2A' if bs['standart_skor'] >= 45 else '#B83A3A')
                    st.markdown(
                        f"<div style='text-align: center; padding: 30px; "
                        f"background: linear-gradient(135deg, #FAFAF7 0%, #F0EDE3 100%); "
                        f"border-radius: 8px; border: 1px solid #E8E5DD;'>"
                        f"<div style='font-size: 0.85rem; color: #888;'>Standart Skor</div>"
                        f"<div style='font-size: 3.5rem; font-weight: 600; color: {skor_renk}; "
                        f"font-family: Georgia, serif;'>{bs['standart_skor']:.0f}</div>"
                        f"<div style='font-size: 0.95rem; color: #4A5560;'>{bs['kalite']}</div>"
                        f"</div>", unsafe_allow_html=True)
                    aciklama_expander("standart_skor", bs['standart_skor'], kalite=bs['kalite'])

                with col_st2:
                    st.markdown("**Neden 'Standart Skor'?**")
                    st.markdown(f"""
                    Farklı tahmin ufukları doğrudan karşılaştırılamaz. **Standart skor** sapmayı
                    √t kuralıyla yıllık eşdeğere çevirir.

                    Mevcut ayar: {bt['tahmin_ufku_is']} işlem günü
                    """)

            st.markdown("---")
            st.markdown("#### Ham Sonuçlar")
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                aciklamali_metrik("Bant Kapsama", f"%{bs['ham_bant']:.0f}",
                                 "backtest_bant", bs['ham_bant'], delta="Hedef: %90")
            with col_h2:
                aciklamali_metrik("Yön Doğruluğu", f"%{bs['ham_yon']:.0f}",
                                 "backtest_yon", bs['ham_yon'], delta="Random: %50")
            with col_h3:
                st.metric("Medyan Sapma", f"%{bs['medyan_sapma']:.1f}",
                         delta=f"Yıllık eşdeğer: %{bs['yillik_esdeger_sapma']:.1f}")

            st.markdown("---")
            st.markdown("#### Tahmin vs Gerçek")

            df_bt = bt['sonuclar']
            fig_bt = make_subplots(rows=1, cols=2,
                subplot_titles=("P50 vs Gerçek", "Zaman İçinde Sapma"),
                column_widths=[0.55, 0.45])

            renkler_scatter = ['#2E7D5C' if x else '#B83A3A' for x in df_bt['bant_ici']]
            fig_bt.add_trace(go.Scatter(x=df_bt['p50'], y=df_bt['reel_gercek'], mode='markers',
                marker=dict(color=renkler_scatter, size=8, opacity=0.7,
                           line=dict(color='white', width=1)),
                text=[f"Test: {d.strftime('%Y-%m')}<br>Rejim: {r}<br>Sapma: %{s:+.1f}"
                      for d, r, s in zip(df_bt['test_tarihi'], df_bt['rejim'], df_bt['sapma_yuzde'])],
                hovertemplate='%{text}<br>P50: %{x:.3f}<br>Gerçek: %{y:.3f}<extra></extra>',
                showlegend=False), row=1, col=1)
            mn = min(df_bt['p50'].min(), df_bt['reel_gercek'].min())
            mx = max(df_bt['p50'].max(), df_bt['reel_gercek'].max())
            fig_bt.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode='lines',
                line=dict(color='#888', dash='dash', width=1),
                showlegend=False, hoverinfo='skip'), row=1, col=1)

            fig_bt.add_trace(go.Bar(x=df_bt['test_tarihi'], y=df_bt['sapma_yuzde'],
                marker=dict(color=['#2E7D5C' if x else '#B83A3A' for x in df_bt['bant_ici']]),
                showlegend=False), row=1, col=2)
            fig_bt.add_hline(y=0, line_dash="dot", line_color="#888", row=1, col=2)

            fig_bt.update_xaxes(title_text="P50 Tahmin", row=1, col=1)
            fig_bt.update_yaxes(title_text="Gerçek", row=1, col=1)
            fig_bt.update_xaxes(title_text="Test Tarihi", row=1, col=2)
            fig_bt.update_yaxes(title_text="Sapma (%)", row=1, col=2)
            fig_bt.update_layout(height=400, margin=dict(l=10, r=10, t=50, b=30),
                plot_bgcolor='#FAFAF7', paper_bgcolor='white')
            st.plotly_chart(fig_bt, use_container_width=True)

            st.caption("🟢 Yeşil: bant içinde. 🔴 Kırmızı: bant dışında.")

            with st.expander(f"📋 Tüm {bt['test_sayisi']} test noktasının detayı"):
                df_gosterim = df_bt.copy()
                df_gosterim['test_tarihi'] = df_gosterim['test_tarihi'].dt.strftime('%Y-%m-%d')
                for kol in ['p5', 'p50', 'p95', 'reel_gercek', 'baslangic']:
                    df_gosterim[kol] = df_gosterim[kol].round(3)
                df_gosterim['sapma_yuzde'] = df_gosterim['sapma_yuzde'].round(1)
                df_gosterim['bant_ici'] = df_gosterim['bant_ici'].map({True: '✓', False: '✗'})
                df_gosterim['yon_dogru'] = df_gosterim['yon_dogru'].map({True: '↑', False: '↓'})
                df_gosterim = df_gosterim.rename(columns={
                    'test_tarihi': 'Tarih', 'baslangic': 'Başlangıç',
                    'p5': 'P5', 'p50': 'P50', 'p95': 'P95',
                    'reel_gercek': 'Gerçek', 'sapma_yuzde': 'Sapma %',
                    'bant_ici': 'Bant', 'yon_dogru': 'Yön', 'rejim': 'Rejim'})
                st.dataframe(df_gosterim, use_container_width=True, hide_index=True)

    # ----- TAB 6: DETAY TABLO -----
    with tab6:
        st.markdown("### Tüm Metrikler")

        detay = {
            'Genel': {
                'Fon kodu': sonuc['fon_kodu'],
                'Fon adı': sonuc['fon_adi'],
                'Kategori': sonuc['kategori_ad'],
                'Veri başlangıç': sonuc['baslangic_tarih'].strftime('%d.%m.%Y'),
                'Veri bitiş': sonuc['bitis_tarih'].strftime('%d.%m.%Y'),
                'Toplam işlem günü': sonuc['gun_sayisi'],
                'Son fiyat': f"{sonuc['son_fiyat']:.4f}",
            },
            'Getiri': {
                'Toplam getiri': f"{sonuc['bench_sonuc']['fon_toplam']:+.2f}%",
                'Yıllık ortalama getiri': f"{sonuc['bench_sonuc']['fon_yillik']:+.2f}%",
                'Süre (yıl)': f"{sonuc['bench_sonuc']['sure_yil']:.2f}",
            },
            'Risk': {
                'Yıllık volatilite': f"{sonuc['risk']['yillik_oynaklik']:.2f}%",
                'Sharpe oranı': f"{sonuc['risk']['sharpe']:.3f}",
                'Sortino oranı': f"{sonuc['risk']['sortino']:.3f}",
                'Güncel drawdown': f"{sonuc['risk']['guncel_drawdown']:.2f}%",
                'Maks drawdown': f"{sonuc['risk']['max_drawdown']:.2f}%",
                'Güncel risksiz faiz': f"{sonuc['risk']['guncel_rf_yillik']:.1f}%",
            },
            'Sinyaller': {
                'Z-skor': f"{sonuc['z_skor']:+.3f}",
                'Konum': sonuc['konum_yorum'],
                'Trend rejimi': sonuc['trend']['rejim'],
                'SMA sinyali': sonuc['trend']['sma_sinyali'],
                '90g yıllık eğim': f"%{sonuc['trend']['yillik_egim_yuzde']:+.2f}",
                'Trend gücü R²': f"{sonuc['trend']['trend_gucu_r2']:.3f}",
                'RSI(14)': f"{sonuc['rsi']['rsi']:.1f}" if sonuc['rsi']['rsi'] else "N/A",
                'Rejim uyarısı': sonuc['rejim_uyari']['karar'],
            },
            'Monte Carlo': {
                'P5': f"{sonuc['p5']:.4f} ({(sonuc['p5']/sonuc['son_fiyat']-1)*100:+.1f}%)",
                'P50': f"{sonuc['p50']:.4f} ({(sonuc['p50']/sonuc['son_fiyat']-1)*100:+.1f}%)",
                'P95': f"{sonuc['p95']:.4f} ({(sonuc['p95']/sonuc['son_fiyat']-1)*100:+.1f}%)",
                'Reel kayıp olasılığı': f"%{sonuc['zarar_ihtimal']:.1f}",
            },
        }

        if sonuc['beta_alpha']:
            detay['Beta / Alpha'] = {
                'Beta': f"{sonuc['beta_alpha']['beta']:+.3f}",
                'Alpha (yıllık)': f"{sonuc['beta_alpha']['alpha_yillik_yuzde']:+.2f}%",
                'p-değeri': f"{sonuc['beta_alpha']['p_value']:.4f}",
                'R²': f"{sonuc['beta_alpha']['r_squared']:.3f}",
                'Tracking error': f"{sonuc['beta_alpha']['tracking_error']:.2f}%",
                'Information Ratio': f"{sonuc['beta_alpha']['information_ratio']:+.3f}",
            }

        if sonuc['backtest_skor'] is not None:
            bs = sonuc['backtest_skor']
            bt = sonuc['backtest']
            detay['Backtest'] = {
                'Standart skor': f"{bs['standart_skor']:.1f}/100 ({bs['kalite']})",
                'Bant kapsama': f"%{bs['ham_bant']:.1f}",
                'Yön doğruluğu': f"%{bs['ham_yon']:.1f}",
                'Medyan sapma': f"%{bs['medyan_sapma']:.1f}",
                'Yıllık eşdeğer sapma': f"%{bs['yillik_esdeger_sapma']:.1f}",
                'Eğitim penceresi': f"{bt['egitim_gun']} işlem günü",
                'Tahmin ufku': f"{bt['tahmin_ufku_is']} işlem günü",
                'Test sayısı': bt['test_sayisi'],
            }
        elif sonuc.get('backtest_hata'):
            detay['Backtest'] = {'Durum': f"Çalıştırılamadı"}

        for grup_ad, metrikler in detay.items():
            st.markdown(f"**{grup_ad}**")
            df_d = pd.DataFrame([(k, v) for k, v in metrikler.items()],
                               columns=['Metrik', 'Değer'])
            st.dataframe(df_d, use_container_width=True, hide_index=True)

        st.markdown("---")
        csv_data = sonuc['df'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Fiyat geçmişi (CSV)", data=csv_data,
            file_name=f"{sonuc['fon_kodu']}_fiyat_gecmisi.csv", mime="text/csv")


# ================= FOOTER =================
st.markdown("""
<div class="footer-disclaimer">
<strong>📜 Önemli:</strong> Bu uygulama eğitim ve araştırma amaçlıdır. Yatırım tavsiyesi
değildir. Yatırım kararı vermeden önce SPK lisanslı bir danışmana başvurun.
</div>
""", unsafe_allow_html=True)
