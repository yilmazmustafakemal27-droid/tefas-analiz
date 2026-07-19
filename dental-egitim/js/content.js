// ============================================================
//  DentaLab 3D — Eğitim içeriği (çift dilli: TR / EN)
//  Metin alanları { tr, en } biçimindedir; t() ile çözülür.
//  Kaynak: temel diş hekimliği müfredatı (anatomi, kariyoloji,
//  endodonti, periodontoloji, protez).
// ============================================================

// ---- Arayüz metinleri (i18n) ----
export const I18N = {
  tagline: { tr: "Diş Hekimliği 4–5. Sınıf · İnteraktif Öğrenme", en: "Dentistry Years 4–5 · Interactive Learning" },
  mode_anatomi: { tr: "Anatomi", en: "Anatomy" },
  mode_fdi: { tr: "Diş Haritası (FDI)", en: "Tooth Chart (FDI)" },
  mode_caries: { tr: "Çürük / Kavite", en: "Caries / Cavity" },
  mode_endo: { tr: "Endodonti", en: "Endodontics" },
  mode_perio: { tr: "Periodontoloji", en: "Periodontology" },
  mode_prostho: { tr: "Protez", en: "Prosthodontics" },
  mode_gallery: { tr: "Görseller", en: "Gallery" },
  mode_quiz: { tr: "Quiz", en: "Quiz" },

  btn_rotate: { tr: "⟳ Döndür", en: "⟳ Rotate" },
  btn_reset: { tr: "⌂ Sıfırla", en: "⌂ Reset" },
  btn_section: { tr: "◑ Kesit", en: "◑ Section" },

  layers: { tr: "Katmanlar", en: "Layers" },
  tissue_info: { tr: "Doku Bilgileri", en: "Tissue Info" },
  root_count: { tr: "Kök sayısı", en: "Roots" },
  canal_label: { tr: "Kanal", en: "Canals" },

  anatomi_title: { tr: "Diş Anatomisi", en: "Tooth Anatomy" },
  anatomi_sub: { tr: "Diş tipini seç, katmanları aç/kapat, modeli döndür ve incele.", en: "Pick a tooth type, toggle layers, rotate and explore." },

  fdi_title: { tr: "FDI Diş Numaralandırma", en: "FDI Tooth Numbering" },
  fdi_sub: { tr: "İki basamaklı sistem: 1. rakam çeyreği (1–4), 2. rakam orta hattan dişi (1–8) gösterir. Bir dişe tıkla.", en: "Two-digit system: 1st digit = quadrant (1–4), 2nd = tooth from midline (1–8). Click a tooth." },
  fdi_pick: { tr: "Diş seç", en: "Select a tooth" },
  fdi_pick_desc: { tr: "Şemadan bir diş numarasına tıkla; türü ve konumu burada açıklanır ve 3D modelde gösterilir.", en: "Click a tooth number in the chart; its type and location appear here and in the 3D model." },
  fdi_upper: { tr: "▲ Üst çene (maksilla)", en: "▲ Upper jaw (maxilla)" },
  fdi_lower: { tr: "▼ Alt çene (mandibula)", en: "▼ Lower jaw (mandible)" },
  fdi_quad_codes: { tr: "Çeyrek kodları", en: "Quadrant codes" },
  fdi_quadrant: { tr: "Çeyrek", en: "Quadrant" },
  fdi_position: { tr: "Konum", en: "Position" },
  fdi_type: { tr: "Tür", en: "Type" },
  fdi_nth: { tr: "orta hattan {n}. diş", en: "tooth #{n} from midline" },

  caries_title: { tr: "Çürük & Kavite Sınıflaması", en: "Caries & Cavity Classification" },
  caries_sub: { tr: "G.V. Black kavite sınıflaması. Bir sınıfa tıklayınca 3D'de mine & dentin kesiti açılır.", en: "G.V. Black cavity classification. Click a class to open an enamel & dentin section in 3D." },

  endo_title: { tr: "Endodonti — Kanal Tedavisi", en: "Endodontics — Root Canal Treatment" },
  endo_sub: { tr: "Kök kanal tedavisinin adımları. Kanal anatomisini görmek için pulpa ve kanalları açık tut.", en: "Steps of root canal treatment. Keep pulp and canals visible to study canal anatomy." },
  endo_only_canals: { tr: "Sadece kanal + pulpa", en: "Canals + pulp only" },
  endo_all_layers: { tr: "Tüm katmanlar", en: "All layers" },

  perio_title: { tr: "Periodontoloji", en: "Periodontology" },
  perio_sub: { tr: "Periodonsiyum, hastalık evreleri ve klinik ölçümler. Diş etini görmek için katmanı aç.", en: "The periodontium, disease stages and clinical measures. Enable the gingiva layer to view it." },

  prostho_title: { tr: "Protez", en: "Prosthodontics" },
  prostho_sub: { tr: "Sabit ve hareketli protez ile implant üstü restorasyonlara giriş.", en: "Introduction to fixed, removable and implant-supported restorations." },

  gallery_title: { tr: "Görsel Galeri", en: "Image Gallery" },
  gallery_sub: { tr: "Şematik radyografi ve anatomi çizimleri. Büyütmek için bir görsele tıkla.", en: "Schematic radiographs and anatomy illustrations. Click an image to enlarge." },
  gallery_add: { tr: "Kendi gerçek fotoğraf/röntgenlerini nasıl eklerim?", en: "How do I add my own real photos/radiographs?" },
  gallery_add_body: {
    tr: "Kendi görsellerini <code>assets/gallery/</code> klasörüne koy ve <code>js/content.js</code> içindeki GALLERY listesine bir kayıt ekle (title, category, src, caption, license, source). Yalnızca kullanım hakkına sahip olduğun (kendi arşivin veya açık lisanslı) görselleri ekle ve kaynağını belirt.",
    en: "Drop your images into <code>assets/gallery/</code> and add an entry to the GALLERY list in <code>js/content.js</code> (title, category, src, caption, license, source). Only add images you are licensed to use (your own archive or openly licensed) and cite the source.",
  },
  gallery_license: { tr: "Lisans", en: "License" },
  gallery_source: { tr: "Kaynak", en: "Source" },
  gallery_original: { tr: "Orijinal çizim (DentaLab 3D)", en: "Original illustration (DentaLab 3D)" },

  quiz_title: { tr: "Quiz", en: "Quiz" },
  quiz_pick_topic: { tr: "Konu seç", en: "Pick a topic" },
  quiz_pick_diff: { tr: "Zorluk", en: "Difficulty" },
  quiz_all: { tr: "Tümü", en: "All" },
  quiz_start: { tr: "Testi başlat", en: "Start quiz" },
  quiz_q: { tr: "Soru", en: "Question" },
  quiz_score: { tr: "Skor", en: "Score" },
  quiz_explain: { tr: "Açıklama", en: "Explanation" },
  quiz_next: { tr: "Sonraki soru →", en: "Next question →" },
  quiz_see_result: { tr: "Sonucu gör", en: "See result" },
  quiz_result: { tr: "Sonuç", en: "Result" },
  quiz_retry: { tr: "Yeniden dene", en: "Try again" },
  quiz_back: { tr: "Konu seçimine dön", en: "Back to topics" },
  quiz_correct: { tr: "Doğru! ✓", en: "Correct! ✓" },
  quiz_wrong: { tr: "Yanlış ✗", en: "Wrong ✗" },
  quiz_none: { tr: "Bu seçime uygun soru yok.", en: "No questions match this selection." },
  quiz_success: { tr: "Başarı", en: "Score" },
  quiz_best: { tr: "En iyi", en: "Best" },
  progress_title: { tr: "İlerlemen", en: "Your progress" },
  progress_reset: { tr: "İlerlemeyi sıfırla", en: "Reset progress" },
  progress_none: { tr: "Henüz quiz çözmedin.", en: "No quizzes completed yet." },

  hint_anatomi: { tr: "Döndürmek için sürükle · tekerlekle yakınlaştır · katmanları sağdan aç/kapat", en: "Drag to rotate · scroll to zoom · toggle layers on the right" },
  hint_fdi: { tr: "Şemadan bir dişe tıkla — 3D model o diş tipine dönüşür", en: "Click a tooth in the chart — the 3D model morphs to that type" },
  hint_caries: { tr: "Sınıf kartına tıkla — 3D'de mine & dentin kesiti açılır", en: "Click a class card — an enamel & dentin section opens in 3D" },
  hint_endo: { tr: "Kanal sistemini izole etmek için 'Sadece kanal' düğmesini kullan", en: "Use the 'Canals only' button to isolate the canal system" },
  hint_perio: { tr: "Diş eti katmanını açıp servikal bölgeyi incele", en: "Enable the gingiva layer and study the cervical region" },
  hint_prostho: { tr: "Diş tiplerini karşılaştırarak restorasyon planlamayı düşün", en: "Compare tooth types to reason about restoration planning" },
  hint_gallery: { tr: "Büyütmek için görsele tıkla · kategoriye göre süz", en: "Click an image to enlarge · filter by category" },
  hint_quiz: { tr: "Konu ve zorluk seç, testi başlat", en: "Pick a topic and difficulty, then start" },
};

