// ============================================================
//  DentaLab 3D — Uygulama orkestrasyonu
// ============================================================
import { ToothScene } from "./tooth3d.js";
import { LAYERS, TEETH, CARIES_CLASSES, ENDO_STEPS, QUIZ } from "./content.js";

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
};

const canvasWrap = $("#canvas-wrap");
const sidepanel = $("#sidepanel");
const toothTitle = $("#tooth-title");
const toothFdi = $("#tooth-fdi");
const hotspotLabel = $("#hotspot-label");
const sceneHint = $("#scene-hint");

const scene = new ToothScene(canvasWrap);

let currentMode = "anatomi";
let currentTooth = "molar";

// ---------------- Toast ----------------
let toastTimer;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add("hidden"), 2200);
}

// ---------------- Diş başlığı ----------------
function setToothInfo(key) {
  const t = TEETH[key];
  toothTitle.textContent = t.name;
  toothFdi.textContent = "FDI: " + t.fdi;
}

// ---------------- 3D üst kontroller ----------------
$("#btn-rotate").addEventListener("click", (e) => {
  const on = scene.toggleRotate();
  e.currentTarget.classList.toggle("on", on);
});
$("#btn-reset").addEventListener("click", () => scene.resetView());
$("#btn-section").addEventListener("click", (e) => {
  const on = scene.toggleSection();
  e.currentTarget.classList.toggle("on", on);
  toast(on ? "Kesit görünümü açık — iç yapılar görünür" : "Kesit görünümü kapalı");
});

// ---------------- Hotspot tıklama (sürüklemeden ayır) ----------------
let downPt = null;
canvasWrap.addEventListener("pointerdown", (ev) => {
  downPt = { x: ev.clientX, y: ev.clientY };
});
canvasWrap.addEventListener("pointerup", (ev) => {
  if (!downPt) return;
  const moved = Math.hypot(ev.clientX - downPt.x, ev.clientY - downPt.y);
  downPt = null;
  if (moved > 6) return; // sürükleme → etiket gösterme
  const hit = scene.pick(ev.clientX, ev.clientY);
  if (!hit) { hotspotLabel.classList.add("hidden"); return; }
  const layer = LAYERS.find((l) => l.id === hit.id);
  if (!layer) return;
  const p = scene.projectToScreen(hit.point);
  hotspotLabel.innerHTML = `<b>${layer.name}</b><br>${layer.desc}`;
  hotspotLabel.style.left = p.x + "px";
  hotspotLabel.style.top = p.y + "px";
  hotspotLabel.classList.remove("hidden");
});

// ============================================================
//  MOD: ANATOMİ
// ============================================================
function renderAnatomi() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", "Diş Anatomisi"));
  sidepanel.appendChild(el("p", "panel-sub", "Diş tipini seç, katmanları aç/kapat, modeli döndür ve incele."));

  // Diş tipi seçimi
  const pills = el("div", "pill-row");
  for (const key of Object.keys(TEETH)) {
    const p = el("button", "pill" + (key === currentTooth ? " active" : ""), TEETH[key].short || TEETH[key].name);
    p.addEventListener("click", () => {
      currentTooth = key;
      scene.buildTooth(key);
      setToothInfo(key);
      renderAnatomi();
      toast(TEETH[key].name + " yüklendi");
    });
    pills.appendChild(p);
  }
  sidepanel.appendChild(pills);

  // Katman toggle'ları
  sidepanel.appendChild(el("h3", "", "Katmanlar"));
  LAYERS.forEach((layer) => {
    const row = el("div", "layer-row");
    const on = scene.layerVisible[layer.id];
    row.innerHTML = `
      <div class="l-left">
        <span class="swatch" style="background:${layer.color}"></span>
        <div>
          <div class="l-name">${layer.name}</div>
          <div class="l-desc">${layer.desc}</div>
        </div>
      </div>
      <div class="toggle ${on ? "on" : ""}"></div>`;
    row.addEventListener("click", () => {
      const nv = !scene.layerVisible[layer.id];
      scene.setLayer(layer.id, nv);
      row.querySelector(".toggle").classList.toggle("on", nv);
    });
    sidepanel.appendChild(row);
  });

  // Seçili dişin bilgileri
  const t = TEETH[currentTooth];
  const card = el("div", "card");
  card.innerHTML = `<h3>${t.name} · FDI ${t.fdi}</h3>
    <p><b>Kök sayısı:</b> ${t.roots} &nbsp;·&nbsp; <b>Kanal:</b> ${t.canals}</p>
    <ul class="mini-list">${t.facts.map((f) => `<li>${f}</li>`).join("")}</ul>`;
  sidepanel.appendChild(card);

  // Katman detay kartları
  sidepanel.appendChild(el("h3", "", "Doku Bilgileri"));
  LAYERS.forEach((layer) => {
    const c = el("div", "card");
    c.innerHTML = `<h3><span class="swatch" style="display:inline-block;vertical-align:-2px;background:${layer.color}"></span> ${layer.name}</h3>
      <p>${layer.detail}</p>`;
    sidepanel.appendChild(c);
  });
}

