from __future__ import annotations

from dataclasses import dataclass

from src.battle_engine import Formation, Terrain
from src.game import (
    GameConfig,
    GameState,
    InternalAffairsAction,
    apply_internal_affairs,
    run_round,
    starter_state,
    winner,
)


@dataclass(frozen=True)
class CampaignConfig:
    max_months: int = 8
    rounds_per_month: int = 3
    random_seed: int | None = None


@dataclass(frozen=True)
class TurnResult:
    month: int
    turn_in_month: int
    round_no: int
    affair_message: str
    battle_message: str


class CampaignSession:
    def __init__(self, config: CampaignConfig) -> None:
        self.config = config
        self.state: GameState = starter_state(seed=config.random_seed)

    def _round_limit(self) -> int:
        return self.config.max_months * self.config.rounds_per_month

    def is_finished(self) -> bool:
        return (
            self.state.player.troops <= 0
            or self.state.enemy.troops <= 0
            or self.state.round_no > self._round_limit()
        )

    def champion(self) -> str:
        return winner(self.state)

    def play_turn(
        self,
        affair_action: InternalAffairsAction,
        player_formation: Formation,
        terrain: Terrain,
        random_factor: float | None = None,
    ) -> TurnResult:
        if self.is_finished():
            raise RuntimeError("campaign already finished")

        month = ((self.state.round_no - 1) // self.config.rounds_per_month) + 1
        turn_in_month = ((self.state.round_no - 1) % self.config.rounds_per_month) + 1

        affair_message = apply_internal_affairs(self.state, affair_action)
        run_round(
            self.state,
            player_formation=player_formation,
            terrain=terrain,
            random_factor=random_factor,
        )
        battle_message = self.state.log[-1]

        return TurnResult(
            month=month,
            turn_in_month=turn_in_month,
            round_no=self.state.round_no - 1,
            affair_message=affair_message,
            battle_message=battle_message,
        )


def config_from_game(config: GameConfig) -> CampaignConfig:
    return CampaignConfig(
        max_months=config.max_months,
        rounds_per_month=config.rounds_per_month,
        random_seed=config.random_seed,
    )
