// One low-poly agent per role. Draws what the snapshot says; decides nothing about the workflow.
import * as THREE from "three";
import { TEAM_COLORS } from "./layout.js";
import { STATE_COLORS, STATE_GLYPHS, roleTitle } from "./roles.js";

const SPEED = 3; // world units per second while walking a handoff: slow enough to follow with the eye
const TRAIL_STEP = 0.45; // distance between the dots that show where the handoff is going
const DIM_SPEED = 5; // how fast a role outside the run fades to grey, and back
const DIM_TARGET = 0.8; // how much of its color is lost, 1 being a flat grey
const HANDOVER_PAUSE = 0.6;
const DEFER_MAX = 9; // the receiver starts working when the walker arrives, or after this
const CHECK_SECONDS = 3;
const IDLE_CYCLE = 18; // seconds of one resting routine: look around, stretch, sip, daydream
const SKIN = 0xf1c7a0;

function textSprite(text, { fg, bg, size, w, h, scale }) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  const g = c.getContext("2d");
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  const draw = (label) => {
    g.clearRect(0, 0, w, h);
    g.fillStyle = bg;
    g.beginPath();
    g.roundRect(2, 2, w - 4, h - 4, h / 2.4);
    g.fill();
    g.fillStyle = fg;
    // A long label ("Product Owner → Architect") shrinks to fit the pill instead of being cut.
    let fontSize = size;
    g.font = `bold ${fontSize}px system-ui, sans-serif`;
    while (g.measureText(label).width > w - h * 0.6 && fontSize > 18) {
      fontSize -= 2;
      g.font = `bold ${fontSize}px system-ui, sans-serif`;
    }
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.fillText(label, w / 2, h / 2 + 2);
    texture.needsUpdate = true;
  };
  draw(text);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false, toneMapped: false }));
  sprite.scale.set(scale[0], scale[1], 1);
  sprite.renderOrder = 10;
  sprite.visible = false;
  sprite.userData.set = (label) => {
    if (sprite.userData.text !== label) {
      sprite.userData.text = label;
      draw(label);
    }
  };
  return sprite;
}

// The state above each head is a glyph on a colored disc, so it never rests on color alone.
const statusSprite = (text, bg) => textSprite(text, { fg: "#fff", bg, size: 64, w: 96, h: 96, scale: [0.55, 0.55] });

// A resting agent should look alive: it glances around, stretches, sips a drink, then daydreams.
// Each is a smooth bump over its own slice of the cycle; the phase of the agent offsets the cycle
// so that the whole floor never moves in step. Returns the pose offsets, all in radians.
function restingPose(time, phase) {
  const c = (time + phase * 3) % IDLE_CYCLE;
  const bump = (from, to) => (c >= from && c < to ? Math.sin(((c - from) / (to - from)) * Math.PI) : 0);
  const look = c < 6 ? Math.sin((c / 6) * Math.PI * 2) * 0.6 : 0;
  const stretch = bump(8, 11);
  const sip = bump(12, 15);
  const daydream = bump(15, 18);
  return {
    yaw: look + daydream * 0.35,
    pitch: -0.25 * stretch - 0.2 * sip + 0.12 * daydream,
    lean: -0.14 * stretch,
    armLeft: -2.5 * stretch,
    armRight: -2.5 * stretch - 1.45 * sip,
  };
}

