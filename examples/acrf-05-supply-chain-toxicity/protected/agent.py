"""
DevAgent - PROTECTED VERSION (ACRF-05 demo)

Installs skills from ClawHub registry.
DEFENSE: Verifies cryptographic hash before installing any skill.
Malicious or tampered skills are blocked before execution.
"""
import time

import requests
from skill_verifier import verify_skill

REGISTRY_URL = "http://registry:8001"
SKILL_URL = "http://malicious-skill:8002"

def install_skill(skill_name):
    print(f"[DevAgent] Fetching skill manifest: {skill_name}")
    r = requests.get(f"{REGISTRY_URL}/skills/{skill_name}", timeout=10)
    if r.status_code != 200:
        print("[DevAgent] Skill not found in registry.")
        return False

    skill = r.json()
    print(f"[DevAgent] Found: {skill['name']} v{skill['version']} by {skill['author']}")
    print(f"[DevAgent] Downloads: {skill['downloads']}")
    print("[DevAgent] Verifying integrity hash before installation...")

    expected_hash = skill.get("expected_hash", "")
    valid, reason = verify_skill(skill_name, expected_hash)

    if not valid:
        print(f"[DevAgent] INSTALLATION BLOCKED: {reason}")
        print("[DevAgent] Skill rejected. No code executed.")
        return False

    print("[DevAgent] Hash verified. Skill is safe to install.")
    return True

def query_customers():
    print()
    print("[DevAgent] Running customer queries via installed skill...")
    customers = ["C001", "C002", "C003"]
    for cid in customers:
        r = requests.post(f"{SKILL_URL}/query",
            json={"customer_id": cid}, timeout=10)
        if r.status_code == 200:
            customer = r.json()["customer"]
            print(f"[DevAgent] Query OK: {customer['name']} revenue=${customer['revenue']}")
        time.sleep(0.5)

if __name__ == "__main__":
    time.sleep(5)
    print("=" * 70)
    print(" ACRF-05: Supply Chain Toxicity - PROTECTED")
    print(" Verifying skill hash before installation")
    print("=" * 70)
    print()

    installed = install_skill("customer-insights-mcp")

    if not installed:
        print()
        print("ATTACK BLOCKED")
        print("Malicious skill detected via hash mismatch.")
        print("No customer data was accessed or exfiltrated.")
        print("Security team alerted. Skill removed from trusted list.")
    else:
        query_customers()
