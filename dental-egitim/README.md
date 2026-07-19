# DentaLab 3D — İnteraktif Diş Hekimliği Öğrenme Programı

Diş hekimliği **4–5. sınıf** öğrencileri için tarayıcıda çalışan, kurulum
gerektirmeyen, **Three.js tabanlı 3D interaktif** öğrenme aracı.

> ⚠️ **Eğitim amaçlıdır.** İçerik temel ders müfredatına dayanan öğrenme
> materyalidir; klinik karar veya tanı aracı değildir.

## Modüller

| Modül | Ne yapar |
|-------|----------|
| **Anatomi** | Diş tipi seç (molar / premolar / kanin / kesici), mine–dentin–pulpa–sement–kanal katmanlarını aç/kapat, modeli döndür, doku bilgilerini oku |
| **Diş Haritası (FDI)** | Tıklanabilir iki-çene şeması; her diş numarasının çeyreği, konumu ve türü açıklanır ve 3D modelde canlanır |
| **Çürük / Kavite** | G.V. Black kavite sınıflaması (Sınıf I–VI); kart seçince 3D'de mine+dentin kesiti açılır |
| **Endodonti** | Kanal tedavisi adımları; kök kanal anatomisini izole ederek gösterir |
| **Quiz** | 10 soruluk, karışık sıralı, açıklamalı bilgi testi + skor |

## 3D özellikleri

- **Parametrik diş modeli** — her diş tipi kendi kron/kök/kanal oranlarıyla üretilir
- **Katman görünürlüğü** — mine, dentin, pulpa, sement, kök kanalı ayrı ayrı açılıp kapanır
- **Kesit (clipping)** — dişi ikiye bölerek iç yapıları gösterir
- **Tıklanabilir noktalar** — model üzerinde bir dokuya tıklayınca adı ve özeti belirir
- **Otomatik döndürme / yakınlaştırma / sıfırlama**

## Çalıştırma

Tamamen statik bir sitedir; **derleme veya bağımlılık yükleme gerekmez.**
Basit bir HTTP sunucusuyla açmanız yeterli (ES modülleri `file://` altında
çalışmaz):

```bash
cd dental-egitim
python3 -m http.server 8000
# tarayıcıda:  http://localhost:8000
```

Alternatif: `npx http-server` veya herhangi bir statik sunucu.

## Dosya yapısı

```
dental-egitim/
├── index.html            # Uygulama kabuğu + importmap
├── css/style.css         # Arayüz teması
├── js/
│   ├── main.js           # Orkestrasyon: navigasyon, paneller, quiz
│   ├── tooth3d.js        # Three.js sahnesi ve parametrik diş modeli
│   └── content.js        # Eğitim içeriği (anatomi, kariyoloji, endodonti, quiz)
└── vendor/three/         # three.js r160 (yerel, çevrimdışı çalışsın diye)
```

## Notlar

- **Çevrimdışı çalışır**: three.js CDN yerine `vendor/` altına yerleştirilmiştir
  (MIT lisanslı, three.js r160).
- Diş modelleri **anatomiyi temsil eden yaklaşık geometrilerdir**; birebir
  klinik doğrulukta hasta taramaları değildir. "Gerçek görselli" bir sürüm için
  yol haritasına bakın.

## Yol haritası

- [ ] Gerçek diş fotoğrafları / radyografi (panoramik, periapikal) galerisi
- [ ] glTF ile gerçek taranmış diş modelleri (CBCT/STL) desteği
- [ ] Konu bazlı quiz modları ve zorluk seviyeleri
- [ ] Periodontoloji ve protez modülleri
- [ ] İlerleme kaydı (localStorage) ve öğrenci profili
- [ ] Türkçe/İngilizce dil seçeneği