function makeAgent(role, seat) {
  // Every material of the body, with its own color and the grey it fades to outside the run.
  const materials = [];
  const standard = (color) => {
    const material = new THREE.MeshStandardMaterial({ color, roughness: 0.8 });
    const grey = material.color.getHSL({}).l * 0.8;
    materials.push({ material, base: material.color.clone(), grey: new THREE.Color(grey, grey, grey) });
    return material;
  };
  const part = (w, h, d, color, y) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), standard(color));
    mesh.position.y = y;
    mesh.castShadow = true;
    return mesh;
  };
  const pivot = (x, y) => {
    const g = new THREE.Group();
    g.position.set(x, y, 0);
    return g;
  };

  const root = new THREE.Group();
  root.position.set(seat.x, 0, seat.z);
  root.rotation.y = seat.rotY;
  const body = new THREE.Group();
  body.position.y = 0.58; // the hip, the same seated and standing
  root.add(body);

  // A few looks per role, picked from the role name so they stay the same between reloads.
  let hash = 0;
  for (const ch of role) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  const pick = (list, shift) => list[(hash >> shift) % list.length];
  const skin = pick([0xf1c7a0, 0xe0ac80, 0xc68642, 0x8d5524, 0xf6d3b5], 0);
  const hair = pick([0x1b1b2a, 0x3b2a1a, 0x6b4a2b, 0x111111, 0x7a4a24], 3);
  const pants = pick([0x222638, 0x2d3350, 0x3a3f55, 0x1f2a44], 6);
  const shirt = TEAM_COLORS[seat.team];

  body.add(part(0.5, 0.6, 0.3, shirt, 0.38));
  body.add(part(0.52, 0.1, 0.32, 0xf4f6fb, 0.08)); // belt line
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 12), standard(skin));
  head.position.y = 0.95;
  head.castShadow = true;
  const hairTop = part(0.4, 0.14, 0.4, hair, 1.1);
  const hairBack = part(0.4, 0.3, 0.1, hair, 0.98);
  hairBack.position.z = -0.15; // the back of the head faces the camera
  // The head turns on the neck, so the hair goes with it.
  const neck = pivot(0, 0.78);
  for (const piece of [head, hairTop, hairBack]) piece.position.y -= 0.78;
  neck.add(head, hairTop, hairBack);
  body.add(neck);

  const arms = [pivot(-0.33, 0.62), pivot(0.33, 0.62)];
  const legs = [pivot(-0.13, 0), pivot(0.13, 0)];
  for (const arm of arms) {
    arm.add(part(0.15, 0.3, 0.15, shirt, -0.15), part(0.12, 0.2, 0.12, skin, -0.4));
    body.add(arm);
  }
  for (const leg of legs) {
    leg.add(part(0.17, 0.55, 0.17, pants, -0.27), part(0.19, 0.08, 0.27, 0xf4f6fb, -0.55));
    leg.children[1].position.z = 0.05;
    body.add(leg);
  }
  body.scale.setScalar(1.12);

  const folder = part(0.32, 0.04, 0.42, 0xf4f4f4, 0.45);
  folder.position.z = 0.42;
  folder.visible = false;
  folder.scale.setScalar(1.5); // big enough to follow across the floor
  body.add(folder);
  // The folder takes the color of the verdict while it walks, so it does not fade with the body.
  materials.splice(materials.findIndex((m) => m.material === folder.material), 1);

  const label = textSprite(roleTitle(role), { fg: "#fff", bg: "rgba(10,12,28,0.9)", size: 56, w: 640, h: 96, scale: [3.2, 0.48] });
  label.userData.text = roleTitle(role);
  label.position.y = 2.3;
  // Small glyphs for the calm states; blocked and escalate have the large pulsing signs below.
  const pips = Object.fromEntries(["working", "done"].map((state) => [state, statusSprite(STATE_GLYPHS[state], STATE_COLORS[state])]));
  for (const pip of Object.values(pips)) {
    pip.position.y = 1.85;
    pip.renderOrder = 9;
  }
  const sprites = { "?": statusSprite(STATE_GLYPHS.blocked, STATE_COLORS.blocked), "!": statusSprite(STATE_GLYPHS.escalate, STATE_COLORS.escalate), check: statusSprite("✓", STATE_COLORS.done) };
  for (const s of Object.values(sprites)) s.position.y = 3.0;
  root.add(label, ...Object.values(pips), ...Object.values(sprites));

  return { role, seat, root, body, neck, arms, legs, folder, label, pips, sprites, materials, dim: 0, mode: "seated", phase: Math.random() * 6 };
}

