from __future__ import annotations

import pytest

from src.battle_engine import Formation, Terrain
from src.campaign import CampaignConfig, CampaignSession
from src.game import InternalAffairsAction


def test_campaign_turn_progression_normal_path() -> None:
    session = CampaignSession(
        config=CampaignConfig(max_months=2, rounds_per_month=3, random_seed=7)
    )

    result = session.play_turn(
        affair_action=InternalAffairsAction.FARM,
        player_formation=Formation.YULIN,
        terrain=Terrain.PLAIN,
        random_factor=1.0,
    )

    assert result.round_no == 1
    assert result.month == 1
    assert result.turn_in_month == 1
    assert session.state.round_no == 2


def test_campaign_month_rollover_boundary() -> None:
    session = CampaignSession(
        config=CampaignConfig(max_months=2, rounds_per_month=3, random_seed=7)
    )

    for _ in range(3):
        turn_result = session.play_turn(
            affair_action=InternalAffairsAction.RECRUIT,
            player_formation=Formation.FENGSHI,
            terrain=Terrain.PLAIN,
            random_factor=1.0,
        )

    assert turn_result.month == 1
    assert turn_result.turn_in_month == 3
    assert session.state.round_no == 4


def test_campaign_rejects_turn_after_finish_exception() -> None:
    session = CampaignSession(
        config=CampaignConfig(max_months=1, rounds_per_month=1, random_seed=7)
    )

    session.play_turn(
        affair_action=InternalAffairsAction.ORDER,
        player_formation=Formation.YULIN,
        terrain=Terrain.FOREST,
        random_factor=1.0,
    )

    assert session.is_finished()

    with pytest.raises(RuntimeError, match="campaign already finished"):
        session.play_turn(
            affair_action=InternalAffairsAction.ORDER,
            player_formation=Formation.YULIN,
            terrain=Terrain.FOREST,
            random_factor=1.0,
        )
