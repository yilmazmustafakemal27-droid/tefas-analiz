"""
TEFAS Karar Destek - Sade Dil Açıklama Modülü (v9)
====================================================
YENİ EKLENENLER:
- _sma_sinyali: SMA-50/200 yorumu
- _yillik_egim: 90 gün yıllık eğim
- _trend_gucu_r2: trend gücü
- _rolling_beta, _rolling_alpha, _rolling_ir, _rolling_sharpe: rolling grafik açıklamaları
- _konum_yorum: Z-skor metinsel yorumu
- _rejim_stat: rejim istatistikleri tablosu
- _backtest_hata: backtest başarısız olunca açıklama
"""

import streamlit as st


# =============================================================
# DİNAMİK AÇIKLAMA FONKSİYONLARI
# =============================================================

def _sharpe(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Sharpe Oranı**, aldığın risk başına ne kadar kazandığını gösterir. "
             "Yani 'bu fon riske değer mi?' sorusunun cevabı.\n\n")
    if deger > 2:
        yorum = f"📊 Bu fonun Sharpe'ı **{deger:.2f}** — bu çok iyi bir rakam. Aldığı risk fazlasıyla karşılığını vermiş."
    elif deger > 1:
        yorum = f"📊 Bu fonun Sharpe'ı **{deger:.2f}** — iyi bir seviye. Risk-getiri dengesi sağlıklı."
    elif deger > 0.5:
        yorum = f"📊 Bu fonun Sharpe'ı **{deger:.2f}** — ortalama. Çok da kötü değil ama harika da değil."
    elif deger > 0:
        yorum = f"📊 Bu fonun Sharpe'ı **{deger:.2f}** — zayıf. Risk aldığın halde çok kazandırmamış."
    else:
        yorum = f"📊 Bu fonun Sharpe'ı **{deger:.2f}** — negatif. Bu fon riske değmiyor; mevduata yatırsan daha iyiydi."
    return temel + yorum + "\n\n💡 *Genel kural: 1'in üstü iyi, 2'nin üstü çok iyi.*"


def _sortino(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Sortino Oranı**, Sharpe'a benzer ama sadece 'kötü günlerdeki' düşüşlere bakar. "
             "Çünkü yukarı oynaklık zaten istediğin şey; aşağı oynaklık seni üzen şey.\n\n")
    if deger > 2:
        yorum = f"📊 **{deger:.2f}** — çok iyi. Fonun düşüşleri kontrollü, getirisi sağlam."
    elif deger > 1:
        yorum = f"📊 **{deger:.2f}** — iyi. Aşağı yönlü risk iyi yönetilmiş."
    elif deger > 0:
        yorum = f"📊 **{deger:.2f}** — vasat. Düşüşler getiriye baskın değil ama yeterince iyi de değil."
    else:
        yorum = f"📊 **{deger:.2f}** — kötü. Bu fon düşerken çok düşmüş."
    return temel + yorum


def _z_skor(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Z-Skor**, fonun şu anki fiyatının son 1 yıllık 'normal' seviyesinden ne kadar saptığını gösterir. "
             "Pahalı mı, ucuz mu olduğunu anlamanı sağlar.\n\n")
    if deger > 2:
        yorum = f"🔴 Z-skor **{deger:+.2f}** — fon **zirve bölgesinde**. Çok pahalı, balon riski var. Şimdi almak için kötü zaman."
    elif deger > 1:
        yorum = f"🟠 Z-skor **{deger:+.2f}** — fon **pahalı**. Normalden yukarıda. Almak için ideal değil."
    elif deger > -1:
        yorum = f"🟡 Z-skor **{deger:+.2f}** — fon **adil değerde**. Normal seviyelerde, ne pahalı ne ucuz."
    elif deger > -2:
        yorum = f"🟢 Z-skor **{deger:+.2f}** — fon **ucuz görünüyor**. Normalin altında, almak için makul zaman."
    else:
        yorum = f"💚 Z-skor **{deger:+.2f}** — fon **dip bölgesinde**. Çok ucuz, ama dikkat: 'ucuz' bazen 'bozuk' demektir."
    return temel + yorum + "\n\n💡 *Genel kural: -1 ile +1 arası normal. Dışına çıkarsa dikkat.*"


def _max_drawdown(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Maksimum Düşüş (Max Drawdown)**, fonun geçmişteki en yüksek noktasından en düşük noktasına kadar yaşadığı en büyük düşüş. "
             "Yani 'en kötü an'da ne kaybetmiş olurdun?\n\n")
    abs_d = abs(deger)
    if abs_d < 5:
        yorum = f"💚 **%{deger:.1f}** — çok düşük düşüş. Çok stabil bir fon."
    elif abs_d < 15:
        yorum = f"🟢 **%{deger:.1f}** — kabul edilebilir düşüş. Normal piyasa dalgalanması."
    elif abs_d < 30:
        yorum = f"🟡 **%{deger:.1f}** — orta seviye düşüş. Stresli dönemlerde sinirlerin gerilebilir."
    elif abs_d < 50:
        yorum = f"🟠 **%{deger:.1f}** — büyük düşüş. Riskli bir fon."
    else:
        yorum = f"🔴 **%{deger:.1f}** — çok ciddi düşüş. Bu fon zirvede alanı yarı yarıya zarara uğratmış."
    return temel + yorum + "\n\n💡 *Kendine sor: 'Param yarıya inse panik yapar mıyım?' Cevabın evetse bu fon sana göre değil.*"


