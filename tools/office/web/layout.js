// Geometry of the floor. Pure data and functions: no three.js import here.
// x runs along the width, z along the depth; the camera looks from +x, +z, so the
// back walls are the ones at x = 0 and z = 0.

export const FLOOR = { w: 20, d: 14 };

export const ROOMS = {
  product: { x: 0, z: 0, w: 8, d: 6 },
  design: { x: 12, z: 0, w: 8, d: 6 },
  build: { x: 0, z: 8, w: 8, d: 6 },
  quality: { x: 12, z: 8, w: 8, d: 6 },
  common: { x: 8, z: 4, w: 4, d: 6 },
};

export const HUB = { x: 10, z: 7 };

export const TEAM_COLORS = {
  product: "#f59e0b",
  design: "#8b5cf6",
  build: "#22c55e",
  quality: "#3b82f6",
  common: "#94a3b8",
};

export const SIGN_LABELS = { product: "제품", design: "설계", build: "개발", quality: "품질", common: "공용" };
export const SIGN_FALLBACK = { product: "product", design: "design", build: "build", quality: "quality", common: "common" };

// Glass partitions between the rooms: [x1, z1, x2, z2, doorway], the doorway being the open span along the line.
export const PARTITIONS = [
  [0, 6, 8, 6, [5, 7]],
  [8, 0, 8, 6],
  [12, 6, 20, 6, [13, 15]],
  [12, 0, 12, 6],
  [0, 8, 8, 8, [5, 7]],
  [8, 8, 8, 14],
  [12, 8, 20, 8, [13, 15]],
  [12, 8, 12, 14],
  [8.9, 10, 11.1, 10], // the break room's glass behind the sofa, a doorway on each side of it
];

// Where the furniture stands, so that scene.js draws it and the walkers go round it from the same numbers.
export const PLANTS = [[0.8, 0.8], [11.4, 4.6], [8.6, 4.6], [0.8, 13.2], [19.2, 13.2], [19.2, 0.8], [7.4, 13.2], [12.6, 13.2]];
export const BOOKSHELVES = [[[7.2, 0.28], "z"], [[19.2, 0.28], "z"], [[0.28, 11], "x"], [[0.28, 3.4], "x"]];
export const CABINETS = [[5.2, 11.5], [16.4, 0.35]];
export const SOFA = { x: 10, z: 10.9, w: 2.0 }; // its back to the hub, facing the break room
export const VENDING = { x: 8.53, z: 10.9 }; // against the west glass, beside the sofa, which it no longer hides

// The break room, past the hub's second row: the sofa, the vending machine, a coffee counter and a high table.
export const BREAK_ROOM = { x: 8, z: 10, w: 4, d: 4, color: "#14b8a6" };
export const COFFEE = { x: 8.55, z: 12.4 }; // a counter 0.7 by 1.4, the machine on top
export const HIGH_TABLE = { x: 10, z: 12.7 };
// Where a resting agent goes: two places on the sofa, one at the coffee counter, three round the high table.
// rotY is the way it faces, as on a seat; `sits` for the sofa; `table` where two can chat.
export const BREAK_SPOTS = [
  { x: 9.5, z: 11.0, rotY: 0, sits: true },
  { x: 10.5, z: 11.0, rotY: 0, sits: true },
  { x: 9.2, z: 11.95, rotY: -Math.PI / 2 },
  { x: 10, z: 12.02, rotY: 0, table: true },
  { x: 10, z: 13.38, rotY: Math.PI, table: true },
  { x: 9.33, z: 12.85, rotY: Math.PI / 2, table: true },
];

const rect = (name, x, z, w, d) => ({ name, x0: x - w / 2, x1: x + w / 2, z0: z - d / 2, z1: z + d / 2 });

