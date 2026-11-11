"""Which open space each role of agents/ sits in."""

from __future__ import annotations

TEAMS = ("product", "design", "build", "quality", "common")

ROLE_TEAM = {
    "orchestrator": "product",
    "product-owner": "product",
    "product-manager": "product",
    "architect": "design",
    "planner": "design",
    "developer": "build",
    "diagnostician": "build",
    "reviewer": "quality",
    "auditor": "quality",
    "failure-analyst": "quality",
    "cartographer": "common",
    "harness-engineer": "common",
    "coach": "common",
}
