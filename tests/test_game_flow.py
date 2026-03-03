from __future__ import annotations

from dataclasses import replace

from src.battle_engine import Formation, Terrain
from src.game import is_finished, run_round, starter_state, winner


def test_run_round_advances_and_logs() -> None:
    state = starter_state(seed=1)
    run_round(state, Formation.FENGSHI, Terrain.PLAIN, random_factor=1.0)

    assert state.round_no == 2
    assert len(state.log) == 1
    assert "R1" in state.log[0]


def test_finished_by_round_limit() -> None:
    state = starter_state(seed=1)
    assert not is_finished(state, max_rounds=1)

    run_round(state, Formation.YULIN, Terrain.FOREST, random_factor=1.0)

    assert is_finished(state, max_rounds=1)


def test_winner_resolution() -> None:
    state = starter_state(seed=1)
    state.player = replace(state.player, troops=100)
    state.enemy = replace(state.enemy, troops=0)

    assert winner(state) == "player"