def _guncel_drawdown(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = "**Güncel Düşüş**, fonun şu anki fiyatının son zirvesine göre nerede olduğunu gösterir.\n\n"
    abs_d = abs(deger)
    if abs_d < 2:
        yorum = f"📈 **%{deger:.1f}** — fon şu an zirvesinde veya çok yakınında. Yükselişte."
    elif abs_d < 10:
        yorum = f"📊 **%{deger:.1f}** — fon zirvesinin biraz altında. Normal geri çekilme."
    elif abs_d < 20:
        yorum = f"📉 **%{deger:.1f}** — fon zirvesinden epey uzakta. Önemli bir düşüş yaşıyor."
    else:
        yorum = f"⚠️ **%{deger:.1f}** — fon ciddi bir düşüş içinde. Zirveden bayağı uzak."
    return temel + yorum


def _yillik_volatilite(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Yıllık Volatilite (Oynaklık)**, fonun fiyatının bir yıl içinde ortalama ne kadar oynadığını gösterir. "
             "Yüksek = heyecanlı yolculuk, düşük = sakin yolculuk.\n\n")
    if deger < 10:
        yorum = f"😌 **%{deger:.1f}/yıl** — çok sakin. Para piyasası veya mevduat benzeri bir fon olabilir."
    elif deger < 20:
        yorum = f"🙂 **%{deger:.1f}/yıl** — düşük oynaklık. Borçlanma araçları seviyesinde."
    elif deger < 35:
        yorum = f"😐 **%{deger:.1f}/yıl** — orta seviye oynaklık. Karma fon veya yumuşak hisse fonu."
    elif deger < 50:
        yorum = f"😬 **%{deger:.1f}/yıl** — yüksek oynaklık. Hisse senedi yoğun fon. Mide gerektirir."
    else:
        yorum = f"🎢 **%{deger:.1f}/yıl** — çok yüksek oynaklık. Kemerleri bağla, roller coaster."
    return temel + yorum


def _beta(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Beta**, fonun piyasaya (endeksine) göre ne kadar hassas olduğunu gösterir. "
             "'Piyasa %10 yükselirse bu fon ne yapar?' sorusunun cevabı.\n\n")
    if deger > 1.3:
        yorum = f"🚀 Beta **{deger:.2f}** — fon piyasadan **çok daha agresif**. Piyasa %10 yükselirse fon ~%{deger*10:.0f} yükselir; düşerse de o kadar düşer."
    elif deger > 1.05:
        yorum = f"📈 Beta **{deger:.2f}** — fon piyasadan **biraz daha hareketli**. Hem yukarı hem aşağı biraz fazla oynar."
    elif deger > 0.95:
        yorum = f"📊 Beta **{deger:.2f}** — fon **piyasayla aynı tempoda** hareket ediyor. Klasik endeks davranışı."
    elif deger > 0.7:
        yorum = f"🛡️ Beta **{deger:.2f}** — fon piyasadan **daha yumuşak**. Düştüğünde daha az düşer, çıktığında daha az çıkar."
    elif deger > 0:
        yorum = f"🐢 Beta **{deger:.2f}** — fon piyasaya **çok az tepki veriyor**. Defansif bir fon."
    else:
        yorum = f"🔄 Beta **{deger:.2f}** — fon piyasanın **tersine** hareket ediyor. İlginç, korunma amaçlı olabilir."
    return temel + yorum


def _alpha(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Alpha**, fon yöneticisinin piyasanın üstünde yarattığı 'ekstra' getiri. "
             "Yani sadece piyasanın itmesiyle değil, gerçek beceriyle kazandırılan kısım.\n\n")
    if deger > 10:
        yorum = f"⭐ Alpha **%{deger:+.1f}/yıl** — yönetici **piyasayı ciddi şekilde yenmiş**. Çok başarılı bir yönetim."
    elif deger > 5:
        yorum = f"✅ Alpha **%{deger:+.1f}/yıl** — yönetici **piyasanın üstünde** getiri sağlamış. İyi yönetim."
    elif deger > 0:
        yorum = f"🟡 Alpha **%{deger:+.1f}/yıl** — yönetici **hafif piyasanın üstünde**. Marjinal başarı."
    elif deger > -5:
        yorum = f"🟠 Alpha **%{deger:+.1f}/yıl** — yönetici **piyasanın altında** kalmış. Komisyonu boşa veriyor olabilirsin."
    else:
        yorum = f"❌ Alpha **%{deger:+.1f}/yıl** — yönetici **piyasayı belirgin şekilde alta yenmiş**. Endeks fonu daha iyi olurdu."
    return temel + yorum + "\n\n💡 *Pozitif alpha = yönetim parana değiyor. Negatif = bedava endeks fonu al, daha iyi.*"


def _information_ratio(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Information Ratio (IR)**, yöneticinin piyasayı yenme becerisinin **ne kadar tutarlı** olduğunu gösterir. "
             "Bir kere şanslı mı vurmuş, yoksa sürekli mi başarılı?\n\n")
    if deger > 0.75:
        yorum = f"⭐ IR **{deger:+.2f}** — yönetici **sürekli ve tutarlı** şekilde piyasayı yeniyor. Çok kaliteli yönetim."
    elif deger > 0.5:
        yorum = f"✅ IR **{deger:+.2f}** — yönetici **istikrarlı şekilde** piyasanın üstünde. İyi seviye."
    elif deger > 0.25:
        yorum = f"🟡 IR **{deger:+.2f}** — yönetici **bazen** üstünde, bazen değil. Karışık performans."
    elif deger > 0:
        yorum = f"🟠 IR **{deger:+.2f}** — yönetici **şans eseri** üstünde. Tutarlılık yok."
    else:
        yorum = f"❌ IR **{deger:+.2f}** — yönetici tutarlı şekilde **piyasanın altında**. Endeks daha iyi."
    return temel + yorum


def _tracking_error(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Tracking Error (İzleme Hatası)**, fonun piyasadan ne kadar farklı hareket ettiğini gösterir. "
             "Düşük = endekse yapışmış, yüksek = aktif yönetiliyor.\n\n")
    if deger < 3:
        yorum = f"📌 **%{deger:.1f}** — fon piyasayı **neredeyse birebir taklit ediyor**. Pasif endeks fonu gibi davranıyor."
    elif deger < 8:
        yorum = f"📊 **%{deger:.1f}** — fon **biraz aktif yönetiliyor**. Piyasadan ufak sapmalar var."
    elif deger < 15:
        yorum = f"🎯 **%{deger:.1f}** — fon **belirgin şekilde aktif yönetiliyor**. Yönetici kendi kararlarını veriyor."
    else:
        yorum = f"🎨 **%{deger:.1f}** — fon **çok aktif yönetiliyor**. Piyasadan çok farklı hareket ediyor — risk de ödül de büyük."
    return temel + yorum


def _r_squared(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**R² (R-Kare)**, fonun hareketlerinin yüzde kaçını endeksin açıkladığını gösterir. "
             "Yani 'bu fon endeksten ne kadar bağımsız?' sorusu.\n\n")
    yuzde = deger * 100
    if deger > 0.85:
        yorum = f"📊 **{deger:.2f}** — fonun hareketlerinin **%{yuzde:.0f}'i endeks tarafından açıklanıyor**. Endeks bağımlısı."
    elif deger > 0.6:
        yorum = f"📊 **{deger:.2f}** — fonun **%{yuzde:.0f}'i endeksle uyumlu**, gerisi yönetici kararı."
    elif deger > 0.3:
        yorum = f"📊 **{deger:.2f}** — fon **kısmen bağımsız** hareket ediyor. Aktif yönetim payı yüksek."
    else:
        yorum = f"📊 **{deger:.2f}** — fon **endeksten çok bağımsız**. Tamamen kendine has bir strateji izliyor."
    return temel + yorum


def _rsi(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**RSI** (Relative Strength Index), fonun son 14 günde aşırı mı alındığını, aşırı mı satıldığını gösterir. "
             "Kısa vadeli aşırı tepkileri yakalamaya yarar.\n\n")
    if deger > 80:
        yorum = f"🔴 RSI **{deger:.0f}** — **çok aşırı alım**. Fon çok hızlı yükselmiş, kısa vadede geri çekilme çok olası."
    elif deger > 70:
        yorum = f"🟠 RSI **{deger:.0f}** — **aşırı alım**. Yorulma sinyali, dikkat."
    elif deger > 50:
        yorum = f"🟢 RSI **{deger:.0f}** — **pozitif momentum**. Sağlıklı yükseliş."
    elif deger > 30:
        yorum = f"🟡 RSI **{deger:.0f}** — **negatif momentum**. Hafif zayıflık."
    elif deger > 20:
        yorum = f"💚 RSI **{deger:.0f}** — **aşırı satım**. Çok satılmış, kısa vadede toparlanma olası."
    else:
        yorum = f"⭐ RSI **{deger:.0f}** — **çok aşırı satım**. Panik satışı bölgesi, dip yakalama fırsatı olabilir."
    return temel + yorum + "\n\n💡 *RSI kısa vadeli (14 günlük). Uzun vadeli yatırım kararı vermek için tek başına yeterli değil.*"


def _trend_rejimi(rejim_str):
    temel = "**Trend Rejimi**, fonun şu anda hangi 'modda' olduğunu gösterir.\n\n"
    r = str(rejim_str).upper()
    if "YÜKSELİŞ" in r:
        yorum = "📈 **Yükseliş Modu**: Fon belirgin bir yükseliş trendinde. Yıllık eğim risksiz faizin epey üzerinde, momentum lehine."
    elif "DÜŞÜŞ" in r:
        yorum = "📉 **Düşüş Modu**: Fon belirgin bir düşüş trendinde. Yıllık eğim risksiz faizin altında, momentum aleyhine."
    else:
        yorum = "↔️ **Yatay Mod**: Fon belirgin bir yön göstermiyor. Karışık sinyal — kararsız piyasa."
    return temel + yorum


# ============ YENİ EKLENENLER ============

def _sma_sinyali(sinyal_str):
    """SMA-50/200 yorumu — fiyat ile 50-200 günlük ortalamaların ilişkisi."""
    temel = ("**SMA Sinyali**, fonun fiyatının **50 günlük** ve **200 günlük** ortalamalarına göre konumunu gösterir. "
             "Klasik bir teknik analiz göstergesidir:\n"
             "- SMA 50 > SMA 200 → 'Altın Çapraz' (yükseliş kalıbı)\n"
             "- SMA 50 < SMA 200 → 'Ölüm Çaprazı' (düşüş kalıbı)\n\n")
    s = str(sinyal_str)
    if "Yükseliş trendi" in s:
        yorum = "✅ **Yükseliş trendi** — Hem SMA-50 SMA-200'ün üstünde, hem de fiyat SMA-50'nin üstünde. En sağlam yükseliş sinyali."
    elif "geri çekilme" in s:
        yorum = "🟡 **Yükselişte geri çekilme** — SMA-50 hâlâ SMA-200'ün üstünde ama fiyat SMA-50'nin altına düşmüş. Geçici düzeltme olabilir."
    elif "Düşüş trendi" in s:
        yorum = "🔴 **Düşüş trendi** — Hem SMA-50 SMA-200'ün altında, hem de fiyat SMA-50'nin altında. En sert düşüş sinyali."
    elif "toparlanma" in s:
        yorum = "🟠 **Düşüşte toparlanma** — SMA-50 SMA-200'ün altında ama fiyat SMA-50'nin üstüne çıkmış. Sahte yükseliş olabilir."
    else:
        yorum = "❔ **Veri yetersiz** — 200 günlük ortalama için yeterli geçmiş veri yok."
    return temel + yorum + "\n\n💡 *Tek başına karar verme. Diğer sinyallerle birlikte yorumla.*"


def _yillik_egim(deger):
    """90 günlük log-eğimin yıllığa çevrilmiş halı."""
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**90g Yıllık Eğim**, son 3 ayın fiyat trendinin **yıllık bileşik büyüme hızına** çevrilmiş hali. "
             "Logaritmik regresyonla hesaplanır.\n\n")
    if deger > 100:
        yorum = f"🚀 **%{deger:+.1f}/yıl** — Çok güçlü yukarı momentum. Bu hızla devam etmesi olası değil."
    elif deger > 50:
        yorum = f"📈 **%{deger:+.1f}/yıl** — Güçlü yükseliş ritmi."
    elif deger > 20:
        yorum = f"🟢 **%{deger:+.1f}/yıl** — Sağlıklı yükseliş ritmi."
    elif deger > 0:
        yorum = f"🟡 **%{deger:+.1f}/yıl** — Yavaş ama pozitif. Enflasyonun altında kalabilir."
    elif deger > -20:
        yorum = f"🟠 **%{deger:+.1f}/yıl** — Hafif düşüş trendi."
    else:
        yorum = f"🔴 **%{deger:+.1f}/yıl** — Sert düşüş trendi."
    return temel + yorum + "\n\n💡 *Risksiz faizle kıyasla. Faizin altındaysa fon momentumu zayıf demektir.*"


