import unittest

from src.battle_engine import (
    Arms,
    BattleContext,
    Formation,
    Officer,
    Terrain,
    Unit,
    apply_damage,
    arms_multiplier,
    calculate_damage,
    formation_multiplier,
    simulate_skirmish,
    tactic_success_rate,
)


class BattleEngineTests(unittest.TestCase):
    def setUp(self):
        self.attacker_officer = Officer("測試甲", leadership=80, might=80, intelligence=70)
        self.defender_officer = Officer("測試乙", leadership=70, might=75, intelligence=60)

    def _unit(self, arms: Arms, formation: Formation, morale: int = 80, troops: int = 4000) -> Unit:
        return Unit(self.attacker_officer, troops=troops, arms=arms, formation=formation, morale=morale)

    def test_arms_counter_and_reverse(self):
        self.assertEqual(arms_multiplier(Arms.SPEAR, Arms.CAVALRY, False), 1.2)
        self.assertEqual(arms_multiplier(Arms.CAVALRY, Arms.SPEAR, False), 0.85)

    def test_siege_unit_special_case(self):
        self.assertEqual(arms_multiplier(Arms.SIEGE, Arms.HALBERD, True), 1.5)
        self.assertEqual(arms_multiplier(Arms.SIEGE, Arms.HALBERD, False), 0.75)

    def test_formation_counter_and_reverse(self):
        self.assertEqual(formation_multiplier(Formation.FENGSHI, Formation.FANGYUAN), 1.12)
        self.assertEqual(formation_multiplier(Formation.FANGYUAN, Formation.FENGSHI), 0.9)

    def test_damage_is_deterministic_with_random_factor(self):
        attacker = self._unit(Arms.CAVALRY, Formation.FENGSHI)
        defender = Unit(self.defender_officer, troops=4200, arms=Arms.BOW, formation=Formation.YULIN, morale=70)

        ctx = BattleContext(terrain=Terrain.PLAIN, is_siege_target=False, random_factor=1.0)
        dmg_1 = calculate_damage(attacker, defender, ctx)
        dmg_2 = calculate_damage(attacker, defender, ctx)

        self.assertEqual(dmg_1, dmg_2)
        self.assertGreater(dmg_1, 0)

    def test_apply_damage_updates_troops_and_morale(self):
        unit = self._unit(Arms.SPEAR, Formation.YULIN, morale=90, troops=3000)
        after = apply_damage(unit, 500)
        self.assertEqual(after.troops, 2500)
        self.assertLess(after.morale, unit.morale)

    def test_simulate_skirmish_changes_both_sides(self):
        attacker = self._unit(Arms.CAVALRY, Formation.FENGSHI, morale=85, troops=4500)
        defender = Unit(self.defender_officer, troops=4300, arms=Arms.BOW, formation=Formation.FANGYUAN, morale=78)
        ctx = BattleContext(terrain=Terrain.PLAIN, is_siege_target=False, random_factor=1.0)

        result = simulate_skirmish(attacker, defender, ctx)

        self.assertGreater(result.attacker_damage, 0)
        self.assertGreater(result.defender_damage, 0)
        self.assertLess(result.attacker_after.troops, attacker.troops)
        self.assertLess(result.defender_after.troops, defender.troops)

    def test_tactic_success_rate_clamp(self):
        self.assertEqual(tactic_success_rate(10, 100), 15)
        self.assertEqual(tactic_success_rate(200, 10), 90)
        self.assertAlmostEqual(tactic_success_rate(80, 60), 69.0)


if __name__ == "__main__":
    unittest.main()
