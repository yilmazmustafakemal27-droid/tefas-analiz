// ============================================================
//  DentaLab 3D — Uygulama orkestrasyonu (çift dilli)
// ============================================================
import { ToothScene } from "./tooth3d.js";
import {
  I18N, LAYERS, TEETH, CARIES_CLASSES, ENDO_STEPS, PERIO, PROSTHO,
  GALLERY, QUIZ, QUIZ_TOPICS, QUIZ_DIFF,
} from "./content.js";

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
};

// ---------------- Dil ----------------
let lang = localStorage.getItem("dl_lang") || "tr";
const t = (obj) => (obj && typeof obj === "object" ? obj[lang] ?? obj.tr : obj);
const T = (key) => t(I18N[key]);

// ---------------- DOM ----------------
const canvasWrap = $("#canvas-wrap");
const sidepanel = $("#sidepanel");
const toothTitle = $("#tooth-title");
const toothFdi = $("#tooth-fdi");
const hotspotLabel = $("#hotspot-label");
const sceneHint = $("#scene-hint");
const galleryView = $("#gallery-view");
const viewport = document.querySelector(".viewport");

const scene = new ToothScene(canvasWrap);

let currentMode = "anatomi";
let currentTooth = "molar";

// ---------------- Menü modları ----------------
const MODES = [
  { id: "anatomi", i18n: "mode_anatomi", threeD: true },
  { id: "fdi", i18n: "mode_fdi", threeD: true },
  { id: "caries", i18n: "mode_caries", threeD: true },
  { id: "endo", i18n: "mode_endo", threeD: true },
  { id: "perio", i18n: "mode_perio", threeD: true },
  { id: "prostho", i18n: "mode_prostho", threeD: true },
  { id: "gallery", i18n: "mode_gallery", threeD: false },
  { id: "quiz", i18n: "mode_quiz", threeD: false },
];

function buildNav() {
  const nav = $("#modes");
  nav.innerHTML = "";
  MODES.forEach((m) => {
    const b = el("button", "mode-btn" + (m.id === currentMode ? " active" : ""), T(m.i18n));
    b.dataset.mode = m.id;
    b.addEventListener("click", () => switchMode(m.id));
    nav.appendChild(b);
  });
}

// ---------------- Toast ----------------
let toastTimer;
function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add("hidden"), 2200);
}

// ---------------- Statik i18n + dil değişimi ----------------
function applyStaticI18n() {
  $("#tagline").textContent = T("tagline");
  $("#lang-toggle").textContent = lang.toUpperCase();
  $("#btn-rotate").title = T("btn_rotate");
  $("#btn-reset").title = T("btn_reset");
  $("#btn-section").title = T("btn_section");
  document.documentElement.lang = lang;
}
$("#lang-toggle").addEventListener("click", () => {
  lang = lang === "tr" ? "en" : "tr";
  localStorage.setItem("dl_lang", lang);
  galleryFilter = "all"; // yerelleştirilmiş süzgeç etiketini sıfırla
  applyStaticI18n();
  buildNav();
  switchMode(currentMode);
});

// ---------------- Diş başlığı ----------------
function setToothInfo(key) {
  const tt = TEETH[key];
  toothTitle.textContent = t(tt.name);
  toothFdi.textContent = "FDI: " + tt.fdi;
}

// ---------------- 3D üst kontroller ----------------
$("#btn-rotate").addEventListener("click", (e) => e.currentTarget.classList.toggle("on", scene.toggleRotate()));
$("#btn-reset").addEventListener("click", () => scene.resetView());
$("#btn-section").addEventListener("click", (e) => {
  const on = scene.toggleSection();
  e.currentTarget.classList.toggle("on", on);
  toast(on ? (lang === "tr" ? "Kesit görünümü açık" : "Section view on") : (lang === "tr" ? "Kesit kapalı" : "Section off"));
});

