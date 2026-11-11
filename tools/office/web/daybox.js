// The time-of-day control: the hour that is shown, and a way to pick a period or an hour by hand.
import { daylightAt, formatHour, twilightAt } from "./daylight.js";

const PERIODS = [["dawn", "Dawn"], ["day", "Day"], ["dusk", "Dusk"], ["night", "Night"]];

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

const icon = (hour) => (twilightAt(hour) > 0.45 ? "🌅" : daylightAt(hour) > 0.5 ? "☀️" : "🌙");

export function createDayBox(root, { onPeriod, onAuto, onHour }) {
  document.head.append(Object.assign(el("style"), {
    textContent: `
      .daybox { margin-top: 8px; pointer-events: auto; padding: 8px 10px; border-radius: 14px; background: rgba(10,12,28,.78); border: 1px solid rgba(255,255,255,.12); backdrop-filter: blur(6px); font-size: 12px; display: flex; flex-direction: column; gap: 6px; width: 230px; box-sizing: border-box; }
      .daybox .top { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 0; font: inherit; font-size: 14px; font-weight: 700; color: inherit; background: none; border: 0; border-radius: 0; cursor: pointer; }
      .daybox .top .caret { font-size: 10px; opacity: .6; margin-left: 6px; }
      .daybox:not(.open) .modes, .daybox:not(.open) input[type=range] { display: none; }
      .daybox:not(.open) { padding: 6px 10px; }
      .daybox .top small { font-weight: 400; opacity: .65; font-size: 12px; }
      .daybox .modes { display: flex; gap: 4px; }
      .daybox button { font: inherit; font-size: 11px; color: inherit; cursor: pointer; flex: 1; padding: 3px 0; border-radius: 999px; border: 1px solid rgba(255,255,255,.25); background: none; }
      .daybox button.on { background: #2563eb; border-color: #2563eb; }
      .daybox input[type=range] { width: 100%; margin: 0; accent-color: #60a5fa; }
      @media (max-width: 700px) { .daybox { display: none; } }
    `,
  }));
  // Folded by default: the hour is read at a glance, and the controls open on a click (they are rarely needed).
  const box = el("div", "daybox");
  box.setAttribute("aria-label", "Time of day");
  const top = el("button", "top");
  top.setAttribute("aria-expanded", "false");
  top.title = "Time of day: click to set it";
  const time = el("span");
  const mode = el("small");
  const caret = el("span", "caret", "▾");
  const label = el("span");
  label.append(mode, caret);
  top.append(time, label);
  top.onclick = () => {
    const open = box.classList.toggle("open");
    top.setAttribute("aria-expanded", String(open));
    caret.textContent = open ? "▴" : "▾";
  };
  const modes = el("div", "modes");
  const auto = el("button", "", "Auto");
  auto.onclick = onAuto;
  modes.append(auto);
  const buttons = new Map([["auto", auto]]);
  for (const [name, label] of PERIODS) {
    const b = el("button", "", label);
    b.onclick = () => onPeriod(name);
    buttons.set(name, b);
    modes.append(b);
  }
  const slider = el("input");
  slider.type = "range";
  slider.min = "0";
  slider.max = "24";
  slider.step = "0.25";
  slider.setAttribute("aria-label", "Hour of the day");
  slider.oninput = () => onHour(Number(slider.value));
  box.append(top, modes, slider);
  root.append(box);

  // state: { mode: "auto" | "manual", label, hour }
  function update(state) {
    time.textContent = `${icon(state.hour)} ${formatHour(state.hour)}`;
    mode.textContent = state.mode === "auto" ? "follows your clock" : state.label === "custom" ? "set by hand" : `${state.label} (by hand)`;
    for (const [name, b] of buttons) b.classList.toggle("on", name === state.label);
    slider.hidden = state.mode === "auto"; // the slider only matters once the hour is set by hand
    if (document.activeElement !== slider) slider.value = String(state.hour);
  }
  return { update };
}
