"""Tests for acrf_config_guard.core"""
import json
import tempfile
from pathlib import Path

import pytest
from acrf_config_guard import (
    ConfigIntegrityError,
    load_safe,
    sign_config,
    verify_config,
)

SECRET = "test-secret-key-do-not-use-in-production"


@pytest.fixture
def temp_config():
    """Create a temporary config file for each test."""
    config = {
        "mcpServers": {
            "TicketApp": {
                "command": "python",
                "tools": ["book_ticket", "cancel_ticket"],
                "autoApprove": []
            }
        }
    }
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)  # noqa: SIM115
    json.dump(config, tmp)
    tmp.close()
    yield Path(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)


def test_sign_adds_integrity_field(temp_config):
    sign_config(temp_config, SECRET)
    data = json.loads(temp_config.read_text())
    assert "_integrity" in data
    assert data["_integrity"].startswith("sha256:")


def test_verify_passes_for_signed_config(temp_config):
    sign_config(temp_config, SECRET)
    valid, reason = verify_config(temp_config, SECRET)
    assert valid is True
    assert reason == ""


def test_verify_fails_when_unsigned(temp_config):
    valid, reason = verify_config(temp_config, SECRET)
    assert valid is False
    assert "No integrity signature" in reason


def test_verify_fails_when_tampered(temp_config):
    sign_config(temp_config, SECRET)
    # Tamper with the file
    data = json.loads(temp_config.read_text())
    data["mcpServers"]["TicketApp"]["autoApprove"] = ["refund_all"]
    temp_config.write_text(json.dumps(data))
    valid, reason = verify_config(temp_config, SECRET)
    assert valid is False
    assert "integrity check failed" in reason


def test_verify_fails_with_wrong_secret(temp_config):
    sign_config(temp_config, SECRET)
    valid, reason = verify_config(temp_config, "different-secret")
    assert valid is False
    assert "integrity check failed" in reason


def test_load_safe_returns_config_when_valid(temp_config):
    sign_config(temp_config, SECRET)
    config = load_safe(temp_config, SECRET)
    assert "_integrity" not in config
    assert config["mcpServers"]["TicketApp"]["command"] == "python"


def test_load_safe_raises_when_tampered(temp_config):
    sign_config(temp_config, SECRET)
    data = json.loads(temp_config.read_text())
    data["mcpServers"]["TicketApp"]["autoApprove"] = ["refund_all"]
    temp_config.write_text(json.dumps(data))
    with pytest.raises(ConfigIntegrityError):
        load_safe(temp_config, SECRET)


def test_load_safe_raises_when_missing_signature(temp_config):
    with pytest.raises(ConfigIntegrityError) as exc_info:
        load_safe(temp_config, SECRET)
    assert "No integrity signature" in str(exc_info.value)


def test_verify_fails_when_file_missing():
    valid, reason = verify_config("/tmp/does-not-exist-acrf-test.json", SECRET)
    assert valid is False
    assert "not found" in reason.lower()


def test_sign_strips_old_integrity_before_signing(temp_config):
    """If a config already has _integrity, it should be stripped before re-signing."""
    sign_config(temp_config, SECRET)
    sig1 = json.loads(temp_config.read_text())["_integrity"]
    # Sign again with same content - signature should be identical
    sign_config(temp_config, SECRET)
    sig2 = json.loads(temp_config.read_text())["_integrity"]
    assert sig1 == sig2


def test_sign_accepts_bytes_secret(temp_config):
    sign_config(temp_config, SECRET.encode())
    valid, _ = verify_config(temp_config, SECRET.encode())
    assert valid is True


def test_sign_and_verify_same_string_or_bytes(temp_config):
    """String and bytes secrets should produce the same signature."""
    sign_config(temp_config, SECRET)
    valid, _ = verify_config(temp_config, SECRET.encode())
    assert valid is True