// ---------------- Hotspot (sürükleme/tıklama ayrımı) ----------------
let downPt = null;
canvasWrap.addEventListener("pointerdown", (ev) => (downPt = { x: ev.clientX, y: ev.clientY }));
canvasWrap.addEventListener("pointerup", (ev) => {
  if (!downPt) return;
  const moved = Math.hypot(ev.clientX - downPt.x, ev.clientY - downPt.y);
  downPt = null;
  if (moved > 6) return;
  const hit = scene.pick(ev.clientX, ev.clientY);
  if (!hit) { hotspotLabel.classList.add("hidden"); return; }
  const layer = LAYERS.find((l) => l.id === hit.id);
  if (!layer) return;
  const p = scene.projectToScreen(hit.point);
  hotspotLabel.innerHTML = `<b>${t(layer.name)}</b><br>${t(layer.desc)}`;
  hotspotLabel.style.left = p.x + "px";
  hotspotLabel.style.top = p.y + "px";
  hotspotLabel.classList.remove("hidden");
});

// ============================================================
//  Ortak yardımcılar
// ============================================================
function layerToggleRow(layer) {
  const row = el("div", "layer-row");
  const on = scene.layerVisible[layer.id];
  row.innerHTML = `
    <div class="l-left">
      <span class="swatch" style="background:${layer.color}"></span>
      <div>
        <div class="l-name">${t(layer.name)}</div>
        <div class="l-desc">${t(layer.desc)}</div>
      </div>
    </div>
    <div class="toggle ${on ? "on" : ""}"></div>`;
  row.addEventListener("click", () => {
    const nv = !scene.layerVisible[layer.id];
    scene.setLayer(layer.id, nv);
    row.querySelector(".toggle").classList.toggle("on", nv);
  });
  return row;
}

// ============================================================
//  MOD: ANATOMİ
// ============================================================
function renderAnatomi() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("anatomi_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("anatomi_sub")));

  const pills = el("div", "pill-row");
  for (const key of Object.keys(TEETH)) {
    const p = el("button", "pill" + (key === currentTooth ? " active" : ""), t(TEETH[key].short));
    p.addEventListener("click", () => {
      currentTooth = key;
      scene.buildTooth(key);
      setToothInfo(key);
      renderAnatomi();
      toast(t(TEETH[key].name));
    });
    pills.appendChild(p);
  }
  sidepanel.appendChild(pills);

  sidepanel.appendChild(el("h3", "", T("layers")));
  LAYERS.forEach((layer) => sidepanel.appendChild(layerToggleRow(layer)));

  const tt = TEETH[currentTooth];
  const card = el("div", "card");
  card.innerHTML = `<h3>${t(tt.name)} · FDI ${tt.fdi}</h3>
    <p><b>${T("root_count")}:</b> ${tt.roots} &nbsp;·&nbsp; <b>${T("canal_label")}:</b> ${t(tt.canals)}</p>
    <ul class="mini-list">${t(tt.facts).map((f) => `<li>${f}</li>`).join("")}</ul>`;
  sidepanel.appendChild(card);

  sidepanel.appendChild(el("h3", "", T("tissue_info")));
  LAYERS.forEach((layer) => {
    const c = el("div", "card");
    c.innerHTML = `<h3><span class="swatch" style="display:inline-block;vertical-align:-2px;background:${layer.color}"></span> ${t(layer.name)}</h3>
      <p>${t(layer.detail)}</p>`;
    sidepanel.appendChild(c);
  });
}

// ============================================================
//  MOD: FDI
// ============================================================
const FDI_TYPE = (n) => {
  const d = n % 10;
  if (d <= 2) return { type: "incisor", label: { tr: "Kesici (santral/lateral)", en: "Incisor (central/lateral)" } };
  if (d === 3) return { type: "canine", label: { tr: "Kanin (köpek dişi)", en: "Canine" } };
  if (d <= 5) return { type: "premolar", label: { tr: "Küçük azı (premolar)", en: "Premolar" } };
  return { type: "molar", label: { tr: "Büyük azı (molar)", en: "Molar" } };
};
const FDI_QUAD_LABEL = {
  1: { tr: "Üst sağ", en: "Upper right" }, 2: { tr: "Üst sol", en: "Upper left" },
  3: { tr: "Alt sol", en: "Lower left" }, 4: { tr: "Alt sağ", en: "Lower right" },
};

