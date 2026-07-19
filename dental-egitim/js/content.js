// ============================================================
//  DentaLab 3D — Eğitim içeriği veri katmanı
//  Kaynak niteliğindeki bilgiler diş hekimliği temel ders
//  müfredatına (anatomi, endodonti, kariyoloji) dayanır.
// ============================================================

// Diş katmanları — 3D modelde açılıp kapanan yapılar
export const LAYERS = [
  {
    id: "enamel",
    name: "Mine (Enamel)",
    color: "#eef1f6",
    desc: "Vücudun en sert dokusu · %96 mineral",
    detail:
      "Mine, kronu örten yarı saydam, avasküler ve hücresiz dokudur. Ağırlıkça yaklaşık %96 hidroksiapatit içerir; bu nedenle vücuttaki en sert dokudur. Rejenerasyon yeteneği yoktur — hasar gördüğünde kendini onaramaz. Kalınlığı tüberkül tepesinde en fazla (~2.5 mm), servikal bölgede en incedir.",
  },
  {
    id: "dentin",
    name: "Dentin",
    color: "#f2d9a8",
    desc: "Dişin ana kütlesi · canlı, duyarlı doku",
    detail:
      "Dentin, dişin ana kütlesini oluşturan sarımsı, canlı dokudur. Odontoblast uzantılarını barındıran dentin tübülleri sayesinde uyaranları pulpaya iletir (dentin duyarlılığı). Ömür boyu üretilmeye devam eder: primer, sekonder ve (uyarana yanıt olarak) tersiyer dentin. Mineye göre daha esnektir ve mineyi kırılmaya karşı destekler.",
  },
  {
    id: "pulp",
    name: "Pulpa",
    color: "#ff7a8a",
    desc: "Damar-sinir paketi · dişin canlı çekirdeği",
    detail:
      "Pulpa; kan damarları, sinirler, bağ dokusu ve odontoblastları içeren yumuşak dokudur. Pulpa odası (kron) ve kök kanalları (radiküler) olmak üzere iki bölümden oluşur. Beslenme, duyu (yalnızca ağrı), savunma ve dentin yapımı görevlerini üstlenir. Endodontik tedavinin (kanal tedavisi) hedef dokusudur.",
  },
  {
    id: "cementum",
    name: "Sement",
    color: "#d8c7a0",
    desc: "Kök yüzeyi · periodontal bağlantı",
    detail:
      "Sement, kök dentinini örten mineralize bağ dokusudur. Periodontal ligament liflerinin (Sharpey lifleri) tutunduğu yüzeyi sağlar; böylece dişi alveol kemiğine bağlar. Selüler ve aselüler tipleri vardır. Mineye kıyasla çok daha yumuşaktır.",
  },
  {
    id: "canal",
    name: "Kök Kanalı",
    color: "#c94b6b",
    desc: "Pulpanın kök içi uzantısı",
    detail:
      "Kök kanalı, pulpanın apikal foramen'e uzanan kısmıdır. Kanal morfolojisi diş tipine göre değişir (örn. üst 1. büyük azıda sıklıkla 3–4 kanal, MB2 dahil). Endodontide kanalların tam olarak tespiti, şekillendirilmesi ve doldurulması başarının anahtarıdır.",
  },
];

// Diş tipleri (parametrik 3D üretimi ve içerik için)
export const TEETH = {
  molar: {
    key: "molar",
    name: "Alt 1. Büyük Azı Dişi",
    fdi: "36",
    roots: 2,
    canals: "3 kanal (MB, ML, D)",
    facts: [
      "Genellikle 2 kök: meziyal ve distal.",
      "Meziyal kökte sıkça 2 kanal (MB + ML) bulunur.",
      "5 tüberkül tipiktir (2 bukkal, 2 lingual + 1 distal).",
      "Ağızda en erken (≈6 yaş) süren daimi diştir.",
    ],
  },
  premolar: {
    key: "premolar",
    name: "Üst 1. Küçük Azı Dişi",
    fdi: "14",
    roots: 2,
    canals: "2 kanal (B, P)",
    facts: [
      "Sıklıkla 2 kök: bukkal ve palatinal.",
      "İki tüberkül: bukkal daha belirgin.",
      "Ortodontik çekimlerde sık tercih edilir.",
    ],
  },
  canine: {
    key: "canine",
    name: "Üst Kanin (Köpek Dişi)",
    fdi: "13",
    roots: 1,
    canals: "1 kanal",
    facts: [
      "Ağızdaki en uzun köke sahip diştir.",
      "Tek tüberkül (kesici kenar sivri).",
      "Kanin rehberliği — lateral harekette diğer dişleri korur.",
    ],
  },
  incisor: {
    key: "incisor",
    name: "Üst Santral Kesici",
    fdi: "11",
    roots: 1,
    canals: "1 kanal",
    facts: [
      "Kürek şeklinde, tek köklü.",
      "Estetikte anahtar diş (gülme hattı).",
      "Palatinalde singulum ve marjinal sırtlar bulunur.",
    ],
  },
};

