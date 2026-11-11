// Names and colors shared by the HUD, the tooltip and the panel.
export const STATE_COLORS = { working: "#3b82f6", done: "#16a34a", blocked: "#d97706", escalate: "#dc2626", idle: "#64748b" };

const SHORT = {
  orchestrator: "Orch", "product-owner": "PO", "product-manager": "PM", architect: "Arch", planner: "Plan",
  developer: "Dev", diagnostician: "Diag", reviewer: "Review", auditor: "Audit", "failure-analyst": "Fail",
  cartographer: "Map", "harness-engineer": "Harness", coach: "Coach",
};

export const roleTitle = (role) => role.split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
export const roleShort = (role) => SHORT[role] ?? roleTitle(role);

export function ago(seconds) {
  const s = Math.max(0, Math.round(Date.now() / 1000 - seconds));
  if (s < 5) return "just now";
  if (s < 90) return `${s}s ago`;
  if (s < 5400) return `${Math.round(s / 60)} min ago`;
  return `${Math.round(s / 3600)} h ago`;
}

// How long a finished task took, for a label ("45s", "4 min", "1 h 20"). null when the page cannot tell.
export function took(seconds) {
  if (seconds == null) return null;
  const s = Math.round(seconds);
  if (s < 60) return `${s}s`;
  if (s < 3600) return `${Math.round(s / 60)} min`;
  const minutes = Math.round((s % 3600) / 60);
  return minutes ? `${Math.floor(s / 3600)} h ${String(minutes).padStart(2, "0")}` : `${Math.floor(s / 3600)} h`;
}