function renderFdi() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("fdi_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("fdi_sub")));

  const wrap = el("div", "fdi-wrap");
  function buildQuadrant(quadNo, lower) {
    const row = el("div", "fdi-quadrant" + (quadNo === 1 || quadNo === 4 ? " left" : ""));
    for (let i = 1; i <= 8; i++) {
      const fdi = quadNo * 10 + i;
      const btn = el("button", "tooth-btn" + (lower ? " lower" : ""), String(fdi));
      btn.dataset.fdi = fdi;
      btn.addEventListener("click", () => selectFdi(fdi, btn));
      row.appendChild(btn);
    }
    return row;
  }
  const upper = el("div", "fdi-arch");
  upper.appendChild(buildQuadrant(1, false));
  upper.appendChild(el("div", "fdi-midline"));
  upper.appendChild(buildQuadrant(2, false));
  wrap.appendChild(upper);
  wrap.appendChild(el("div", "fdi-legend", `${T("fdi_upper")} &nbsp;·&nbsp; ${T("fdi_lower")}`));
  const lower = el("div", "fdi-arch");
  lower.appendChild(buildQuadrant(4, true));
  lower.appendChild(el("div", "fdi-midline"));
  lower.appendChild(buildQuadrant(3, true));
  wrap.appendChild(lower);
  sidepanel.appendChild(wrap);

  const info = el("div", "card");
  info.id = "fdi-info";
  info.innerHTML = `<h3>${T("fdi_pick")}</h3><p>${T("fdi_pick_desc")}</p>`;
  sidepanel.appendChild(info);

  const legend = el("div", "card");
  legend.innerHTML = `<h3>${T("fdi_quad_codes")}</h3>
    <ul class="mini-list">
      <li><b>1x</b> — ${t(FDI_QUAD_LABEL[1])}</li>
      <li><b>2x</b> — ${t(FDI_QUAD_LABEL[2])}</li>
      <li><b>3x</b> — ${t(FDI_QUAD_LABEL[3])}</li>
      <li><b>4x</b> — ${t(FDI_QUAD_LABEL[4])}</li>
    </ul>`;
  sidepanel.appendChild(legend);
}

