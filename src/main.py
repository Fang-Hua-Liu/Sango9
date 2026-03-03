from __future__ import annotations

import argparse

from src.battle_engine import Formation, Terrain
from src.campaign import CampaignSession, config_from_game
from src.game import (
    GameConfig,
    InternalAffairsAction,
    apply_internal_affairs,
    is_finished,
    run_round,
    starter_state,
    winner,
)
from src.gui import run_gui


def parse_formation(raw: str) -> Formation:
    return Formation(raw)


def parse_terrain(raw: str) -> Terrain:
    return Terrain(raw)


def parse_affair(raw: str) -> InternalAffairsAction:
    return InternalAffairsAction(raw)


def run_demo() -> None:
    state = starter_state(seed=7)
    apply_internal_affairs(state, InternalAffairsAction.FARM)
    for formation, terrain in [
        (Formation.FENGSHI, Terrain.PLAIN),
        (Formation.YULIN, Terrain.FOREST),
        (Formation.FANGYUAN, Terrain.MOUNTAIN),
    ]:
        run_round(state, formation, terrain, random_factor=1.0)
    for line in state.log:
        print(line)
    print(
        f"城市資源: 金={state.city.gold} 糧={state.city.food} "
        f"預備兵={state.city.reserve_troops} 治安={state.city.public_order}"
    )
    print(f"勝者: {winner(state)}")


def run_interactive(config: GameConfig) -> None:
    state = starter_state(seed=config.random_seed)
    print("=== 三國戰鬥手動測試版 ===")
    print("可輸入陣型: yulin/fengshi/fangyuan/heyi/changshe")
    print("可輸入地形: plain/mountain/forest")
    print("可輸入內政: recruit/farm/fund/order")

    while not is_finished(state, config.max_rounds):
        print(
            f"\nRound {state.round_no} | 我方兵力={state.player.troops} 士氣={state.player.morale} "
            f"vs 敵方兵力={state.enemy.troops} 士氣={state.enemy.morale}"
        )
        affair_raw = input("先做內政(可留空跳過) > ").strip().lower()
        if affair_raw:
            try:
                affair = parse_affair(affair_raw)
                print(apply_internal_affairs(state, affair))
            except ValueError:
                print("內政輸入錯誤，已跳過。")

        formation_raw = input("選擇陣型 > ").strip().lower()
        terrain_raw = input("選擇地形 > ").strip().lower()

        try:
            formation = parse_formation(formation_raw)
            terrain = parse_terrain(terrain_raw)
        except ValueError:
            print("輸入錯誤，請重試。")
            continue

        run_round(state, formation, terrain)
        print(state.log[-1])

    print("\n=== 對局結束 ===")
    print(
        f"城市資源: 金={state.city.gold} 糧={state.city.food} "
        f"預備兵={state.city.reserve_troops} 治安={state.city.public_order}"
    )
    print(f"勝者: {winner(state)}")
    print("戰報:")
    for line in state.log:
        print(f"- {line}")


def run_campaign(config: GameConfig) -> None:
    session = CampaignSession(config=config_from_game(config))
    print("=== 三國戰役模式 ===")
    print(f"月份上限: {config.max_months} | 每月旬數: {config.rounds_per_month}")
    print("每回合流程: 內政 -> 戰鬥")

    while not session.is_finished():
        current_round = session.state.round_no
        month = ((current_round - 1) // config.rounds_per_month) + 1
        turn_in_month = ((current_round - 1) % config.rounds_per_month) + 1

        print(
            f"\nMonth {month}, Turn {turn_in_month} | "
            f"我方兵力={session.state.player.troops} vs 敵方兵力={session.state.enemy.troops}"
        )

        affair = parse_affair(input("內政(recruit/farm/fund/order) > ").strip().lower())
        formation = parse_formation(
            input("陣型(yulin/fengshi/fangyuan/heyi/changshe) > ").strip().lower()
        )
        terrain = parse_terrain(input("地形(plain/mountain/forest) > ").strip().lower())

        turn_result = session.play_turn(
            affair_action=affair,
            player_formation=formation,
            terrain=terrain,
        )
        print(turn_result.affair_message)
        print(turn_result.battle_message)

    print("\n=== 戰役結束 ===")
    print(f"勝者: {session.champion()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="戰爭核心手動測試程式")
    parser.add_argument(
        "--mode", choices=["demo", "interactive", "gui", "campaign"], default="demo"
    )
    parser.add_argument("--max-rounds", type=int, default=12)
    parser.add_argument("--max-months", type=int, default=8)
    parser.add_argument("--rounds-per-month", type=int, default=3)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    config = GameConfig(
        max_rounds=args.max_rounds,
        max_months=args.max_months,
        rounds_per_month=args.rounds_per_month,
        random_seed=args.seed,
    )

    if args.mode == "demo":
        run_demo()
        return

    if args.mode == "interactive":
        run_interactive(config)
        return

    if args.mode == "campaign":
        run_campaign(config)
        return

    run_gui(config)


if __name__ == "__main__":
    main()