// ---- Diş katmanları ----
export const LAYERS = [
  {
    id: "enamel", color: "#eef1f6",
    name: { tr: "Mine (Enamel)", en: "Enamel" },
    desc: { tr: "Vücudun en sert dokusu · %96 mineral", en: "Hardest tissue in the body · 96% mineral" },
    detail: {
      tr: "Mine, kronu örten yarı saydam, avasküler ve hücresiz dokudur. Ağırlıkça yaklaşık %96 hidroksiapatit içerir; bu nedenle vücuttaki en sert dokudur. Rejenerasyon yeteneği yoktur — hasar gördüğünde kendini onaramaz. Kalınlığı tüberkül tepesinde en fazla (~2.5 mm), servikal bölgede en incedir.",
      en: "Enamel is the translucent, avascular and acellular tissue covering the crown. It is ~96% hydroxyapatite by weight, making it the hardest tissue in the body. It cannot regenerate — once damaged it does not repair itself. It is thickest at the cusp tips (~2.5 mm) and thinnest at the cervical region.",
    },
  },
  {
    id: "dentin", color: "#f2d9a8",
    name: { tr: "Dentin", en: "Dentin" },
    desc: { tr: "Dişin ana kütlesi · canlı, duyarlı doku", en: "Bulk of the tooth · living, sensitive tissue" },
    detail: {
      tr: "Dentin, dişin ana kütlesini oluşturan sarımsı, canlı dokudur. Odontoblast uzantılarını barındıran dentin tübülleri sayesinde uyaranları pulpaya iletir (dentin duyarlılığı). Ömür boyu üretilir: primer, sekonder ve (uyarana yanıt) tersiyer dentin. Mineye göre daha esnektir ve mineyi kırılmaya karşı destekler.",
      en: "Dentin is the yellowish, living tissue that forms the bulk of the tooth. Dentinal tubules housing odontoblast processes transmit stimuli to the pulp (dentin sensitivity). It is produced throughout life: primary, secondary and (in response to stimuli) tertiary dentin. It is more elastic than enamel and supports it against fracture.",
    },
  },
  {
    id: "pulp", color: "#ff7a8a",
    name: { tr: "Pulpa", en: "Pulp" },
    desc: { tr: "Damar-sinir paketi · dişin canlı çekirdeği", en: "Neurovascular core of the tooth" },
    detail: {
      tr: "Pulpa; kan damarları, sinirler, bağ dokusu ve odontoblastları içeren yumuşak dokudur. Pulpa odası (kron) ve kök kanalları (radiküler) olmak üzere iki bölümden oluşur. Beslenme, duyu (yalnızca ağrı), savunma ve dentin yapımı görevlerini üstlenir. Endodontik tedavinin hedef dokusudur.",
      en: "The pulp is soft tissue containing blood vessels, nerves, connective tissue and odontoblasts. It has two parts: the pulp chamber (coronal) and root canals (radicular). It provides nutrition, sensation (pain only), defense and dentinogenesis. It is the target tissue of endodontic treatment.",
    },
  },
  {
    id: "cementum", color: "#d8c7a0",
    name: { tr: "Sement", en: "Cementum" },
    desc: { tr: "Kök yüzeyi · periodontal bağlantı", en: "Root surface · periodontal attachment" },
    detail: {
      tr: "Sement, kök dentinini örten mineralize bağ dokusudur. Periodontal ligament liflerinin (Sharpey lifleri) tutunduğu yüzeyi sağlar; böylece dişi alveol kemiğine bağlar. Selüler ve aselüler tipleri vardır. Mineye kıyasla çok daha yumuşaktır.",
      en: "Cementum is the mineralized connective tissue covering root dentin. It provides the surface where periodontal ligament fibers (Sharpey's fibers) attach, anchoring the tooth to the alveolar bone. It has cellular and acellular types and is much softer than enamel.",
    },
  },
  {
    id: "canal", color: "#c94b6b",
    name: { tr: "Kök Kanalı", en: "Root Canal" },
    desc: { tr: "Pulpanın kök içi uzantısı", en: "Radicular extension of the pulp" },
    detail: {
      tr: "Kök kanalı, pulpanın apikal foramen'e uzanan kısmıdır. Kanal morfolojisi diş tipine göre değişir (örn. üst 1. büyük azıda sıklıkla 3–4 kanal, MB2 dahil). Endodontide kanalların tam tespiti, şekillendirilmesi ve doldurulması başarının anahtarıdır.",
      en: "The root canal is the part of the pulp extending to the apical foramen. Canal morphology varies by tooth type (e.g. the maxillary first molar often has 3–4 canals, including MB2). Accurate location, shaping and filling of canals is the key to endodontic success.",
    },
  },
  {
    id: "gingiva", color: "#e08b93",
    name: { tr: "Diş Eti (Gingiva)", en: "Gingiva" },
    desc: { tr: "Bağlam için · varsayılan kapalı", en: "For context · off by default" },
    detail: {
      tr: "Diş eti, dişi çevreleyen ve alveol kemiğini örten yumuşak dokudur. Serbest ve yapışık diş eti bölümleriyle birlikte diş-eti oluğu (sulkus) ve birleşim epiteli periodontal sağlığın anahtarıdır. Model, servikal bölgedeki diş eti yakasını yaklaşık temsil eder.",
      en: "The gingiva is the soft tissue surrounding the tooth and covering the alveolar bone. Along with the free and attached gingiva, the gingival sulcus and junctional epithelium are key to periodontal health. The model approximates the gingival collar at the cervical region.",
    },
  },
];