def _trend_gucu_r2(deger):
    """Trend gücü (R²)."""
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Trend Gücü (R²)**, son 90 günlük trendin **ne kadar 'düzgün' bir çizgi** olduğunu gösterir. "
             "1'e yakın = fiyat trende sıkı sıkı yapışmış, 0'a yakın = trend zayıf, sallantılı.\n\n")
    if deger > 0.7:
        yorum = f"📐 **{deger:.2f}** — Çok güçlü, düzgün trend. Yön belirgin."
    elif deger > 0.4:
        yorum = f"📊 **{deger:.2f}** — Orta seviye trend gücü. Yön var ama sallantılı."
    elif deger > 0.2:
        yorum = f"🌀 **{deger:.2f}** — Zayıf trend. Fiyat dağınık hareket ediyor."
    else:
        yorum = f"🎲 **{deger:.2f}** — Trend yok denecek kadar zayıf. Fiyat rastgele görünüyor."
    return temel + yorum


def _konum_yorum(z_skor, yorum_str):
    """Z-skor'un metinsel yorumu (Zirve/Pahalı/Adil/Ucuz/Dip) için ek bağlam."""
    if z_skor is None:
        return "Hesaplanamadı."
    temel = ("**Konum Yorumu**, Z-skor değerinin **kategorik anlamı**. "
             "Z-skor sürekli bir sayı; bu yorum onu 5 kovaya böler:\n"
             "- **Zirve bölgesi** (z > 2): %2'lik en pahalı kuyruk\n"
             "- **Pahalı** (1 < z < 2)\n"
             "- **Adil değer** (-1 < z < 1): normal dağılımın orta %68'i\n"
             "- **Ucuz** (-2 < z < -1)\n"
             "- **Dip bölgesi** (z < -2): %2'lik en ucuz kuyruk\n\n")
    yorum = f"📍 Şu anki konum: **{yorum_str}** (Z = **{z_skor:+.2f}**)"
    return temel + yorum


