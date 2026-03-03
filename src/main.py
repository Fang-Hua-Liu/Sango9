from __future__ import annotations

import argparse

from src.battle_engine import Formation, Terrain
from src.game import GameConfig, is_finished, run_round, starter_state, winner


def parse_formation(raw: str) -> Formation:
    return Formation(raw)


def parse_terrain(raw: str) -> Terrain:
    return Terrain(raw)


def run_demo() -> None:
    state = starter_state(seed=7)
    for formation, terrain in [
        (Formation.FENGSHI, Terrain.PLAIN),
        (Formation.YULIN, Terrain.FOREST),
        (Formation.FANGYUAN, Terrain.MOUNTAIN),
    ]:
        run_round(state, formation, terrain, random_factor=1.0)
    for line in state.log:
        print(line)
    print(f"勝者: {winner(state)}")


def run_interactive(config: GameConfig) -> None:
    state = starter_state(seed=config.random_seed)
    print("=== 三國戰鬥手動測試版 ===")
    print("可輸入陣型: yulin/fengshi/fangyuan/heyi/changshe")
    print("可輸入地形: plain/mountain/forest")

    while not is_finished(state, config.max_rounds):
        print(
            f"\nRound {state.round_no} | 我方兵力={state.player.troops} 士氣={state.player.morale} "
            f"vs 敵方兵力={state.enemy.troops} 士氣={state.enemy.morale}"
        )
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
    print(f"勝者: {winner(state)}")
    print("戰報:")
    for line in state.log:
        print(f"- {line}")


def main() -> None:
    parser = argparse.ArgumentParser(description="戰爭核心手動測試程式")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo")
    parser.add_argument("--max-rounds", type=int, default=12)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()
        return

    run_interactive(GameConfig(max_rounds=args.max_rounds, random_seed=args.seed))


if __name__ == "__main__":
    main()