// ---- Diş tipleri ----
export const TEETH = {
  molar: {
    key: "molar", fdi: "36", roots: 2,
    name: { tr: "Alt 1. Büyük Azı Dişi", en: "Mandibular First Molar" },
    short: { tr: "Büyük Azı (Molar)", en: "Molar" },
    canals: { tr: "3 kanal (MB, ML, D)", en: "3 canals (MB, ML, D)" },
    facts: {
      tr: ["Genellikle 2 kök: meziyal ve distal.", "Meziyal kökte sıkça 2 kanal (MB + ML) bulunur.", "5 tüberkül tipiktir (2 bukkal, 2 lingual + 1 distal).", "Ağızda en erken (≈6 yaş) süren daimi diştir."],
      en: ["Usually 2 roots: mesial and distal.", "The mesial root often has 2 canals (MB + ML).", "Typically 5 cusps (2 buccal, 2 lingual + 1 distal).", "The earliest-erupting permanent tooth (≈age 6)."],
    },
  },
  premolar: {
    key: "premolar", fdi: "14", roots: 2,
    name: { tr: "Üst 1. Küçük Azı Dişi", en: "Maxillary First Premolar" },
    short: { tr: "Küçük Azı (Premolar)", en: "Premolar" },
    canals: { tr: "2 kanal (B, P)", en: "2 canals (B, P)" },
    facts: {
      tr: ["Sıklıkla 2 kök: bukkal ve palatinal.", "İki tüberkül: bukkal daha belirgin.", "Ortodontik çekimlerde sık tercih edilir."],
      en: ["Frequently 2 roots: buccal and palatal.", "Two cusps: the buccal is more prominent.", "Commonly chosen for orthodontic extractions."],
    },
  },
  canine: {
    key: "canine", fdi: "13", roots: 1,
    name: { tr: "Üst Kanin (Köpek Dişi)", en: "Maxillary Canine" },
    short: { tr: "Kanin", en: "Canine" },
    canals: { tr: "1 kanal", en: "1 canal" },
    facts: {
      tr: ["Ağızdaki en uzun köke sahip diştir.", "Tek tüberkül (kesici kenar sivri).", "Kanin rehberliği — lateral harekette diğer dişleri korur."],
      en: ["Has the longest root in the mouth.", "Single cusp (pointed incisal edge).", "Canine guidance — protects other teeth in lateral movement."],
    },
  },
  incisor: {
    key: "incisor", fdi: "11", roots: 1,
    name: { tr: "Üst Santral Kesici", en: "Maxillary Central Incisor" },
    short: { tr: "Kesici", en: "Incisor" },
    canals: { tr: "1 kanal", en: "1 canal" },
    facts: {
      tr: ["Kürek şeklinde, tek köklü.", "Estetikte anahtar diş (gülme hattı).", "Palatinalde singulum ve marjinal sırtlar bulunur."],
      en: ["Shovel-shaped, single-rooted.", "Key esthetic tooth (smile line).", "Has a cingulum and marginal ridges on the palatal surface."],
    },
  },
};

