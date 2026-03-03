from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.battle_engine import Formation, Terrain
from src.game import (
    GameConfig,
    GameState,
    InternalAffairsAction,
    apply_internal_affairs,
    is_finished,
    run_round,
    starter_state,
    winner,
)

WINDOW_WIDTH = 920
WINDOW_HEIGHT = 640
LOG_KEEP_LINES = 16


class GameGUI:
    def __init__(self, root: tk.Tk, config: GameConfig) -> None:
        self.root = root
        self.config = config
        self.state: GameState = starter_state(seed=config.random_seed)

        self.root.title("三國戰鬥測試版 GUI")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.formation_var = tk.StringVar(value=Formation.YULIN.value)
        self.terrain_var = tk.StringVar(value=Terrain.PLAIN.value)
        self.affair_var = tk.StringVar(value=InternalAffairsAction.RECRUIT.value)

        self.status_var = tk.StringVar(value="準備開始")
        self.city_var = tk.StringVar()
        self.battle_var = tk.StringVar()
        self._refresh_state_labels()

        self._build_layout()

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill=tk.X)

        ttk.Label(top, text="陣型").pack(side=tk.LEFT)
        ttk.Combobox(
            top,
            textvariable=self.formation_var,
            state="readonly",
            values=[f.value for f in Formation],
            width=12,
        ).pack(side=tk.LEFT, padx=8)

        ttk.Label(top, text="地形").pack(side=tk.LEFT)
        ttk.Combobox(
            top,
            textvariable=self.terrain_var,
            state="readonly",
            values=[t.value for t in Terrain],
            width=12,
        ).pack(side=tk.LEFT, padx=8)

        ttk.Button(top, text="進行回合", command=self.on_next_round).pack(side=tk.LEFT, padx=8)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        affair = ttk.Frame(self.root, padding=12)
        affair.pack(fill=tk.X)

        ttk.Label(affair, text="內政").pack(side=tk.LEFT)
        ttk.Combobox(
            affair,
            textvariable=self.affair_var,
            state="readonly",
            values=[a.value for a in InternalAffairsAction],
            width=12,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(
            affair,
            text="執行內政",
            command=self.on_internal_affairs,
        ).pack(side=tk.LEFT, padx=8)

        info = ttk.Frame(self.root, padding=12)
        info.pack(fill=tk.X)
        ttk.Label(info, textvariable=self.battle_var).pack(anchor="w")
        ttk.Label(info, textvariable=self.city_var).pack(anchor="w", pady=4)
        ttk.Label(info, textvariable=self.status_var, foreground="#1d4ed8").pack(anchor="w", pady=4)

        self.log_widget = tk.Text(self.root, height=22, wrap=tk.WORD)
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.log_widget.insert(tk.END, "歡迎進入手動測試 GUI\n")
        self.log_widget.configure(state=tk.DISABLED)

    def _append_log(self, line: str) -> None:
        self.log_widget.configure(state=tk.NORMAL)
        self.log_widget.insert(tk.END, f"{line}\n")
        lines = self.log_widget.get("1.0", tk.END).splitlines()
        if len(lines) > LOG_KEEP_LINES:
            keep = "\n".join(lines[-LOG_KEEP_LINES:]) + "\n"
            self.log_widget.delete("1.0", tk.END)
            self.log_widget.insert("1.0", keep)
        self.log_widget.configure(state=tk.DISABLED)
        self.log_widget.see(tk.END)

    def _refresh_state_labels(self) -> None:
        self.battle_var.set(
            f"Round {self.state.round_no} | "
            f"我方兵力={self.state.player.troops} 士氣={self.state.player.morale} | "
            f"敵方兵力={self.state.enemy.troops} 士氣={self.state.enemy.morale}"
        )
        self.city_var.set(
            f"城市資源 | 金={self.state.city.gold} 糧={self.state.city.food} "
            f"預備兵={self.state.city.reserve_troops} 治安={self.state.city.public_order}"
        )

    def on_internal_affairs(self) -> None:
        action = InternalAffairsAction(self.affair_var.get())
        message = apply_internal_affairs(self.state, action)
        self.status_var.set(message)
        self._append_log(message)
        self._refresh_state_labels()

    def on_next_round(self) -> None:
        if is_finished(self.state, self.config.max_rounds):
            self.status_var.set(f"對局已結束，勝者: {winner(self.state)}")
            return

        formation = Formation(self.formation_var.get())
        terrain = Terrain(self.terrain_var.get())
        run_round(self.state, formation, terrain)
        self._append_log(self.state.log[-1])

        if is_finished(self.state, self.config.max_rounds):
            self.status_var.set(f"對局結束，勝者: {winner(self.state)}")
        else:
            self.status_var.set("回合完成")

        self._refresh_state_labels()


def run_gui(config: GameConfig) -> None:
    root = tk.Tk()
    GameGUI(root=root, config=config)
    root.mainloop()