def _rejim_stat():
    """Rejim istatistikleri tablosu için açıklama."""
    return ("**Rejim İstatistikleri**, fonun **3 farklı piyasa rejiminde** geçmişte nasıl davrandığını gösterir:\n\n"
            "- **YÜKSELİŞ** rejimi: 90g yıllık eğim, risksiz faiz + %15'ten büyük\n"
            "- **YATAY** rejimi: 90g yıllık eğim, risksiz faizin ±%10-15 aralığında\n"
            "- **DÜŞÜŞ** rejimi: 90g yıllık eğim, risksiz faiz - %10'dan küçük\n\n"
            "Tabloda her rejimin **yıllık μ (ortalama getiri)** ve **yıllık σ (volatilite)** değerleri var. "
            "Gözlem sayısı 0 ise o rejim hiç yaşanmamış demektir.\n\n"
            "💡 *Monte Carlo simülasyonu güncel rejimin μ ve σ değerlerini ağırlıklı kullanır.*")


def _rolling_beta():
    """Rolling beta grafiği açıklaması."""
    return ("**Rolling Beta (6 ay)**, fonun **endekse hassasiyetinin zaman içinde nasıl değiştiğini** gösterir.\n\n"
            "Tek bir 'genel beta' yerine, **her 126 günlük (~6 ay) pencerede** yeniden hesaplanır. Böylece:\n"
            "- Beta yükseliyorsa → fon zamanla daha agresifleşmiş\n"
            "- Beta düşüyorsa → fon zamanla defansifleşmiş\n"
            "- Çok dalgalanıyorsa → fon stratejisi değişken / tutarsız\n\n"
            "**1.0 çizgisi (kesikli)**: tam endeks gibi davranma noktası.\n\n"
            "💡 *Beta sürekli 1'in üstündeyse fon agresif. 1'in altındaysa defansif.*")


