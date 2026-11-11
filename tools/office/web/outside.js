// Everything outside the office: Seoul seen from above, around the floating floor, by night and by day.
import * as THREE from "three";
import { FONT_STACK, mulberry32 } from "./textures.js";

const THEMES = {
  warm: { ground: 0x8f98c0 },
  cool: { ground: 0x7fb4d8 },
};

// Two palettes for the same map: the lit night city and the clean daylight one.
const PALETTES = {
  night: {
    base: "#0a1028",
    block: (r) => `rgb(${22 + r() * 18}, ${28 + r() * 18}, ${58 + r() * 28})`,
    lights: 0.2,
    lightColors: ["rgba(255,214,140,.6)", "rgba(160,215,255,.55)"],
    avenue: "rgba(255,196,110,.2)",
    street: "rgba(255,186,100,.07)",
    river: ["#0c1f44", "#12315f", "rgba(90,140,230,.25)"],
    riverScale: 1,
    glint: (a) => `rgba(150,195,255,${a})`,
    bridge: "rgba(255,225,170,.7)",
    bridgeLights: "#ffe2a8",
  },
  day: {
    base: "#d6dde8",
    block: (r) => (r() < 0.09 ? `rgb(${150 + r() * 14}, ${196 + r() * 14}, ${152 + r() * 12})` : `rgb(${222 + r() * 10}, ${228 + r() * 8}, ${238 + r() * 6})`),
    lights: 0,
    lightColors: [],
    avenue: "rgba(255,255,255,.55)",
    street: "rgba(255,255,255,.3)",
    river: ["#7aa0cc", "#8fb3d9", "rgba(225,242,255,.4)"], // muted: the river must not outshine the floor
    riverScale: 1.6,
    glint: (a) => `rgba(255,255,255,${a * 0.5})`,
    bridge: "rgba(255,255,255,.95)",
    bridgeLights: "#eef3fa",
  },
};

// The whole backdrop is one city map: blocks, streets, the Han river and its bridges.
function groundTexture(p) {
  const S = 2048;
  const K = S / 1024; // the river is laid out on a 1024 grid
  const c = document.createElement("canvas");
  c.width = c.height = S;
  const g = c.getContext("2d");
  const rand = mulberry32(99); // the same layout for both palettes
  g.fillStyle = p.base;
  g.fillRect(0, 0, S, S);

  const CELL = 20;
  for (let y = 0; y < S; y += CELL) {
    for (let x = 0; x < S; x += CELL) {
      g.fillStyle = p.block(rand);
      g.fillRect(x + 2, y + 2, CELL - 4, CELL - 4);
      for (let i = 0; i < 3; i++) {
        const lx = x + 4 + rand() * 12, ly = y + 4 + rand() * 12, on = rand() < p.lights, warm = rand() < 0.7;
        if (on && p.lightColors.length) {
          g.fillStyle = p.lightColors[warm ? 0 : 1];
          g.fillRect(lx, ly, 1.5, 1.5);
        }
      }
    }
  }
  for (let i = 0; i <= S; i += CELL) {
    const avenue = i % (CELL * 6) === 0;
    g.strokeStyle = avenue ? p.avenue : p.street;
    g.lineWidth = avenue ? 3 : 1;
    g.beginPath(); g.moveTo(i, 0); g.lineTo(i, S); g.stroke();
    g.beginPath(); g.moveTo(0, i); g.lineTo(S, i); g.stroke();
  }

  // The river, and its bridges.
  const river = (width, style) => {
    g.strokeStyle = style;
    g.lineWidth = width * p.riverScale;
    g.beginPath();
    g.moveTo(-40 * K, 380 * K);
    g.bezierCurveTo(260 * K, 300 * K, 420 * K, 520 * K, 640 * K, 470 * K);
    g.bezierCurveTo(820 * K, 430 * K, 900 * K, 560 * K, 1080 * K, 520 * K);
    g.stroke();
  };
  river(96, p.river[0]);
  river(80, p.river[1]);
  river(54, p.river[2]);
  g.lineWidth = 1;
  for (let i = 0; i < 260; i++) {
    g.strokeStyle = p.glint(0.1 + rand() * 0.25);
    const x = rand() * S;
    const y = (360 + Math.sin(x / (150 * K)) * 90) * K + rand() * 70 * K;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + 20 + rand() * 40, y + 2); g.stroke();
  }
  for (const x of [290, 610, 850]) {
    g.strokeStyle = p.bridge;
    g.lineWidth = 4;
    g.beginPath(); g.moveTo(x * K, 300 * K); g.lineTo((x + 30) * K, 630 * K); g.stroke();
    g.fillStyle = p.bridgeLights;
    for (let t = 0; t < 1; t += 0.012) g.fillRect((x + 30 * t) * K - 1.5, (300 + 330 * t) * K - 1.5, 3, 3);
  }
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

