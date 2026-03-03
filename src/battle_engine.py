from __future__ import annotations

import random
from dataclasses import dataclass, replace
from enum import Enum


class Arms(str, Enum):
    SPEAR = "spear"
    CAVALRY = "cavalry"
    BOW = "bow"
    HALBERD = "halberd"
    SIEGE = "siege"


class Terrain(str, Enum):
    PLAIN = "plain"
    MOUNTAIN = "mountain"
    FOREST = "forest"


class Formation(str, Enum):
    YULIN = "yulin"  # 魚鱗
    FENGSHI = "fengshi"  # 鋒矢
    FANGYUAN = "fangyuan"  # 方圓
    HEYI = "heyi"  # 鶴翼
    CHANGSHE = "changshe"  # 長蛇


@dataclass(frozen=True)
class Officer:
    name: str
    leadership: int
    might: int
    intelligence: int


@dataclass(frozen=True)
class Unit:
    officer: Officer
    troops: int
    arms: Arms
    formation: Formation
    morale: int  # 0~100


@dataclass(frozen=True)
class BattleContext:
    terrain: Terrain
    attacking_city: bool = False
    is_siege_target: bool = False
    random_factor: float | None = None


@dataclass(frozen=True)
class SkirmishResult:
    attacker_after: Unit
    defender_after: Unit
    attacker_damage: int
    defender_damage: int


ARM_COUNTER = {
    (Arms.SPEAR, Arms.CAVALRY): 1.2,
    (Arms.CAVALRY, Arms.BOW): 1.2,
    (Arms.BOW, Arms.SPEAR): 1.2,
}

FORMATION_ATTACK_MOD = {
    Formation.YULIN: 1.05,
    Formation.FENGSHI: 1.15,
    Formation.FANGYUAN: 0.92,
    Formation.HEYI: 1.03,
    Formation.CHANGSHE: 1.0,
}

FORMATION_COUNTER = {
    (Formation.FENGSHI, Formation.FANGYUAN): 1.12,
    (Formation.FANGYUAN, Formation.HEYI): 1.12,
    (Formation.HEYI, Formation.YULIN): 1.12,
    (Formation.YULIN, Formation.CHANGSHE): 1.12,
    (Formation.CHANGSHE, Formation.FENGSHI): 1.12,
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def arms_multiplier(attacker: Arms, defender: Arms, is_siege_target: bool) -> float:
    if attacker == Arms.SIEGE:
        return 1.5 if is_siege_target else 0.75

    direct = ARM_COUNTER.get((attacker, defender))
    if direct:
        return direct

    reverse = ARM_COUNTER.get((defender, attacker))
    if reverse:
        return 0.85

    return 1.0


def formation_multiplier(attacker: Formation, defender: Formation) -> float:
    direct = FORMATION_COUNTER.get((attacker, defender))
    if direct:
        return direct

    reverse = FORMATION_COUNTER.get((defender, attacker))
    if reverse:
        return 0.9

    return 1.0


def terrain_multiplier(arms: Arms, terrain: Terrain) -> float:
    if terrain == Terrain.PLAIN:
        return 1.0
    if terrain == Terrain.MOUNTAIN:
        return 0.75 if arms == Arms.CAVALRY else 0.85
    if terrain == Terrain.FOREST:
        return 1.1 if arms == Arms.BOW else 0.9
    return 1.0


def morale_multiplier(morale: int) -> float:
    # 0~100 => 0.7~1.3
    morale = int(clamp(morale, 0, 100))
    return 0.7 + (morale / 100.0) * 0.6


def attack_base(leadership: int, might: int) -> float:
    return 25 + leadership * 0.5 + might * 0.5


def calculate_damage(attacker: Unit, defender: Unit, context: BattleContext) -> int:
    base = attack_base(attacker.officer.leadership, attacker.officer.might)
    troop_factor = max(attacker.troops, 1) / 1000.0
    arm_mod = arms_multiplier(attacker.arms, defender.arms, context.is_siege_target)
    formation_attack_mod = FORMATION_ATTACK_MOD[attacker.formation]
    formation_counter_mod = formation_multiplier(attacker.formation, defender.formation)
    terrain_mod = terrain_multiplier(attacker.arms, context.terrain)
    morale_mod = morale_multiplier(attacker.morale)

    if context.random_factor is None:
        rand = random.uniform(0.9, 1.1)
    else:
        rand = clamp(context.random_factor, 0.9, 1.1)

    damage = (
        base
        * troop_factor
        * arm_mod
        * formation_attack_mod
        * formation_counter_mod
        * terrain_mod
        * morale_mod
        * rand
    )
    return max(int(round(damage)), 1)


def apply_damage(unit: Unit, damage: int) -> Unit:
    remaining = max(unit.troops - max(damage, 0), 0)
    morale_drop = min(30, max(1, damage // 250))
    next_morale = int(clamp(unit.morale - morale_drop, 0, 100))
    return replace(unit, troops=remaining, morale=next_morale)


def simulate_skirmish(attacker: Unit, defender: Unit, context: BattleContext) -> SkirmishResult:
    attacker_damage = calculate_damage(attacker, defender, context)
    defender_damage = calculate_damage(defender, attacker, context)

    defender_after = apply_damage(defender, attacker_damage)
    attacker_after = apply_damage(attacker, defender_damage)

    return SkirmishResult(
        attacker_after=attacker_after,
        defender_after=defender_after,
        attacker_damage=attacker_damage,
        defender_damage=defender_damage,
    )


def tactic_success_rate(caster_int: int, target_int: int) -> float:
    rate = 55 + (caster_int - target_int) * 0.7
    return clamp(rate, 15, 90)