def _rolling_alpha():
    """Rolling alpha grafiği açıklaması."""
    return ("**Rolling Alpha (6 ay, yıllık %)**, fon yöneticisinin **endekse göre yarattığı ekstra getirinin zaman içindeki seyri**.\n\n"
            "Her 126 günlük pencerede alpha yeniden hesaplanır. Böylece:\n"
            "- Alpha sürekli pozitifse → yönetici **istikrarlı şekilde başarılı**\n"
            "- Alpha bazen pozitif bazen negatifse → yönetim **tutarsız**, şansa bağımlı\n"
            "- Alpha sürekli negatifse → yönetim **endeksten kötü**, masraf veriyorsun\n\n"
            "**0 çizgisi (kesikli)**: endeksle aynı performans noktası.\n\n"
            "💡 *İdeal: çizginin çoğu zaman 0'ın üstünde olması.*")


def _rolling_ir():
    """Rolling Information Ratio açıklaması."""
    return ("**Rolling Information Ratio (6 ay)**, yöneticinin **fazla getirisinin tutarlılığının** zaman içinde nasıl değiştiğini gösterir.\n\n"
            "IR = (Fon getirisi − Endeks getirisi) / (Aktif riskin standart sapması)\n\n"
            "- IR sürekli > 0.5 ise → **profesyonel kalite yönetim**\n"
            "- IR 0 etrafında geziniyorsa → **şansa bağımlı performans**\n"
            "- IR sürekli negatifse → **endeks fonu daha iyi olurdu**\n\n"
            "💡 *Alpha 'ne kadar fazla' getiri verdiğini söyler, IR ise 'ne kadar tutarlı' verdiğini.*")


def _rolling_sharpe():
    """Rolling Sharpe açıklaması."""
    return ("**Rolling Sharpe (6 ay)**, fonun **riske göre getiri kalitesinin zaman içinde nasıl değiştiğini** gösterir.\n\n"
            "Her 126 günlük pencerede Sharpe yeniden hesaplanır. Tek bir 'genel Sharpe' yerine zaman serisi verir:\n"
            "- Sharpe yükseliyorsa → fon **iyileşiyor** (daha az risk, daha çok getiri)\n"
            "- Sharpe düşüyorsa → fon **bozuluyor**\n"
            "- Çok dalgalanıyorsa → fon **piyasa rejimine çok bağımlı**\n\n"
            "💡 *Sharpe'ın son 6 ayı önemli — şu anki performansı yansıtır.*")