// The footprint of everything a walker must go round, desks and chairs aside: they come with the seats.
export const OBSTACLES = [
  ...PARTITIONS.flatMap(([x1, z1, x2, z2, gap]) => {
    const horizontal = z1 === z2;
    const lo = horizontal ? Math.min(x1, x2) : Math.min(z1, z2);
    const hi = horizontal ? Math.max(x1, x2) : Math.max(z1, z2);
    return (gap ? [[lo, gap[0]], [gap[1], hi]] : [[lo, hi]])
      .filter(([a, b]) => b > a)
      .map(([a, b]) => (horizontal ? rect("partition", (a + b) / 2, z1, b - a, 0.1) : rect("partition", x1, (a + b) / 2, 0.1, b - a)));
  }),
  ...PLANTS.map(([x, z]) => rect("plant", x, z, 0.8, 0.8)), // the leaves spread wider than the pot
  ...BOOKSHELVES.map(([[x, z], facing]) => (facing === "z" ? rect("bookshelf", x, z, 1.2, 0.42) : rect("bookshelf", x, z, 0.42, 1.2))),
  ...CABINETS.map(([x, z]) => rect("cabinet", x, z, 1.0, 0.5)),
  { name: "sofa", x0: SOFA.x - SOFA.w / 2, x1: SOFA.x + SOFA.w / 2, z0: SOFA.z - 0.5, z1: SOFA.z + 0.45 },
  rect("vending machine", VENDING.x, VENDING.z, 0.95, 0.85),
  rect("coffee counter", COFFEE.x, COFFEE.z, 0.7, 1.4),
  rect("high table", HIGH_TABLE.x, HIGH_TABLE.z, 0.7, 0.7),
];

const DESK = { w: 1.9, d: 0.85 };
const CHAIR = { w: 0.62, front: -0.15, back: 0.45 }; // around seat.z: 0.6 deep, the back towards the camera
const CLEARANCE = 0.22; // how far a walker's middle keeps from anything: half a body and its arms
const STEP = 0.1; // the grid the walkers' routes are searched on

