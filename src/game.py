from __future__ import annotations

from dataclasses import dataclass
import random

from src.battle_engine import (
    Arms,
    BattleContext,
    Formation,
    Officer,
    Terrain,
    Unit,
    simulate_skirmish,
)


@dataclass(frozen=True)
class GameConfig:
    max_rounds: int = 12
    random_seed: int | None = None


@dataclass
class GameState:
    player: Unit
    enemy: Unit
    round_no: int
    log: list[str]


def starter_state(seed: int | None = None) -> GameState:
    if seed is not None:
        random.seed(seed)

    player_officer = Officer(name="趙雲", leadership=92, might=94, intelligence=76)
    enemy_officer = Officer(name="張遼", leadership=90, might=89, intelligence=80)

    player = Unit(player_officer, troops=5000, arms=Arms.CAVALRY, formation=Formation.YULIN, morale=85)
    enemy = Unit(enemy_officer, troops=5000, arms=Arms.SPEAR, formation=Formation.FANGYUAN, morale=82)

    return GameState(player=player, enemy=enemy, round_no=1, log=[])


def pick_enemy_formation() -> Formation:
    return random.choice(list(Formation))


def run_round(state: GameState, player_formation: Formation, terrain: Terrain, random_factor: float | None = None) -> None:
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
        f"R{state.round_no} {terrain.value} | 我方[{player_formation.value}]傷害={result.attacker_damage}, "
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
