"""Session helper for Scanopy API."""

import os
from typing import Any

import httpx


def get_session_id() -> str | None:
    """Return a session_id using env vars or optional login.

    Order:
    1) SCANOPY_SESSION_ID
    2) SCANOPY_LOGIN_URL + SCANOPY_LOGIN_USER + SCANOPY_LOGIN_PASSWORD
    """
    session_id = os.getenv("SCANOPY_SESSION_ID")
    if session_id:
        return session_id

    login_url = os.getenv("SCANOPY_LOGIN_URL")
    user = os.getenv("SCANOPY_LOGIN_USER")
    password = os.getenv("SCANOPY_LOGIN_PASSWORD")
    if not (login_url and user and password):
        return None

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(login_url, json={"email": user, "password": password})
        resp.raise_for_status()
        data: Any = None
        if resp.headers.get("content-type", "").startswith("application/json"):
            data = resp.json()
        if isinstance(data, dict) and data.get("session_id"):
            return data["session_id"]
        return resp.cookies.get("session_id")
