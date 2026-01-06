from scanopy_mcp import session


def test_session_env_preferred(monkeypatch):
    monkeypatch.setenv("SCANOPY_SESSION_ID", "abc")
    assert session.get_session_id() == "abc"


def test_session_missing_returns_none(monkeypatch):
    monkeypatch.delenv("SCANOPY_SESSION_ID", raising=False)
    monkeypatch.delenv("SCANOPY_LOGIN_URL", raising=False)
    monkeypatch.delenv("SCANOPY_LOGIN_USER", raising=False)
    monkeypatch.delenv("SCANOPY_LOGIN_PASSWORD", raising=False)
    assert session.get_session_id() is None
