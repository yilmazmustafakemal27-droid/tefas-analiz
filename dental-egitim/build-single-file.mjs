// ============================================================
//  DentaLab 3D — tek dosyalık (self-contained) HTML üretici
//  Kullanım:  node build-single-file.mjs
//  Çıktı:     dist/DentaLab-3D.html  (çift tıklayıp açılabilir)
// ============================================================
import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const HERE = dirname(fileURLToPath(import.meta.url));
const R = (p) => readFileSync(join(HERE, p), "utf8");

const css = R("css/style.css");
const three = R("vendor/three/three.module.js");
const orbit = R("vendor/three/addons/controls/OrbitControls.js");
let content = R("js/content.js");
const tooth3d = R("js/tooth3d.js");
const main = R("js/main.js");

// SVG'leri data URI olarak content.js'e göm
const svgs = ["radyografi-molar", "panoramik-sema", "curuk-asamalari", "periodontal-cep", "dis-histoloji"];
for (const name of svgs) {
  const svg = R(`assets/gallery/${name}.svg`);
  const dataUri = "data:image/svg+xml," + encodeURIComponent(svg);
  content = content.split(`assets/gallery/${name}.svg`).join(dataUri);
}

// Güvenlik: </script> kaçışı (kaynaklarda yok ama garanti)
const safe = (s) => s.split("</script").join("<\\/script");

// index.html gövdesini al, importmap ve modül script'ini çıkar
let html = R("index.html");
let body = html.slice(html.indexOf("<body>") + 6, html.indexOf("</body>"));
body = body.replace(/<script type="module" src="js\/main\.js"><\/script>/, "");

const out = `<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>DentaLab 3D — İnteraktif Diş Hekimliği Öğrenme Programı</title>
<style>
${css}
</style>
</head>
<body>
${body}

<script type="text/plain" id="src-three">${safe(three)}</script>
<script type="text/plain" id="src-orbit">${safe(orbit)}</script>
<script type="text/plain" id="src-content">${safe(content)}</script>
<script type="text/plain" id="src-tooth3d">${safe(tooth3d)}</script>
<script type="text/plain" id="src-main">${safe(main)}</script>

<script type="module">
  const get = (id) => document.getElementById(id).textContent;
  const mk = (src) => URL.createObjectURL(new Blob([src], { type: "text/javascript" }));

  const threeURL = mk(get("src-three"));
  const orbitURL = mk(get("src-orbit").split("'three'").join("'" + threeURL + "'").split('"three"').join('"' + threeURL + '"'));
  const contentURL = mk(get("src-content"));
  const toothURL = mk(
    get("src-tooth3d")
      .split('"three/addons/controls/OrbitControls.js"').join('"' + orbitURL + '"')
      .split('"three"').join('"' + threeURL + '"')
  );
  const mainURL = mk(
    get("src-main")
      .split('"./tooth3d.js"').join('"' + toothURL + '"')
      .split('"./content.js"').join('"' + contentURL + '"')
  );
  import(mainURL).catch((e) => {
    document.body.insertAdjacentHTML("beforeend",
      '<div style="position:fixed;inset:0;background:#0e1420;color:#ff6b6b;padding:40px;font-family:sans-serif;z-index:999">Yükleme hatası: ' + e.message + '</div>');
    console.error(e);
  });
</script>
</body>
</html>
`;

mkdirSync(join(HERE, "dist"), { recursive: true });
const outPath = join(HERE, "dist", "DentaLab-3D.html");
writeFileSync(outPath, out);
console.log("Yazıldı:", outPath, "(" + (out.length / 1024 / 1024).toFixed(2) + " MB)");
