from __future__ import annotations

import pytest

from src.game import InternalAffairsAction, apply_internal_affairs, starter_state


@pytest.mark.parametrize(
    ("action", "expected_field"),
    [
        (InternalAffairsAction.RECRUIT, "reserve_troops"),
        (InternalAffairsAction.FARM, "food"),
        (InternalAffairsAction.FUND, "gold"),
        (InternalAffairsAction.ORDER, "public_order"),
    ],
)
def test_apply_internal_affairs_normal_path(
    action: InternalAffairsAction,
    expected_field: str,
) -> None:
    state = starter_state(seed=11)
    before = getattr(state.city, expected_field)

    apply_internal_affairs(state, action)

    after = getattr(state.city, expected_field)
    assert after > before


def test_apply_internal_affairs_order_boundary_clamped() -> None:
    state = starter_state(seed=11)
    state.city.public_order = 95

    apply_internal_affairs(state, InternalAffairsAction.ORDER)

    assert state.city.public_order == 100


def test_apply_internal_affairs_rejects_invalid_action() -> None:
    state = starter_state(seed=11)

    with pytest.raises(ValueError, match="invalid internal affairs action"):
        apply_internal_affairs(state, "bad_action")
