import assert from "node:assert/strict";
import test from "node:test";

import { createLayout } from "../web/layout.js";

// The role-to-team map the server sends (floor/roles.py), every role of agents/.
const ROLE_TEAMS = {
  orchestrator: "product", "product-owner": "product", "product-manager": "product",
  architect: "design", planner: "design",
  developer: "build", diagnostician: "build",
  reviewer: "quality", auditor: "quality", "failure-analyst": "quality",
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