// Opaque over the whole view, fading only far beyond it.
function fadeTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d");
  const gradient = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gradient.addColorStop(0, "#fff");
  gradient.addColorStop(0.72, "#fff");
  gradient.addColorStop(1, "#000");
  g.fillStyle = gradient;
  g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

// The facade of a glass tower: blue panes by day, and a map of the lit windows for the night.
function glassTextures() {
  const W = 64, H = 128;
  const rand = mulberry32(5);
  const make = () => {
    const c = document.createElement("canvas");
    c.width = W;
    c.height = H;
    return [c, c.getContext("2d")];
  };
  const [dayCanvas, d] = make();
  const sky = d.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, "#6f9ad8");
  sky.addColorStop(1, "#3d68a8");
  d.fillStyle = sky;
  d.fillRect(0, 0, W, H);
  const [litCanvas, l] = make();
  l.fillStyle = "#000";
  l.fillRect(0, 0, W, H);
  for (let y = 3; y < H; y += 10) {
    for (let x = 3; x < W; x += 10) {
      d.fillStyle = `rgba(${170 + rand() * 40}, ${205 + rand() * 30}, 255, ${0.4 + rand() * 0.3})`;
      d.fillRect(x, y, 7, 7);
      if (rand() < 0.45) {
        l.fillStyle = rand() < 0.75 ? "#ffd9a0" : "#bfe3ff";
        l.fillRect(x, y, 7, 7);
      }
    }
  }
  d.strokeStyle = "rgba(255,255,255,.18)";
  d.lineWidth = 1;
  for (let x = 0; x <= W; x += 10) { d.beginPath(); d.moveTo(x, 0); d.lineTo(x, H); d.stroke(); }
  const wrap = (canvas) => {
    const t = new THREE.CanvasTexture(canvas);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  };
  return { glass: wrap(dayCanvas), lit: wrap(litCanvas) };
}

// A floating holographic sign over the city.
function hologramTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 300;
  const g = c.getContext("2d");
  g.fillStyle = "rgba(20, 70, 120, 0.5)"; // dark enough to read against a daylight map
  g.beginPath();
  g.roundRect(14, 14, 484, 272, 34);
  g.fill();
  g.strokeStyle = "#8be9ff";
  g.lineWidth = 6;
  g.shadowColor = "#4fd8ff";
  g.shadowBlur = 24;
  g.stroke();
  g.fillStyle = "#e6fbff";
  g.font = `bold 150px ${FONT_STACK}`;
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillText("서울", 256, 140);
  g.shadowBlur = 10;
  g.font = `600 34px ${FONT_STACK}`;
  g.fillText("S E O U L", 256, 236);
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const smooth = (x) => x * x * (3 - 2 * x);
const HOLOGRAM_Y = 3;
const TOWER_NIGHT_GLOW = 0.45; // the lit windows of the towers, kept below the office's own lights

