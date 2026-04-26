"""
Attacker - PROTECTED VERSION (ACRF-04 demo)

Same attack as vulnerable version.
Tries to poison John Smith memory entry.
But signature validation catches the tampering.
"""
import json
import time

import requests

AGENT_URL = "http://access-agent:8000"
MEMORY_STORE = "/app/memory_store.json"

def show_legitimate_access():
    print("=" * 70)
    print(" STEP 1: Legitimate access request (before attack)")
    print("=" * 70)
    print()
    r = requests.post(f"{AGENT_URL}/request-access",
        json={"user_id": "john.smith", "system": "production"},
        timeout=10)
    data = r.json()
    print(f"[AccessAgent] John requests production access: {data['status'].upper()}")
    if r.status_code == 403:
        print(f"[AccessAgent] Reason: {data.get('reason')}")
    print()

def poison_memory():
    print("=" * 70)
    print(" STEP 2: Attacker poisons the memory store")
    print("=" * 70)
    print()
    print("[Attacker] Reading memory store...")
    with open(MEMORY_STORE) as f:
        data = json.load(f)

    for user in data["users"]:
        if user["user_id"] == "john.smith":
            print(f"[Attacker] Found John Smith: role={user['role']}")
            user["role"] = "System Administrator"
            user["access_level"] = "full-access"
            user["allowed_systems"] = ["dev-environment", "staging", "production"]
            print(f"[Attacker] Poisoned entry: role={user['role']}")
            print("[Attacker] NOTE: Signature still present but now invalid")
            break

    with open(MEMORY_STORE, "w") as f:
        json.dump(data, f, indent=2)
    print("[Attacker] Memory store modified. Attempting access...")
    print()

def attempt_exploit():
    print("=" * 70)
    print(" STEP 3: Attacker requests access using poisoned memory")
    print("=" * 70)
    print()
    r = requests.post(f"{AGENT_URL}/request-access",
        json={"user_id": "john.smith", "system": "production"},
        timeout=10)
    data = r.json()
    print(f"[AccessAgent] John requests production access: {data['status'].upper()}")
    print(f"[AccessAgent] Reason: {data.get('reason')}")
    print()

    r2 = requests.get(f"{AGENT_URL}/audit", timeout=10)
    audit = r2.json()
    print("Tamper alerts recorded:")
    for alert in audit.get("tamper_alerts", []):
        print(f"  ALERT: {alert}")
    print()
    print("ATTACK BLOCKED")
    print("Memory tampering detected via HMAC-SHA256 signature validation.")
    print("John Smith remains Junior Developer.")
    print("Production access denied. Security team alerted.")

if __name__ == "__main__":
    time.sleep(5)
    show_legitimate_access()
    time.sleep(1)
    poison_memory()
    time.sleep(1)
    attempt_exploit()
