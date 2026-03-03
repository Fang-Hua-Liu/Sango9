from __future__ import annotations

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


def make_officers() -> tuple[Officer, Officer]:
    return (
        Officer("測試甲", leadership=80, might=80, intelligence=70),
        Officer("測試乙", leadership=70, might=75, intelligence=60),
    )


def make_unit(
    officer: Officer,
    arms: Arms,
    formation: Formation,
    morale: int = 80,
    troops: int = 4000,
) -> Unit:
    return Unit(officer=officer, troops=troops, arms=arms, formation=formation, morale=morale)


def test_arms_counter_and_reverse() -> None:
    assert arms_multiplier(Arms.SPEAR, Arms.CAVALRY, False) == 1.2
    assert arms_multiplier(Arms.CAVALRY, Arms.SPEAR, False) == 0.85


def test_siege_unit_special_case() -> None:
    assert arms_multiplier(Arms.SIEGE, Arms.HALBERD, True) == 1.5
    assert arms_multiplier(Arms.SIEGE, Arms.HALBERD, False) == 0.75


def test_formation_counter_and_reverse() -> None:
    assert formation_multiplier(Formation.FENGSHI, Formation.FANGYUAN) == 1.12
    assert formation_multiplier(Formation.FANGYUAN, Formation.FENGSHI) == 0.9


def test_damage_is_deterministic_with_random_factor() -> None:
    attacker_officer, defender_officer = make_officers()
    attacker = make_unit(attacker_officer, Arms.CAVALRY, Formation.FENGSHI)
    defender = make_unit(defender_officer, Arms.BOW, Formation.YULIN, morale=70, troops=4200)

    ctx = BattleContext(terrain=Terrain.PLAIN, is_siege_target=False, random_factor=1.0)
    dmg_1 = calculate_damage(attacker, defender, ctx)
    dmg_2 = calculate_damage(attacker, defender, ctx)

    assert dmg_1 == dmg_2
    assert dmg_1 > 0


def test_apply_damage_updates_troops_and_morale() -> None:
    attacker_officer, _ = make_officers()
    unit = make_unit(attacker_officer, Arms.SPEAR, Formation.YULIN, morale=90, troops=3000)

    after = apply_damage(unit, 500)

    assert after.troops == 2500
    assert after.morale < unit.morale


def test_simulate_skirmish_changes_both_sides() -> None:
    attacker_officer, defender_officer = make_officers()
    attacker = make_unit(attacker_officer, Arms.CAVALRY, Formation.FENGSHI, morale=85, troops=4500)
    defender = make_unit(defender_officer, Arms.BOW, Formation.FANGYUAN, morale=78, troops=4300)
    ctx = BattleContext(terrain=Terrain.PLAIN, is_siege_target=False, random_factor=1.0)

    result = simulate_skirmish(attacker, defender, ctx)

    assert result.attacker_damage > 0
    assert result.defender_damage > 0
    assert result.attacker_after.troops < attacker.troops
    assert result.defender_after.troops < defender.troops


def test_tactic_success_rate_clamp() -> None:
    assert tactic_success_rate(10, 100) == 15
    assert tactic_success_rate(200, 10) == 90
    assert tactic_success_rate(80, 60) == 69.0
