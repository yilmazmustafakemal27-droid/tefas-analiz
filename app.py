"""
TEFAS Fon Analiz Aracı — Web Uygulaması
=========================================
v8 GÜNCELLEMELERİ:
- Her metriğin yanında (?) ikonu → tıklayınca sade dil açıklaması
- Yeni "Backtest" sekmesi → dinamik walk-forward + standart skor
- Dinamik backtest: gecmis_gun_sayisi'nin 2/3'ü eğitim, 1/3'ü tahmin

"AL/SAT" tavsiyesi YOK. Sadece veri ve metrikler.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

import analiz
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


# ================= ÖZEL CSS =================
st.markdown("""
<style>
    :root {
        --primary: #0F4C81;
        --accent: #D4A574;
        --success: #2E7D5C;
        --warning: #C77D2A;
        --danger: #B83A3A;
        --neutral: #4A5560;
        --bg-soft: #F7F4EE;
    }

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

    .signal-bar {
        background: linear-gradient(90deg, #FAFAF7 0%, #F7F4EE 100%);
        padding: 12px;
        border-radius: 4px;
        margin: 4px 0;
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

    /* Popover button daha küçük göster */
    [data-testid="stPopover"] button {
        padding: 4px 8px !important;
        min-height: 32px !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)


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
Yatırım tavsiyesi, danışmanlığı veya öneri içermez. Gösterilen tüm metrikler ve skorlar
geçmiş veriye dayalı istatistiksel hesaplamalardır; gelecekteki performansı garanti etmez.
Yatırım kararlarınız için <strong>SPK lisanslı bir yatırım danışmanına</strong> başvurunuz.
</div>
""", unsafe_allow_html=True)


# ================= SIDEBAR (KONTROL PANELİ) =================
with st.sidebar:
    st.markdown("### Analiz Parametreleri")

    fon_kodu = st.text_input(
        "Fon Kodu (3 harf)",
        value="THV",
        max_chars=3,
        help="Örn: THV, AFA, GPB. TEFAS'ta listelenen 3 harfli kod."
    ).upper().strip()

    gun_sayisi = st.select_slider(
        "Geçmiş veri (gün)",
        options=[365, 500, 750, 1000, 1500, 1825],
        value=1000,
        help="Daha uzun veri = daha sağlam istatistik. 1000 gün ≈ 4 yıl. "
             "Backtest: bunun 2/3'ü ile eğitim, 1/3'ü ile tahmin yapar."
    )

    # Backtest pencere bilgisi (kullanıcıya göster)
    egt_g = int(gun_sayisi * 2/3)
    tah_g = int(gun_sayisi * 1/3)
    st.caption(f"📊 Backtest: **{egt_g}g** eğitim → **{tah_g}g** tahmin")

    st.markdown("---")
    st.markdown("### Beklentiler")

    enflasyon = st.slider(
        "Beklenen yıllık enflasyon (%)",
        min_value=10.0, max_value=80.0, value=45.0, step=2.5,
        help="Reel getiri hesabında kullanılır."
    ) / 100

    enf_belirsizlik = st.slider(
        "Enflasyon belirsizliği (σ, %)",
        min_value=5.0, max_value=25.0, value=13.0, step=1.0,
        help="Stokastik enflasyon modeli için yıllık standart sapma."
    ) / 100

    st.markdown("---")
    st.markdown("### Gelişmiş")

    senaryo_sayisi = st.select_slider(
        "Monte Carlo senaryo sayısı",
        options=[1000, 2000, 5000, 10000],
        value=5000
    )

    backtest_calistir = st.checkbox(
        "Walk-forward backtest çalıştır",
        value=True,
        help="Geçmiş tahminlerin başarısını ölçer. Biraz yavaştır."
    )

    makro_kullan = st.checkbox(
        "Makro veri kullan (Yahoo Finance)",
        value=True,
        help="BIST100, USD/TRY, S&P 500 vb. ile karşılaştırma yapar."
    )

    st.markdown("---")
    analiz_basla = st.button("🔍 Analizi Başlat", type="primary", use_container_width=True)

    st.markdown("---")
    with st.expander("ℹ️ Bu araç ne yapar?"):
        st.markdown("""
        **Yapar:**
        - TEFAS'tan fon fiyat verisini çeker
        - Volatilite, Sharpe, drawdown hesaplar
        - Endeks ile karşılaştırır (alpha, beta)
        - Monte Carlo simülasyonu (1 yıl reel getiri)
        - Trend rejimi tespiti
        - Walk-forward backtest (tahmin doğruluğu)

        **Yapmaz:**
        - Yatırım tavsiyesi vermez
        - "AL/SAT" demez
        - Geleceği tahmin etmez (sadece olasılık dağılımı gösterir)
        - Vergi/komisyon hesabı yapmaz

        **❓ İkonları:** Her metriğin yanında (?) ikonu var.
        Tıklayınca o metriğin senin değerine göre ne anlama geldiğini sade dilde anlatır.
        """)


# ================= ANA İÇERİK =================
if not analiz_basla:
    st.markdown("### Nasıl Kullanılır?")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        **1. Fon kodu girin**

        Sol panelden 3 harfli TEFAS fon kodunu girin (örnek: THV, AFA, IPB).
        """)
    with col_b:
        st.markdown("""
        **2. Parametreleri ayarlayın**

        Beklediğiniz enflasyon ve veri uzunluğunu seçin. Varsayılanlar TR için makul.
        """)
    with col_c:
        st.markdown("""
        **3. Sonuçları yorumlayın**

        Her metriğin yanında **(?) ikonu** var — tıklayınca sade dilde açıklama açılır.
        """)

    st.markdown("---")
    st.markdown("### Hangi metrikler hesaplanır?")
    st.markdown("""
    | Grup | Metrik | Anlam |
    |------|--------|-------|
    | Değerleme | Z-skor (252 gün rolling) | Fiyat trendinden ne kadar sapmış |
    | Trend | SMA-50/200, RSI | Yön ve momentum |
    | Risk | Sharpe, Sortino, Drawdown | Riske göre getiri kalitesi |
    | Aktif Yön. | Alpha, Information Ratio | Endekse göre fon yöneticisi katma değeri |
    | Tahmin | Monte Carlo (1 yıl) | Olasılık dağılımı |
    | Doğrulama | Walk-forward backtest | Sistemin geçmiş tahmin başarısı |
    """)

    st.info("💡 Sonuçlarda her metriğin yanında **(?)** ikonu bulacaksın. Tıklarsan o metriğin **senin değerine göre** ne anlama geldiğini sıradan insan diliyle anlatır.")

else:
    if not fon_kodu or len(fon_kodu) != 3:
        st.error("Lütfen 3 harfli geçerli bir fon kodu girin (örn: THV).")
        st.stop()

    with st.spinner(f"📡 {fon_kodu} verileri çekiliyor ve analiz ediliyor..."):
        try:
            sonuc = analiz.tam_analiz(
                fon_kodu=fon_kodu,
                gun_sayisi=gun_sayisi,
                beklenen_enflasyon=enflasyon,
                enflasyon_sigma=enf_belirsizlik,
                makro_kullan=makro_kullan,
                senaryo_sayisi=senaryo_sayisi,
                backtest_calistir=backtest_calistir,
            )
        except ValueError as e:
            st.error(f"❌ {e}")
            st.info("İpucu: Fon kodu büyük harf, 3 karakter olmalı. Örn: THV, AFA, IPB.")
            st.stop()
        except Exception as e:
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

    # ================= ANA METRİK KARTLARI (AÇIKLAMALI) =================
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Son Fiyat", f"{sonuc['son_fiyat']:.4f}")
    with col2:
        aciklamali_metrik(
            "Yıllık Getiri",
            f"{sonuc['bench_sonuc']['fon_yillik']:+.1f}%",
            "yillik_getiri",
            sonuc['bench_sonuc']['fon_yillik'],
            delta=f"Toplam: %{sonuc['bench_sonuc']['fon_toplam']:+.1f}"
        )
    with col3:
        aciklamali_metrik(
            "Sharpe Oranı",
            f"{sonuc['risk']['sharpe']:.2f}",
            "sharpe",
            sonuc['risk']['sharpe']
        )
    with col4:
        aciklamali_metrik(
            "Yıllık Volatilite",
            f"{sonuc['risk']['yillik_oynaklik']:.1f}%",
            "volatilite",
            sonuc['risk']['yillik_oynaklik']
        )
    with col5:
        aciklamali_metrik(
            "Güncel Düşüş",
            f"{sonuc['risk']['guncel_drawdown']:.1f}%",
            "guncel_drawdown",
            sonuc['risk']['guncel_drawdown']
        )

    # Rejim uyarısı
    if sonuc['rejim_uyari']['siddet'] >= 1:
        renk = "#B83A3A" if sonuc['rejim_uyari']['siddet'] >= 3 else "#C77D2A"
        col_uy1, col_uy2 = st.columns([20, 1])
        with col_uy1:
            st.markdown(
                f"<div style='background: #FFF3E0; border-left: 3px solid {renk}; "
                f"padding: 10px 14px; margin: 10px 0; border-radius: 4px;'>"
                f"<strong style='color: {renk};'>📡 {sonuc['rejim_uyari']['karar']}</strong><br>"
                f"<small>{' • '.join(sonuc['rejim_uyari']['uyarilar'])}</small>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_uy2:
            st.markdown("<div style='padding-top: 18px;'></div>", unsafe_allow_html=True)
            popover_aciklama(
                "rejim_uyarisi",
                sonuc['rejim_uyari']['siddet'],
                karar=sonuc['rejim_uyari']['karar']
            )

    # ================= TAB YAPISI (BACKTEST EKLENDİ) =================
    tab_listesi = [
        "📊 Genel Bakış",
        "🎯 Sinyaller",
        "📈 Karşılaştırma",
        "🎲 Monte Carlo",
        "🕰️ Backtest",
        "📋 Detay Tablo"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_listesi)

    # ----- TAB 1: GENEL BAKIŞ -----
    with tab1:
        st.markdown("### Fiyat Geçmişi ve Trend")
        df = sonuc['df']

        fig_fiyat = go.Figure()
        fig_fiyat.add_trace(go.Scatter(
            x=df['date'], y=df['price'],
            mode='lines', name='Fiyat',
            line=dict(color='#0F4C81', width=2)
        ))
        if len(df) >= 252:
            son_252 = df.tail(252)
            log_p = np.log(son_252['price'].values)
            x_arr = np.arange(len(log_p))
            from scipy import stats as sp_stats
            slope, intercept, _, _, _ = sp_stats.linregress(x_arr, log_p)
            trend = np.exp(slope * x_arr + intercept)
            fig_fiyat.add_trace(go.Scatter(
                x=son_252['date'], y=trend,
                mode='lines', name='252g log-trend',
                line=dict(color='#D4A574', width=2, dash='dash')
            ))
        fig_fiyat.update_layout(
            height=380, margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="", yaxis_title="Fiyat (TL)",
            plot_bgcolor='#FAFAF7', paper_bgcolor='white',
            legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1)
        )
        st.plotly_chart(fig_fiyat, use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Trend & Konum**")

            # Z-skor + açıklama
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Konum (Z-skor): **{sonuc['z_skor']:+.2f}** → {sonuc['konum_yorum']}")
            with col_b:
                popover_aciklama("z_skor", sonuc['z_skor'])

            # Trend rejimi + açıklama
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Trend rejimi: **{sonuc['trend']['rejim']}**")
            with col_b:
                popover_aciklama("trend", sonuc['trend']['rejim'])

            st.markdown(f"- 90g yıllık eğim: **%{sonuc['trend']['yillik_egim_yuzde']:+.1f}**")
            st.markdown(f"- SMA sinyali: {sonuc['trend']['sma_sinyali']}")

            # RSI + açıklama
            if sonuc['rsi']['rsi'] is not None:
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(f"- RSI(14): **{sonuc['rsi']['rsi']:.1f}** — {sonuc['rsi']['yorum']}")
                with col_b:
                    popover_aciklama("rsi", sonuc['rsi']['rsi'])

        with col_r:
            st.markdown("**Risk Profili**")

            # Sharpe + açıklama
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Sharpe: **{sonuc['risk']['sharpe']:.2f}**")
            with col_b:
                popover_aciklama("sharpe", sonuc['risk']['sharpe'])

            # Sortino + açıklama
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Sortino: **{sonuc['risk']['sortino']:.2f}**")
            with col_b:
                popover_aciklama("sortino", sonuc['risk']['sortino'])

            # Volatilite + açıklama
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Yıllık volatilite: **%{sonuc['risk']['yillik_oynaklik']:.1f}**")
            with col_b:
                popover_aciklama("volatilite", sonuc['risk']['yillik_oynaklik'])

            # Max drawdown + açıklama
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- Maks düşüş: **%{sonuc['risk']['max_drawdown']:.1f}**")
            with col_b:
                popover_aciklama("max_drawdown", sonuc['risk']['max_drawdown'])

            st.markdown(f"- Risksiz faiz (güncel): **%{sonuc['risk']['guncel_rf_yillik']:.1f}**")

        st.markdown("**Rejim İstatistikleri** (geçmişteki rejim dağılımı)")
        rejim_data = []
        for r, s in sonuc['rejim_stat'].items():
            yil_mu = ((1 + s['mu']) ** 252 - 1) * 100
            yil_sig = s['sigma'] * np.sqrt(252) * 100
            rejim_data.append({
                'Rejim': r,
                'Yıllık μ (%)': f"{yil_mu:+.1f}",
                'Yıllık σ (%)': f"{yil_sig:.1f}",
                'Gözlem (gün)': s['n']
            })
        st.dataframe(pd.DataFrame(rejim_data), use_container_width=True, hide_index=True)

    # ----- TAB 2: SİNYALLER -----
    with tab2:
        st.markdown("### Sinyal Grupları")
        st.caption(
            "Skorlar 0-100 arası bilgilendiricidir. Yüksek skor = göstergeler olumlu, "
            "düşük skor = göstergeler olumsuz. **Yatırım kararı için tek başına yeterli değildir.**"
        )

        gruplar = sonuc['sinyal']['gruplar']
        renkler = []
        for v in gruplar.values():
            if v >= 60: renkler.append('#2E7D5C')
            elif v >= 40: renkler.append('#C77D2A')
            else: renkler.append('#B83A3A')

        fig_sinyal = go.Figure(go.Bar(
            x=list(gruplar.values()),
            y=list(gruplar.keys()),
            orientation='h',
            marker=dict(color=renkler),
            text=[f"{v:.0f}" for v in gruplar.values()],
            textposition='outside',
            textfont=dict(size=14, color='#1a1a1a')
        ))
        fig_sinyal.update_layout(
            height=300,
            margin=dict(l=10, r=40, t=10, b=30),
            xaxis=dict(range=[0, 110], showgrid=True, gridcolor='#E8E5DD',
                      title="Skor (0-100)"),
            yaxis=dict(showgrid=False),
            plot_bgcolor='#FAFAF7', paper_bgcolor='white',
            showlegend=False
        )
        fig_sinyal.add_vline(x=50, line_dash="dot", line_color="#888")
        st.plotly_chart(fig_sinyal, use_container_width=True)

        # Toplam skor
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
                f"</div>",
                unsafe_allow_html=True
            )
            # Birleşik skor açıklaması
            aciklama_expander(
                "genel_skor", skor,
                etiket=sonuc['sinyal']['etiket']
            )

        with col_s2:
            st.markdown("**Skor Nasıl Yorumlanır?**")
            st.markdown("""
            - **70+** : Çok güçlü göstergeler (değerleme + trend + risk + alpha hep olumlu)
            - **58-70**: Güçlü göstergeler
            - **45-58**: Karışık göstergeler — bazı metrikler olumlu, bazıları olumsuz
            - **32-45**: Zayıf göstergeler
            - **0-32**: Çok zayıf göstergeler

            **Önemli:** Yüksek skor "AL" anlamına gelmez. Düşük skor "SAT" anlamına gelmez.
            Skor sadece geçmiş verilerin **istatistiksel özetidir**. Gelecek farklı olabilir.
            """)

        # Rolling beta/alpha grafikleri
        if sonuc['rolling_ba'] is not None:
            st.markdown("---")
            st.markdown("### Zamana Göre Performans")

            rba = sonuc['rolling_ba']
            fig_roll = make_subplots(rows=1, cols=3,
                                    subplot_titles=("Rolling Beta (6ay)",
                                                    "Rolling Alpha (yıllık %)",
                                                    "Rolling Information Ratio"))
            fig_roll.add_trace(go.Scatter(x=rba['date'], y=rba['beta'],
                                          line=dict(color='#0F4C81', width=1.5),
                                          showlegend=False), row=1, col=1)
            fig_roll.add_hline(y=1.0, line_dash="dot", line_color="#888", row=1, col=1)

            fig_roll.add_trace(go.Scatter(x=rba['date'], y=rba['alpha_yillik'],
                                          line=dict(color='#7B4B94', width=1.5),
                                          showlegend=False), row=1, col=2)
            fig_roll.add_hline(y=0, line_dash="dot", line_color="#888", row=1, col=2)

            fig_roll.add_trace(go.Scatter(x=rba['date'], y=rba['info_ratio'],
                                          line=dict(color='#1A8B9D', width=1.5),
                                          showlegend=False), row=1, col=3)
            fig_roll.add_hline(y=0, line_dash="dot", line_color="#888", row=1, col=3)

            fig_roll.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=30),
                                  plot_bgcolor='#FAFAF7', paper_bgcolor='white')
            st.plotly_chart(fig_roll, use_container_width=True)

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
            fig_kum.add_trace(go.Scatter(
                x=fon_df['date'], y=fon_df['kum'],
                mode='lines', name=f"Fon ({sonuc['fon_kodu']})",
                line=dict(color='#0F4C81', width=2)
            ))
            endeks_isim = analiz.kategoriye_gore_endeks_kodu(sonuc['kategori'])[1]
            fig_kum.add_trace(go.Scatter(
                x=endeks_df['date'], y=endeks_df['kum'],
                mode='lines', name=endeks_isim,
                line=dict(color='#D4A574', width=2)
            ))
            fig_kum.update_layout(
                height=380, margin=dict(l=10, r=10, t=10, b=30),
                yaxis_title="Kümülatif Getiri (%)",
                plot_bgcolor='#FAFAF7', paper_bgcolor='white',
                legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1)
            )
            st.plotly_chart(fig_kum, use_container_width=True)

        # Beta/Alpha detay — AÇIKLAMALI
        if sonuc['beta_alpha']:
            st.markdown("#### Beta / Alpha Analizi")
            ba = sonuc['beta_alpha']
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                aciklamali_metrik("Beta", f"{ba['beta']:+.2f}", "beta", ba['beta'])
            with col_b2:
                aciklamali_metrik(
                    "Alpha (yıllık)",
                    f"{ba['alpha_yillik_yuzde']:+.1f}%",
                    "alpha",
                    ba['alpha_yillik_yuzde'],
                    delta=f"p={ba['p_value']:.3f}"
                )
            with col_b3:
                aciklamali_metrik(
                    "R²",
                    f"{ba['r_squared']:.2f}",
                    "r_squared",
                    ba['r_squared']
                )
            with col_b4:
                aciklamali_metrik(
                    "Information Ratio",
                    f"{ba['information_ratio']:+.2f}",
                    "info_ratio",
                    ba['information_ratio']
                )

            # Tracking error de
            st.markdown("---")
            col_te1, col_te2 = st.columns(2)
            with col_te1:
                aciklamali_metrik(
                    "Tracking Error (yıllık)",
                    f"%{ba['tracking_error']:.1f}",
                    "tracking_error",
                    ba['tracking_error']
                )
            with col_te2:
                st.metric("Gözlem sayısı", f"{ba['gozlem_sayisi']}")

            st.info(f"**Özet yorum:** {ba['alpha_yorum']}")

    # ----- TAB 4: MONTE CARLO -----
    with tab4:
        st.markdown("### 1 Yıl Sonrası Reel Getiri Simülasyonu")
        st.caption(
            f"{senaryo_sayisi:,} olası senaryo simüle edildi. Enflasyon stokastik modellendi. "
            "Bu **bir tahmin değil**, geçmiş veri ve mevcut rejim altındaki **olasılık dağılımıdır**."
        )

        senaryolar = sonuc['senaryolar']
        gun_aralik = np.arange(senaryolar.shape[0])

        p5_yol = np.percentile(senaryolar, 5, axis=1)
        p50_yol = np.percentile(senaryolar, 50, axis=1)
        p95_yol = np.percentile(senaryolar, 95, axis=1)

        fig_mc = go.Figure()
        fig_mc.add_trace(go.Scatter(
            x=gun_aralik, y=p95_yol, mode='lines',
            line=dict(color='rgba(46,125,92,0.3)', width=0),
            showlegend=False, hoverinfo='skip'
        ))
        fig_mc.add_trace(go.Scatter(
            x=gun_aralik, y=p5_yol, mode='lines',
            line=dict(color='rgba(46,125,92,0.3)', width=0),
            fill='tonexty', fillcolor='rgba(46,125,92,0.15)',
            name='P5–P95 bandı'
        ))
        fig_mc.add_trace(go.Scatter(
            x=gun_aralik, y=p5_yol, mode='lines', name='P5 (kötü senaryo)',
            line=dict(color='#B83A3A', width=1.5, dash='dash')
        ))
        fig_mc.add_trace(go.Scatter(
            x=gun_aralik, y=p50_yol, mode='lines', name='P50 (medyan)',
            line=dict(color='#0F4C81', width=2.5)
        ))
        fig_mc.add_trace(go.Scatter(
            x=gun_aralik, y=p95_yol, mode='lines', name='P95 (iyi senaryo)',
            line=dict(color='#2E7D5C', width=1.5, dash='dash')
        ))
        fig_mc.add_hline(y=sonuc['son_fiyat'], line_dash="dot", line_color="#888",
                        annotation_text=f"Bugün: {sonuc['son_fiyat']:.4f}",
                        annotation_position="bottom right")

        fig_mc.update_layout(
            height=420, margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="İşlem günü", yaxis_title="Reel fiyat (enflasyondan arındırılmış)",
            plot_bgcolor='#FAFAF7', paper_bgcolor='white',
            legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1)
        )
        st.plotly_chart(fig_mc, use_container_width=True)

        st.markdown("#### 1 Yıl Sonrası Olasılık Dağılımı")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            getiri_p5 = (sonuc['p5'] / sonuc['son_fiyat'] - 1) * 100
            st.metric("Kötü senaryo (P5)", f"{getiri_p5:+.1f}%",
                     help="%5 ihtimalle bundan daha kötü olabilir")
        with col_p2:
            getiri_p50 = (sonuc['p50'] / sonuc['son_fiyat'] - 1) * 100
            aciklamali_metrik(
                "Medyan (P50)",
                f"{getiri_p50:+.1f}%",
                "p50_reel",
                sonuc['p50'],
                baslangic=sonuc['son_fiyat']
            )
        with col_p3:
            getiri_p95 = (sonuc['p95'] / sonuc['son_fiyat'] - 1) * 100
            st.metric("İyi senaryo (P95)", f"{getiri_p95:+.1f}%",
                     help="%5 ihtimalle bundan daha iyi olabilir")
        with col_p4:
            aciklamali_metrik(
                "Reel Kayıp İhtimali",
                f"%{sonuc['zarar_ihtimal']:.0f}",
                "reel_kayip",
                sonuc['zarar_ihtimal']
            )

        st.info(
            f"💡 **Yorum:** {sonuc['fon_kodu']} fonunun 1 yıl sonra **enflasyondan arındırılmış** "
            f"reel getirisi %{getiri_p5:+.1f} ile %{getiri_p95:+.1f} aralığında olmaktadır "
            f"(geçmiş veriye dayalı 90% güven aralığı). Bu bir tahmin **değildir**; geçmiş davranış "
            f"ve şu anki rejim altında yapılan bir simülasyondur."
        )

    # ----- TAB 5: BACKTEST (YENİ) -----
    with tab5:
        st.markdown("### Walk-Forward Backtest — Sistem Tahmin Başarısı")
        st.caption(
            "Sistemin geçmişte yaptığı tahminleri **gerçekleşen** sonuçlarla karşılaştırır. "
            "Her test noktasında **sadece o tarihe kadarki veri** kullanılır (geleceği görmez). "
            "Bu, sistemin tahmin doğruluğunu objektif olarak ölçer."
        )

        bt = sonuc['backtest']
        bs = sonuc['backtest_skor']

        if bt is None:
            st.warning(
                "⚠️ Backtest çalıştırılamadı. Sebep olabilir:\n"
                "- Geçmiş veri yetersiz (en az ~400 gün gerekli)\n"
                "- Sidebar'dan backtest seçeneği kapatılmış\n"
                "- Hesaplama sırasında bir hata oluştu"
            )
        else:
            # Pencere bilgisi
            st.markdown(f"""
            **Test Yapılandırması:**
            - Eğitim verisi: **{bt['egitim_gun']} gün** (geçmiş verinin 2/3'ü)
            - Tahmin ufku: **{bt['tahmin_ufku_takvim']} takvim günü** (≈ {bt['tahmin_ufku_is']} iş günü)
            - Toplam test sayısı: **{bt['test_sayisi']}**
            """)

            # ⭐ STANDART SKOR — en üstte, büyük
            if bs is not None:
                col_st1, col_st2 = st.columns([1, 2])
                with col_st1:
                    skor_renk = ('#2E7D5C' if bs['standart_skor'] >= 60
                                else '#C77D2A' if bs['standart_skor'] >= 45
                                else '#B83A3A')
                    st.markdown(
                        f"<div style='text-align: center; padding: 30px; "
                        f"background: linear-gradient(135deg, #FAFAF7 0%, #F0EDE3 100%); "
                        f"border-radius: 8px; border: 1px solid #E8E5DD;'>"
                        f"<div style='font-size: 0.85rem; color: #888; text-transform: uppercase; "
                        f"letter-spacing: 0.1em; margin-bottom: 8px;'>Standart Skor (Ufuk-Bağımsız)</div>"
                        f"<div style='font-size: 3.5rem; font-weight: 600; color: {skor_renk}; "
                        f"font-family: Georgia, serif; line-height: 1;'>{bs['standart_skor']:.0f}</div>"
                        f"<div style='font-size: 0.95rem; color: #4A5560; margin-top: 8px;'>{bs['kalite']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    aciklama_expander(
                        "standart_skor",
                        bs['standart_skor'],
                        kalite=bs['kalite']
                    )

                with col_st2:
                    st.markdown("**Neden 'Standart Skor'?**")
                    st.markdown(f"""
                    Geçmiş veri uzunluğunu değiştirdiğinde **tahmin ufku da değişir**:
                    - 600 gün seçtiysen: 200 gün ileri tahmin
                    - 1000 gün seçtiysen: 333 gün ileri tahmin
                    - 1825 gün seçtiysen: 608 gün ileri tahmin

                    Uzun ufuk tahmini doğal olarak daha zordur. **Standart skor**, sapma
                    büyüklüğünü **√t kuralıyla yıllık eşdeğere çevirerek** bu eşitsizliği düzeltir.

                    Yani farklı ayarlarla yapılan backtest sonuçları **karşılaştırılabilir** hale gelir.

                    **Mevcut ayar:** {bt['tahmin_ufku_is']} iş günü tahmin ufku
                    """)

            # Ham sonuçlar — 3 metrik
            st.markdown("---")
            st.markdown("#### Ham Backtest Sonuçları")
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                aciklamali_metrik(
                    "Bant Kapsama",
                    f"%{bs['ham_bant']:.0f}" if bs else "N/A",
                    "backtest_bant",
                    bs['ham_bant'] if bs else None,
                    delta="Hedef: %90"
                )
            with col_h2:
                aciklamali_metrik(
                    "Yön Doğruluğu",
                    f"%{bs['ham_yon']:.0f}" if bs else "N/A",
                    "backtest_yon",
                    bs['ham_yon'] if bs else None,
                    delta="Random: %50"
                )
            with col_h3:
                if bs:
                    st.metric(
                        "Medyan Sapma",
                        f"%{bs['medyan_sapma']:.1f}",
                        delta=f"Yıllık eşdeğer: %{bs['yillik_esdeger_sapma']:.1f}",
                        help="Tahmin merkezi (P50) ile gerçek değer arasındaki medyan fark"
                    )

            # Grafik: P50 vs Gerçek
            st.markdown("---")
            st.markdown("#### Tahmin vs Gerçek (Test Noktası Başına)")

            df_bt = bt['sonuclar']

            fig_bt = make_subplots(rows=1, cols=2,
                                   subplot_titles=("P50 Tahmin vs Gerçekleşen",
                                                   "Zaman İçinde Sapma (%)"),
                                   column_widths=[0.55, 0.45])

            # Sol: scatter
            renkler_scatter = ['#2E7D5C' if x else '#B83A3A' for x in df_bt['bant_ici']]
            fig_bt.add_trace(
                go.Scatter(
                    x=df_bt['p50'], y=df_bt['reel_gercek'],
                    mode='markers',
                    marker=dict(color=renkler_scatter, size=8, opacity=0.7,
                               line=dict(color='white', width=1)),
                    text=[f"Test: {d.strftime('%Y-%m')}<br>Rejim: {r}<br>Sapma: %{s:+.1f}"
                          for d, r, s in zip(df_bt['test_tarihi'], df_bt['rejim'], df_bt['sapma_yuzde'])],
                    hovertemplate='%{text}<br>P50: %{x:.3f}<br>Gerçek: %{y:.3f}<extra></extra>',
                    showlegend=False
                ),
                row=1, col=1
            )
            # 45° referans
            mn = min(df_bt['p50'].min(), df_bt['reel_gercek'].min())
            mx = max(df_bt['p50'].max(), df_bt['reel_gercek'].max())
            fig_bt.add_trace(
                go.Scatter(x=[mn, mx], y=[mn, mx], mode='lines',
                          line=dict(color='#888', dash='dash', width=1),
                          showlegend=False, hoverinfo='skip'),
                row=1, col=1
            )

            # Sağ: zaman içinde sapma
            fig_bt.add_trace(
                go.Bar(
                    x=df_bt['test_tarihi'],
                    y=df_bt['sapma_yuzde'],
                    marker=dict(color=['#2E7D5C' if x else '#B83A3A' for x in df_bt['bant_ici']]),
                    showlegend=False,
                    hovertemplate='%{x|%Y-%m-%d}<br>Sapma: %{y:+.1f}%<extra></extra>'
                ),
                row=1, col=2
            )
            fig_bt.add_hline(y=0, line_dash="dot", line_color="#888", row=1, col=2)

            fig_bt.update_xaxes(title_text="P50 Tahmin", row=1, col=1)
            fig_bt.update_yaxes(title_text="Gerçek Reel Fiyat", row=1, col=1)
            fig_bt.update_xaxes(title_text="Test Tarihi", row=1, col=2)
            fig_bt.update_yaxes(title_text="Sapma (%)", row=1, col=2)

            fig_bt.update_layout(
                height=400, margin=dict(l=10, r=10, t=50, b=30),
                plot_bgcolor='#FAFAF7', paper_bgcolor='white'
            )
            st.plotly_chart(fig_bt, use_container_width=True)

            # Renk açıklaması
            st.caption(
                "🟢 Yeşil noktalar: Gerçek değer P5-P95 bandı **içinde** kaldı (sistem doğru). "
                "🔴 Kırmızı noktalar: Gerçek değer banttan **dışarı** çıktı (sistem yanıldı)."
            )

            # Test detay tablosu (expandable)
            with st.expander(f"📋 Tüm {bt['test_sayisi']} test noktasının detayı"):
                df_gosterim = df_bt.copy()
                df_gosterim['test_tarihi'] = df_gosterim['test_tarihi'].dt.strftime('%Y-%m-%d')
                df_gosterim['p5'] = df_gosterim['p5'].round(3)
                df_gosterim['p50'] = df_gosterim['p50'].round(3)
                df_gosterim['p95'] = df_gosterim['p95'].round(3)
                df_gosterim['reel_gercek'] = df_gosterim['reel_gercek'].round(3)
                df_gosterim['sapma_yuzde'] = df_gosterim['sapma_yuzde'].round(1)
                df_gosterim['bant_ici'] = df_gosterim['bant_ici'].map({True: '✓', False: '✗'})
                df_gosterim['yon_dogru'] = df_gosterim['yon_dogru'].map({True: '↑', False: '↓'})
                df_gosterim = df_gosterim.rename(columns={
                    'test_tarihi': 'Tarih',
                    'baslangic': 'Başlangıç',
                    'p5': 'P5', 'p50': 'P50', 'p95': 'P95',
                    'reel_gercek': 'Gerçek',
                    'sapma_yuzde': 'Sapma %',
                    'bant_ici': 'Bant',
                    'yon_dogru': 'Yön',
                    'rejim': 'Rejim'
                })
                st.dataframe(df_gosterim, use_container_width=True, hide_index=True)

    # ----- TAB 6: DETAY TABLO -----
    with tab6:
        st.markdown("### Tüm Metrikler (Detaylı)")

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
                'Güncel risksiz faiz (yıllık)': f"{sonuc['risk']['guncel_rf_yillik']:.1f}%",
            },
            'Sinyaller': {
                'Z-skor (252g)': f"{sonuc['z_skor']:+.3f}",
                'Konum yorumu': sonuc['konum_yorum'],
                'Trend rejimi': sonuc['trend']['rejim'],
                'SMA sinyali': sonuc['trend']['sma_sinyali'],
                'RSI(14)': f"{sonuc['rsi']['rsi']:.1f}" if sonuc['rsi']['rsi'] else "N/A",
                'Rejim uyarısı': sonuc['rejim_uyari']['karar'],
            },
            'Monte Carlo (1Y reel)': {
                'P5 fiyat': f"{sonuc['p5']:.4f} ({(sonuc['p5']/sonuc['son_fiyat']-1)*100:+.1f}%)",
                'P50 fiyat': f"{sonuc['p50']:.4f} ({(sonuc['p50']/sonuc['son_fiyat']-1)*100:+.1f}%)",
                'P95 fiyat': f"{sonuc['p95']:.4f} ({(sonuc['p95']/sonuc['son_fiyat']-1)*100:+.1f}%)",
                'Reel kayıp olasılığı': f"%{sonuc['zarar_ihtimal']:.1f}",
            },
        }

        if sonuc['beta_alpha']:
            detay['Beta / Alpha'] = {
                'Beta': f"{sonuc['beta_alpha']['beta']:+.3f}",
                'Alpha (yıllık)': f"{sonuc['beta_alpha']['alpha_yillik_yuzde']:+.2f}%",
                'Alpha p-değeri': f"{sonuc['beta_alpha']['p_value']:.4f}",
                'R²': f"{sonuc['beta_alpha']['r_squared']:.3f}",
                'Tracking error': f"{sonuc['beta_alpha']['tracking_error']:.2f}%",
                'Information Ratio': f"{sonuc['beta_alpha']['information_ratio']:+.3f}",
            }

        # Backtest detayları
        if sonuc['backtest_skor'] is not None:
            bs = sonuc['backtest_skor']
            bt = sonuc['backtest']
            detay['Backtest'] = {
                'Standart skor': f"{bs['standart_skor']:.1f}/100 ({bs['kalite']})",
                'Bant kapsama (ham)': f"%{bs['ham_bant']:.1f} (hedef %90)",
                'Yön doğruluğu (ham)': f"%{bs['ham_yon']:.1f} (random %50)",
                'Medyan sapma': f"%{bs['medyan_sapma']:.1f}",
                'Yıllık eşdeğer sapma': f"%{bs['yillik_esdeger_sapma']:.1f}",
                'Eğitim penceresi': f"{bt['egitim_gun']} gün",
                'Tahmin ufku': f"{bt['tahmin_ufku_is']} iş günü",
                'Test sayısı': bt['test_sayisi'],
            }

        for grup_ad, metrikler in detay.items():
            st.markdown(f"**{grup_ad}**")
            df_d = pd.DataFrame(
                [(k, v) for k, v in metrikler.items()],
                columns=['Metrik', 'Değer']
            )
            st.dataframe(df_d, use_container_width=True, hide_index=True)

        # Veri indirme
        st.markdown("---")
        st.markdown("**Ham veriyi indir:**")
        csv_data = sonuc['df'].to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Fon fiyat geçmişi (CSV)",
            data=csv_data,
            file_name=f"{sonuc['fon_kodu']}_fiyat_gecmisi.csv",
            mime="text/csv"
        )