function selectFdi(fdi, btn) {
  document.querySelectorAll(".tooth-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  const quad = Math.floor(fdi / 10);
  const info = FDI_TYPE(fdi);
  scene.buildTooth(info.type);
  toothTitle.textContent = t(FDI_QUAD_LABEL[quad]) + " · " + t(info.label);
  toothFdi.textContent = "FDI: " + fdi;
  const box = $("#fdi-info");
  if (box) {
    const nth = T("fdi_nth").replace("{n}", fdi % 10);
    box.innerHTML = `<h3>${lang === "tr" ? "Diş" : "Tooth"} ${fdi}</h3>
      <p><b>${T("fdi_quadrant")}:</b> ${t(FDI_QUAD_LABEL[quad])} (${quad})<br>
      <b>${T("fdi_position")}:</b> ${nth}<br>
      <b>${T("fdi_type")}:</b> ${t(info.label)}</p>`;
  }
  toast("FDI " + fdi + " — " + t(info.label));
}

// ============================================================
//  MOD: ÇÜRÜK / KAVİTE
// ============================================================
function renderCaries() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("caries_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("caries_sub")));

  scene.buildTooth("molar");
  toothTitle.textContent = lang === "tr" ? "Black Kavite Sınıflaması" : "Black Cavity Classification";
  toothFdi.textContent = lang === "tr" ? "Referans: Alt 1. molar (36)" : "Reference: mandibular 1st molar (36)";

  CARIES_CLASSES.forEach((cc) => {
    const c = el("div", "card");
    c.style.cursor = "pointer";
    c.innerHTML = `<h3><span class="swatch" style="display:inline-block;vertical-align:-2px;background:${cc.color}"></span> ${lang === "tr" ? "Sınıf" : "Class"} ${cc.roman} — ${t(cc.title)}</h3>
      <p>${t(cc.desc)}</p>
      <p style="margin-top:8px;color:var(--accent)"><em>${t(cc.ex)}</em></p>`;
    c.addEventListener("click", () => {
      ["enamel", "dentin", "cementum", "pulp", "canal", "gingiva"].forEach((id) =>
        scene.setLayer(id, id === "enamel" || id === "dentin")
      );
      if (!scene.sectioned) { scene.toggleSection(); $("#btn-section").classList.add("on"); }
      toast((lang === "tr" ? "Sınıf " : "Class ") + cc.roman);
    });
    sidepanel.appendChild(c);
  });
}

// ============================================================
//  MOD: ENDODONTİ
// ============================================================
function renderEndo() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("endo_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("endo_sub")));

  scene.buildTooth("molar");
  setToothInfo("molar");
  ["enamel", "cementum", "gingiva"].forEach((id) => scene.setLayer(id, false));
  ["dentin", "pulp", "canal"].forEach((id) => scene.setLayer(id, true));

  const btnRow = el("div", "pill-row");
  const showCanals = el("button", "pill active", T("endo_only_canals"));
  showCanals.addEventListener("click", () => {
    ["enamel", "cementum", "dentin", "gingiva"].forEach((id) => scene.setLayer(id, false));
    ["pulp", "canal"].forEach((id) => scene.setLayer(id, true));
  });
  const showAll = el("button", "pill", T("endo_all_layers"));
  showAll.addEventListener("click", () => LAYERS.forEach((l) => scene.setLayer(l.id, l.id !== "gingiva")));
  btnRow.appendChild(showCanals);
  btnRow.appendChild(showAll);
  sidepanel.appendChild(btnRow);

  ENDO_STEPS.forEach((s) => {
    const c = el("div", "card");
    c.innerHTML = `<h3>${s.n}. ${t(s.title)}</h3><p>${t(s.body)}</p>`;
    sidepanel.appendChild(c);
  });
}

// ============================================================
//  MOD: PERİODONTOLOJİ
// ============================================================
function renderPerio() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("perio_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("perio_sub")));

  scene.buildTooth("canine");
  toothTitle.textContent = T("perio_title");
  toothFdi.textContent = lang === "tr" ? "Diş eti katmanı açık" : "Gingiva layer on";
  LAYERS.forEach((l) => scene.setLayer(l.id, true)); // gingiva dahil

  sidepanel.appendChild(el("h3", "", lang === "tr" ? "Periodonsiyum" : "The periodontium"));
  PERIO.parts.forEach((p) => {
    const c = el("div", "card");
    c.innerHTML = `<h3>${t(p.title)}</h3><p>${t(p.body)}</p>`;
    sidepanel.appendChild(c);
  });

  sidepanel.appendChild(el("h3", "", lang === "tr" ? "Hastalık evreleri" : "Disease stages"));
  PERIO.stages.forEach((s) => {
    const c = el("div", "card");
    c.innerHTML = `<h3><span class="tag ${s.tag}">${t(s.name)}</span></h3><p>${t(s.body)}</p>`;
    sidepanel.appendChild(c);
  });

  const m = el("div", "card");
  m.innerHTML = `<h3>${lang === "tr" ? "Klinik ölçümler" : "Clinical measures"}</h3>
    <ul class="mini-list">${PERIO.measures.map((x) => `<li>${t(x)}</li>`).join("")}</ul>`;
  sidepanel.appendChild(m);
}

// ============================================================
//  MOD: PROTEZ
// ============================================================
function renderProstho() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("prostho_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("prostho_sub")));

  scene.buildTooth("premolar");
  toothTitle.textContent = T("prostho_title");
  toothFdi.textContent = "";
  LAYERS.forEach((l) => scene.setLayer(l.id, l.id !== "gingiva"));

  sidepanel.appendChild(el("h3", "", lang === "tr" ? "Restorasyon tipleri" : "Restoration types"));
  PROSTHO.types.forEach((p) => {
    const c = el("div", "card");
    c.innerHTML = `<h3>${t(p.title)}</h3><p>${t(p.body)}</p>`;
    sidepanel.appendChild(c);
  });

  const s = el("div", "card");
  s.innerHTML = `<h3>${lang === "tr" ? "Genel iş akışı" : "General workflow"}</h3>
    <ul class="mini-list">${PROSTHO.steps.map((x) => `<li>${t(x)}</li>`).join("")}</ul>`;
  sidepanel.appendChild(s);
}

// ============================================================
//  MOD: GALERİ
// ============================================================
let galleryFilter = "all";
function renderGallery() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("gallery_title")));
  sidepanel.appendChild(el("p", "panel-sub", T("gallery_sub")));

  // kategori süzgeçleri
  const cats = ["all", ...new Set(GALLERY.map((g) => t(g.category)))];
  const pills = el("div", "pill-row");
  cats.forEach((cat) => {
    const label = cat === "all" ? T("quiz_all") : cat;
    const p = el("button", "pill" + (galleryFilter === cat ? " active" : ""), label);
    p.addEventListener("click", () => { galleryFilter = cat; renderGallery(); });
    pills.appendChild(p);
  });
  sidepanel.appendChild(pills);

  const add = el("div", "card");
  add.innerHTML = `<h3>${T("gallery_add")}</h3><p>${T("gallery_add_body")}</p>`;
  sidepanel.appendChild(add);

  // ana alanda grid
  galleryView.innerHTML = "";
  const grid = el("div", "gallery-grid");
  GALLERY.filter((g) => galleryFilter === "all" || t(g.category) === galleryFilter).forEach((g) => {
    const card = el("div", "gallery-card");
    card.innerHTML = `
      <div class="gallery-thumb"><img src="${g.src}" alt="${t(g.title)}" loading="lazy" /></div>
      <div class="gallery-meta">
        <div class="gallery-tt">${t(g.title)}</div>
        <div class="gallery-cap">${t(g.caption)}</div>
        <div class="gallery-cat"><span class="tag blue">${t(g.category)}</span></div>
      </div>`;
    card.addEventListener("click", () => openLightbox(g));
    grid.appendChild(card);
  });
  galleryView.appendChild(grid);
}