// ============================================================
//  MOD: FDI DİŞ HARİTASI
// ============================================================
// FDI çeyrekler: üst-sağ(1), üst-sol(2), alt-sol(3), alt-sağ(4)
function renderFdi() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", "FDI Diş Numaralandırma"));
  sidepanel.appendChild(el("p", "panel-sub", "İki basamaklı sistem: 1. rakam çeyreği (1–4), 2. rakam orta hattan dişi (1–8) gösterir. Bir dişe tıkla."));

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
  upper.appendChild(buildQuadrant(1, false)); // üst sağ
  upper.appendChild(el("div", "fdi-midline"));
  upper.appendChild(buildQuadrant(2, false)); // üst sol
  wrap.appendChild(upper);

  wrap.appendChild(el("div", "fdi-legend", "▲ Üst çene (maksilla) &nbsp;·&nbsp; ▼ Alt çene (mandibula)"));

  const lower = el("div", "fdi-arch");
  lower.appendChild(buildQuadrant(4, true)); // alt sağ
  lower.appendChild(el("div", "fdi-midline"));
  lower.appendChild(buildQuadrant(3, true)); // alt sol
  wrap.appendChild(lower);

  sidepanel.appendChild(wrap);

  const info = el("div", "card");
  info.id = "fdi-info";
  info.innerHTML = `<h3>Diş seç</h3><p>Şemadan bir diş numarasına tıkla; türü ve konumu burada açıklanır ve 3D modelde gösterilir.</p>`;
  sidepanel.appendChild(info);

  const legend = el("div", "card");
  legend.innerHTML = `<h3>Çeyrek kodları</h3>
    <ul class="mini-list">
      <li><b>1x</b> — Üst sağ (maksiller sağ)</li>
      <li><b>2x</b> — Üst sol (maksiller sol)</li>
      <li><b>3x</b> — Alt sol (mandibular sol)</li>
      <li><b>4x</b> — Alt sağ (mandibular sağ)</li>
    </ul>
    <p style="margin-top:10px"><b>Diş no (2. rakam):</b> 1–2 kesiciler, 3 kanin, 4–5 premolar, 6–8 molar.</p>`;
  sidepanel.appendChild(legend);
}

const FDI_TYPE = (n) => {
  const d = n % 10;
  if (d <= 2) return { type: "incisor", label: "Kesici (santral/lateral)" };
  if (d === 3) return { type: "canine", label: "Kanin (köpek dişi)" };
  if (d <= 5) return { type: "premolar", label: "Küçük azı (premolar)" };
  return { type: "molar", label: "Büyük azı (molar)" };
};
const FDI_QUAD_LABEL = { 1: "Üst sağ", 2: "Üst sol", 3: "Alt sol", 4: "Alt sağ" };

