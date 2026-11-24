import assert from "node:assert/strict";
import test from "node:test";

import { createLayout } from "../web/layout.js";

// The role-to-team map the server sends (floor/roles.py), every role of agents/.
const ROLE_TEAMS = {
  orchestrator: "product", "product-owner": "product", "product-manager": "product",
  architect: "design", planner: "design",
  developer: "build", diagnostician: "build",
  qa: "quality", reviewer: "quality", auditor: "quality", "failure-analyst": "quality",
  cartographer: "common", "harness-engineer": "common", coach: "common",
};

const DESK = { halfW: 0.95, halfD: 0.425 }; // station(): a 1.9 x 0.85 desk
const CHAIR = { halfW: 0.31, front: 0.15, back: 0.45 }; // chair centred on seat.z + 0.15, 0.6 deep

const desk = (seat) => ({ x0: seat.x - DESK.halfW, x1: seat.x + DESK.halfW, z0: seat.deskZ - DESK.halfD, z1: seat.deskZ + DESK.halfD });
const chair = (seat) => ({ x0: seat.x - CHAIR.halfW, x1: seat.x + CHAIR.halfW, z0: seat.z + CHAIR.front - 0.3, z1: seat.z + CHAIR.back });
const overlap = (a, b) => a.x0 < b.x1 && b.x0 < a.x1 && a.z0 < b.z1 && b.z0 < a.z1;

test("no two desks, and no desk and chair of another seat, overlap", () => {
  const layout = createLayout(ROLE_TEAMS);
  const seats = [...layout.seats.entries()];
  for (const [roleA, a] of seats) {
    for (const [roleB, b] of seats) {
      if (roleA >= roleB) continue;
      assert.ok(!overlap(desk(a), desk(b)), `desks of ${roleA} and ${roleB} overlap`);
    }
    for (const [roleB, b] of seats) {
      if (roleA === roleB) continue;
      assert.ok(!overlap(desk(a), chair(b)), `desk of ${roleA} and chair of ${roleB} overlap`);
    }
  }
});

test("every seat stays inside its own room", () => {
  const layout = createLayout(ROLE_TEAMS);
  for (const [role, seat] of layout.seats) {
    const room = layout.ROOMS[seat.team];
    const d = desk(seat);
    assert.ok(d.x0 >= room.x && d.x1 <= room.x + room.w, `${role}: desk leaves its room along x`);
    assert.ok(d.z0 >= room.z && chair(seat).z1 <= room.z + room.d, `${role}: desk or chair leaves its room along z`);
  }
});

test("a walker never crosses a desk of the hub", () => {
  const layout = createLayout(ROLE_TEAMS);
  const hub = layout.ROOMS.common;
  const inHub = (x, z) => x >= hub.x && x <= hub.x + hub.w && z >= hub.z && z <= hub.z + hub.d;
  const roles = [...layout.seats.keys()];
  const desks = roles.map((role) => [role, desk(layout.seats.get(role))]);
  const margin = 0.2; // half the width of an agent, less its arms
  for (const from of roles) {
    for (const to of roles) {
      if (from === to) continue;
      const path = layout.walkPath(from, to);
      for (let i = 1; i < path.length; i++) {
        const a = path[i - 1];
        const b = path[i];
        const steps = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.z - a.z) / 0.05));
        for (let s = 0; s <= steps; s++) {
          const x = a.x + ((b.x - a.x) * s) / steps;
          const z = a.z + ((b.z - a.z) * s) / steps;
          if (!inHub(x, z)) continue;
          for (const [owner, d] of desks) {
            const inside = x > d.x0 - margin && x < d.x1 + margin && z > d.z0 - margin && z < d.z1 + margin;
            assert.ok(!inside, `${from} -> ${to} walks through the desk of ${owner} at (${x.toFixed(2)}, ${z.toFixed(2)})`);
          }
        }
      }
    }
  }
});