function openLightbox(g) {
  $("#lightbox-img").src = g.src;
  const lic = g.original ? T("gallery_original") : `${T("gallery_license")}: ${t(g.license) || "—"} · ${T("gallery_source")}: ${t(g.source) || "—"}`;
  $("#lightbox-cap").innerHTML = `<b>${t(g.title)}</b><br>${t(g.caption)}<br><span class="lightbox-lic">${lic}</span>`;
  $("#lightbox").classList.remove("hidden");
}
$("#lightbox-close").addEventListener("click", () => $("#lightbox").classList.add("hidden"));
$("#lightbox").addEventListener("click", (e) => { if (e.target.id === "lightbox") $("#lightbox").classList.add("hidden"); });

// ============================================================
//  MOD: QUIZ + ilerleme kaydı
// ============================================================
const PROGRESS_KEY = "dl_progress";
const loadProgress = () => { try { return JSON.parse(localStorage.getItem(PROGRESS_KEY)) || {}; } catch { return {}; } };
const saveProgress = (p) => localStorage.setItem(PROGRESS_KEY, JSON.stringify(p));

let quizState = { topic: "all", diff: 0, idx: 0, score: 0, answered: false, order: [] };

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function renderQuiz() {
  // seçim ekranı
  sidepanel.innerHTML = "";
  toothTitle.textContent = T("quiz_title");
  toothFdi.textContent = "";
  sidepanel.appendChild(el("h2", "panel-h", T("quiz_title")));

  sidepanel.appendChild(el("h3", "", T("quiz_pick_topic")));
  const topicRow = el("div", "pill-row");
  const topics = [{ id: "all", name: I18N.quiz_all }, ...QUIZ_TOPICS];
  topics.forEach((tp) => {
    const p = el("button", "pill" + (quizState.topic === tp.id ? " active" : ""), t(tp.name));
    p.addEventListener("click", () => { quizState.topic = tp.id; renderQuiz(); });
    topicRow.appendChild(p);
  });
  sidepanel.appendChild(topicRow);

  sidepanel.appendChild(el("h3", "", T("quiz_pick_diff")));
  const diffRow = el("div", "pill-row");
  const diffs = [{ id: 0, name: I18N.quiz_all }, ...QUIZ_DIFF];
  diffs.forEach((df) => {
    const p = el("button", "pill" + (quizState.diff === df.id ? " active" : ""), t(df.name));
    p.addEventListener("click", () => { quizState.diff = df.id; renderQuiz(); });
    diffRow.appendChild(p);
  });
  sidepanel.appendChild(diffRow);

  const pool = quizPool();
  const startBtn = el("button", "btn-primary", `${T("quiz_start")} (${pool.length})`);
  startBtn.disabled = pool.length === 0;
  if (pool.length === 0) sidepanel.appendChild(el("p", "panel-sub", T("quiz_none")));
  startBtn.addEventListener("click", startQuiz);
  sidepanel.appendChild(startBtn);

  renderProgress();
}

