// The time of day: how much light there is, the color of the sky, where the sun stands.
// Pure functions and a small clock, with no three.js: they run in the page and in node's tests.

export const PERIODS = { dawn: 6.5, day: 13, dusk: 17.5, night: 23 };

const DAY_SKY = ["#5aa9ff", "#cfe9ff"];
const TWILIGHT_SKY = ["#4a4f9a", "#ff9a6b"];

const smooth = (a, b, x) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

// Sunrise at 6:00 and sunset at 18:00, the same every day: no location, no season.
export const elevation = (hour) => Math.sin(((hour - 6) / 12) * Math.PI);
export const daylightAt = (hour) => smooth(-0.1, 0.3, elevation(hour));
export const twilightAt = (hour) => Math.exp(-((elevation(hour) / 0.2) ** 2));

export function mix(a, b, t) {
  const channel = (hex, shift) => (parseInt(hex.slice(1), 16) >> shift) & 255;
  const part = (shift) => Math.round(channel(a, shift) + (channel(b, shift) - channel(a, shift)) * t);
  return `#${[16, 8, 0].map((shift) => part(shift).toString(16).padStart(2, "0")).join("")}`;
}

// [top, bottom] of the sky gradient; `night` is the theme's own night sky.
export function skyGradient(hour, night) {
  const d = daylightAt(hour);
  const tw = twilightAt(hour);
  const top = mix(mix(night[0], DAY_SKY[0], d), TWILIGHT_SKY[0], tw * 0.7);
  const bottom = mix(mix(night[1], DAY_SKY[1], d), TWILIGHT_SKY[1], tw * 0.85);
  return [top, bottom];
}

// Where the sun is, from the east in the morning to the west in the evening.
export function sunArc(hour) {
  const a = Math.min(1, Math.max(0, (hour - 6) / 12)) * Math.PI;
  return { x: 10 + 24 * Math.cos(a), y: 6 + 24 * Math.sin(a), z: 23, a };
}

export function formatHour(hour) {
  const minutes = Math.round(hour * 60) % 1440;
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(Math.floor(minutes / 60))}:${pad(minutes % 60)}`;
}

const ORDER = ["auto", "dawn", "day", "dusk", "night"];

// Follows the machine's clock, until a period or an hour is picked by hand (or ?time=HH:MM is given).
export function createDayClock({ now = () => new Date(), search = "" } = {}) {
  let manual = null;
  let name = "auto";
  const given = /[?&]time=(\d{1,2}):(\d{2})/.exec(search);
  if (given) {
    manual = Number(given[1]) + Number(given[2]) / 60;
    name = "custom";
  }
  const local = () => {
    const d = now();
    return d.getHours() + d.getMinutes() / 60 + d.getSeconds() / 3600;
  };
  const clock = {
    mode: () => (manual === null ? "auto" : "manual"),
    hour: () => manual ?? local(),
    label: () => name,
    setPeriod(period) {
      manual = PERIODS[period];
      name = period;
    },
    setHour(hour) {
      manual = ((hour % 24) + 24) % 24;
      name = "custom";
    },
    setAuto() {
      manual = null;
      name = "auto";
    },
    cycle() {
      const next = ORDER[(ORDER.indexOf(name) + 1) % ORDER.length];
      if (next === "auto") clock.setAuto();
      else clock.setPeriod(next);
    },
  };
  return clock;
}
