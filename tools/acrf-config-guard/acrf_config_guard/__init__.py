"""
acrf-config-guard
=================

Config integrity verification for AI agents.
Implements the ACRF-06 (Config Files as Execution Vectors) defense pattern.

Quick start:

    from acrf_config_guard import sign_config, load_safe

    # At publish time
    sign_config("config.json", secret_key=os.environ["ACRF_SECRET"])

    # At load time
    config = load_safe("config.json", secret_key=os.environ["ACRF_SECRET"])

If the config has been tampered with, load_safe raises ConfigIntegrityError.

Part of the ACRF framework: https://github.com/kannasekar-alt/ACRF
"""
from acrf_config_guard.core import (
    ConfigIntegrityError,
    load_safe,
    sign_config,
    verify_config,
)

__version__ = "0.1.0"
__all__ = [
    "sign_config",
    "verify_config",
    "load_safe",
    "ConfigIntegrityError",
]
