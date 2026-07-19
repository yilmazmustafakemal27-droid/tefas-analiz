// ============================================================
//  DentaLab 3D — Three.js diş sahnesi
//  Anatomik yaklaşık, çok katmanlı diş modeli
//  (mine / dentin / pulpa / sement / kanal / diş eti)
// ============================================================
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

// Tüberkül (cusp) yükseklik haritaları — normalize koordinat:
//  x = meziyodistal (-1..1), z = bukkolingual (+z = bukkal)
//  sx/sz = gaussian yayılımı, h = bağıl yükseklik
const CUSPS = {
  // Alt 1. büyük azı: 5 tüberkül (MB, DB, D + ML, DL)
  molar: [
    { x: -0.5, z: 0.55, h: 1.0, sx: 0.42, sz: 0.42 }, // meziyobukkal
    { x: 0.18, z: 0.6, h: 0.95, sx: 0.42, sz: 0.42 }, // distobukkal
    { x: 0.72, z: 0.12, h: 0.8, sx: 0.38, sz: 0.42 }, // distal
    { x: -0.5, z: -0.58, h: 0.95, sx: 0.42, sz: 0.42 }, // meziyolingual
    { x: 0.28, z: -0.58, h: 0.88, sx: 0.42, sz: 0.42 }, // distolingual
  ],
  // Üst 1. küçük azı: 2 tüberkül (bukkal büyük, palatinal)
  premolar: [
    { x: 0.0, z: 0.5, h: 1.0, sx: 0.55, sz: 0.4 }, // bukkal
    { x: 0.0, z: -0.48, h: 0.82, sx: 0.55, sz: 0.4 }, // palatinal
  ],
  // Kanin: tek sivri tüberkül
  canine: [{ x: 0.0, z: 0.08, h: 1.0, sx: 0.5, sz: 0.5 }],
  // Kesici: keskin insizal kenar (meziyodistal sırt) + hafif mamelonlar
  incisor: [
    { x: -0.42, z: 0.0, h: 0.55, sx: 0.28, sz: 0.7 },
    { x: 0.0, z: 0.0, h: 0.6, sx: 0.28, sz: 0.7 },
    { x: 0.42, z: 0.0, h: 0.55, sx: 0.28, sz: 0.7 },
  ],
};

const smoothstep = (a, b, x) => {
  const t = THREE.MathUtils.clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};

export class ToothScene {
  constructor(container) {
    this.container = container;
    this.layerVisible = { enamel: true, dentin: true, pulp: true, cementum: true, canal: true, gingiva: false };
    this.autoRotate = false;
    this.sectioned = false;
    this._initRenderer();
    this._initScene();
    this._initEnvironment();
    this._initLights();
    this._initClipping();
    this.buildTooth("molar");
    this._bindResize();
    this._loop();
  }

  _initRenderer() {
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.localClippingEnabled = true;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.container.appendChild(this.renderer.domElement);
  }