// ---- Black kavite sınıflaması ----
export const CARIES_CLASSES = [
  {
    id: "1", roman: "I", color: "#3ea6ff",
    title: { tr: "Oklüzal çukur ve fissürler", en: "Occlusal pits and fissures" },
    desc: { tr: "Molar/premolar oklüzal yüzeyleri, ön dişlerin palatinal çukurları ve tüm çukur-fissürler.", en: "Occlusal surfaces of molars/premolars, palatal pits of anteriors and all pit-and-fissure sites." },
    ex: { tr: "Örn. büyük azının çiğneme yüzeyindeki fissür çürüğü.", en: "e.g. a fissure caries on the chewing surface of a molar." },
  },
  {
    id: "2", roman: "II", color: "#48d19a",
    title: { tr: "Arka dişlerin proksimal yüzeyleri", en: "Proximal surfaces of posterior teeth" },
    desc: { tr: "Premolar ve molarların mezial/distal (approksimal) yüzeyleri; sıklıkla oklüzale uzanır (MO, DO, MOD).", en: "Mesial/distal (approximal) surfaces of premolars and molars; often extending to the occlusal (MO, DO, MOD)." },
    ex: { tr: "Örn. iki molar arasındaki temas noktasında başlayan çürük.", en: "e.g. caries starting at the contact point between two molars." },
  },
  {
    id: "3", roman: "III", color: "#ffb547",
    title: { tr: "Ön dişlerin proksimali (kenar açısı sağlam)", en: "Proximal of anteriors (angle intact)" },
    desc: { tr: "Kesici ve kaninlerin mezial/distal yüzeyleri; insizal kenar açısı korunmuştur.", en: "Mesial/distal surfaces of incisors and canines; the incisal angle is preserved." },
    ex: { tr: "Örn. iki santral kesici arasındaki çürük.", en: "e.g. caries between two central incisors." },
  },
  {
    id: "4", roman: "IV", color: "#ff7a8a",
    title: { tr: "Ön dişlerin proksimali + insizal köşe", en: "Proximal of anteriors + incisal angle" },
    desc: { tr: "Sınıf III'e ek olarak insizal kenar açısının kaybı. Estetik restorasyon gerektirir.", en: "Class III plus loss of the incisal angle. Requires esthetic restoration." },
    ex: { tr: "Örn. travma veya ilerlemiş çürükle kırılan kesici köşesi.", en: "e.g. an incisor corner broken by trauma or advanced caries." },
  },
  {
    id: "5", roman: "V", color: "#c94b6b",
    title: { tr: "Servikal 1/3 (diş eti kenarı)", en: "Cervical third (gingival margin)" },
    desc: { tr: "Tüm dişlerin bukkal/lingual yüzeylerinin gingival üçlüsü. Kök çürükleri ve abfraksiyonlarla ilişkili.", en: "Gingival third of buccal/lingual surfaces of any tooth. Associated with root caries and abfraction." },
    ex: { tr: "Örn. diş eti çekilmesi olan hastada kök yüzeyi çürüğü.", en: "e.g. root-surface caries in a patient with gingival recession." },
  },
  {
    id: "6", roman: "VI", color: "#9aa8c2",
    title: { tr: "Tüberkül tepeleri / insizal kenar", en: "Cusp tips / incisal edges" },
    desc: { tr: "Aşınmaya açık tüberkül uçları ve kesici kenarlar (Black'in orijinaline sonradan eklenmiştir).", en: "Wear-prone cusp tips and incisal edges (added later to Black's original scheme)." },
    ex: { tr: "Örn. tüberkül tepesinde aşınma sonrası oluşan lezyon.", en: "e.g. a lesion at a cusp tip following wear." },
  },
];

