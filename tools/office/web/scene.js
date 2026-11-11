// The static floor: building, furniture, signs, night city. No workflow knowledge here.
import * as THREE from "three";
import { FLOOR, ROOMS, HUB, TEAM_COLORS, SIGN_LABELS, SIGN_FALLBACK } from "./layout.js";
import { daylightAt, mix, skyGradient, sunArc, twilightAt } from "./daylight.js";
import { createOutside } from "./outside.js";
import { hangulAvailable, mulberry32, signTexture } from "./textures.js";

const THEMES = {
  warm: { sky: ["#0d1738", "#2b3068"], floor: 0xffffff, wall: { product: 0xd98a4a, design: 0x6c4cc0, build: 0x3f9d9a, common: 0xa89bd8 }, rug: 0x6d5bd0, lamp: 0xffb86b, ambient: 0x5a52a0 },
  cool: { sky: ["#091c33", "#1f4a66"], floor: 0xa9c3e6, wall: { product: 0x3f9d8a, design: 0x6c4cc0, build: 0x4aa3c0, common: 0x9ec7e0 }, rug: 0x2f7fa8, lamp: 0x8ecbff, ambient: 0x4f7fb0 },
};
const WALL_COLOR = 0x3a3358;

function box(w, h, d, color, [x, y, z], material = {}) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshStandardMaterial({ color, roughness: 0.8, ...material }),
  );
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function glass(w, h, d, [x, y, z]) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshStandardMaterial({ color: 0x9fb8ff, transparent: true, opacity: 0.08, roughness: 0.1, metalness: 0.3, depthWrite: false }),
  );
  mesh.position.set(x, y, z);
  return mesh;
}

function plankTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d");
  const rand = mulberry32(7);
  g.fillStyle = "#c18a55";
  g.fillRect(0, 0, 256, 256);
  for (let row = 0; row < 8; row++) {
    for (let x = (row % 2) * 64 - 128; x < 256; x += 128) {
      const shade = 150 + Math.floor(rand() * 36);
      g.fillStyle = `rgb(${shade + 40}, ${shade - 8}, ${shade - 62})`;
      g.fillRect(x, row * 32, 128, 32);
      g.strokeStyle = "rgba(70, 40, 18, 0.5)";
      g.lineWidth = 2;
      g.strokeRect(x, row * 32, 128, 32);
    }
  }
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(5, 3.5);
  return texture;
}

function glowTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d");
  const gradient = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gradient.addColorStop(0, "rgba(255,255,255,1)");
  gradient.addColorStop(0.35, "rgba(255,255,255,0.35)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gradient;
  g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}
const GLOW = glowTexture();

// Lights that the daylight turns down: halos, lamp shades, neon signs.
const GLOWS = [];
const SHADES = [];
const SIGN_MATERIALS = [];

function glow(color, size, opacity, [x, y, z]) {
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
  sprite.scale.set(size, size, 1);
  sprite.position.set(x, y, z);
  GLOWS.push({ sprite, base: opacity });
  return sprite;
}

function lamp([x, y, z], color = 0xffd9a0) {
  const g = new THREE.Group();
  g.add(box(0.2, 0.04, 0.2, 0x2a2e44, [x, y + 0.02, z]));
  g.add(box(0.04, 0.34, 0.04, 0x2a2e44, [x, y + 0.2, z]));
  const shade = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.18, 12), new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 1.4 }));
  shade.position.set(x, y + 0.42, z);
  SHADES.push({ material: shade.material, base: 1.4 });
  g.add(shade, glow(color, 1.5, 0.55, [x, y + 0.4, z]));
  return g;
}

function bookshelf([x, z], facing = "z", rand = mulberry32(x * 13 + z)) {
  const g = new THREE.Group();
  const w = 1.2, h = 2.0, d = 0.42;
  const wood = 0xb98a58;
  const along = (a, b, c) => (facing === "z" ? [a, b, c] : [c, b, a]);
  const dims = (a, b, c) => (facing === "z" ? [a, b, c] : [c, b, a]);
  g.add(box(...dims(w, h, 0.05), 0x8a6238, along(0, h / 2, -d / 2 + 0.03)));
  for (const dx of [-w / 2, w / 2]) g.add(box(...dims(0.05, h, d), wood, along(dx, h / 2, 0)));
  for (let row = 0; row <= 4; row++) g.add(box(...dims(w, 0.05, d), wood, along(0, 0.05 + row * 0.47, 0)));
  const palette = [0xe8505b, 0x3b82f6, 0xf5a623, 0x22c55e, 0x8b5cf6, 0xf1f5f9, 0x14b8a6];
  for (let row = 0; row < 4; row++) {
    let at = -w / 2 + 0.08;
    while (at < w / 2 - 0.12) {
      const bw = 0.07 + rand() * 0.06, bh = 0.26 + rand() * 0.14;
      g.add(box(...dims(bw, bh, d - 0.12), palette[Math.floor(rand() * palette.length)], along(at + bw / 2, 0.08 + row * 0.47 + bh / 2 + 0.02, 0.02)));
      at += bw + 0.01;
    }
  }
  g.position.set(x, 0, z);
  return g;
}