function selectFdi(fdi, btn) {
  document.querySelectorAll(".tooth-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  const quad = Math.floor(fdi / 10);
  const info = FDI_TYPE(fdi);
  scene.buildTooth(info.type);
  toothTitle.textContent = FDI_QUAD_LABEL[quad] + " · " + info.label;
  toothFdi.textContent = "FDI: " + fdi;
  const box = $("#fdi-info");
  if (box) {
    box.innerHTML = `<h3>Diş ${fdi}</h3>
      <p><b>Çeyrek:</b> ${FDI_QUAD_LABEL[quad]} (${quad})<br>
      <b>Konum:</b> orta hattan ${fdi % 10}. diş<br>
      <b>Tür:</b> ${info.label}</p>`;
  }
  toast("Diş " + fdi + " — " + info.label);
}

// ============================================================
//  MOD: ÇÜRÜK / KAVİTE (Black sınıflaması)
// ============================================================
function renderCaries() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", "Çürük & Kavite Sınıflaması"));
  sidepanel.appendChild(el("p", "panel-sub", "G.V. Black kavite sınıflaması. Bir sınıfa tıklayınca açıklaması ve klinik örneği görünür."));

  scene.buildTooth("molar");
  toothTitle.textContent = "Black Kavite Sınıflaması";
  toothFdi.textContent = "Referans: Alt 1. molar (36)";

  CARIES_CLASSES.forEach((cc) => {
    const c = el("div", "card");
    c.style.cursor = "pointer";
    c.innerHTML = `<h3><span class="swatch" style="display:inline-block;vertical-align:-2px;background:${cc.color}"></span> ${cc.roman} — ${cc.title}</h3>
      <p>${cc.desc}</p>
      <p style="margin-top:8px;color:var(--accent)"><em>${cc.ex}</em></p>`;
    c.addEventListener("click", () => {
      // vurgulamak için sadece mine + dentin göster, kesit aç
      ["enamel", "dentin", "cementum", "pulp", "canal"].forEach((id) =>
        scene.setLayer(id, id === "enamel" || id === "dentin")
      );
      if (!scene.sectioned) { scene.toggleSection(); $("#btn-section").classList.add("on"); }
      toast(cc.roman + " seçildi — mine & dentin kesiti");
    });
    sidepanel.appendChild(c);
  });

  const note = el("div", "card");
  note.innerHTML = `<h3>İpucu</h3><p>Sınıf kartına tıklamak 3D modelde mine + dentin kesitini açar; böylece lezyonun tipik yerleşimini üç boyutlu düşünebilirsin.</p>`;
  sidepanel.appendChild(note);
}

// ============================================================
//  MOD: ENDODONTİ
// ============================================================
function renderEndo() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", "Endodonti — Kanal Tedavisi"));
  sidepanel.appendChild(el("p", "panel-sub", "Kök kanal tedavisinin adımları. 3D modelde kanal anatomisini görmek için pulpayı ve kanalları açık tut."));

  scene.buildTooth("molar");
  setToothInfo("molar");
  // kanal anatomisine odak: dış katmanları yarı sakla, kanalları vurgula
  ["enamel", "cementum"].forEach((id) => scene.setLayer(id, false));
  ["dentin", "pulp", "canal"].forEach((id) => scene.setLayer(id, true));

  const btnRow = el("div", "pill-row");
  const showAll = el("button", "pill", "Tüm katmanlar");
  showAll.addEventListener("click", () => { LAYERS.forEach((l) => scene.setLayer(l.id, true)); toast("Tüm katmanlar açık"); });
  const showCanals = el("button", "pill active", "Sadece kanal + pulpa");
  showCanals.addEventListener("click", () => {
    ["enamel", "cementum", "dentin"].forEach((id) => scene.setLayer(id, false));
    ["pulp", "canal"].forEach((id) => scene.setLayer(id, true));
    toast("Kanal sistemi izole edildi");
  });
  btnRow.appendChild(showCanals);
  btnRow.appendChild(showAll);
  sidepanel.appendChild(btnRow);

  ENDO_STEPS.forEach((s) => {
    const c = el("div", "card");
    c.innerHTML = `<h3>${s.n}. ${s.title}</h3><p>${s.body}</p>`;
    sidepanel.appendChild(c);
  });

  const morph = el("div", "card");
  morph.innerHTML = `<h3>Kanal morfolojisi notu</h3>
    <p>Alt 1. molarda tipik olarak <b>meziyal kökte 2 kanal</b> (MB, ML) ve <b>distal kökte 1 kanal</b> bulunur. Model bu yapıyı yaklaşık olarak temsil eder. Klinikte kanal sayısı ve kavisleri değişkendir — CBCT ve büyütme yardımcı olur.</p>`;
  sidepanel.appendChild(morph);
}

// ============================================================
//  MOD: QUIZ
// ============================================================
let quizState = { idx: 0, score: 0, answered: false, order: [] };

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function startQuiz() {
  quizState = { idx: 0, score: 0, answered: false, order: shuffle([...Array(QUIZ.length).keys()]) };
  renderQuizQuestion();
}

function renderQuiz() {
  if (!quizState.order.length) startQuiz();
  else renderQuizQuestion();
}

