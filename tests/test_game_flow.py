import unittest
from dataclasses import replace

from src.battle_engine import Formation, Terrain
from src.game import is_finished, run_round, starter_state, winner


class GameFlowTests(unittest.TestCase):
    def test_run_round_advances_and_logs(self):
        state = starter_state(seed=1)
        run_round(state, Formation.FENGSHI, Terrain.PLAIN, random_factor=1.0)

        self.assertEqual(state.round_no, 2)
        self.assertEqual(len(state.log), 1)
        self.assertIn("R1", state.log[0])

    def test_finished_by_round_limit(self):
        state = starter_state(seed=1)
        self.assertFalse(is_finished(state, max_rounds=1))
        run_round(state, Formation.YULIN, Terrain.FOREST, random_factor=1.0)
        self.assertTrue(is_finished(state, max_rounds=1))

    def test_winner_resolution(self):
        state = starter_state(seed=1)
        state.player = replace(state.player, troops=100)
        state.enemy = replace(state.enemy, troops=0)
        self.assertEqual(winner(state), "player")


if __name__ == "__main__":
    unittest.main()
