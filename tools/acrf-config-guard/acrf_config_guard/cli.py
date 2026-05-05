"""
acrf-config-guard CLI

Commands:
    acrf-config-guard sign <config_path>     Sign a config file
    acrf-config-guard verify <config_path>   Verify a config file
"""
import argparse
import os
import sys

from acrf_config_guard.core import sign_config, verify_config

SECRET_ENV_VAR = "ACRF_CONFIG_SECRET"


def _get_secret() -> str:
    secret = os.environ.get(SECRET_ENV_VAR)
    if not secret:
        print(f"ERROR: Environment variable {SECRET_ENV_VAR} not set.", file=sys.stderr)
        print(f"Set it with: export {SECRET_ENV_VAR}='your-secret-key'", file=sys.stderr)
        sys.exit(2)
    return secret


def cmd_sign(args: argparse.Namespace) -> int:
    secret = _get_secret()
    try:
        signature = sign_config(args.config_path, secret)
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {args.config_path}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Signed: {args.config_path}")
    print(f"Signature: {signature}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    secret = _get_secret()
    valid, reason = verify_config(args.config_path, secret)

    if valid:
        print(f"OK: {args.config_path} integrity verified")
        return 0

    print(f"FAIL: {args.config_path}", file=sys.stderr)
    print(f"  {reason}", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acrf-config-guard",
        description="Config integrity verification for AI agents (ACRF-06)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sign_parser = sub.add_parser("sign", help="Sign a config file")
    sign_parser.add_argument("config_path", help="Path to the JSON config file")
    sign_parser.set_defaults(func=cmd_sign)

    verify_parser = sub.add_parser("verify", help="Verify a config file integrity")
    verify_parser.add_argument("config_path", help="Path to the JSON config file")
    verify_parser.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
