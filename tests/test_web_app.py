from __future__ import annotations

from flask import Flask

from src.web_app import create_app


def test_index_normal_path() -> None:
    app: Flask = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert "三國戰役" in response.get_data(as_text=True)


def test_turn_progression_boundary_month_end() -> None:
    app: Flask = create_app(max_months=1, rounds_per_month=1, seed=7)
    client = app.test_client()

    response = client.post(
        "/turn",
        data={"affair": "farm", "formation": "yulin", "terrain": "plain"},
        follow_redirects=True,
    )

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "戰役已結束" in body


def test_turn_invalid_input_exception_path() -> None:
    app: Flask = create_app()
    client = app.test_client()

    response = client.post(
        "/turn",
        data={"affair": "bad", "formation": "yulin", "terrain": "plain"},
    )

    assert response.status_code == 400
    assert "invalid action" in response.get_data(as_text=True)