def _backtest_hata(hata_metni):
    """Backtest başarısız olduğunda gösterilecek açıklama."""
    return ("**Backtest neden çalışmadı?**\n\n"
            f"`{hata_metni}`\n\n"
            "**Olası çözümler:**\n"
            "1. **Sidebar → 'Geçmiş veri (gün)'** ayarını **en az 750'ye** çıkar. Backtest için minimum ~250 işlem günü gerekli, "
            "ama anlamlı sonuç için 500+ işlem günü ister (yaklaşık 750 takvim günü = 2 yıl).\n"
            "2. **Fon çok yeni olabilir** — kuruluş tarihinden itibaren 250'den az işlem günü varsa backtest yapılamaz.\n"
            "3. **Veri çekmede gecikme/hata** olduysa analizi tekrar başlat.\n\n"
            "💡 *Backtest 'sistem ne kadar güvenilir tahmin yapıyor?' sorusuna cevap arar. Yeni fonlar için cevap üretilemez — yeterli geçmiş yok.*")


# Mevcut açıklamalar devam ediyor...
def _p50_reel(p50, baslangic):
    if p50 is None or baslangic is None or baslangic == 0:
        return "Hesaplanamadı."
    yuzde = (p50 / baslangic - 1) * 100
    temel = ("**P50 Reel Getiri (Medyan Tahmin)**, 1 yıl sonraki **en olası** durum. "
             "Hem fiyat değişimi hem enflasyon hesaba katıldı — yani gerçek satın alma gücün bu kadar değişir.\n\n")
    if yuzde > 20:
        yorum = f"🚀 **%{yuzde:+.1f} reel** — enflasyonu büyük farkla yeneceğin tahmin ediliyor. Çok güçlü beklenti."
    elif yuzde > 5:
        yorum = f"✅ **%{yuzde:+.1f} reel** — enflasyonu yeneceğin tahmin ediliyor. Sağlıklı reel getiri."
    elif yuzde > 0:
        yorum = f"🟡 **%{yuzde:+.1f} reel** — enflasyonu hafifçe yeneceğin tahmin ediliyor. Marjinal."
    elif yuzde > -10:
        yorum = f"🟠 **%{yuzde:+.1f} reel** — enflasyonun **altında** kalman bekleniyor. Satın alma gücün düşecek."
    else:
        yorum = f"🔴 **%{yuzde:+.1f} reel** — büyük reel kayıp bekleniyor. Bu fon sana göre olmayabilir."
    return temel + yorum + "\n\n💡 *P50 = 'medyan tahmin'. Yarı yarıya bunun üstüne, yarı yarıya altına çıkma olasılığı var.*"


def _reel_kayip_ihtimal(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Reel Kayıp İhtimali**, 1 yıl sonra **enflasyona yenilme** olasılığın. "
             "Yani 'paranı koysam, alım gücüm azalır mıydı?' sorusunun cevabı.\n\n")
    if deger < 20:
        yorum = f"💚 **%{deger:.0f}** — düşük kayıp ihtimali. Enflasyonu büyük ihtimalle yenersin."
    elif deger < 40:
        yorum = f"🟢 **%{deger:.0f}** — makul kayıp ihtimali. Çoğu zaman enflasyonu yenersin."
    elif deger < 60:
        yorum = f"🟡 **%{deger:.0f}** — yazı-tura. Yarı yarıya enflasyona yenilebilirsin."
    elif deger < 80:
        yorum = f"🟠 **%{deger:.0f}** — yüksek kayıp ihtimali. Genelde enflasyonun altında kalırsın."
    else:
        yorum = f"🔴 **%{deger:.0f}** — çok yüksek kayıp ihtimali. Bu fon enflasyonla baş edemiyor."
    return temel + yorum


def _genel_skor(deger, etiket=""):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Birleşik Skor**, 4 farklı analizin (değerleme, trend, risk, aktif yönetim) **ortalaması**. "
             "0 = göstergeler çok zayıf, 100 = göstergeler çok güçlü.\n\n")
    yorum = f"📊 Skor: **{deger:.0f}/100** → **{etiket}**\n\n"
    if deger >= 70:
        ek = "4 sinyalin neredeyse hepsi olumlu. Çok güçlü göstergeler."
    elif deger >= 58:
        ek = "Sinyallerin çoğunluğu olumlu. Güçlü göstergeler."
    elif deger >= 45:
        ek = "Sinyaller karışık — bazıları olumlu, bazıları olumsuz. Acele etme."
    elif deger >= 32:
        ek = "Sinyallerin çoğu olumsuz. Zayıf göstergeler."
    else:
        ek = "Sinyaller belirgin şekilde olumsuz. Çok zayıf göstergeler."
    return temel + yorum + ek + "\n\n💡 *Bu bir robot tavsiyesi değildir — son karar senin. Yatırım tavsiyesi olarak kullanma.*"


