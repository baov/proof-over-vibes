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

const DOORS = {
  product: { x: 6, z: 6.5 },
  design: { x: 14, z: 6.5 },
  build: { x: 6, z: 7.5 },
  quality: { x: 14, z: 7.5 },
  common: HUB,
};

// roleTeams: { role: team }, as sent by the server. Returns the seats and the paths.
export function createLayout(roleTeams) {
  const byTeam = {};
  for (const [role, team] of Object.entries(roleTeams)) (byTeam[team] ||= []).push(role);

  // A desk is 1.9 wide: a row holds as many as fit side by side. The hub is only 4 wide, so it seats two a row.
  const PER_ROW = { common: 2 };
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
      // A seat behind another row cannot walk north through it: it leaves by the side, then north.
      if (row > 0) seat.exit = [{ x, z: seat.z + 0.9 }, { x: room.x + room.w - 0.45, z: seat.z + 0.9 }, { x: room.x + room.w - 0.45, z: HUB.z }];
      seats.set(role, seat);
    });
  }

  const seatOf = (role) => seats.get(role);
  const doorOf = (team) => DOORS[team];
  const front = (seat) => seat.exit ?? [{ x: seat.x, z: seat.z + 0.9 }];

  // Straight segments only: out of the desk, door, hub, door, in front of the target desk.
  function walkPath(fromRole, toRole) {
    const a = seatOf(fromRole);
    const b = seatOf(toRole);
    const points = [
      { x: a.x, z: a.z },
      ...front(a),
      doorOf(a.team),
      HUB,
      doorOf(b.team),
      ...[...front(b)].reverse(),
    ];
    return points.filter((p, i) => i === 0 || p.x !== points[i - 1].x || p.z !== points[i - 1].z);
  }

  return { FLOOR, ROOMS, HUB, seats, seatOf, doorOf, walkPath };
}