export function createOutside(scene) {
  let clock = 0;
  const rand = mulberry32(2025);
  const fade = fadeTexture();

  // Night underneath, day on top: the day map fades in as the sun rises.
  const plane = (palette, order) => {
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(230, 230),
      new THREE.MeshBasicMaterial({ map: groundTexture(palette), alphaMap: fade, transparent: true, toneMapped: false, depthWrite: false }),
    );
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.set(10, -14, 7);
    mesh.renderOrder = order;
    scene.add(mesh);
    return mesh;
  };
  const night = plane(PALETTES.night, -2);
  const day = plane(PALETTES.day, -1);
  day.material.opacity = 0;
  day.visible = false;

  // Namsan: a green mound with trees, and the tower on top with a beacon that blinks.
  const NAMSAN = { x: 11, z: -8 };
  const mound = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 10, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0x6fb26a, roughness: 1 }));
  mound.scale.set(3.4, 1.8, 3.4);
  mound.position.set(NAMSAN.x, -0.5, NAMSAN.z);
  scene.add(mound);
  const leafMaterials = [];
  for (let i = 0; i < 18; i++) {
    const angle = rand() * Math.PI * 2;
    const r = 0.6 + rand() * 2.3;
    const top = 1.8 * Math.sqrt(Math.max(0, 1 - (r / 3.4) ** 2)) - 0.5;
    const material = new THREE.MeshStandardMaterial({ color: 0x3f9a4f, roughness: 0.9, flatShading: true });
    leafMaterials.push(material);
    const tree = new THREE.Mesh(new THREE.ConeGeometry(0.32 + rand() * 0.12, 0.95, 7), material);
    tree.position.set(NAMSAN.x + Math.cos(angle) * r, top + 0.4, NAMSAN.z + Math.sin(angle) * r);
    scene.add(tree);
  }
  const glowMat = new THREE.MeshStandardMaterial({ color: 0xe6ebf2, emissive: 0xffe9b0, emissiveIntensity: 0.9 });
  const tower = new THREE.Group();
  const beacons = [];
  const part = (geometry, y, material = glowMat) => {
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.y = y;
    tower.add(mesh);
    return mesh;
  };
  part(new THREE.CylinderGeometry(0.3, 0.6, 16, 12), 8);
  part(new THREE.CylinderGeometry(1.5, 1.1, 1.4, 16), 16.5);
  part(new THREE.CylinderGeometry(0.04, 0.1, 9, 8), 22);
  beacons.push(part(new THREE.SphereGeometry(0.22, 8, 8), 26.6, new THREE.MeshBasicMaterial({ color: 0xff3b3b })));
  tower.position.set(NAMSAN.x, 1.1, NAMSAN.z);
  tower.scale.setScalar(0.38);
  scene.add(tower);

  // Glass towers on the flanks and behind: bright panes by day, lit windows by night (fewer of them then).
  const { glass, lit } = glassTextures();
  const towers = [];
  const free = (x, z) => !(x > -5 && x < 25 && z > -5 && z < 19) && Math.hypot(x - NAMSAN.x, z - NAMSAN.z) > 6.5;
  const addTower = (x, z, keepAtNight) => {
    const w = 2.4 + rand() * 1.2, d = 2.4 + rand() * 1.2, h = 4.5 + rand() * rand() * 11 + rand() * 3;
    const repeat = (tex) => {
      const t = tex.clone();
      t.needsUpdate = true;
      t.repeat.set(Math.max(2, Math.round(w)), Math.max(2, Math.round(h / 1.8)));
      return t;
    };
    const material = new THREE.MeshStandardMaterial({ map: repeat(glass), emissiveMap: repeat(lit), emissive: 0xffffff, emissiveIntensity: 0, roughness: 0.4, metalness: 0.1, transparent: !keepAtNight });
    const group = new THREE.Group();
    group.position.set(x, 0, z);
    const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
    body.position.y = h / 2 - 0.3;
    const roofMaterial = new THREE.MeshStandardMaterial({ color: 0xf1f4f9, roughness: 0.7, transparent: !keepAtNight });
    const roof = new THREE.Mesh(new THREE.BoxGeometry(w + 0.3, 0.26, d + 0.3), roofMaterial);
    roof.position.y = h - 0.3 + 0.13;
    const plant = new THREE.Mesh(new THREE.BoxGeometry(w * 0.35, 0.5, d * 0.35), roofMaterial);
    plant.position.y = h - 0.3 + 0.5;
    group.add(body, roof, plant);
    scene.add(group);
    towers.push({ group, material, roofMaterial, keepAtNight });
  };
  const cluster = (x0, x1, z0, z1, cell) => {
    for (let x = x0; x < x1; x += cell) {
      for (let z = z0; z < z1; z += cell) {
        const px = x + rand() * (cell - 3.6);
        const pz = z + rand() * (cell - 3.6);
        if (free(px, pz) && rand() < 0.85) addTower(px, pz, rand() < 0.5);
      }
    }
  };
  // Never in front of the office: only on the left, behind, and on the right-hand back.
  cluster(-30, -7, -10, 9, 5.4);
  cluster(-14, 8, -26, -10, 5.4);
  cluster(14, 34, -22, 3, 5.4);

  // The holographic sign, floating a little.
  const hologram = new THREE.Sprite(new THREE.SpriteMaterial({ map: hologramTexture(), transparent: true, depthTest: false, toneMapped: false }));
  hologram.scale.set(4.4, 2.57, 1); // smaller and dimmer than the floor's own signs: a backdrop, not an announcement
  hologram.position.set(-4, HOLOGRAM_Y, -5);
  hologram.renderOrder = 8;
  scene.add(hologram);

  let themeGround = THEMES.warm.ground;
  const tint = new THREE.Color();
  const lerpColor = (target, a, b, t) => target.setHex(a).lerp(tint.setHex(b), t);
  function setTheme(name) {
    const t = THEMES[name];
    if (t) themeGround = t.ground;
  }

  // d: 0 at night, 1 in full daylight. tw: how close the sun is to the horizon. morning: before noon.
  // The map hides the sky, so the colors of dawn and dusk are carried by the map itself.
  function setDaylight(d, tw = 0, morning = false) {
    const glowColor = morning ? 0xffa9b8 : 0xffb070;
    day.material.opacity = d;
    day.visible = d > 0.01;
    day.material.color.setScalar(1).lerp(tint.setHex(glowColor), tw * 0.5);
    night.material.color.setHex(themeGround).lerp(tint.setHex(morning ? 0xc79ab8 : 0xb98f9a), tw * 0.6);
    glowMat.emissiveIntensity = 0.9 * (1 - 0.75 * d);
    lerpColor(mound.material.color, 0x1f4a3a, 0x6fb26a, d);
    for (const m of leafMaterials) lerpColor(m.color, 0x143d2a, 0x3f9a4f, d);
    const visibility = smooth(Math.min(1, Math.max(0, d)));
    for (const t of towers) {
      // The towers kept at night stay; the others fade out with the sun.
      const opacity = t.keepAtNight ? 1 : visibility;
      t.group.visible = opacity > 0.02;
      if (!t.keepAtNight) {
        t.material.opacity = opacity;
        t.roofMaterial.opacity = opacity;
      }
      t.material.emissiveIntensity = TOWER_NIGHT_GLOW * (1 - d);
      t.material.color.setHex(0x7d8fb8).lerp(tint.setHex(0xffffff), d);
      t.roofMaterial.color.setHex(0x5a6788).lerp(tint.setHex(0xf1f4f9), d);
    }
    hologram.material.opacity = 0.45 + 0.2 * (1 - d);
  }

  function update(dt) {
    clock += dt;
    beacons.forEach((beacon, i) => { beacon.visible = Math.sin(clock * 2.4 + i) > -0.2; });
    hologram.position.y = HOLOGRAM_Y + Math.sin(clock * 1.1) * 0.22;
  }

  setTheme("warm");
  return { update, setTheme, setDaylight };
}