def _backtest_bant(deger, hedef=90):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Bant Kapsama Oranı**, sistemin geçmişteki tahminlerinin ne kadarının P5-P95 bandı içinde tuttuğunu gösterir. "
             "İdeal: %90 (yani tahminlerimizin %90'ı doğru aralıkta).\n\n")
    if deger >= hedef:
        yorum = f"✅ **%{deger:.0f}** — Hedefe ulaşılmış. Sistem güven aralıklarını doğru hesaplıyor."
    elif deger >= hedef - 10:
        yorum = f"🟡 **%{deger:.0f}** — Hedefe yakın ama altında. Tahminler genelde iyi ama bazen şaşırıyor."
    elif deger >= hedef - 20:
        yorum = f"🟠 **%{deger:.0f}** — Hedefin epey altında. Sistem aralıkları dar tahmin ediyor."
    else:
        yorum = f"🔴 **%{deger:.0f}** — Hedefin çok altında. Tahminlere fazla güvenme."
    return temel + yorum


def _backtest_yon(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Yön Doğruluğu**, sistemin 'yükselecek mi, düşecek mi' sorusunu ne kadar doğru cevapladığı. "
             "Rastgele tahmin %50 olur — bunun üstü beceri sayılır.\n\n")
    if deger >= 70:
        yorum = f"🎯 **%{deger:.0f}** — Sistem yönü çok iyi biliyor. Rastgeleden anlamlı şekilde iyi."
    elif deger >= 55:
        yorum = f"📊 **%{deger:.0f}** — Sistem yönü genellikle doğru bilmiş. Rastgeleden iyi."
    elif deger >= 45:
        yorum = f"🟡 **%{deger:.0f}** — Sistem yön konusunda **rastgeleyle aynı**. Tahminlere fazla güvenme."
    else:
        yorum = f"⚠️ **%{deger:.0f}** — Sistem yönü zar atmak kadar bile bilemiyor. Şüpheyle yaklaş."
    return temel + yorum


def _standart_skor(deger, kalite=""):
    if deger is None:
        return "Hesaplanamadı."
    temel = ("**Standart Backtest Skoru**, sistemin geçmiş tahmin başarısını **ufuk-bağımsız** bir 0-100 skoruna çevirir. "
             "Farklı 'geçmiş veri uzunluğu' ayarları arasında karşılaştırma yapmanı sağlar.\n\n"
             "Üç bileşen birleştirilir:\n"
             "- Bant kapsama (%50 ağırlık)\n"
             "- Yön doğruluğu (%30 ağırlık)\n"
             "- Sapma büyüklüğü (%20 ağırlık, √t ile normalize)\n\n")
    yorum = f"📊 Skor: **{deger:.0f}/100** → **{kalite}**\n\n"
    if deger >= 75:
        ek = "Sistem bu fon için çok güvenilir tahmin yapıyor. Sonuçlara güvenebilirsin."
    elif deger >= 60:
        ek = "Sistem bu fon için iyi tahmin yapıyor. Güvenilir."
    elif deger >= 45:
        ek = "Sistem bu fon için orta düzey tahmin yapıyor. Sonuçları yedek bir kontrolle değerlendir."
    elif deger >= 30:
        ek = "Sistem bu fon için zayıf tahmin yapıyor. Şüpheyle yaklaş."
    else:
        ek = "Sistem bu fon için çok zayıf tahmin yapıyor. Tahminlere güvenme."
    return temel + yorum + ek


def _yillik_getiri(deger):
    if deger is None:
        return "Hesaplanamadı."
    temel = "**Yıllık Getiri**, fonun **nominal** (enflasyondan arındırılmamış) yıllık ortalama getirisi.\n\n"
    if deger > 100:
        yorum = f"🚀 **%{deger:+.1f}/yıl** — olağanüstü nominal getiri. Ama enflasyonla kıyaslayıp **reel getiriye** bak."
    elif deger > 50:
        yorum = f"📈 **%{deger:+.1f}/yıl** — yüksek nominal getiri. Enflasyonu yenip yenmediğini reel skorlardan kontrol et."
    elif deger > 25:
        yorum = f"📊 **%{deger:+.1f}/yıl** — makul nominal getiri."
    elif deger > 0:
        yorum = f"🟡 **%{deger:+.1f}/yıl** — düşük nominal getiri."
    else:
        yorum = f"🔴 **%{deger:+.1f}/yıl** — negatif getiri. Fon değer kaybetmiş."
    return temel + yorum + "\n\n💡 *Nominal getiri yanıltıcı olabilir. Enflasyonu yenmiyorsa reel olarak kaybediyorsundur.*"


def _rejim_uyarisi(siddet, karar=""):
    if siddet is None:
        return "Hesaplanamadı."
    temel = ("**Rejim Değişimi Uyarısı**, fonun **son 30 günkü davranışının** geçmişten **belirgin şekilde farklı** olup olmadığını kontrol eder. "
             "Volatilite patlaması veya trend kırılması varsa uyarır.\n\n")
    if siddet == 0:
        yorum = "✅ **Normal davranış**. Fon geçmişteki kalıplarına uygun hareket ediyor. Modele güvenebilirsin."
    elif siddet <= 2:
        yorum = f"🟡 **{karar}**. Son dönemde bazı anormal sinyaller var. Modelin güveni biraz düşürüldü."
    else:
        yorum = f"🔴 **{karar}**. Fon belirgin şekilde geçmişten farklı davranıyor. Model güvenliği %50'ye çekildi — sonuçlara fazla güvenme."
    return temel + yorum