test("a walker goes round every desk, chair, partition and piece of furniture", async () => {
  const { OBSTACLES } = await import("../web/layout.js");
  const layout = createLayout(ROLE_TEAMS);
  const roles = [...layout.seats.keys()];
  const margin = 0.15; // half the width of an agent, less its arms
  const solid = [
    ...OBSTACLES.map((o) => ({ ...o, owner: null })),
    ...roles.map((role) => ({ ...desk(layout.seats.get(role)), name: `desk of ${role}`, owner: null })),
    ...roles.map((role) => ({ ...chair(layout.seats.get(role)), name: `chair of ${role}`, owner: role })),
  ];
  for (const from of roles) {
    for (const to of roles) {
      if (from === to) continue;
      const path = layout.walkPath(from, to);
      for (let i = 1; i < path.length; i++) {
        const a = path[i - 1];
        const b = path[i];
        const steps = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.z - a.z) / 0.05));
        for (let s = 0; s <= steps; s++) {
          const x = a.x + ((b.x - a.x) * s) / steps;
          const z = a.z + ((b.z - a.z) * s) / steps;
          assert.ok(x > 0 && x < 20 && z > 0 && z < 14, `${from} -> ${to} leaves the floor at (${x.toFixed(2)}, ${z.toFixed(2)})`);
          for (const o of solid) {
            if (o.owner === from) continue; // the walker gets up from its own chair
            const inside = x > o.x0 - margin && x < o.x1 + margin && z > o.z0 - margin && z < o.z1 + margin;
            assert.ok(!inside, `${from} -> ${to} walks through the ${o.name} at (${x.toFixed(2)}, ${z.toFixed(2)})`);
          }
        }
      }
    }
  }
});

test("every handoff is short enough to arrive before the receiver starts anyway", () => {
  const layout = createLayout(ROLE_TEAMS);
  const roles = [...layout.seats.keys()];
  // agents.js: SPEED 3 units a second, DEFER_MAX 9 seconds.
  for (const from of roles) {
    for (const to of roles) {
      if (from === to) continue;
      const path = layout.walkPath(from, to);
      let length = 0;
      for (let i = 1; i < path.length; i++) length += Math.hypot(path[i].x - path[i - 1].x, path[i].z - path[i - 1].z);
      assert.ok(length < 27, `${from} -> ${to} is ${length.toFixed(1)} long`);
    }
  }
});

test("every role reaches every place of the break room round the furniture", async () => {
  const { OBSTACLES, BREAK_SPOTS, BREAK_ROOM } = await import("../web/layout.js");
  const layout = createLayout(ROLE_TEAMS);
  const roles = [...layout.seats.keys()];
  const margin = 0.15;
  const solid = [
    ...OBSTACLES.map((o) => ({ ...o, owner: null })),
    ...roles.map((role) => ({ ...desk(layout.seats.get(role)), name: `desk of ${role}`, owner: null })),
    ...roles.map((role) => ({ ...chair(layout.seats.get(role)), name: `chair of ${role}`, owner: role })),
  ];
  for (const role of roles) {
    for (const spot of BREAK_SPOTS) {
      const path = layout.breakPath(role, spot);
      const end = path.at(-1);
      assert.deepEqual([end.x, end.z], [spot.x, spot.z], `${role} does not reach (${spot.x}, ${spot.z})`);
      const inRoom = (p) => p.x >= BREAK_ROOM.x && p.x <= BREAK_ROOM.x + BREAK_ROOM.w && p.z >= BREAK_ROOM.z && p.z <= BREAK_ROOM.z + BREAK_ROOM.d;
      assert.ok(inRoom(end), `(${spot.x}, ${spot.z}) is outside the break room`);
      // The last step sits down on the sofa: it may only be a step long.
      const before = path.at(-2);
      if (spot.sits) assert.ok(Math.hypot(end.x - before.x, end.z - before.z) < 0.7, `${role} sits down from too far`);
      const walked = spot.sits ? path.slice(0, -1) : path;
      for (let i = 1; i < walked.length; i++) {
        const a = walked[i - 1];
        const b = walked[i];
        const steps = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.z - a.z) / 0.05));
        for (let s = 0; s <= steps; s++) {
          const x = a.x + ((b.x - a.x) * s) / steps;
          const z = a.z + ((b.z - a.z) * s) / steps;
          for (const o of solid) {
            if (o.owner === role) continue;
            const inside = x > o.x0 - margin && x < o.x1 + margin && z > o.z0 - margin && z < o.z1 + margin;
            assert.ok(!inside, `${role} -> break walks through the ${o.name} at (${x.toFixed(2)}, ${z.toFixed(2)})`);
          }
        }
      }
    }
  }
});