  _initScene() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(
      42,
      this.container.clientWidth / this.container.clientHeight,
      0.1,
      100
    );
    this.camera.position.set(0, 1.2, 9);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 4;
    this.controls.maxDistance = 20;
    this.controls.target.set(0, 0, 0);

    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(6, 48),
      new THREE.MeshBasicMaterial({ color: 0x0a0f18, transparent: true, opacity: 0.5 })
    );
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = -4.2;
    this.scene.add(disc);
  }

  // Gerçekçi yansımalar için PMREM ortam haritası
  _initEnvironment() {
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    const envTex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    this.scene.environment = envTex;
  }

  _initLights() {
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.25));
    const key = new THREE.DirectionalLight(0xffffff, 1.4);
    key.position.set(5, 9, 7);
    this.scene.add(key);
    const rim = new THREE.DirectionalLight(0x6fb2ff, 0.7);
    rim.position.set(-6, 3, -5);
    this.scene.add(rim);
    const fill = new THREE.DirectionalLight(0xffffff, 0.3);
    fill.position.set(0, -5, 4);
    this.scene.add(fill);
  }

  _initClipping() {
    this.clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
  }

  // ---- Materyaller ----
  _matEnamel() {
    return new THREE.MeshPhysicalMaterial({
      color: new THREE.Color("#eef2f8"),
      roughness: 0.14,
      metalness: 0.0,
      clearcoat: 1.0,
      clearcoatRoughness: 0.08,
      transmission: 0.12,
      thickness: 0.6,
      ior: 1.6,
      transparent: true,
      opacity: 0.9,
      envMapIntensity: 1.25,
      side: THREE.DoubleSide,
      clippingPlanes: [],
    });
  }
  _matDentin() {
    return new THREE.MeshPhysicalMaterial({
      color: new THREE.Color("#ecd29a"),
      roughness: 0.5,
      metalness: 0.0,
      clearcoat: 0.25,
      clearcoatRoughness: 0.4,
      envMapIntensity: 0.7,
      side: THREE.DoubleSide,
      clippingPlanes: [],
    });
  }
  _matCementum() {
    return new THREE.MeshPhysicalMaterial({
      color: new THREE.Color("#e0cfa2"),
      roughness: 0.68,
      metalness: 0.0,
      envMapIntensity: 0.5,
      side: THREE.DoubleSide,
      clippingPlanes: [],
    });
  }
  _matPulp() {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color("#e0556a"),
      emissive: new THREE.Color("#5c1622"),
      emissiveIntensity: 0.35,
      roughness: 0.45,
      side: THREE.DoubleSide,
    });
  }
  _matCanal() {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color("#c33f5f"),
      roughness: 0.45,
      side: THREE.DoubleSide,
    });
  }
  _matGingiva() {
    return new THREE.MeshPhysicalMaterial({
      color: new THREE.Color("#e08b93"),
      roughness: 0.55,
      clearcoat: 0.3,
      envMapIntensity: 0.6,
      transparent: true,
      opacity: 0.96,
      side: THREE.DoubleSide,
    });
  }

  // ---- Kron geometrisi (anatomik yaklaşım) ----
  //  dims: { w: meziyodistal, d: bukkolingual, h: yükseklik }
  _crownGeom(type, dims, shrink = 1) {
    const w = dims.w * shrink, d = dims.d * shrink, h = dims.h * shrink;
    const cusps = CUSPS[type];
    const geo = new THREE.SphereGeometry(1, 120, 90);
    const pos = geo.attributes.position;
    const v = new THREE.Vector3();

    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      const yy = (v.y + 1) / 2; // 0 (servikal) .. 1 (oklüzal)

      // Servikal daralma + kron karnı: tabana doğru incelt
      const taper = 0.66 + 0.4 * Math.pow(yy, 0.65);
      let x = v.x * w * taper;
      let z = v.z * d * taper;
      let y = v.y * h;

      // Oklüzal (üst) bölgede tüberkül alanı oluştur
      if (v.y > -0.1) {
        const nx = w > 0 ? x / w : 0;
        const nz = d > 0 ? z / d : 0;
        let field = 0;
        for (const c of cusps) {
          const dx = (nx - c.x) / c.sx;
          const dz = (nz - c.z) / c.sz;
          field = Math.max(field, c.h * Math.exp(-(dx * dx + dz * dz) / 2));
        }
        // üst dome'u bir miktar düzleştir (oklüzal tabla), sonra tüberkülleri yükselt
        const topW = smoothstep(0.0, 0.85, v.y);
        y = y * (1 - 0.28 * topW); // dome'u alçalt
        y += field * h * 0.42 * topW; // tüberkül kabartıları
        // fissür etkisi: tüberkül arası hafif çukur
        y -= (1 - field) * h * 0.06 * topW;
      }

      pos.setXYZ(i, x, y, z);
    }
    geo.computeVertexNormals();
    return geo;
  }

  // ---- Kök geometrisi (bukkolingual yönde oval, sivrilen, eğimli) ----
  _rootGeom(length, topR, offsetX, curve, ovality = 1.35) {
    const path = new THREE.CatmullRomCurve3([
      new THREE.Vector3(offsetX, 0, 0),
      new THREE.Vector3(offsetX + curve * 0.3, -length * 0.4, 0),
      new THREE.Vector3(offsetX + curve * 0.8, -length * 0.8, 0),
      new THREE.Vector3(offsetX + curve, -length, 0),
    ]);
    const geo = new THREE.TubeGeometry(path, 48, topR, 24, false);
    const pos = geo.attributes.position;
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      const t = THREE.MathUtils.clamp(-v.y / length, 0, 1);
      const taper = 1 - 0.8 * t; // apekse doğru sivril
      const cx = offsetX + curve * t;
      v.x = cx + (v.x - cx) * taper;
      v.z *= taper * ovality; // bukkolingual genişlik
      pos.setXYZ(i, v.x, v.y, v.z);
    }
    geo.computeVertexNormals();
    return geo;
  }

  buildTooth(type) {
    if (this.tooth) {
      this.scene.remove(this.tooth);
      this.tooth.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) o.material.dispose();
      });
    }
    this.type = type;
    const g = new THREE.Group();
    this.tooth = g;
    this.meshes = {};

    const P = {
      molar:    { crown: { w: 1.55, d: 1.45, h: 1.35 }, roots: [[-0.6, -0.45], [0.6, 0.45]], rootLen: 2.9, rootR: 0.6, ovality: 1.5, canalsPerRoot: [2, 1] },
      premolar: { crown: { w: 1.05, d: 1.25, h: 1.55 }, roots: [[-0.28, -0.22], [0.28, 0.22]], rootLen: 3.1, rootR: 0.42, ovality: 1.3, canalsPerRoot: [1, 1] },
      canine:   { crown: { w: 0.95, d: 1.05, h: 2.0 }, roots: [[0, 0]], rootLen: 4.0, rootR: 0.6, ovality: 1.25, canalsPerRoot: [1] },
      incisor:  { crown: { w: 1.3, d: 0.72, h: 1.85 }, roots: [[0, 0]], rootLen: 3.1, rootR: 0.52, ovality: 0.85, canalsPerRoot: [1] },
    }[type];

    const crownY = 1.55;

    // ---- MINE ----
    const enamel = new THREE.Mesh(this._crownGeom(type, P.crown), this._matEnamel());
    enamel.position.y = crownY;
    enamel.name = "enamel";
    this.meshes.enamel = enamel;
    g.add(enamel);

    // ---- SEMENT + kök dış yüzey ----
    const cementumGroup = new THREE.Group();
    cementumGroup.name = "cementum";
    P.roots.forEach(([ox, curve]) => {
      const root = new THREE.Mesh(this._rootGeom(P.rootLen, P.rootR, ox, curve, P.ovality), this._matCementum());
      root.position.y = 1.0;
      cementumGroup.add(root);
    });
    this.meshes.cementum = cementumGroup;
    g.add(cementumGroup);

    // ---- DENTIN ----
    const dentinGroup = new THREE.Group();
    dentinGroup.name = "dentin";
    const dCrown = new THREE.Mesh(this._crownGeom(type, P.crown, 0.8), this._matDentin());
    dCrown.position.y = crownY - 0.02;
    dentinGroup.add(dCrown);
    P.roots.forEach(([ox, curve]) => {
      const dRoot = new THREE.Mesh(this._rootGeom(P.rootLen * 0.98, P.rootR * 0.74, ox, curve, P.ovality), this._matDentin());
      dRoot.position.y = 1.0;
      dentinGroup.add(dRoot);
    });
    this.meshes.dentin = dentinGroup;
    g.add(dentinGroup);

    // ---- PULPA odası ----
    const pulpGroup = new THREE.Group();
    pulpGroup.name = "pulp";
    const chamber = new THREE.Mesh(new THREE.SphereGeometry(0.5, 32, 24), this._matPulp());
    chamber.scale.set(P.crown.w * 0.5, P.crown.h * 0.42, P.crown.d * 0.46);
    chamber.position.y = crownY - 0.05;
    pulpGroup.add(chamber);
    this.meshes.pulp = pulpGroup;

    // ---- KÖK KANALLARI ----
    const canalGroup = new THREE.Group();
    canalGroup.name = "canal";
    P.roots.forEach(([ox, curve], ri) => {
      const nCanals = P.canalsPerRoot[ri] || 1;
      for (let c = 0; c < nCanals; c++) {
        const spread = nCanals > 1 ? (c === 0 ? -0.16 : 0.16) : 0;
        const path = new THREE.CatmullRomCurve3([
          new THREE.Vector3(ox + spread, crownY + 0.2, spread * 0.4),
          new THREE.Vector3(ox + spread + curve * 0.3, 0.4, spread),
          new THREE.Vector3(ox + spread + curve * 0.75, -1.0, spread * 0.5),
          new THREE.Vector3(ox + curve, -1.85, 0),
        ]);
        const canal = new THREE.Mesh(new THREE.TubeGeometry(path, 48, 0.075, 14, false), this._matCanal());
        canalGroup.add(canal);
      }
    });
    this.meshes.canal = canalGroup;

    g.add(canalGroup);
    g.add(pulpGroup);

    // ---- DİŞ ETİ (gingiva) — servikal bölgede yaka ----
    const gingiva = new THREE.Mesh(
      new THREE.CylinderGeometry(
        Math.max(P.crown.w, P.crown.d) * 0.92,
        Math.max(P.crown.w, P.crown.d) * 1.05,
        0.9, 40, 1, true
      ),
      this._matGingiva()
    );
    gingiva.position.y = crownY - P.crown.h * 0.72;
    gingiva.name = "gingiva";
    this.meshes.gingiva = gingiva;
    g.add(gingiva);

    g.position.y = -0.6;
    this.scene.add(g);

    this._applyLayerVisibility();
    this._applyClipping();
    this.resetView();
  }

  setLayer(id, visible) {
    this.layerVisible[id] = visible;
    this._applyLayerVisibility();
  }
  _applyLayerVisibility() {
    for (const id of Object.keys(this.meshes)) {
      if (this.meshes[id]) this.meshes[id].visible = this.layerVisible[id];
    }
  }

  toggleSection() {
    this.sectioned = !this.sectioned;
    this._applyClipping();
    return this.sectioned;
  }
  _applyClipping() {
    const planes = this.sectioned ? [this.clipPlane] : [];
    for (const id of ["enamel", "dentin", "cementum", "gingiva"]) {
      const obj = this.meshes[id];
      if (!obj) continue;
      obj.traverse((o) => {
        if (o.material) o.material.clippingPlanes = planes;
      });
    }
  }

  toggleRotate() {
    this.autoRotate = !this.autoRotate;
    return this.autoRotate;
  }

  resetView() {
    this.camera.position.set(0, 1.2, 9);
    this.controls.target.set(0, 0, 0);
    this.controls.update();
  }

  pick(clientX, clientY) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      ((clientX - rect.left) / rect.width) * 2 - 1,
      -((clientY - rect.top) / rect.height) * 2 + 1
    );
    const ray = new THREE.Raycaster();
    ray.setFromCamera(ndc, this.camera);
    const order = ["pulp", "canal", "dentin", "cementum", "gingiva", "enamel"];
    for (const id of order) {
      const obj = this.meshes[id];
      if (!obj || !obj.visible) continue;
      const hits = ray.intersectObject(obj, true);
      if (hits.length) return { id, point: hits[0].point };
    }
    return null;
  }

  projectToScreen(point3) {
    const v = point3.clone().project(this.camera);
    const rect = this.renderer.domElement.getBoundingClientRect();
    return {
      x: (v.x * 0.5 + 0.5) * rect.width + rect.left,
      y: (-v.y * 0.5 + 0.5) * rect.height + rect.top,
    };
  }

  _bindResize() {
    this._onResize = () => {
      const w = this.container.clientWidth, h = this.container.clientHeight;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    };
    window.addEventListener("resize", this._onResize);
  }

  _loop() {
    this._raf = requestAnimationFrame(() => this._loop());
    if (this.autoRotate && this.tooth) this.tooth.rotation.y += 0.006;
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    cancelAnimationFrame(this._raf);
    window.removeEventListener("resize", this._onResize);
    this.renderer.dispose();
  }
}
