"""Tests for acrf_config_guard.cli"""
import json
import tempfile
from pathlib import Path

import pytest
from acrf_config_guard.cli import main

SECRET = "test-secret-key-do-not-use-in-production"


@pytest.fixture
def temp_config():
    config = {"mcpServers": {"TicketApp": {"tools": ["book_ticket"]}}}
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)  # noqa: SIM115
    json.dump(config, tmp)
    tmp.close()
    yield Path(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def secret_env(monkeypatch):
    monkeypatch.setenv("ACRF_CONFIG_SECRET", SECRET)


def test_sign_command_succeeds(temp_config, secret_env, capsys):
    rc = main(["sign", str(temp_config)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Signed" in captured.out
    assert "sha256:" in captured.out


def test_verify_command_succeeds_after_sign(temp_config, secret_env, capsys):
    main(["sign", str(temp_config)])
    rc = main(["verify", str(temp_config)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "OK" in captured.out


def test_verify_command_fails_when_unsigned(temp_config, secret_env, capsys):
    rc = main(["verify", str(temp_config)])
    assert rc == 1


def test_verify_command_fails_when_tampered(temp_config, secret_env, capsys):
    main(["sign", str(temp_config)])
    data = json.loads(temp_config.read_text())
    data["mcpServers"]["TicketApp"]["tools"].append("refund_all")
    temp_config.write_text(json.dumps(data))
    rc = main(["verify", str(temp_config)])
    assert rc == 1


def test_missing_secret_env_var_exits_2(temp_config, monkeypatch):
    monkeypatch.delenv("ACRF_CONFIG_SECRET", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        main(["verify", str(temp_config)])
    assert exc_info.value.code == 2