function renderQuizQuestion() {
  sidepanel.innerHTML = "";
  toothTitle.textContent = "Bilgi Testi";
  toothFdi.textContent = "10 soruluk quiz";

  if (quizState.idx >= quizState.order.length) return renderQuizResult();

  const qi = quizState.order[quizState.idx];
  const item = QUIZ[qi];

  sidepanel.appendChild(el("h2", "panel-h", "Quiz"));
  sidepanel.appendChild(el("div", "quiz-progress", `Soru ${quizState.idx + 1} / ${quizState.order.length} · Skor: ${quizState.score}`));
  sidepanel.appendChild(el("div", "quiz-q", item.q));

  quizState.answered = false;
  const optWrap = el("div");
  item.opts.forEach((opt, i) => {
    const b = el("button", "quiz-opt", opt);
    b.addEventListener("click", () => answerQuiz(i, item, optWrap));
    optWrap.appendChild(b);
  });
  sidepanel.appendChild(optWrap);

  const nextBtn = el("button", "btn-primary hidden", quizState.idx + 1 >= quizState.order.length ? "Sonucu gör" : "Sonraki soru →");
  nextBtn.id = "quiz-next";
  nextBtn.addEventListener("click", () => { quizState.idx++; renderQuizQuestion(); });
  sidepanel.appendChild(nextBtn);
}

function answerQuiz(chosen, item, optWrap) {
  if (quizState.answered) return;
  quizState.answered = true;
  const btns = [...optWrap.querySelectorAll(".quiz-opt")];
  btns.forEach((b, i) => {
    b.disabled = true;
    if (i === item.a) b.classList.add("correct");
    if (i === chosen && chosen !== item.a) b.classList.add("wrong");
  });
  if (chosen === item.a) { quizState.score++; toast("Doğru! ✓"); }
  else toast("Yanlış ✗");

  const exp = el("div", "quiz-explain", `<b>Açıklama:</b> ${item.exp}`);
  optWrap.appendChild(exp);
  $("#quiz-next").classList.remove("hidden");
}

function renderQuizResult() {
  sidepanel.innerHTML = "";
  sidepanel.appendChild(el("h2", "panel-h", "Sonuç"));
  const pct = Math.round((quizState.score / quizState.order.length) * 100);
  sidepanel.appendChild(el("div", "quiz-score", `${quizState.score}/${quizState.order.length}`));
  let msg = pct >= 80 ? "Mükemmel! Temel kavramlara hâkimsin. 🎓"
    : pct >= 50 ? "İyi gidiyorsun — eksik konuları modüllerden tekrar et."
    : "Başlangıç için fena değil; anatomi ve endodonti modüllerini gözden geçir.";
  sidepanel.appendChild(el("p", "panel-sub", msg + ` (Başarı: %${pct})`));

  const retry = el("button", "btn-primary", "Yeniden dene");
  retry.addEventListener("click", startQuiz);
  sidepanel.appendChild(retry);

  const study = el("button", "btn-ghost", "Anatomiye dön");
  study.addEventListener("click", () => switchMode("anatomi"));
  sidepanel.appendChild(study);
}

// ============================================================
//  Mod değişimi
// ============================================================
const RENDERERS = {
  anatomi: renderAnatomi,
  fdi: renderFdi,
  caries: renderCaries,
  endo: renderEndo,
  quiz: renderQuiz,
};
const HINTS = {
  anatomi: "Döndürmek için sürükle · tekerlekle yakınlaştır · katmanları sağdan aç/kapat",
  fdi: "Şemadan bir dişe tıkla — 3D model o diş tipine dönüşür",
  caries: "Sınıf kartına tıkla — 3D'de mine & dentin kesiti açılır",
  endo: "Kanal sistemini izole etmek için sağdaki 'Sadece kanal' düğmesini kullan",
  quiz: "Soruyu yanıtla, açıklamayı oku, sonraki soruya geç",
};

function switchMode(mode) {
  currentMode = mode;
  document.querySelectorAll(".mode-btn").forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));
  hotspotLabel.classList.add("hidden");
  sceneHint.textContent = HINTS[mode];
  // reset layers for a clean state (except quiz which ignores 3D)
  // diş eti (gingiva) varsayılan kapalı, diğerleri açık
  if (mode !== "quiz") LAYERS.forEach((l) => scene.setLayer(l.id, l.id !== "gingiva"));
  RENDERERS[mode]();
}

document.querySelectorAll(".mode-btn").forEach((b) => {
  b.addEventListener("click", () => switchMode(b.dataset.mode));
});

// ---------------- Başlangıç ----------------
setToothInfo(currentTooth);
switchMode("anatomi");