export function createAgents(scene, layout, stations) {
  const agents = new Map();
  const targets = []; // invisible boxes the pointer can hit, one on the desk and one on the agent
  const hitMaterial = new THREE.MeshBasicMaterial({ visible: false });
  const hit = (w, h, d, x, y, z, role, parent) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), hitMaterial);
    mesh.position.set(x, y, z);
    mesh.userData.role = role;
    parent.add(mesh);
    targets.push(mesh);
  };
  for (const [role, seat] of layout.seats) {
    const agent = makeAgent(role, seat);
    agents.set(role, agent);
    scene.add(agent.root);
    hit(2.0, 2.0, 2.2, seat.x, 1.0, (seat.deskZ + seat.z) / 2 + 0.1, role, scene);
    hit(0.9, 2.0, 0.9, 0, 1.0, 0, role, agent.root);
    agent.ring = new THREE.Mesh(
      new THREE.RingGeometry(0.95, 1.1, 40),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85, toneMapped: false, depthTest: false }),
    );
    agent.ring.rotation.x = -Math.PI / 2;
    agent.ring.position.set(seat.x, 0.04, (seat.deskZ + seat.z) / 2 + 0.1);
    agent.ring.renderOrder = 5;
    agent.ring.visible = false;
    scene.add(agent.ring);
  }
  let hovered = null;
  let selected = null;

  let run = null;
  let slug = null;
  let prevActive;
  let prevStates = null;
  let walk = null;
  const deferred = new Map(); // role -> seconds left before it shows as working
  const checks = new Map(); // role -> seconds left of the green check
  let time = 0;

  const stateOf = (role) => (deferred.has(role) ? "idle" : run?.roles?.[role]?.state ?? "idle");
  // A role the run does not use stays on the floor as furniture: dimmed, so the roles that matter stand out.
  const outside = (role) => Boolean(run?.route?.length) && !run.route.includes(role);

  function sit(agent) {
    agent.root.position.set(agent.seat.x, 0, agent.seat.z);
    agent.root.rotation.y = agent.seat.rotY;
    agent.mode = "seated";
    agent.folder.visible = false;
    agent.label.userData.set(roleTitle(agent.role));
  }

  // The route of a handoff, drawn on the floor as dots in the color of the receiver (red after a NO-GO),
  // so that a handoff missed by the eye still shows where it went.
  function makeTrail(path, color) {
    const trail = new THREE.Group();
    const dot = new THREE.CircleGeometry(0.11, 12);
    const material = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85, depthTest: false, toneMapped: false });
    for (let i = 1; i < path.length; i++) {
      const a = path[i - 1];
      const b = path[i];
      const length = Math.hypot(b.x - a.x, b.z - a.z);
      const count = Math.max(1, Math.round(length / TRAIL_STEP));
      for (let k = 0; k < count; k++) {
        const mesh = new THREE.Mesh(dot, material);
        mesh.rotation.x = -Math.PI / 2;
        mesh.position.set(a.x + ((b.x - a.x) * k) / count, 0.06, a.z + ((b.z - a.z) * k) / count);
        mesh.renderOrder = 4;
        trail.add(mesh);
      }
    }
    scene.add(trail);
    return { trail, material };
  }

  function clearTrail() {
    if (!walk?.trail) return;
    scene.remove(walk.trail.trail);
    walk.trail.material.dispose();
  }

  function cancelWalk() {
    clearTrail();
    if (walk) sit(walk.agent);
    walk = null;
    deferred.clear();
  }

  function startWalk(from, to, red) {
    cancelWalk();
    const agent = agents.get(from);
    if (!agent || !agents.has(to)) return;
    const path = layout.walkPath(from, to);
    agent.folder.material.color.set(red ? 0xef4444 : 0xf4f4f4);
    agent.folder.visible = true;
    agent.mode = "walking";
    agent.label.userData.set(`${roleTitle(from)} → ${roleTitle(to)}`);
    const trail = makeTrail(path, red ? 0xef4444 : TEAM_COLORS[layout.seats.get(to).team]);
    walk = { agent, path, back: [...path].reverse(), idx: 1, phase: "out", pause: 0, to, trail };
    deferred.set(to, DEFER_MAX);
  }

  function apply(next) {
    if (next && next.slug !== slug) {
      cancelWalk();
      prevActive = undefined;
      prevStates = null;
    }
    slug = next ? next.slug : null;
    run = next;
    const active = next?.active_role ?? null;
    if (prevActive !== undefined && prevActive && active && prevActive !== active) {
      const red = prevActive === "reviewer" && next.roles.reviewer?.verdict === "NO-GO";
      startWalk(prevActive, active, red);
    }
    prevActive = active;
    const states = Object.fromEntries(Object.entries(next?.roles ?? {}).map(([r, v]) => [r, v.state]));
    if (prevStates) {
      for (const [role, state] of Object.entries(states)) {
        if (state === "done" && prevStates[role] && prevStates[role] !== "done") checks.set(role, CHECK_SECONDS);
      }
    }
    prevStates = states;
  }

  function stepWalk(dt) {
    const { agent } = walk;
    if (walk.phase === "pause") {
      walk.pause -= dt;
      if (walk.pause <= 0) {
        walk.phase = "back";
        walk.idx = 1;
        agent.folder.visible = false;
      }
      return;
    }
    const path = walk.phase === "out" ? walk.path : walk.back;
    const target = path[walk.idx];
    const dx = target.x - agent.root.position.x;
    const dz = target.z - agent.root.position.z;
    const dist = Math.hypot(dx, dz);
    const step = SPEED * dt;
    if (dist > 1e-6) agent.root.rotation.y = Math.atan2(dx, dz);
    if (step >= dist) {
      agent.root.position.set(target.x, 0, target.z);
      walk.idx += 1;
      if (walk.idx >= path.length) {
        if (walk.phase === "out") {
          walk.phase = "pause";
          walk.pause = HANDOVER_PAUSE;
          deferred.delete(walk.to);
        } else {
          clearTrail();
          sit(agent);
          walk = null;
        }
      }
    } else {
      agent.root.position.x += (dx / dist) * step;
      agent.root.position.z += (dz / dist) * step;
    }
  }

  function update(dt) {
    time += dt;
    if (walk) stepWalk(dt);
    for (const [role, left] of deferred) {
      if (left - dt <= 0) deferred.delete(role);
      else deferred.set(role, left - dt);
    }
    for (const [role, left] of checks) {
      if (left - dt <= 0) checks.delete(role);
      else checks.set(role, left - dt);
    }

    for (const [role, agent] of agents) {
      const state = stateOf(role);
      const working = state === "working";
      const walking = agent.mode === "walking";
      const t = time * 12 + agent.phase;

      if (walking) {
        const swing = Math.sin(time * 9) * 0.6;
        agent.legs[0].rotation.x = swing;
        agent.legs[1].rotation.x = -swing;
        agent.arms[0].rotation.x = -0.9;
        agent.arms[1].rotation.x = -0.9;
        agent.body.rotation.z = 0;
      } else {
        agent.legs[0].rotation.x = agent.legs[1].rotation.x = -Math.PI / 2; // seated: thighs forward
        const typing = working ? Math.sin(t) * 0.18 : 0;
        agent.arms[0].rotation.x = (working ? -1.15 : -0.35) + typing;
        agent.arms[1].rotation.x = (working ? -1.15 : -0.35) - typing;
        agent.body.rotation.z = state === "blocked" || state === "escalate" ? Math.sin(time * 6) * 0.06 : 0;
        // Nothing to do (or done): the resting routine. At work, the head follows the typing.
        const resting = state === "idle" || state === "done";
        const pose = resting ? restingPose(time, agent.phase) : null;
        agent.neck.rotation.y = pose ? pose.yaw : 0;
        agent.neck.rotation.x = pose ? pose.pitch : working ? 0.08 + Math.sin(t * 0.5) * 0.04 : 0;
        agent.body.rotation.x = pose ? pose.lean : 0;
        if (pose) {
          agent.arms[0].rotation.x += pose.armLeft;
          agent.arms[1].rotation.x += pose.armRight;
        }
      }
      if (walking) {
        agent.neck.rotation.set(0, 0, 0);
        agent.body.rotation.x = 0;
      }
      agent.body.position.y = 0.58 + (walking ? Math.abs(Math.sin(time * 9)) * 0.05 : Math.sin(time * 2 + agent.phase) * 0.008);

      const off = outside(role);
      const target = off ? DIM_TARGET : 0;
      if (agent.dim !== target) {
        agent.dim += (target - agent.dim) * Math.min(1, dt * DIM_SPEED);
        if (Math.abs(target - agent.dim) < 0.01) agent.dim = target;
        for (const { material, base, grey } of agent.materials) material.color.copy(base).lerp(grey, agent.dim);
      }

      const marked = role === hovered || role === selected;
      const active = state === "working" || state === "blocked" || state === "escalate";
      const flagged = active || walking || marked;
      agent.label.visible = flagged;
      for (const [key, pip] of Object.entries(agent.pips)) pip.visible = !off && state === key;
      agent.pips.working.scale.setScalar(0.42 + 0.06 * Math.sin(time * 6));
      agent.pips.done.scale.setScalar(0.42);
      agent.sprites["?"].visible = state === "blocked";
      agent.sprites["!"].visible = state === "escalate";
      agent.sprites.check.visible = checks.has(role) && state === "done";
      const pulse = 0.55 + 0.45 * Math.sin(time * 6);
      for (const key of ["?", "!"]) agent.sprites[key].scale.setScalar(0.55 + 0.08 * pulse);

      // The ring stays under whoever is at work, in the color of its state, and pulses; hover and selection override it.
      agent.ring.visible = marked || active;
      if (marked || active) {
        agent.ring.material.color.set(role === selected ? TEAM_COLORS[agent.seat.team] : marked ? 0xffffff : STATE_COLORS[state]);
        agent.ring.material.opacity = role === selected ? 0.95 : marked ? 0.55 : 0.6 + 0.3 * pulse;
        agent.ring.scale.setScalar(active && !marked ? 1 + 0.07 * pulse : 1);
      }

      const screen = stations.get(role)?.screen;
      if (screen) {
        const alert = state === "blocked" || state === "escalate";
        screen.material.emissive.set(alert ? 0xff3b3b : TEAM_COLORS[agent.seat.team]);
        screen.material.emissiveIntensity = off ? 0.02 : (working ? 0.8 + 0.25 * Math.sin(time * 5 + agent.phase) : alert ? 0.4 + 0.3 * pulse : 0.12) + (marked ? 0.35 : 0);
      }
    }
  }

  const setHighlight = (hover, select) => {
    hovered = hover;
    selected = select;
  };

  return { apply, update, targets, setHighlight };
}