# =============================================================
# ANA SÖZLÜK — terim_id → (başlık, fonksiyon)
# =============================================================

TERIMLER = {
    "sharpe":             ("Sharpe Oranı",          _sharpe),
    "sortino":            ("Sortino Oranı",         _sortino),
    "z_skor":             ("Z-Skor (Konum)",        _z_skor),
    "max_drawdown":       ("Maksimum Düşüş",        _max_drawdown),
    "guncel_drawdown":    ("Güncel Düşüş",          _guncel_drawdown),
    "volatilite":         ("Yıllık Volatilite",     _yillik_volatilite),
    "beta":               ("Beta",                  _beta),
    "alpha":              ("Alpha",                 _alpha),
    "info_ratio":         ("Information Ratio",     _information_ratio),
    "tracking_error":     ("Tracking Error",        _tracking_error),
    "r_squared":          ("R² (R-Kare)",           _r_squared),
    "rsi":                ("RSI (Momentum)",        _rsi),
    "trend":              ("Trend Rejimi",          _trend_rejimi),
    "p50_reel":           ("P50 Reel Getiri",       _p50_reel),
    "reel_kayip":         ("Reel Kayıp İhtimali",   _reel_kayip_ihtimal),
    "genel_skor":         ("Birleşik Skor",         _genel_skor),
    "backtest_bant":      ("Bant Kapsama",          _backtest_bant),
    "backtest_yon":       ("Yön Doğruluğu",         _backtest_yon),
    "standart_skor":      ("Standart Skor",         _standart_skor),
    "yillik_getiri":      ("Yıllık Getiri",         _yillik_getiri),
    "rejim_uyarisi":      ("Rejim Uyarısı",         _rejim_uyarisi),
    # YENİ EKLENENLER
    "sma_sinyali":        ("SMA Sinyali",           _sma_sinyali),
    "yillik_egim":        ("90g Yıllık Eğim",       _yillik_egim),
    "trend_gucu":         ("Trend Gücü (R²)",       _trend_gucu_r2),
    "konum_yorum":        ("Konum Yorumu",          _konum_yorum),
    "rejim_stat":         ("Rejim İstatistikleri",  _rejim_stat),
    "rolling_beta":       ("Rolling Beta",          _rolling_beta),
    "rolling_alpha":      ("Rolling Alpha",         _rolling_alpha),
    "rolling_ir":         ("Rolling IR",            _rolling_ir),
    "rolling_sharpe":     ("Rolling Sharpe",        _rolling_sharpe),
    "backtest_hata":      ("Backtest Hatası",       _backtest_hata),
}


# =============================================================
# DIŞA AÇIK FONKSİYONLAR
# =============================================================

def dinamik_aciklama(terim_id, *args, **kwargs):
    if terim_id not in TERIMLER:
        return "Bu terim için açıklama bulunamadı."
    _, fonksiyon = TERIMLER[terim_id]
    return fonksiyon(*args, **kwargs)


def popover_aciklama(terim_id, *args, label="❓", **kwargs):
    if terim_id not in TERIMLER:
        return
    baslik, fonksiyon = TERIMLER[terim_id]
    with st.popover(label, help=f"{baslik} ne demek?"):
        st.markdown(f"#### {baslik}")
        st.markdown(fonksiyon(*args, **kwargs))


def aciklamali_metrik(etiket, deger_str, terim_id, *args, delta=None, **kwargs):
    if terim_id not in TERIMLER:
        st.metric(etiket, deger_str, delta=delta)
        return

    baslik, fonksiyon = TERIMLER[terim_id]

    container = st.container()
    with container:
        col_m, col_q = st.columns([6, 1])
        with col_m:
            st.metric(etiket, deger_str, delta=delta)
        with col_q:
            st.markdown("<div style='padding-top: 18px;'></div>", unsafe_allow_html=True)
            with st.popover("❓", help=f"{baslik} ne demek?"):
                st.markdown(f"#### {baslik}")
                st.markdown(fonksiyon(*args, **kwargs))


def aciklama_expander(terim_id, *args, baslik_ek="", **kwargs):
    if terim_id not in TERIMLER:
        return
    baslik, fonksiyon = TERIMLER[terim_id]
    with st.expander(f"❓ {baslik}{baslik_ek} ne anlama geliyor?"):
        st.markdown(fonksiyon(*args, **kwargs))


def aciklama_inline(terim_id, *args, **kwargs):
    if terim_id not in TERIMLER:
        return
    _, fonksiyon = TERIMLER[terim_id]
    st.info(fonksiyon(*args, **kwargs))