// Black kavite sınıflaması
export const CARIES_CLASSES = [
  {
    id: "1",
    roman: "Sınıf I",
    color: "#3ea6ff",
    title: "Oklüzal çukur ve fissürler",
    desc: "Molar/premolar oklüzal yüzeyleri, ön dişlerin palatinal çukurları ve tüm çukur-fissürler.",
    ex: "Örn. büyük azının çiğneme yüzeyindeki fissür çürüğü.",
  },
  {
    id: "2",
    roman: "Sınıf II",
    color: "#48d19a",
    title: "Arka dişlerin proksimal yüzeyleri",
    desc: "Premolar ve molarların mezial/distal (approksimal) yüzeylerini içerir; sıklıkla oklüzale uzanır (MO, DO, MOD).",
    ex: "Örn. iki molar arasındaki temas noktasında başlayan çürük.",
  },
  {
    id: "3",
    roman: "Sınıf III",
    color: "#ffb547",
    title: "Ön dişlerin proksimali (kenar açısı sağlam)",
    desc: "Kesici ve kaninlerin mezial/distal yüzeyleri; insizal kenar açısı korunmuştur.",
    ex: "Örn. iki santral kesici arasındaki çürük.",
  },
  {
    id: "4",
    roman: "Sınıf IV",
    color: "#ff7a8a",
    title: "Ön dişlerin proksimali + insizal köşe",
    desc: "Sınıf III'e ek olarak insizal kenar açısının kaybı. Estetik restorasyon gerektirir.",
    ex: "Örn. travma veya ilerlemiş çürükle kırılan kesici köşesi.",
  },
  {
    id: "5",
    roman: "Sınıf V",
    color: "#c94b6b",
    title: "Servikal 1/3 (diş eti kenarı)",
    desc: "Tüm dişlerin bukkal/lingual yüzeylerinin gingival üçlüsü. Kök çürükleri ve abfraksiyonlarla ilişkili.",
    ex: "Örn. diş eti çekilmesi olan hastada kök yüzeyi çürüğü.",
  },
  {
    id: "6",
    roman: "Sınıf VI",
    color: "#9aa8c2",
    title: "Tüberkül tepeleri / insizal kenar",
    desc: "Aşınmaya açık tüberkül uçları ve kesici kenarlar (Black'in orijinaline sonradan eklenmiştir).",
    ex: "Örn. tüberkül tepesinde aşınma sonrası oluşan lezyon.",
  },
];

// Endodonti — kök kanal tedavisi adımları
export const ENDO_STEPS = [
  {
    n: 1,
    title: "Tanı ve İzolasyon",
    body: "Pulpa canlılık testleri, perküsyon ve radyografi ile teşhis. Rubber dam ile mutlak izolasyon sağlanır.",
  },
  {
    n: 2,
    title: "Giriş Kavitesi (Access)",
    body: "Pulpa odasına ulaşmak için uygun giriş kavitesi açılır. Tüm kanal ağızları görülmelidir (örn. molar için üçgen/yamuk açı).",
  },
  {
    n: 3,
    title: "Çalışma Boyu Tayini",
    body: "Apeks lokatör ve radyografi ile her kanalın çalışma boyu belirlenir; apikal foramenden ~0.5–1 mm kısa hedeflenir.",
  },
  {
    n: 4,
    title: "Şekillendirme (Kemomekanik)",
    body: "Eğeler (el/döner NiTi) ile kanal şekillendirilir; NaOCl irrigasyonu ile kimyasal dezenfeksiyon yapılır. Apikal açıklık korunur.",
  },
  {
    n: 5,
    title: "Kanal Dolumu (Obturasyon)",
    body: "Kurutulan kanal, güta-perka ve kanal patı ile üç boyutlu doldurulur (lateral/vertikal kondansasyon).",
  },
  {
    n: 6,
    title: "Restorasyon",
    body: "Koronal sızıntıyı önlemek için kalıcı restorasyon; arka dişlerde çoğunlukla kron endikedir.",
  },
];