// ---- Endodonti adımları ----
export const ENDO_STEPS = [
  { n: 1, title: { tr: "Tanı ve İzolasyon", en: "Diagnosis & Isolation" }, body: { tr: "Pulpa canlılık testleri, perküsyon ve radyografi ile teşhis. Rubber dam ile mutlak izolasyon sağlanır.", en: "Diagnosis via pulp vitality tests, percussion and radiography. Absolute isolation is achieved with a rubber dam." } },
  { n: 2, title: { tr: "Giriş Kavitesi (Access)", en: "Access Cavity" }, body: { tr: "Pulpa odasına ulaşmak için uygun giriş kavitesi açılır. Tüm kanal ağızları görülmelidir.", en: "An appropriate access cavity is prepared to reach the pulp chamber. All canal orifices must be visible." } },
  { n: 3, title: { tr: "Çalışma Boyu Tayini", en: "Working Length" }, body: { tr: "Apeks lokatör ve radyografi ile her kanalın çalışma boyu belirlenir; apikal foramenden ~0.5–1 mm kısa hedeflenir.", en: "Working length of each canal is set with an apex locator and radiography; ~0.5–1 mm short of the apical foramen." } },
  { n: 4, title: { tr: "Şekillendirme (Kemomekanik)", en: "Shaping (Chemomechanical)" }, body: { tr: "Eğeler (el/döner NiTi) ile kanal şekillendirilir; NaOCl irrigasyonu ile kimyasal dezenfeksiyon yapılır.", en: "The canal is shaped with files (hand/rotary NiTi); chemical disinfection is done with NaOCl irrigation." } },
  { n: 5, title: { tr: "Kanal Dolumu (Obturasyon)", en: "Obturation" }, body: { tr: "Kurutulan kanal, güta-perka ve kanal patı ile üç boyutlu doldurulur (lateral/vertikal kondansasyon).", en: "The dried canal is three-dimensionally filled with gutta-percha and sealer (lateral/vertical condensation)." } },
  { n: 6, title: { tr: "Restorasyon", en: "Restoration" }, body: { tr: "Koronal sızıntıyı önlemek için kalıcı restorasyon; arka dişlerde çoğunlukla kron endikedir.", en: "A permanent restoration prevents coronal leakage; a crown is usually indicated on posterior teeth." } },
];

// ---- Periodontoloji ----
export const PERIO = {
  parts: [
    { title: { tr: "Diş Eti (Gingiva)", en: "Gingiva" }, body: { tr: "Serbest ve yapışık diş eti; sağlıklıda soluk pembe, sıkı ve keratinize. Gingival oluk (sulkus) derinliği sağlıklıda ≤3 mm'dir.", en: "Free and attached gingiva; healthy tissue is pale pink, firm and keratinized. Healthy sulcus depth is ≤3 mm." } },
    { title: { tr: "Periodontal Ligament (PDL)", en: "Periodontal Ligament (PDL)" }, body: { tr: "Dişi alveol kemiğine bağlayan lif demetleri; çiğneme kuvvetlerini amortize eder ve propriosepsiyon sağlar.", en: "Fiber bundles anchoring the tooth to bone; they cushion occlusal forces and provide proprioception." } },
    { title: { tr: "Sement", en: "Cementum" }, body: { tr: "Kök yüzeyini örter; Sharpey lifleri buraya tutunur.", en: "Covers the root surface; Sharpey's fibers insert here." } },
    { title: { tr: "Alveol Kemiği", en: "Alveolar Bone" }, body: { tr: "Diş soketini (alveol) oluşturan kemik. Kaybı periodontitisin radyografik belirtisidir.", en: "Bone forming the tooth socket. Its loss is a radiographic sign of periodontitis." } },
  ],
  stages: [
    { tag: "green", name: { tr: "Sağlıklı", en: "Healthy" }, body: { tr: "Sulkus ≤3 mm, kanama yok, kemik seviyesi normal.", en: "Sulcus ≤3 mm, no bleeding, normal bone level." } },
    { tag: "warn", name: { tr: "Gingivitis", en: "Gingivitis" }, body: { tr: "Plağa bağlı diş eti iltihabı; kanama ve kızarıklık var ama ataşman kaybı YOK. Geri dönüşümlüdür.", en: "Plaque-induced gingival inflammation; bleeding and redness but NO attachment loss. Reversible." } },
    { tag: "red", name: { tr: "Periodontitis", en: "Periodontitis" }, body: { tr: "Ataşman ve alveol kemiği kaybı; periodontal cep oluşumu. Geri dönüşümsüz; ilerleyebilir.", en: "Loss of attachment and alveolar bone; periodontal pocket formation. Irreversible; can progress." } },
  ],
  measures: [
    { tr: "Sondlama derinliği (PD): cep tabanı–diş eti kenarı mesafesi.", en: "Probing depth (PD): distance from pocket base to gingival margin." },
    { tr: "Klinik ataşman seviyesi (CAL): mine-sement sınırından ölçülen gerçek kayıp.", en: "Clinical attachment level (CAL): true loss measured from the CEJ." },
    { tr: "Sondlamada kanama (BOP): aktif iltihabın göstergesi.", en: "Bleeding on probing (BOP): a sign of active inflammation." },
    { tr: "Plak indeksi ve mobilite dereceleri.", en: "Plaque index and mobility grades." },
  ],
};

