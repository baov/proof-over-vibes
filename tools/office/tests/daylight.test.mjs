import assert from "node:assert/strict";
import test from "node:test";

import { createDayClock, daylightAt, formatHour, skyGradient, sunArc, twilightAt } from "../web/daylight.js";

const NIGHT_SKY = ["#0d1738", "#2b3068"];
const brightness = (hex) => {
  const n = parseInt(hex.slice(1), 16);
  return ((n >> 16) & 255) + ((n >> 8) & 255) + (n & 255);
};

test("it is day at noon and night at midnight", () => {
  assert.ok(daylightAt(13) > 0.99);
  assert.ok(daylightAt(23) < 0.01);
  assert.ok(daylightAt(2) < 0.01);
});

test("dawn and dusk are half-lit, and light rises then falls", () => {
  assert.ok(daylightAt(6.5) > 0.3 && daylightAt(6.5) < 0.9);
  assert.ok(daylightAt(17.5) > 0.3 && daylightAt(17.5) < 0.9);
  for (let h = 5; h < 8; h += 0.25) assert.ok(daylightAt(h + 0.25) >= daylightAt(h));
  for (let h = 17; h < 20; h += 0.25) assert.ok(daylightAt(h + 0.25) <= daylightAt(h));
});

test("twilight peaks at sunrise and sunset only", () => {
  assert.ok(twilightAt(6) > 0.9);
  assert.ok(twilightAt(18) > 0.9);
  assert.ok(twilightAt(13) < 0.01);
  assert.ok(twilightAt(0) < 0.01);
});

test("the sky is bright by day, dark at night and orange at sunset", () => {
  assert.ok(brightness(skyGradient(13, NIGHT_SKY)[0]) > brightness(skyGradient(23, NIGHT_SKY)[0]) + 200);
  assert.deepEqual(skyGradient(23, NIGHT_SKY), NIGHT_SKY);
  const bottom = skyGradient(18, NIGHT_SKY)[1];
  const red = parseInt(bottom.slice(1, 3), 16);
  const blue = parseInt(bottom.slice(5, 7), 16);
  assert.ok(red > blue + 40);
});

test("the sun crosses the sky from east to west", () => {
  const morning = sunArc(6.5);
  const noon = sunArc(12);
  const evening = sunArc(17.5);
  assert.ok(morning.x > noon.x && noon.x > evening.x);
  assert.ok(noon.y > morning.y && noon.y > evening.y);
});

test("hours are written as HH:MM, wrapping at midnight", () => {
  assert.equal(formatHour(13.5), "13:30");
  assert.equal(formatHour(0), "00:00");
  assert.equal(formatHour(23.9999), "00:00");
});

test("the clock follows the machine in auto mode", () => {
  const clock = createDayClock({ now: () => new Date(2026, 10, 11, 14, 30, 0), search: "" });
  assert.equal(clock.mode(), "auto");
  assert.equal(clock.hour(), 14.5);
});

test("?time= starts in manual mode at that hour", () => {
  const clock = createDayClock({ now: () => new Date(2026, 10, 11, 9, 0, 0), search: "?time=19:30" });
  assert.equal(clock.mode(), "manual");
  assert.equal(clock.hour(), 19.5);
});

test("a period or an hour can be picked by hand, and auto comes back", () => {
  const clock = createDayClock({ now: () => new Date(2026, 10, 11, 9, 0, 0), search: "" });
  clock.setPeriod("night");
  assert.equal(clock.mode(), "manual");
  assert.equal(clock.hour(), 23);
  clock.setHour(7.25);
  assert.equal(clock.hour(), 7.25);
  clock.setAuto();
  assert.equal(clock.mode(), "auto");
  assert.equal(clock.hour(), 9);
});

test("the N key cycles auto, dawn, day, dusk, night, auto", () => {
  const clock = createDayClock({ now: () => new Date(2026, 10, 11, 9, 0, 0), search: "" });
  const seen = [clock.label()];
  for (let i = 0; i < 5; i++) {
    clock.cycle();
    seen.push(clock.label());
  }
  assert.deepEqual(seen, ["auto", "dawn", "day", "dusk", "night", "auto"]);
});
