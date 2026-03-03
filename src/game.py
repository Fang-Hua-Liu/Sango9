from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from src.battle_engine import (
    Arms,
    BattleContext,
    Formation,
    Officer,
    Terrain,
    Unit,
    simulate_skirmish,
)

STARTER_TROOPS = 5000
STARTER_MORALE_PLAYER = 85
STARTER_MORALE_ENEMY = 82
STARTER_GOLD = 12000
STARTER_FOOD = 18000
STARTER_RESERVE_TROOPS = 2500
STARTER_PUBLIC_ORDER = 70
RECRUIT_GAIN = 600
FARM_GAIN = 1800
FUND_GAIN = 1200
ORDER_GAIN = 15
MAX_PUBLIC_ORDER = 100


class InternalAffairsAction(str, Enum):
    RECRUIT = "recruit"
    FARM = "farm"
    FUND = "fund"
    ORDER = "order"


@dataclass(frozen=True)
class GameConfig:
    max_rounds: int = 12
    random_seed: int | None = None


@dataclass
class CityState:
    gold: int = STARTER_GOLD
    food: int = STARTER_FOOD
    reserve_troops: int = STARTER_RESERVE_TROOPS
    public_order: int = STARTER_PUBLIC_ORDER


@dataclass
class GameState:
    player: Unit
    enemy: Unit
    round_no: int
    log: list[str]
    city: CityState = field(default_factory=CityState)


def starter_state(seed: int | None = None) -> GameState:
    if seed is not None:
        random.seed(seed)

    player_officer = Officer(name="趙雲", leadership=92, might=94, intelligence=76)
    enemy_officer = Officer(name="張遼", leadership=90, might=89, intelligence=80)

    player = Unit(
        player_officer,
        troops=STARTER_TROOPS,
        arms=Arms.CAVALRY,
        formation=Formation.YULIN,
        morale=STARTER_MORALE_PLAYER,
    )
    enemy = Unit(
        enemy_officer,
        troops=STARTER_TROOPS,
        arms=Arms.SPEAR,
        formation=Formation.FANGYUAN,
        morale=STARTER_MORALE_ENEMY,
    )

    return GameState(player=player, enemy=enemy, round_no=1, log=[])


def pick_enemy_formation() -> Formation:
    return random.choice(list(Formation))


def apply_internal_affairs(state: GameState, action: InternalAffairsAction | str) -> str:
    try:
        valid_action = InternalAffairsAction(action)
    except ValueError as exc:
        raise ValueError("invalid internal affairs action") from exc

    if valid_action is InternalAffairsAction.RECRUIT:
        state.city.reserve_troops += RECRUIT_GAIN
        return f"內政: 徵兵 +{RECRUIT_GAIN}"

    if valid_action is InternalAffairsAction.FARM:
        state.city.food += FARM_GAIN
        return f"內政: 屯糧 +{FARM_GAIN}"

    if valid_action is InternalAffairsAction.FUND:
        state.city.gold += FUND_GAIN
        return f"內政: 募資 +{FUND_GAIN}"

    state.city.public_order = min(state.city.public_order + ORDER_GAIN, MAX_PUBLIC_ORDER)
    return f"內政: 安民 +{ORDER_GAIN}"


def run_round(
    state: GameState,
    player_formation: Formation,
    terrain: Terrain,
    random_factor: float | None = None,
) -> None:
    state.player = Unit(
        officer=state.player.officer,
        troops=state.player.troops,
        arms=state.player.arms,
        formation=player_formation,
        morale=state.player.morale,
    )
    enemy_formation = pick_enemy_formation()
    state.enemy = Unit(
        officer=state.enemy.officer,
        troops=state.enemy.troops,
        arms=state.enemy.arms,
        formation=enemy_formation,
        morale=state.enemy.morale,
    )

    context = BattleContext(terrain=terrain, random_factor=random_factor)
    result = simulate_skirmish(state.player, state.enemy, context)
    state.player = result.attacker_after
    state.enemy = result.defender_after

    state.log.append(
        f"R{state.round_no} {terrain.value} | "
        f"我方[{player_formation.value}]傷害={result.attacker_damage}, "
        f"敵方[{enemy_formation.value}]傷害={result.defender_damage} | "
        f"兵力 我:{state.player.troops} 敵:{state.enemy.troops}"
    )
    state.round_no += 1


def is_finished(state: GameState, max_rounds: int) -> bool:
    return state.player.troops <= 0 or state.enemy.troops <= 0 or state.round_no > max_rounds


def winner(state: GameState) -> str:
    if state.player.troops <= 0 and state.enemy.troops <= 0:
        return "draw"
    if state.enemy.troops <= 0:
        return "player"
    if state.player.troops <= 0:
        return "enemy"
    if state.player.troops > state.enemy.troops:
        return "player"
    if state.player.troops < state.enemy.troops:
        return "enemy"
    return "draw"
