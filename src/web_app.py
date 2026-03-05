from __future__ import annotations

from dataclasses import dataclass
from secrets import token_hex
from typing import Final

from flask import Flask, make_response, redirect, render_template_string, request, url_for
from flask.typing import ResponseReturnValue

from src.battle_engine import Formation, Terrain
from src.campaign import CampaignConfig, CampaignSession
from src.game import InternalAffairsAction

SESSION_COOKIE_NAME: Final[str] = "sango9_sid"
DEFAULT_MAX_MONTHS: Final[int] = 8
DEFAULT_ROUNDS_PER_MONTH: Final[int] = 3

_TEMPLATE: Final[str] = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>三國戰役 Web 測試</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #111827; color: #e5e7eb; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 16px; }
    .card { background: #1f2937; border-radius: 10px; padding: 12px; margin-bottom: 12px; }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    button { background: #2563eb; color: white; border: none; border-radius: 6px; padding: 8px 12px; }
    select { width: 100%; padding: 8px; border-radius: 6px; }
    .warn { color: #fca5a5; }
    .ok { color: #86efac; }
    .unit { font-size: 20px; margin-right: 6px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>⚔️ 三國戰役（Web 版）</h2>
    <div class="card">
      <div>Month {{ month }}, Turn {{ turn_in_month }}</div>
      <div><span class="unit">🐉</span>我方兵力: {{ player_troops }} / 士氣: {{ player_morale }}</div>
      <div><span class="unit">🐯</span>敵方兵力: {{ enemy_troops }} / 士氣: {{ enemy_morale }}</div>
      <div>城市: 金 {{ gold }}, 糧 {{ food }}, 預備兵 {{ reserve }}, 治安 {{ public_order }}</div>
      {% if ended %}<div class="warn">戰役已結束，勝者: {{ champion }}</div>{% endif %}
      {% if error %}<div class="warn">{{ error }}</div>{% endif %}
      {% if last_affair %}<div class="ok">{{ last_affair }}</div>{% endif %}
      {% if last_battle %}<div>{{ last_battle }}</div>{% endif %}
    </div>

    <div class="card">
      <form method="post" action="{{ url_for('play_turn') }}">
        <div class="grid">
          <div>
            <label>內政</label>
            <select name="affair">
              {% for item in affairs %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
            </select>
          </div>
          <div>
            <label>陣型</label>
            <select name="formation">
              {% for item in formations %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
            </select>
          </div>
          <div>
            <label>地形</label>
            <select name="terrain">
              {% for item in terrains %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
            </select>
          </div>
        </div>
        <div style="margin-top:10px;">
          <button type="submit" {% if ended %}disabled{% endif %}>執行本回合</button>
        </div>
      </form>
      <form method="post" action="{{ url_for('reset_game') }}" style="margin-top:8px;">
        <button type="submit">重開新局</button>
      </form>
    </div>

    <div class="card">
      <h4>戰報</h4>
      <ul>
      {% for line in logs %}
        <li>{{ line }}</li>
      {% endfor %}
      </ul>
    </div>
  </div>
</body>
</html>
"""


@dataclass
class WebContext:
    error: str = ""
    last_affair: str = ""
    last_battle: str = ""


class SessionStore:
    def __init__(self, config: CampaignConfig) -> None:
        self.config = config
        self.sessions: dict[str, CampaignSession] = {}

    def get_or_create(self, session_id: str | None) -> tuple[str, CampaignSession, bool]:
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id], False

        new_id = token_hex(16)
        session = CampaignSession(config=self.config)
        self.sessions[new_id] = session
        return new_id, session, True

    def reset(self, session_id: str | None) -> tuple[str, CampaignSession]:
        if session_id and session_id in self.sessions:
            self.sessions[session_id] = CampaignSession(config=self.config)
            return session_id, self.sessions[session_id]

        new_id, session, _ = self.get_or_create(None)
        return new_id, session


def _state_view(session: CampaignSession, extra: WebContext) -> dict[str, object]:
    round_no = session.state.round_no
    month = ((round_no - 1) // session.config.rounds_per_month) + 1
    turn_in_month = ((round_no - 1) % session.config.rounds_per_month) + 1
    ended = session.is_finished()

    return {
        "month": month,
        "turn_in_month": turn_in_month,
        "player_troops": session.state.player.troops,
        "enemy_troops": session.state.enemy.troops,
        "player_morale": session.state.player.morale,
        "enemy_morale": session.state.enemy.morale,
        "gold": session.state.city.gold,
        "food": session.state.city.food,
        "reserve": session.state.city.reserve_troops,
        "public_order": session.state.city.public_order,
        "logs": session.state.log[-12:],
        "ended": ended,
        "champion": session.champion() if ended else "",
        "error": extra.error,
        "last_affair": extra.last_affair,
        "last_battle": extra.last_battle,
        "affairs": [x.value for x in InternalAffairsAction],
        "formations": [x.value for x in Formation],
        "terrains": [x.value for x in Terrain],
    }


def create_app(
    max_months: int = DEFAULT_MAX_MONTHS,
    rounds_per_month: int = DEFAULT_ROUNDS_PER_MONTH,
    seed: int | None = None,
) -> Flask:
    app = Flask(__name__)
    store = SessionStore(
        CampaignConfig(max_months=max_months, rounds_per_month=rounds_per_month, random_seed=seed)
    )

    @app.get("/")
    def index() -> ResponseReturnValue:
        sid = request.cookies.get(SESSION_COOKIE_NAME)
        sid, session, created = store.get_or_create(sid)
        html = render_template_string(_TEMPLATE, **_state_view(session, WebContext()))
        response = make_response(html)
        if created:
            response.set_cookie(SESSION_COOKIE_NAME, sid)
        return response

    @app.post("/turn")
    def play_turn() -> ResponseReturnValue:
        sid = request.cookies.get(SESSION_COOKIE_NAME)
        sid, session, created = store.get_or_create(sid)

        raw_affair = request.form.get("affair", "")
        raw_formation = request.form.get("formation", "")
        raw_terrain = request.form.get("terrain", "")

        try:
            affair = InternalAffairsAction(raw_affair)
            formation = Formation(raw_formation)
            terrain = Terrain(raw_terrain)
        except ValueError:
            html = render_template_string(
                _TEMPLATE,
                **_state_view(session, WebContext(error="invalid action/formation/terrain")),
            )
            response = make_response(html, 400)
            if created:
                response.set_cookie(SESSION_COOKIE_NAME, sid)
            return response

        if session.is_finished():
            return redirect(url_for("index"))

        turn_result = session.play_turn(
            affair_action=affair,
            player_formation=formation,
            terrain=terrain,
        )
        html = render_template_string(
            _TEMPLATE,
            **_state_view(
                session,
                WebContext(
                    last_affair=turn_result.affair_message,
                    last_battle=turn_result.battle_message,
                ),
            ),
        )
        response = make_response(html)
        if created:
            response.set_cookie(SESSION_COOKIE_NAME, sid)
        return response

    @app.post("/reset")
    def reset_game() -> ResponseReturnValue:
        sid = request.cookies.get(SESSION_COOKIE_NAME)
        sid, _ = store.reset(sid)
        response = redirect(url_for("index"))
        response.set_cookie(SESSION_COOKIE_NAME, sid)
        return response

    return app