function station(seat) {
  const group = new THREE.Group();
  group.position.set(seat.x, 0, seat.deskZ);
  const wood = 0xc79a62;
  group.add(box(1.9, 0.08, 0.85, wood, [0, 0.78, 0]));
  group.add(box(0.06, 0.74, 0.8, 0x8a6238, [-0.9, 0.37, 0]));
  group.add(box(0.5, 0.66, 0.78, 0xb98a58, [0.62, 0.37, 0]));
  group.add(box(0.46, 0.14, 0.02, 0x8a6238, [0.62, 0.55, 0.4]));
  group.add(box(0.46, 0.14, 0.02, 0x8a6238, [0.62, 0.3, 0.4]));
  const screenMaterial = new THREE.MeshStandardMaterial({ color: 0x0a1a2a, emissive: new THREE.Color(TEAM_COLORS[seat.team]), emissiveIntensity: 0.12 });
  let screen;
  for (const [dx, turn] of [[-0.42, 0.18], [0.24, -0.18]]) {
    const monitor = new THREE.Group();
    monitor.position.set(dx, 0, -0.18);
    monitor.rotation.y = turn;
    monitor.add(box(0.1, 0.26, 0.08, 0x222633, [0, 0.95, 0]));
    monitor.add(box(0.66, 0.46, 0.05, 0x151826, [0, 1.3, 0]));
    const pane = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.4), screenMaterial);
    pane.position.set(0, 1.3, 0.03);
    monitor.add(pane);
    group.add(monitor);
    screen ||= pane;
  }
  screen.material = screenMaterial;
  group.add(box(0.5, 0.03, 0.18, 0x2a2e44, [-0.2, 0.84, 0.22]));
  group.add(box(0.1, 0.1, 0.1, 0xf1f5f9, [0.05, 0.87, 0.2]));
  group.add(lamp([-0.8, 0.82, -0.2]));
  const chair = new THREE.Group();
  chair.position.set(seat.x, 0, seat.z + 0.15);
  const fabric = 0x2b2f4a;
  chair.add(box(0.62, 0.1, 0.6, fabric, [0, 0.5, 0]));
  chair.add(box(0.6, 0.74, 0.1, fabric, [0, 0.92, 0.3]));
  for (const dx of [-0.34, 0.34]) chair.add(box(0.06, 0.05, 0.4, 0x1a1c2c, [dx, 0.7, 0.05]));
  chair.add(box(0.07, 0.4, 0.07, 0x9aa3b8, [0, 0.27, 0]));
  for (let i = 0; i < 5; i++) {
    const arm = box(0.34, 0.04, 0.06, 0x1a1c2c, [0, 0.07, 0]);
    arm.rotation.y = (i * Math.PI * 2) / 5;
    arm.translateX(0.17);
    chair.add(arm);
  }
  return { group, chair, screen };
}

function plant(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  g.add(box(0.5, 0.4, 0.5, 0xb45f3c, [0, 0.2, 0]));
  const leaves = new THREE.Mesh(new THREE.IcosahedronGeometry(0.45, 0), new THREE.MeshStandardMaterial({ color: 0x2f9e5a, roughness: 0.8, flatShading: true }));
  leaves.position.y = 0.85;
  leaves.castShadow = true;
  g.add(leaves);
  return g;
}

