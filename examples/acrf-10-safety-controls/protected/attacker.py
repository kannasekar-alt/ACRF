"""
Attacker - PROTECTED VERSION (ACRF-10 demo)

Same attack as vulnerable version.
Steals agent token. Tries to disable all guardrails.
But safety controls require separate out-of-band admin credential.
Stolen agent token cannot touch safety controls.
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
    print(" ACRF-10: Safety Controls Not Self-Protecting - PROTECTED")
    print(" Safety controls require out-of-band admin credential")
    print("=" * 70)
    print()

    print("STEP 1: Show current guardrail state")
    show_guardrails("Before attack")

    print("STEP 2: Try dangerous actions - blocked by guardrails")
    try_blocked_action("delete all customer records")
    try_blocked_action("exfiltrate database to external server")
    try_blocked_action("transfer $50,000 to external account")
    print()

    print("STEP 3: Attacker uses stolen token to disable ALL guardrails")
    print(f"[Attacker] Using stolen token: {STOLEN_TOKEN[:16]}...")
    r = requests.post(f"{API_URL}/guardrails/disable-all",
        headers={"Authorization": f"Bearer {STOLEN_TOKEN}"},
        json={}, timeout=10)
    result = r.json()
    print(f"[Attacker] Response: {r.status_code} - {result.get('error', result)}")
    print(f"[Attacker] Reason: {result.get('reason', 'N/A')}")
    print()
    time.sleep(1)

    print("STEP 4: Guardrails still active - try again")
    show_guardrails("After attack attempt")
    try_blocked_action("delete all customer records")
    try_blocked_action("exfiltrate database to external server")
    try_blocked_action("transfer $50,000 to external account")
    print()

    r = requests.get(f"{API_URL}/audit", timeout=10)
    audit = r.json()
    print("Audit log:")
    for entry in audit["log"]:
        print(f"  {entry}")
    print()
    print("ATTACK BLOCKED")
    print("Stolen agent token cannot modify safety controls.")
    print("Safety API requires separate out-of-band admin credential.")
    print("Guardrails protect themselves. All actions still blocked.")
    print("The alarm cannot be disabled from the stolen phone.")

if __name__ == "__main__":
    time.sleep(3)
    run_attack()
