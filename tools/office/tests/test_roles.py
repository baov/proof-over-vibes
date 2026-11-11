import unittest
from pathlib import Path

from floor.roles import ROLE_TEAM, TEAMS

AGENTS = Path(__file__).resolve().parents[3] / "agents"


class RolesTest(unittest.TestCase):
    def test_every_agent_file_has_a_team(self):
        stems = {p.stem for p in AGENTS.glob("*.md")}
        self.assertEqual(stems, set(ROLE_TEAM))

    def test_teams_are_the_five_known_ids(self):
        self.assertEqual(set(ROLE_TEAM.values()), set(TEAMS))

    def test_mapping_matches_design(self):
        self.assertEqual(ROLE_TEAM["reviewer"], "quality")
        self.assertEqual(ROLE_TEAM["architect"], "design")
        self.assertEqual(ROLE_TEAM["coach"], "common")
        self.assertEqual(ROLE_TEAM["developer"], "build")
        self.assertEqual(ROLE_TEAM["orchestrator"], "product")


if __name__ == "__main__":
    unittest.main()
