// ============================================================
//  DentaLab 3D — Three.js diş sahnesi
//  Parametrik, çok katmanlı diş modeli (mine/dentin/pulpa/kanal)
// ============================================================
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export class ToothScene {
  constructor(container) {
    this.container = container;
    this.layerVisible = { enamel: true, dentin: true, pulp: true, cementum: true, canal: true };
    this.autoRotate = false;
    this.sectioned = false;
    this._initRenderer();
    this._initScene();
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

    // subtle ground shadow disc
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(6, 48),
      new THREE.MeshBasicMaterial({ color: 0x0a0f18, transparent: true, opacity: 0.5 })
    );
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = -4.2;
    this.scene.add(disc);
  }

  _initLights() {
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const key = new THREE.DirectionalLight(0xffffff, 1.15);
    key.position.set(5, 8, 6);
    this.scene.add(key);
    const rim = new THREE.DirectionalLight(0x6fb2ff, 0.6);
    rim.position.set(-6, 2, -4);
    this.scene.add(rim);
    const fill = new THREE.DirectionalLight(0xffffff, 0.35);
    fill.position.set(0, -5, 4);
    this.scene.add(fill);
  }

  _initClipping() {
    // Vertical plane through Z=0 to reveal internal layers
    this.clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
  }

  // ---- Materyaller ----
  _mat(color, opts = {}) {
    return new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(color),
      roughness: opts.roughness ?? 0.45,
      metalness: 0.0,
      clearcoat: opts.clearcoat ?? 0.3,
      transmission: opts.transmission ?? 0,
      transparent: opts.transparent ?? false,
      opacity: opts.opacity ?? 1,
      side: THREE.DoubleSide,
      clippingPlanes: [],
    });
  }

  // ---- Geometri yardımcıları ----
  // Kron: küreden türetilmiş, tüberküllü yumuşak form
  _crownGeom(scale, cuspCount, cuspHeight) {
    const geo = new THREE.SphereGeometry(1, 64, 48);
    const pos = geo.attributes.position;
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      // Kronu üstte genişlet, altta (servikal) daralt
      const y = v.y;
      let r = 1;
      r *= 1 + 0.15 * y; // hafif konik
      // Tüberkül dalgalanması yalnızca üst yüzeyde
      if (y > 0.15) {
        const ang = Math.atan2(v.z, v.x);
        const cusp = Math.cos(ang * cuspCount) * cuspHeight * (y - 0.15);
        r += cusp;
      }
      v.multiplyScalar(r);
      v.x *= 1.05;
      v.z *= 0.95;
      pos.setXYZ(i, v.x * scale.x, v.y * scale.y, v.z * scale.z);
    }
    geo.computeVertexNormals();
    return geo;
  }

  // Kök: yukarıdan aşağıya sivrilen, hafif eğimli
  _rootGeom(length, topR, offsetX, curve) {
    const path = new THREE.CatmullRomCurve3([
      new THREE.Vector3(offsetX, 0, 0),
      new THREE.Vector3(offsetX + curve * 0.3, -length * 0.4, 0),
      new THREE.Vector3(offsetX + curve * 0.8, -length * 0.8, 0),
      new THREE.Vector3(offsetX + curve, -length, 0),
    ]);
    const geo = new THREE.TubeGeometry(path, 40, topR, 20, false);
    // uca doğru sivrilt
    const pos = geo.attributes.position;
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      const t = THREE.MathUtils.clamp((-v.y) / length, 0, 1);
      const taper = 1 - 0.78 * t;
      // eksen etrafında daralt
      const cx = offsetX + curve * t;
      v.x = cx + (v.x - cx) * taper;
      v.z *= taper;
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

    // tip parametreleri
    const P = {
      molar:    { crown: {x:1.5,y:1.1,z:1.4}, cusp:4, ch:0.35, roots:[[-0.55,-0.4],[0.55,0.4]], rootLen:2.8, canalsPerRoot:[2,1] },
      premolar: { crown: {x:1.1,y:1.2,z:1.15}, cusp:2, ch:0.4, roots:[[-0.25,-0.2],[0.25,0.2]], rootLen:3.0, canalsPerRoot:[1,1] },
      canine:   { crown: {x:0.95,y:1.6,z:1.0}, cusp:1, ch:0.55, roots:[[0,0]], rootLen:3.8, canalsPerRoot:[1] },
      incisor:  { crown: {x:1.15,y:1.5,z:0.7}, cusp:1, ch:0.25, roots:[[0,0]], rootLen:3.0, canalsPerRoot:[1] },
    }[type];

    const crownScale = new THREE.Vector3(P.crown.x, P.crown.y, P.crown.z);

    // ---- MINE (dış kron) ----
    const enamel = new THREE.Mesh(
      this._crownGeom(crownScale, P.cusp, P.ch),
      this._mat("#eef1f6", { roughness: 0.25, clearcoat: 0.6, transmission: 0.15, transparent: true, opacity: 0.96 })
    );
    enamel.position.y = 1.6;
    enamel.name = "enamel";
    this.meshes.enamel = enamel;
    g.add(enamel);

    // ---- SEMENT + kök dış yüzeyi ----
    const cementumGroup = new THREE.Group();
    cementumGroup.name = "cementum";
    P.roots.forEach(([ox, curve]) => {
      const root = new THREE.Mesh(
        this._rootGeom(P.rootLen, 0.62, ox, curve),
        this._mat("#e7d7b0", { roughness: 0.6 })
      );
      root.position.y = 1.0;
      cementumGroup.add(root);
    });
    this.meshes.cementum = cementumGroup;
    g.add(cementumGroup);

    // ---- DENTIN (kron + kök iç kütle) ----
    const dentinGroup = new THREE.Group();
    dentinGroup.name = "dentin";
    const dCrown = new THREE.Mesh(
      this._crownGeom(crownScale.clone().multiplyScalar(0.82), P.cusp, P.ch * 0.7),
      this._mat("#f2d9a8", { roughness: 0.5 })
    );
    dCrown.position.y = 1.55;
    dentinGroup.add(dCrown);
    P.roots.forEach(([ox, curve]) => {
      const dRoot = new THREE.Mesh(
        this._rootGeom(P.rootLen * 0.97, 0.46, ox, curve),
        this._mat("#f2d9a8", { roughness: 0.5 })
      );
      dRoot.position.y = 1.0;
      dentinGroup.add(dRoot);
    });
    this.meshes.dentin = dentinGroup;
    g.add(dentinGroup);

    // ---- PULPA odası ----
    const pulpGroup = new THREE.Group();
    pulpGroup.name = "pulp";
    const chamber = new THREE.Mesh(
      new THREE.SphereGeometry(0.5, 32, 24),
      this._mat("#ff7a8a", { roughness: 0.35 })
    );
    chamber.scale.set(P.crown.x * 0.55, P.crown.y * 0.5, P.crown.z * 0.5);
    chamber.position.y = 1.55;
    pulpGroup.add(chamber);
    this.meshes.pulp = pulpGroup;

    // ---- KÖK KANALLARI ----
    const canalGroup = new THREE.Group();
    canalGroup.name = "canal";
    P.roots.forEach(([ox, curve], ri) => {
      const nCanals = P.canalsPerRoot[ri] || 1;
      for (let c = 0; c < nCanals; c++) {
        const spread = nCanals > 1 ? (c === 0 ? -0.18 : 0.18) : 0;
        const path = new THREE.CatmullRomCurve3([
          new THREE.Vector3(ox + spread, 1.9, 0),
          new THREE.Vector3(ox + spread + curve * 0.3, 0.4, 0),
          new THREE.Vector3(ox + spread + curve * 0.75, -1.0, 0),
          new THREE.Vector3(ox + curve, -1.75, 0),
        ]);
        const canal = new THREE.Mesh(
          new THREE.TubeGeometry(path, 40, 0.08, 12, false),
          this._mat("#c94b6b", { roughness: 0.4 })
        );
        canalGroup.add(canal);
      }
    });
    this.meshes.canal = canalGroup;

    // pulpa ve kanal, dentin içinde göründüğü için en sona ekle
    g.add(canalGroup);
    g.add(pulpGroup);

    g.position.y = -0.6;
    this.scene.add(g);

    this._applyLayerVisibility();
    this._applyClipping();
    this.resetView();
  }

  // ---- Görünürlük ----
  setLayer(id, visible) {
    this.layerVisible[id] = visible;
    this._applyLayerVisibility();
  }
  _applyLayerVisibility() {
    for (const id of Object.keys(this.meshes)) {
      if (this.meshes[id]) this.meshes[id].visible = this.layerVisible[id];
    }
  }

  // ---- Kesit (clipping) ----
  toggleSection() {
    this.sectioned = !this.sectioned;
    this._applyClipping();
    return this.sectioned;
  }
  _applyClipping() {
    const planes = this.sectioned ? [this.clipPlane] : [];
    for (const id of ["enamel", "dentin", "cementum"]) {
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

  // ---- Hotspot / tıklama tespiti ----
  pick(clientX, clientY) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      ((clientX - rect.left) / rect.width) * 2 - 1,
      -((clientY - rect.top) / rect.height) * 2 + 1
    );
    const ray = new THREE.Raycaster();
    ray.setFromCamera(ndc, this.camera);
    // görünür katmanları öncelik sırasıyla tara
    const order = ["pulp", "canal", "dentin", "cementum", "enamel"];
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
