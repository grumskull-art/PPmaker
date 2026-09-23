from powerpoint_app.office import powerpoint_available


def test_missing_powerpoint_is_reported(monkeypatch):
    monkeypatch.setattr("powerpoint_app.office.com.platform.system", lambda: "Linux")
    available, reason = powerpoint_available()
    assert not available and "Windows" in reason