# ================= ALT BİLGİ — KAPSAMLI DİSCLAİMER =================
st.markdown("""
<div class="footer-disclaimer">
<strong>📜 Önemli Bilgilendirme</strong><br><br>

<strong>Bu araç hakkında:</strong> Bu uygulama TEFAS'ta listelenen fonların kamuya açık fiyat
verilerini istatistiksel olarak analiz eden bir <strong>eğitim ve araştırma aracıdır</strong>.
Hesaplanan tüm metrikler (Sharpe oranı, Z-skor, Monte Carlo simülasyonları, alpha, beta vb.)
geçmiş verilere dayalı standart finansal istatistik yöntemleridir.

<br><br>

<strong>Yatırım tavsiyesi DEĞİLDİR:</strong> Bu araç hiçbir koşulda yatırım tavsiyesi, danışmanlığı,
kişiye özel öneri veya alım/satım sinyali olarak yorumlanamaz. SPK Kanunu kapsamında yatırım
danışmanlığı yalnızca <strong>SPK lisanslı kuruluşlar</strong> tarafından sunulabilir.

<br><br>

<strong>Sınırlılıklar:</strong>
<ul style="margin: 8px 0 8px 20px;">
<li>Geçmiş performans gelecek getiriyi garanti etmez</li>
<li>Modeller varsayımlara dayanır, gerçek piyasa farklı davranabilir</li>
<li>Vergi, fon yönetim ücreti ve giriş/çıkış komisyonları hesaba dahil değildir</li>
<li>Veri kaynaklarında gecikme veya hata olabilir</li>
</ul>

<strong>Yatırım kararı vermeden önce:</strong> Lisanslı bir yatırım danışmanına başvurun,
fonun KAP'taki resmi izahnamesini okuyun ve risk profilinize uygun olduğundan emin olun.

<br><br>

<small style="color: #888;">
TEFAS verisi <a href="https://www.tefas.gov.tr" target="_blank">tefas.gov.tr</a> kaynaklı, 
piyasa endeksi verisi Yahoo Finance kaynaklıdır.<br>
Bu araç açık kaynaklıdır ve kâr amacı gütmez.
</small>
</div>
""", unsafe_allow_html=True)