function quizPool() {
  return QUIZ.map((q, i) => i).filter((i) => {
    const q = QUIZ[i];
    return (quizState.topic === "all" || q.topic === quizState.topic) &&
           (quizState.diff === 0 || q.diff === quizState.diff);
  });
}

function renderProgress() {
  const prog = loadProgress();
  const keys = Object.keys(prog);
  const wrap = el("div", "card");
  let html = `<h3>${T("progress_title")}</h3>`;
  if (!keys.length) {
    html += `<p>${T("progress_none")}</p>`;
  } else {
    html += `<ul class="mini-list">`;
    keys.sort().forEach((k) => {
      const [tp, df] = k.split("-");
      const topic = QUIZ_TOPICS.find((x) => x.id === tp);
      const diff = QUIZ_DIFF.find((x) => String(x.id) === df);
      const tn = topic ? t(topic.name) : (tp === "all" ? T("quiz_all") : tp);
      const dn = diff ? t(diff.name) : T("quiz_all");
      html += `<li>${tn} · ${dn}: <b>${prog[k].best}/${prog[k].total}</b> (${prog[k].attempts}×)</li>`;
    });
    html += `</ul>`;
  }
  wrap.innerHTML = html;
  sidepanel.appendChild(wrap);
  if (keys.length) {
    const reset = el("button", "btn-ghost", T("progress_reset"));
    reset.addEventListener("click", () => { localStorage.removeItem(PROGRESS_KEY); renderQuiz(); });
    sidepanel.appendChild(reset);
  }
}

function startQuiz() {
  quizState.order = shuffle(quizPool());
  quizState.idx = 0;
  quizState.score = 0;
  quizState.answered = false;
  renderQuizQuestion();
}

function renderQuizQuestion() {
  sidepanel.innerHTML = "";
  toothTitle.textContent = T("quiz_title");
  if (quizState.idx >= quizState.order.length) return renderQuizResult();

  const item = QUIZ[quizState.order[quizState.idx]];
  sidepanel.appendChild(el("h2", "panel-h", T("quiz_title")));
  sidepanel.appendChild(el("div", "quiz-progress", `${T("quiz_q")} ${quizState.idx + 1} / ${quizState.order.length} · ${T("quiz_score")}: ${quizState.score}`));
  sidepanel.appendChild(el("div", "quiz-q", t(item.q)));

  quizState.answered = false;
  const optWrap = el("div");
  t(item.opts).forEach((opt, i) => {
    const b = el("button", "quiz-opt", opt);
    b.addEventListener("click", () => answerQuiz(i, item, optWrap));
    optWrap.appendChild(b);
  });
  sidepanel.appendChild(optWrap);

  const nextBtn = el("button", "btn-primary hidden", quizState.idx + 1 >= quizState.order.length ? T("quiz_see_result") : T("quiz_next"));
  nextBtn.id = "quiz-next";
  nextBtn.addEventListener("click", () => { quizState.idx++; renderQuizQuestion(); });
  sidepanel.appendChild(nextBtn);
}

