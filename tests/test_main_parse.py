from __future__ import annotations

import pytest

from src.battle_engine import Formation, Terrain
from src.game import InternalAffairsAction
from src.main import parse_affair, parse_formation, parse_terrain


def test_parse_helpers_normal_path() -> None:
    assert parse_formation("yulin") is Formation.YULIN
    assert parse_terrain("forest") is Terrain.FOREST
    assert parse_affair("farm") is InternalAffairsAction.FARM


def test_parse_helpers_exception_path() -> None:
    with pytest.raises(ValueError):
        parse_formation("wrong")

    with pytest.raises(ValueError):
        parse_terrain("bad")

    with pytest.raises(ValueError):
        parse_affair("invalid")