// ---- Protez ----
export const PROSTHO = {
  types: [
    { title: { tr: "Sabit Protez (Kron / Köprü)", en: "Fixed Prosthesis (Crown / Bridge)" }, body: { tr: "Aşırı madde kaybı olan dişe kron; eksik dişte komşu dişlere dayanan köprü. Materyaller: metal-seramik, zirkonya, tam seramik.", en: "A crown for a heavily damaged tooth; a bridge supported by adjacent teeth for a missing tooth. Materials: metal-ceramic, zirconia, all-ceramic." } },
    { title: { tr: "Hareketli Protez", en: "Removable Prosthesis" }, body: { tr: "Bölümlü (parsiyel) veya tam protez; birden çok eksik dişte ekonomik çözüm. Retansiyon kroşe veya tutucularla sağlanır.", en: "Partial or complete dentures; an economical solution for multiple missing teeth. Retention via clasps or attachments." } },
    { title: { tr: "İmplant Üstü Restorasyon", en: "Implant-supported Restoration" }, body: { tr: "Kemiğe yerleştirilen titanyum implanta dayanan kron/köprü/protez. Komşu dişleri kesmeden eksik dişi karşılar.", en: "Crown/bridge/denture on a titanium implant placed in bone. Replaces a missing tooth without cutting neighbors." } },
    { title: { tr: "Laminate Veneer", en: "Laminate Veneer" }, body: { tr: "Ön dişlerde minimal preparasyonla estetik amaçlı ince porselen yüzler.", en: "Thin porcelain facings on anteriors for esthetics with minimal preparation." } },
  ],
  steps: [
    { tr: "Muayene, teşhis ve tedavi planı.", en: "Examination, diagnosis and treatment plan." },
    { tr: "Preparasyon (gerekirse) ve ölçü / dijital tarama.", en: "Preparation (if needed) and impression / digital scan." },
    { tr: "Renk seçimi ve laboratuvar/CAD-CAM üretimi.", en: "Shade selection and lab/CAD-CAM fabrication." },
    { tr: "Prova, uyumlama ve simantasyon/teslim.", en: "Try-in, adjustment and cementation/delivery." },
    { tr: "Takip ve bakım önerileri.", en: "Follow-up and maintenance advice." },
  ],
};

// ---- Görsel galeri (orijinal SVG çizimler + kendi görsellerini ekleme) ----
export const GALLERY = [
  { src: "assets/gallery/dis-histoloji.svg", category: { tr: "Anatomi", en: "Anatomy" }, title: { tr: "Diş anatomisi kesiti", en: "Tooth anatomy section" }, caption: { tr: "Kron-kök, mine/dentin/pulpa, sement, PDL ve alveol kemiği.", en: "Crown-root, enamel/dentin/pulp, cementum, PDL and alveolar bone." }, original: true },
  { src: "assets/gallery/radyografi-molar.svg", category: { tr: "Radyografi", en: "Radiography" }, title: { tr: "Periapikal radyografi (molar)", en: "Periapical radiograph (molar)" }, caption: { tr: "Radyoopak mine, radyolusent pulpa/kanal, periapikal bölge.", en: "Radiopaque enamel, radiolucent pulp/canal, periapical region." }, original: true },
  { src: "assets/gallery/panoramik-sema.svg", category: { tr: "Radyografi", en: "Radiography" }, title: { tr: "Panoramik radyografi şeması", en: "Panoramic radiograph schematic" }, caption: { tr: "Çene kavisleri, sinüs maksillaris ve mandibular kanal.", en: "Jaw arches, maxillary sinus and mandibular canal." }, original: true },
  { src: "assets/gallery/curuk-asamalari.svg", category: { tr: "Kariyoloji", en: "Cariology" }, title: { tr: "Çürük ilerleme aşamaları", en: "Caries progression stages" }, caption: { tr: "Mine lezyonundan pulpitise dört aşama.", en: "Four stages from enamel lesion to pulpitis." }, original: true },
  { src: "assets/gallery/periodontal-cep.svg", category: { tr: "Periodontoloji", en: "Periodontology" }, title: { tr: "Periodontal cep ve kemik kaybı", en: "Periodontal pocket & bone loss" }, caption: { tr: "Sağlıklı diş eti ile periodontitis karşılaştırması.", en: "Healthy gingiva vs periodontitis comparison." }, original: true },
];