function answerQuiz(chosen, item, optWrap) {
  if (quizState.answered) return;
  quizState.answered = true;
  [...optWrap.querySelectorAll(".quiz-opt")].forEach((b, i) => {
    b.disabled = true;
    if (i === item.a) b.classList.add("correct");
    if (i === chosen && chosen !== item.a) b.classList.add("wrong");
  });
  if (chosen === item.a) { quizState.score++; toast(T("quiz_correct")); }
  else toast(T("quiz_wrong"));
  optWrap.appendChild(el("div", "quiz-explain", `<b>${T("quiz_explain")}:</b> ${t(item.exp)}`));
  $("#quiz-next").classList.remove("hidden");
}

function renderQuizResult() {
  // ilerleme kaydet
  const total = quizState.order.length;
  if (total) {
    const key = `${quizState.topic}-${quizState.diff}`;
    const prog = loadProgress();
    const prev = prog[key];
    prog[key] = {
      best: Math.max(quizState.score, prev ? prev.best : 0),
      total,
      attempts: (prev ? prev.attempts : 0) + 1,
    };
    saveProgress(prog);
  }

  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", T("quiz_result")));
  sidepanel.appendChild(el("div", "quiz-score", `${quizState.score}/${total}`));
  const pct = total ? Math.round((quizState.score / total) * 100) : 0;
  let msg = pct >= 80 ? (lang === "tr" ? "Mükemmel! 🎓" : "Excellent! 🎓")
    : pct >= 50 ? (lang === "tr" ? "İyi gidiyorsun." : "Good progress.")
    : (lang === "tr" ? "Konuları tekrar et." : "Review the modules.");
  sidepanel.appendChild(el("p", "panel-sub", `${msg} (${T("quiz_success")}: %${pct})`));

  const retry = el("button", "btn-primary", T("quiz_retry"));
  retry.addEventListener("click", startQuiz);
  sidepanel.appendChild(retry);
  const back = el("button", "btn-ghost", T("quiz_back"));
  back.addEventListener("click", renderQuiz);
  sidepanel.appendChild(back);
}

// ============================================================
//  Mod değişimi
// ============================================================
const RENDERERS = {
  anatomi: renderAnatomi, fdi: renderFdi, caries: renderCaries, endo: renderEndo,
  perio: renderPerio, prostho: renderProstho, gallery: renderGallery, quiz: renderQuiz,
};
const HINTS = {
  anatomi: "hint_anatomi", fdi: "hint_fdi", caries: "hint_caries", endo: "hint_endo",
  perio: "hint_perio", prostho: "hint_prostho", gallery: "hint_gallery", quiz: "hint_quiz",
};

function switchMode(mode) {
  currentMode = mode;
  document.querySelectorAll(".mode-btn").forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));
  hotspotLabel.classList.add("hidden");
  sceneHint.textContent = T(HINTS[mode]);

  const cfg = MODES.find((m) => m.id === mode);
  const is3D = cfg && cfg.threeD;
  // 3D kabuğunu (kontroller/başlık) göster/gizle
  viewport.classList.toggle("no-3d", !is3D);
  galleryView.classList.toggle("hidden", mode !== "gallery");
  sceneHint.classList.toggle("hidden", mode === "gallery" || mode === "quiz");

  if (is3D) LAYERS.forEach((l) => scene.setLayer(l.id, l.id !== "gingiva"));
  RENDERERS[mode]();
}

// ---------------- Başlangıç ----------------
applyStaticI18n();
buildNav();
setToothInfo(currentTooth);
switchMode("anatomi");