export function createScene(canvas, layout) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;

  const scene = new THREE.Scene();
  const center = new THREE.Vector3(FLOOR.w / 2, 1.6, FLOOR.d / 2);
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -200, 400);
  camera.position.set(center.x + 24, 24, center.z + 24);
  camera.lookAt(center);
  let zoom = 1;

  const ambient = new THREE.AmbientLight(THEMES.warm.ambient, 0.95);
  const moon = new THREE.DirectionalLight(0xa9b8ff, 0.8);
  moon.position.set(center.x + 14, 26, center.z + 18);
  moon.target.position.copy(center);
  moon.castShadow = true;
  moon.shadow.mapSize.set(2048, 2048);
  Object.assign(moon.shadow.camera, { left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 90 });
  const hemi = new THREE.HemisphereLight(0xb8c4ff, 0xffc890, 0.55);
  scene.add(ambient, hemi, moon, moon.target);

  const floorMat = new THREE.MeshStandardMaterial({ color: THEMES.warm.floor, map: plankTexture(), roughness: 0.8 });
  const slabMat = new THREE.MeshStandardMaterial({ color: 0xdfe7f5, roughness: 0.6 });
  const floor = new THREE.Mesh(new THREE.BoxGeometry(FLOOR.w, 0.55, FLOOR.d), [slabMat, slabMat, floorMat, slabMat, slabMat, slabMat]);
  floor.position.set(FLOOR.w / 2, -0.275, FLOOR.d / 2);
  floor.receiveShadow = true;
  scene.add(floor);

  const rugMat = new THREE.MeshStandardMaterial({ color: THEMES.warm.rug, roughness: 1 });
  const rug = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 5.2), rugMat);
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(HUB.x, 0.02, HUB.z);
  rug.receiveShadow = true;
  scene.add(rug);

  const lamps = [];
  const useHangul = hangulAvailable();
  for (const [team, room] of Object.entries(ROOMS)) {
    if (team !== "common") {
      const tint = new THREE.Mesh(new THREE.PlaneGeometry(room.w, room.d), new THREE.MeshBasicMaterial({ color: TEAM_COLORS[team], transparent: true, opacity: 0.14 }));
      tint.rotation.x = -Math.PI / 2;
      tint.position.set(room.x + room.w / 2, 0.015, room.z + room.d / 2);
      scene.add(tint);
    }
    const lamp = new THREE.PointLight(THEMES.warm.lamp, 30, 13, 1.3);
    lamp.position.set(room.x + room.w / 2, 2.7, room.z + room.d / 2 + 1);
    scene.add(lamp);
    lamps.push(lamp);

    const label = useHangul ? SIGN_LABELS[team] : SIGN_FALLBACK[team];
    const sign = new THREE.Mesh(
      new THREE.PlaneGeometry(3.6, 1.12),
      new THREE.MeshBasicMaterial({ map: signTexture(label, TEAM_COLORS[team]), transparent: true, toneMapped: false }),
    );
    sign.position.set(room.x + room.w / 2, 3.15, room.z + 0.12);
    SIGN_MATERIALS.push(sign.material);
    scene.add(sign, glow(new THREE.Color(TEAM_COLORS[team]), 3.6, 0.2, [sign.position.x, sign.position.y, sign.position.z + 0.2]));
    if (room.z > 0) {
      for (const dx of [-1.7, 1.7]) scene.add(box(0.06, 2.6, 0.06, 0x20243a, [sign.position.x + dx, 1.3, room.z + 0.12]));
    }
  }

  // Back walls (north z = 0, west x = 0): thick, colored per room, with window openings onto the city.
  const WALL_H = 3.0;
  const WALL_T = 0.45;
  const wallMeshes = { product: [], design: [], build: [], common: [] }; // recolored by the theme
  const frameColor = 0xf4f6fb;
  function wallRun(axis, from, to, team, windows) {
    const color = THEMES.warm.wall[team];
    const place = (a, b, y0, y1, c) => {
      const len = b - a;
      const h = y1 - y0;
      if (len <= 0 || h <= 0) return;
      const mid = (a + b) / 2;
      const piece = axis === "x" ? box(len, h, WALL_T, c, [mid, y0 + h / 2, -WALL_T / 2]) : box(WALL_T, h, len, c, [-WALL_T / 2, y0 + h / 2, mid]);
      wallMeshes[team].push(piece);
      scene.add(piece);
    };
    let cursor = from;
    for (const [a, b] of windows) {
      place(cursor, a, 0, WALL_H, color);
      place(a, b, 0, 0.95, color);
      place(a, b, 2.35, WALL_H, color);
      const pane = axis === "x" ? glass(b - a, 1.4, 0.08, [(a + b) / 2, 1.65, -WALL_T / 2]) : glass(0.08, 1.4, b - a, [-WALL_T / 2, 1.65, (a + b) / 2]);
      scene.add(pane);
      for (const edge of [a, b]) {
        scene.add(axis === "x" ? box(0.1, 1.4, WALL_T + 0.04, frameColor, [edge, 1.65, -WALL_T / 2]) : box(WALL_T + 0.04, 1.4, 0.1, frameColor, [-WALL_T / 2, 1.65, edge]));
      }
      scene.add(axis === "x" ? box(b - a, 0.08, WALL_T + 0.04, frameColor, [(a + b) / 2, 1.65, -WALL_T / 2]) : box(WALL_T + 0.04, 0.08, b - a, frameColor, [-WALL_T / 2, 1.65, (a + b) / 2]));
      cursor = b;
    }
    place(cursor, to, 0, WALL_H, color);
  }
  wallRun("x", 0, 8, "product", [[1.4, 6.6]]);
  wallRun("x", 8, 12, "common", []);
  wallRun("x", 12, 20, "design", [[13.4, 18.6]]);
  wallRun("z", 0, 6, "product", [[1.2, 4.8]]);
  wallRun("z", 6, 8, "common", []);
  wallRun("z", 8, 14, "build", [[9.2, 12.8]]);
  scene.add(box(FLOOR.w + WALL_T, 0.16, WALL_T + 0.12, frameColor, [(FLOOR.w - WALL_T) / 2 + WALL_T / 2 - WALL_T / 2, WALL_H + 0.08, -WALL_T / 2]));
  scene.add(box(WALL_T + 0.12, 0.16, FLOOR.d, frameColor, [-WALL_T / 2, WALL_H + 0.08, FLOOR.d / 2]));

  // Glass partitions around the rooms, with a doorway where each team's door is.
  const part = (x1, z1, x2, z2, gap) => {
    const horizontal = z1 === z2;
    const lo = horizontal ? Math.min(x1, x2) : Math.min(z1, z2);
    const hi = horizontal ? Math.max(x1, x2) : Math.max(z1, z2);
    const spans = gap ? [[lo, gap[0]], [gap[1], hi]] : [[lo, hi]];
    const metal = 0xdfe6f2;
    for (const [a, b] of spans) {
      const len = b - a;
      if (len <= 0) continue;
      const mid = (a + b) / 2;
      if (horizontal) {
        scene.add(glass(len, 1.8, 0.06, [mid, 0.95, z1]), box(len, 0.07, 0.1, metal, [mid, 1.88, z1]), box(len, 0.1, 0.1, metal, [mid, 0.05, z1]));
        scene.add(box(0.08, 1.9, 0.08, metal, [a, 0.95, z1]), box(0.08, 1.9, 0.08, metal, [b, 0.95, z1]));
      } else {
        scene.add(glass(0.06, 1.8, len, [x1, 0.95, mid]), box(0.1, 0.07, len, metal, [x1, 1.88, mid]), box(0.1, 0.1, len, metal, [x1, 0.05, mid]));
        scene.add(box(0.08, 1.9, 0.08, metal, [x1, 0.95, a]), box(0.08, 1.9, 0.08, metal, [x1, 0.95, b]));
      }
    }
  };
  part(0, 6, 8, 6, [5, 7]);
  part(8, 0, 8, 6);
  part(12, 6, 20, 6, [13, 15]);
  part(12, 0, 12, 6);
  part(0, 8, 8, 8, [5, 7]);
  part(8, 8, 8, 14);
  part(12, 8, 20, 8, [13, 15]);
  part(12, 8, 12, 14);

  // Stations: one desk and chair per role.
  const stations = new Map();
  for (const [role, seat] of layout.seats) {
    const st = station(seat);
    scene.add(st.group, st.chair);
    stations.set(role, { screen: st.screen, chair: st.chair });
  }

  // Furniture that makes it an office.
  const vending = box(0.95, 2.1, 0.85, 0xe6ebf5, [11.2, 1.05, 9.3]);
  const front = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 1.5), new THREE.MeshStandardMaterial({ color: 0x20324a, emissive: 0x4fb4ff, emissiveIntensity: 0.6 }));
  front.position.set(11.2, 1.2, 9.73);
  scene.add(vending, front);
  const snacks = [0xe8505b, 0xf5a623, 0x22c55e, 0x3b82f6, 0xf1f5f9, 0x8b5cf6];
  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 4; col++) scene.add(box(0.12, 0.2, 0.05, snacks[(row * 3 + col) % snacks.length], [10.92 + col * 0.19, 0.78 + row * 0.33, 9.76], { emissive: 0x111111 }));
  }
  scene.add(glow(0x4fb4ff, 2.6, 0.35, [11.2, 1.2, 9.9]));
  scene.add(bookshelf([7.2, 0.28]), bookshelf([19.2, 0.28]), bookshelf([0.28, 11], "x"), bookshelf([0.28, 3.4], "x"));
  scene.add(box(1.0, 1.0, 0.5, 0xeef2fa, [5.2, 0.5, 11.5]), box(1.0, 1.0, 0.5, 0xeef2fa, [16.4, 0.5, 0.35]));
  scene.add(box(2.4, 0.55, 0.9, 0x4a3f82, [10, 0.28, 8.4]), box(2.4, 0.5, 0.2, 0x4a3f82, [10, 0.7, 8.8]));
  for (const [x, z] of [[0.8, 0.8], [11.4, 4.6], [8.6, 4.6], [0.8, 13.2], [19.2, 13.2], [19.2, 0.8], [7.4, 13.2], [12.6, 13.2]]) scene.add(plant(x, z));
  for (const [x, w] of [[2.4, 1.2], [4.6, 0.9], [14.4, 1.2], [17.2, 0.9]]) {
    scene.add(box(w, 0.8, 0.06, 0xf4f6fb, [x, 2.55, 0.06]), box(w - 0.16, 0.64, 0.02, [0xe8505b, 0x3b82f6, 0xf5a623, 0x22c55e][Math.round(x) % 4], [x, 2.55, 0.1], { emissive: 0x111111 }));
  }

  const outside = createOutside(scene);

  function resize() {
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    // Fit the whole floor in the width left to the canvas, even when the panel narrows it.
    const half = Math.max(13.2, 13.4 / (w / h)) / zoom;
    camera.left = -half * (w / h);
    camera.right = half * (w / h);
    camera.top = half;
    camera.bottom = -half;
    camera.updateProjectionMatrix();
  }
  window.addEventListener("resize", resize);
  canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    zoom = Math.min(2, Math.max(0.6, zoom * (event.deltaY < 0 ? 1.08 : 1 / 1.08)));
    resize();
  }, { passive: false });
  resize();

  const css = (n) => `#${n.toString(16).padStart(6, "0")}`;
  let theme = "warm";
  let hour = 22;

  // The light of the hour: sky, sun, ambient light, and how much of the office's own lighting is needed.
  function setDaylight(h) {
    hour = h;
    const d = daylightAt(h);
    const tw = twilightAt(h);
    const t = THEMES[theme];
    const [top, bottom] = skyGradient(h, t.sky);
    document.body.style.background = `linear-gradient(${top}, ${bottom})`;
    ambient.color.set(mix(css(t.ambient), "#dfe8ff", d));
    ambient.intensity = 0.95 + 0.15 * d;
    hemi.color.set(mix("#b8c4ff", "#bfe0ff", d));
    hemi.intensity = 0.55 + 0.4 * d;
    moon.color.set(mix(mix("#a9b8ff", "#fff1d6", d), "#ffb070", tw * 0.7));
    moon.intensity = 0.8 + 0.9 * d * (1 - 0.3 * tw);
    const sun = sunArc(h);
    moon.position.set(
      center.x + 14 + (sun.x - (center.x + 14)) * d,
      26 + (sun.y - 26) * d,
      center.z + 18 + (sun.z - (center.z + 18)) * d,
    );
    for (const lamp of lamps) lamp.intensity = 30 * (1 - 0.75 * d);
    for (const g of GLOWS) g.sprite.material.opacity = g.base * (1 - 0.7 * d);
    for (const s of SHADES) s.material.emissiveIntensity = s.base * (1 - 0.8 * d);
    for (const m of SIGN_MATERIALS) m.color.setScalar(1 - 0.4 * d);
    renderer.toneMappingExposure = 0.95 + 0.1 * d;
    outside.setDaylight(d, tw, h < 12);
  }

  function setTheme(name) {
    const t = THEMES[name];
    if (!t) return;
    theme = name;
    floorMat.color.setHex(t.floor);
    rugMat.color.setHex(t.rug);
    for (const [team, pieces] of Object.entries(wallMeshes)) for (const piece of pieces) piece.material.color.setHex(t.wall[team]);
    for (const lamp of lamps) lamp.color.setHex(t.lamp);
    outside.setTheme(name);
    setDaylight(hour);
  }
  setTheme("warm");

  return {
    scene, camera, renderer, stations, setTheme, setDaylight,
    toggleTheme: () => setTheme(theme === "warm" ? "cool" : "warm"),
    render: (dt = 0) => {
      outside.update(dt);
      renderer.render(scene, camera);
    },
  };
}