// ---- Quiz (konu + zorluk etiketli) ----
// topic: anatomi | kariyoloji | endodonti | perio | protez ; diff: 1 kolay, 2 orta, 3 zor
export const QUIZ_TOPICS = [
  { id: "anatomi", name: { tr: "Anatomi", en: "Anatomy" } },
  { id: "kariyoloji", name: { tr: "Kariyoloji", en: "Cariology" } },
  { id: "endodonti", name: { tr: "Endodonti", en: "Endodontics" } },
  { id: "perio", name: { tr: "Periodontoloji", en: "Periodontology" } },
  { id: "protez", name: { tr: "Protez", en: "Prosthodontics" } },
];
export const QUIZ_DIFF = [
  { id: 1, name: { tr: "Kolay", en: "Easy" } },
  { id: 2, name: { tr: "Orta", en: "Medium" } },
  { id: 3, name: { tr: "Zor", en: "Hard" } },
];

export const QUIZ = [
  { topic: "anatomi", diff: 1,
    q: { tr: "Vücuttaki en sert doku hangisidir?", en: "What is the hardest tissue in the body?" },
    opts: { tr: ["Dentin", "Mine", "Sement", "Kortikal kemik"], en: ["Dentin", "Enamel", "Cementum", "Cortical bone"] }, a: 1,
    exp: { tr: "Mine, ağırlıkça ~%96 mineral içerdiğinden vücuttaki en sert dokudur ve rejenerasyon yeteneği yoktur.", en: "Enamel is ~96% mineral by weight, making it the hardest tissue in the body, and it cannot regenerate." } },
  { topic: "anatomi", diff: 2,
    q: { tr: "FDI sisteminde '36' numaralı diş hangisidir?", en: "Which tooth is number '36' in the FDI system?" },
    opts: { tr: ["Üst sağ 1. molar", "Alt sol 1. molar", "Alt sağ 1. premolar", "Üst sol kanin"], en: ["Upper right 1st molar", "Lower left 1st molar", "Lower right 1st premolar", "Upper left canine"] }, a: 1,
    exp: { tr: "İlk rakam (3) sol-alt çeyreği, ikinci rakam (6) orta hattan 6. dişi = 1. büyük azıyı belirtir.", en: "The first digit (3) marks the lower-left quadrant, the second (6) the 6th tooth from the midline = the first molar." } },
  { topic: "anatomi", diff: 3,
    q: { tr: "Ağızdaki en uzun köke sahip diş hangisidir?", en: "Which tooth has the longest root in the mouth?" },
    opts: { tr: ["Santral kesici", "Kanin", "1. premolar", "2. molar"], en: ["Central incisor", "Canine", "1st premolar", "2nd molar"] }, a: 1,
    exp: { tr: "Kaninler en uzun köke sahiptir; bu da onları 'köşe taşı' ve kanin rehberliği için ideal kılar.", en: "Canines have the longest roots, making them the 'cornerstone' teeth ideal for canine guidance." } },
  { topic: "anatomi", diff: 2,
    q: { tr: "Dentin duyarlılığından birincil olarak sorumlu yapı hangisidir?", en: "Which structure is primarily responsible for dentin sensitivity?" },
    opts: { tr: ["Mine prizmaları", "Dentin tübülleri", "Sharpey lifleri", "Sement lakünaları"], en: ["Enamel prisms", "Dentinal tubules", "Sharpey's fibers", "Cementum lacunae"] }, a: 1,
    exp: { tr: "Dentin tübülleri içindeki sıvı hareketi (hidrodinamik teori) ve odontoblast uzantıları uyaranı pulpaya iletir.", en: "Fluid movement in dentinal tubules (hydrodynamic theory) and odontoblast processes transmit stimuli to the pulp." } },

  { topic: "kariyoloji", diff: 1,
    q: { tr: "İki molar arasındaki temas noktasında başlayan çürük hangi Black sınıfındadır?", en: "Caries starting at the contact point between two molars is which Black class?" },
    opts: { tr: ["Sınıf I", "Sınıf II", "Sınıf III", "Sınıf V"], en: ["Class I", "Class II", "Class III", "Class V"] }, a: 1,
    exp: { tr: "Arka dişlerin proksimal yüzey çürükleri Sınıf II'dir. Oklüzale uzanınca MO/DO/MOD adını alır.", en: "Proximal caries of posterior teeth is Class II. Extending to the occlusal it becomes MO/DO/MOD." } },
  { topic: "kariyoloji", diff: 2,
    q: { tr: "Diş eti kenarındaki (servikal 1/3) bukkal yüzey çürüğü hangi Black sınıfındadır?", en: "A buccal caries at the gingival margin (cervical third) is which Black class?" },
    opts: { tr: ["Sınıf I", "Sınıf III", "Sınıf V", "Sınıf VI"], en: ["Class I", "Class III", "Class V", "Class VI"] }, a: 2,
    exp: { tr: "Servikal üçlüdeki bukkal/lingual çürükler Sınıf V'tir; kök çürükleri ve abfraksiyonlarla ilişkilidir.", en: "Buccal/lingual caries in the cervical third is Class V; associated with root caries and abfraction." } },
  { topic: "kariyoloji", diff: 1,
    q: { tr: "Mine ile sınırlı, henüz kavitasyon oluşmamış erken lezyon nasıl adlandırılır?", en: "What is an early enamel-limited lesion without cavitation called?" },
    opts: { tr: ["Pulpitis", "Beyaz nokta lezyonu", "Abse", "Hipersementoz"], en: ["Pulpitis", "White spot lesion", "Abscess", "Hypercementosis"] }, a: 1,
    exp: { tr: "Beyaz nokta lezyonu demineralizasyonun ilk klinik bulgusudur ve remineralizasyonla geri döndürülebilir.", en: "A white spot lesion is the first clinical sign of demineralization and can be reversed by remineralization." } },

  { topic: "endodonti", diff: 2,
    q: { tr: "Alt 1. büyük azının meziyal kökünde tipik olarak kaç kanal bulunur?", en: "How many canals are typically in the mesial root of a mandibular first molar?" },
    opts: { tr: ["1", "2", "3", "4"], en: ["1", "2", "3", "4"] }, a: 1,
    exp: { tr: "Meziyal kökte sıklıkla iki kanal bulunur (MB ve ML). Distal kökte genellikle tek kanal vardır.", en: "The mesial root often has two canals (MB and ML). The distal root usually has one." } },
  { topic: "endodonti", diff: 2,
    q: { tr: "Kök kanal tedavisinde çalışma boyu genellikle nereye göre belirlenir?", en: "In root canal treatment, working length is usually set relative to what?" },
    opts: { tr: ["Mine-sement sınırı", "Apikal foramenden ~0.5–1 mm kısa", "Pulpa tavanı", "Furkasyon"], en: ["The CEJ", "~0.5–1 mm short of the apical foramen", "Pulp roof", "Furcation"] }, a: 1,
    exp: { tr: "Apikal konstriksiyon hedeflenir; genelde radyografik apeksten ~0.5–1 mm kısa çalışılır. Apeks lokatör ile teyit edilir.", en: "The apical constriction is targeted; usually ~0.5–1 mm short of the radiographic apex, confirmed with an apex locator." } },
  { topic: "endodonti", diff: 3,
    q: { tr: "Endodontik irrigasyonda en yaygın kullanılan ana solüsyon hangisidir?", en: "What is the most common main solution in endodontic irrigation?" },
    opts: { tr: ["Serum fizyolojik", "Sodyum hipoklorit (NaOCl)", "Hidrojen peroksit", "Klorheksidin (tek başına)"], en: ["Saline", "Sodium hypochlorite (NaOCl)", "Hydrogen peroxide", "Chlorhexidine (alone)"] }, a: 1,
    exp: { tr: "NaOCl; doku çözücü ve antibakteriyel etkisiyle altın standarttır. EDTA smear tabakası için kullanılır.", en: "NaOCl is the gold standard for its tissue-dissolving and antibacterial effect. EDTA is used for the smear layer." } },

  { topic: "perio", diff: 1,
    q: { tr: "Sağlıklı bir gingival sulkus derinliği en fazla kaç mm'dir?", en: "What is the maximum depth of a healthy gingival sulcus?" },
    opts: { tr: ["1 mm", "3 mm", "6 mm", "9 mm"], en: ["1 mm", "3 mm", "6 mm", "9 mm"] }, a: 1,
    exp: { tr: "Sağlıklıda sondlama derinliği genellikle ≤3 mm'dir. Daha derin ölçümler cep oluşumunu düşündürür.", en: "Healthy probing depth is generally ≤3 mm. Deeper readings suggest pocket formation." } },
  { topic: "perio", diff: 2,
    q: { tr: "Gingivitis ile periodontitisi ayıran temel bulgu nedir?", en: "What key finding distinguishes gingivitis from periodontitis?" },
    opts: { tr: ["Diş eti kanaması", "Klinik ataşman/kemik kaybı", "Kızarıklık", "Plak varlığı"], en: ["Gingival bleeding", "Clinical attachment/bone loss", "Redness", "Presence of plaque"] }, a: 1,
    exp: { tr: "Gingivitis geri dönüşümlü ve ataşman kaybı yoktur; periodontitiste ataşman ve alveol kemiği kaybı vardır.", en: "Gingivitis is reversible with no attachment loss; periodontitis involves attachment and alveolar bone loss." } },

  { topic: "protez", diff: 1,
    q: { tr: "Tek bir eksik dişi komşu dişleri kesmeden karşılayan seçenek hangisidir?", en: "Which option replaces a single missing tooth without cutting neighbors?" },
    opts: { tr: ["Sabit köprü", "Dental implant", "Tam protez", "Kron"], en: ["Fixed bridge", "Dental implant", "Complete denture", "Crown"] }, a: 1,
    exp: { tr: "İmplant, komşu dişlere dokunmadan tek diş eksikliğini karşılar; köprü ise dayanak dişlerin preparasyonunu gerektirir.", en: "An implant replaces a single tooth without touching neighbors; a bridge requires preparing the abutment teeth." } },
  { topic: "protez", diff: 2,
    q: { tr: "Aşağıdakilerden hangisi tam seramik/zirkonya kronun başlıca avantajıdır?", en: "Which is a main advantage of all-ceramic/zirconia crowns?" },
    opts: { tr: ["Yüksek estetik ve biyouyumluluk", "En ucuz seçenek olması", "Metalden daha zayıf olması", "Ölçü gerektirmemesi"], en: ["High esthetics and biocompatibility", "Being the cheapest option", "Being weaker than metal", "Requiring no impression"] }, a: 0,
    exp: { tr: "Tam seramik/zirkonya restorasyonlar metal desteksiz yüksek estetik ve iyi biyouyumluluk sağlar.", en: "All-ceramic/zirconia restorations provide high esthetics without metal and good biocompatibility." } },
];
