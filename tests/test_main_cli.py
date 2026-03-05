from __future__ import annotations

from collections.abc import Iterator

from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.game import GameConfig
from src.main import run_campaign, run_demo, run_interactive


def test_run_demo_outputs_winner(capsys: CaptureFixture[str]) -> None:
    run_demo()
    out = capsys.readouterr().out
    assert "勝者:" in out
    assert "城市資源:" in out


def test_run_interactive_single_round(
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    values: Iterator[str] = iter(["farm", "yulin", "plain"])

    def fake_input(_: str) -> str:
        return next(values)

    monkeypatch.setattr("builtins.input", fake_input)

    run_interactive(GameConfig(max_rounds=1, random_seed=7))
    out = capsys.readouterr().out
    assert "對局結束" in out
    assert "戰報:" in out


def test_run_campaign_single_turn(
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    values: Iterator[str] = iter(["farm", "yulin", "plain"])

    def fake_input(_: str) -> str:
        return next(values)

    monkeypatch.setattr("builtins.input", fake_input)

    run_campaign(GameConfig(max_months=1, rounds_per_month=1, random_seed=7))
    out = capsys.readouterr().out
    assert "戰役結束" in out
    assert "勝者:" in out