// roleTeams: { role: team }, as sent by the server. Returns the seats and the paths.
export function createLayout(roleTeams) {
  const byTeam = {};
  for (const [role, team] of Object.entries(roleTeams)) (byTeam[team] ||= []).push(role);

  // A desk is 1.9 wide: a row holds as many as fit side by side. The hub is only 4 wide, so it seats two a row;
  // quality, whose doorway is behind its desks, seats two a row too, so that aisles lead to every chair.
  const PER_ROW = { common: 2, quality: 2 };
  const ROW_STEP = 2.8; // the depth of a row: desk, chair and the room to walk past
  const DESK_W = 1.95; // a desk and a hand of room
  const seats = new Map();
  for (const [team, roles] of Object.entries(byTeam)) {
    const room = ROOMS[team];
    const perRow = PER_ROW[team] ?? roles.length;
    roles.forEach((role, i) => {
      const row = Math.floor(i / perRow);
      const inRow = Math.min(perRow, roles.length - row * perRow);
      const slot = i % perRow;
      // Evenly spaced; when that leaves less than a desk each, one cell per desk instead.
      const x = room.w / (inRow + 1) >= DESK_W
        ? room.x + (room.w * (slot + 1)) / (inRow + 1)
        : room.x + (room.w * (2 * slot + 1)) / (2 * inRow);
      // Desk against the back of the room, the agent sits south of it facing north (-z):
      // the camera sees the agent's back and the screen over the desk.
      const seat = { x, z: room.z + 2.4 + row * ROW_STEP, deskZ: room.z + 1.4 + row * ROW_STEP, rotY: Math.PI, team, row };
      seats.set(role, seat);
    });
  }

  const seatOf = (role) => seats.get(role);

  const deskOf = (seat) => rect("desk", seat.x, seat.deskZ, DESK.w, DESK.d);
  const chairOf = (seat) => ({ name: "chair", x0: seat.x - CHAIR.w / 2, x1: seat.x + CHAIR.w / 2, z0: seat.z + CHAIR.front, z1: seat.z + CHAIR.back });
  const W = Math.round(FLOOR.w / STEP);
  const D = Math.round(FLOOR.d / STEP);
  const routes = new Map(); // from role: the walkable grid and the distances from its seat

  // Everything solid but the walker's own chair, which it gets up from.
  function freeTest(fromRole) {
    const solid = [...OBSTACLES];
    for (const [role, seat] of seats) {
      solid.push(deskOf(seat));
      if (role !== fromRole) solid.push(chairOf(seat));
    }
    const c = CLEARANCE;
    return (x, z) => x > c && x < FLOOR.w - c && z > c && z < FLOOR.d - c
      && !solid.some((o) => x > o.x0 - c && x < o.x1 + c && z > o.z0 - c && z < o.z1 + c);
  }

  // Dijkstra over the grid from the walker's seat, eight neighbours: cheap enough for a 200 x 140 floor.
  function routeFrom(fromRole) {
    if (routes.has(fromRole)) return routes.get(fromRole);
    const free = freeTest(fromRole);
    const seat = seatOf(fromRole);
    const cell = (x, z) => Math.round(z / STEP - 0.5) * W + Math.round(x / STEP - 0.5);
    const centre = (i) => ({ x: ((i % W) + 0.5) * STEP, z: (Math.floor(i / W) + 0.5) * STEP });
    const open = new Uint8Array(W * D);
    for (let i = 0; i < W * D; i++) {
      const p = centre(i);
      open[i] = free(p.x, p.z) ? 1 : 0;
    }
    const dist = new Float64Array(W * D).fill(Infinity);
    const prev = new Int32Array(W * D).fill(-1);
    const start = cell(seat.x, seat.z);
    open[start] = 1;
    dist[start] = 0;
    const heap = [[0, start]];
    const push = (item) => {
      heap.push(item);
      for (let i = heap.length - 1; i > 0;) {
        const up = (i - 1) >> 1;
        if (heap[up][0] <= heap[i][0]) break;
        [heap[up], heap[i]] = [heap[i], heap[up]];
        i = up;
      }
    };
    const pop = () => {
      const top = heap[0];
      const last = heap.pop();
      if (heap.length) {
        heap[0] = last;
        for (let i = 0; ;) {
          const l = 2 * i + 1;
          const r = l + 1;
          let m = i;
          if (l < heap.length && heap[l][0] < heap[m][0]) m = l;
          if (r < heap.length && heap[r][0] < heap[m][0]) m = r;
          if (m === i) break;
          [heap[m], heap[i]] = [heap[i], heap[m]];
          i = m;
        }
      }
      return top;
    };
    while (heap.length) {
      const [d, i] = pop();
      if (d > dist[i]) continue;
      const cx = i % W;
      const cz = Math.floor(i / W);
      for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
        const nx = cx + dx;
        const nz = cz + dz;
        if (nx < 0 || nz < 0 || nx >= W || nz >= D) continue;
        const j = nz * W + nx;
        // A diagonal step may not cut the corner of an obstacle.
        if (!open[j] || (dx && dz && (!open[cz * W + nx] || !open[nz * W + cx]))) continue;
        const nd = d + (dx && dz ? Math.SQRT2 : 1);
        if (nd < dist[j]) {
          dist[j] = nd;
          prev[j] = i;
          push([nd, j]);
        }
      }
    }
    const route = { free, dist, prev, centre };
    routes.set(fromRole, route);
    return route;
  }

  // The straight line from a to b keeps clear of everything.
  const clear = (free, a, b) => {
    const n = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.z - a.z) / 0.05));
    for (let k = 1; k < n; k++) if (!free(a.x + ((b.x - a.x) * k) / n, a.z + ((b.z - a.z) * k) / n)) return false;
    return true;
  };

  // Out of the chair, round the desks, chairs, partitions and furniture, as close to `b` as the floor lets it:
  // next to the receiver's chair for a handoff, onto the sofa or by the counter for a break.
  // The route found on the grid is pulled tight into a few straight segments, the way a person would walk it.
  function walkTo(fromRole, b) {
    const { free, dist, prev, centre } = routeFrom(fromRole);
    let goal = -1;
    let best = Infinity;
    for (let i = 0; i < dist.length; i++) {
      if (dist[i] === Infinity) continue;
      const p = centre(i);
      const near = Math.hypot(p.x - b.x, p.z - b.z);
      if (near < best - 1e-9) {
        best = near;
        goal = i;
      }
    }
    const cells = [];
    for (let i = goal; i !== -1; i = prev[i]) cells.push(centre(i));
    cells.reverse();
    const a = seatOf(fromRole);
    cells[0] = { x: a.x, z: a.z };
    const path = [cells[0]];
    for (let i = 0; i < cells.length - 1;) {
      let j = cells.length - 1;
      while (j > i + 1 && !clear(free, cells[i], cells[j])) j--;
      path.push(cells[j]);
      i = j;
    }
    return path.map((p) => ({ x: Math.round(p.x * 100) / 100, z: Math.round(p.z * 100) / 100 }));
  }

  const walkPath = (fromRole, toRole) => walkTo(fromRole, seatOf(toRole));

  // To a place in the break room. The sofa is solid for the router: the last step sits down on it.
  function breakPath(fromRole, spot) {
    const path = walkTo(fromRole, spot);
    const end = path.at(-1);
    if (Math.hypot(end.x - spot.x, end.z - spot.z) > 0.01) path.push({ x: spot.x, z: spot.z });
    return path;
  }

  return { FLOOR, ROOMS, HUB, seats, seatOf, walkPath, breakPath };
}