// Quiz soru bankası
export const QUIZ = [
  {
    q: "Vücuttaki en sert doku hangisidir?",
    opts: ["Dentin", "Mine", "Sement", "Kortikal kemik"],
    a: 1,
    exp: "Mine, ağırlıkça ~%96 mineral (hidroksiapatit) içerdiğinden vücuttaki en sert dokudur ve rejenerasyon yeteneği yoktur.",
  },
  {
    q: "FDI sisteminde '36' numaralı diş hangisidir?",
    opts: ["Üst sağ 1. molar", "Alt sol 1. molar", "Alt sağ 1. premolar", "Üst sol kanin"],
    a: 1,
    exp: "İlk rakam (3) sol-alt çeyreği, ikinci rakam (6) orta hattan itibaren 6. dişi = 1. büyük azıyı belirtir.",
  },
  {
    q: "Alt 1. büyük azının meziyal kökünde tipik olarak kaç kanal bulunur?",
    opts: ["1", "2", "3", "4"],
    a: 1,
    exp: "Meziyal kökte sıklıkla iki kanal bulunur (meziyobukkal ve meziyolingual). Distal kökte genellikle tek kanal vardır.",
  },
  {
    q: "İki molar arasındaki temas noktasında başlayıp oklüzale uzanan çürük hangi Black sınıfındadır?",
    opts: ["Sınıf I", "Sınıf II", "Sınıf III", "Sınıf V"],
    a: 1,
    exp: "Arka dişlerin proksimal yüzey çürükleri Sınıf II'dir. Oklüzale uzanınca MO/DO/MOD kavite adını alır.",
  },
  {
    q: "Dentin duyarlılığından birincil olarak sorumlu yapı hangisidir?",
    opts: ["Mine prizmaları", "Dentin tübülleri", "Sharpey lifleri", "Sement lakünaları"],
    a: 1,
    exp: "Dentin tübülleri içindeki sıvı hareketi (hidrodinamik teori) ve odontoblast uzantıları uyaranı pulpaya iletir.",
  },
  {
    q: "Kök kanal tedavisinde çalışma boyu genellikle nereye göre belirlenir?",
    opts: ["Mine-sement sınırı", "Apikal foramenden ~0.5–1 mm kısa", "Pulpa tavanı", "Furkasyon"],
    a: 1,
    exp: "Apikal konstriksiyon hedeflenir; genelde radyografik apeksten ~0.5–1 mm kısa çalışılır. Apeks lokatör ile teyit edilir.",
  },
  {
    q: "Ağızdaki en uzun köke sahip diş hangisidir?",
    opts: ["Santral kesici", "Kanin", "1. premolar", "2. molar"],
    a: 1,
    exp: "Kaninler (köpek dişleri) en uzun köke sahiptir; bu da onları 'köşe taşı' ve kanin rehberliği için ideal kılar.",
  },
  {
    q: "Diş eti kenarındaki (servikal 1/3) bukkal yüzey çürüğü hangi Black sınıfındadır?",
    opts: ["Sınıf I", "Sınıf III", "Sınıf V", "Sınıf VI"],
    a: 2,
    exp: "Tüm dişlerin servikal üçlüsündeki bukkal/lingual çürükler Sınıf V'tir; kök çürükleri ve abfraksiyonlarla ilişkilidir.",
  },
  {
    q: "Endodontik irrigasyonda en yaygın kullanılan ana solüsyon hangisidir?",
    opts: ["Serum fizyolojik", "Sodyum hipoklorit (NaOCl)", "Hidrojen peroksit", "Klorheksidin (tek başına)"],
    a: 1,
    exp: "NaOCl; doku çözücü ve antibakteriyel etkisiyle altın standarttır. EDTA smear tabakası için, CHX ise ek irrigan olarak kullanılabilir.",
  },
  {
    q: "Pulpanın sağlamadığı görev hangisidir?",
    opts: ["Dentin yapımı", "Beslenme", "Mine onarımı", "Duyu (ağrı)"],
    a: 2,
    exp: "Mine hücresiz ve avaskülerdir; pulpa onu onaramaz. Pulpa beslenme, savunma, duyu ve dentinogenez sağlar.",
  },
];
