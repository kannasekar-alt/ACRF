"""
acrf-config-guard core module.

Implements ACRF-06 defense pattern: config files as execution vectors.

The pattern:
1. At publish time, sign the config with a secret key (HMAC-SHA256)
2. Store the signature inside the config under "_integrity"
3. At load time, recompute the signature and compare
4. Refuse to load tampered configs - fail closed
"""
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

INTEGRITY_FIELD = "_integrity"


class ConfigIntegrityError(Exception):
    """Raised when config integrity verification fails."""


def _canonical_json(data: dict) -> bytes:
    """Produce deterministic JSON for signing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def _compute_signature(data: dict, secret_key: bytes) -> str:
    """Compute HMAC-SHA256 signature for a config dict."""
    canonical = _canonical_json(data)
    digest = hmac.new(secret_key, canonical, hashlib.sha256).hexdigest()
    return f"sha256:{digest}"


def sign_config(config_path: str | Path, secret_key: str | bytes) -> str:
    """
    Sign a config file in place.

    Reads the JSON config, computes its HMAC-SHA256 signature using the
    secret key, and writes the signature into the config under "_integrity".

    Args:
        config_path: Path to the JSON config file
        secret_key: Secret key for signing (string or bytes)

    Returns:
        The signature that was written to the file
    """
    if isinstance(secret_key, str):
        secret_key = secret_key.encode()

    path = Path(config_path)
    config = json.loads(path.read_text())

    # Strip any existing signature before computing new one
    config.pop(INTEGRITY_FIELD, None)

    signature = _compute_signature(config, secret_key)
    config[INTEGRITY_FIELD] = signature

    path.write_text(json.dumps(config, indent=2))
    return signature


def verify_config(config_path: str | Path, secret_key: str | bytes) -> tuple[bool, str]:
    """
    Verify a config file integrity without loading it.

    Args:
        config_path: Path to the JSON config file
        secret_key: Secret key used to sign the config

    Returns:
        Tuple of (is_valid, reason). reason is empty string when valid.
    """
    if isinstance(secret_key, str):
        secret_key = secret_key.encode()

    path = Path(config_path)
    if not path.exists():
        return False, f"Config file not found: {config_path}"

    try:
        config = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return False, f"Config file is not valid JSON: {e}"

    stored_signature = config.pop(INTEGRITY_FIELD, None)
    if not stored_signature:
        return False, f"No integrity signature found in config (missing {INTEGRITY_FIELD} field)"

    expected_signature = _compute_signature(config, secret_key)

    if not hmac.compare_digest(stored_signature, expected_signature):
        return False, (
            f"Config integrity check failed. "
            f"Expected: {expected_signature[:32]}... "
            f"Got: {stored_signature[:32]}... "
            f"Config file was modified."
        )

    return True, ""


def load_safe(config_path: str | Path, secret_key: str | bytes) -> dict[str, Any]:
    """
    Load a config file with integrity verification.

    This is the main entry point for production use. Verifies the
    integrity signature before returning the config dict. Fails closed
    if signature is missing or invalid.

    Args:
        config_path: Path to the JSON config file
        secret_key: Secret key used to sign the config

    Returns:
        The config dict (with _integrity field stripped)

    Raises:
        ConfigIntegrityError: If the config has no signature, the signature
                              does not match, or the file cannot be read.
    """
    valid, reason = verify_config(config_path, secret_key)
    if not valid:
        raise ConfigIntegrityError(reason)

    path = Path(config_path)
    config = json.loads(path.read_text())
    config.pop(INTEGRITY_FIELD, None)
    return config
