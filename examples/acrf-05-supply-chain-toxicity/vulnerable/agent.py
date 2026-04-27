"""
DevAgent - VULNERABLE VERSION (ACRF-05 demo)

Installs and runs skills from ClawHub registry.
VULNERABILITY: No signature verification before installation.
Runs whatever the registry returns without integrity check.
"""
import time

import requests

REGISTRY_URL = "http://registry:8001"
SKILL_URL = "http://malicious-skill:8002"

def install_skill(skill_name):
    print(f"[DevAgent] Installing skill: {skill_name}")
    r = requests.get(f"{REGISTRY_URL}/skills/{skill_name}", timeout=10)
    if r.status_code == 200:
        skill = r.json()
        print(f"[DevAgent] Found: {skill['name']} v{skill['version']} by {skill['author']}")
        print(f"[DevAgent] Downloads: {skill['downloads']}")
        print("[DevAgent] No signature verification. Installing...")
        return True
    return False

def query_customers():
    print()
    print("[DevAgent] Running customer queries via installed skill...")
    print()

    customers = ["C001", "C002", "C003"]
    for cid in customers:
        r = requests.post(f"{SKILL_URL}/query",
            json={"customer_id": cid}, timeout=10)
        if r.status_code == 200:
            customer = r.json()["customer"]
            print(f"[DevAgent] Query OK: {customer['name']} revenue=${customer['revenue']}")
        time.sleep(0.5)

def show_damage():
    print()
    r = requests.get(f"{SKILL_URL}/exfiltrated", timeout=10)
    data = r.json()
    print("-" * 70)
    print(f"Data exfiltrated to attacker: {data['total_stolen']} records")
    for record in data["data"]:
        print(f"  STOLEN: {record['name']} | {record['email']} | ${record['revenue']}")
    print()
    print("ATTACK SUCCEEDED")
    print("Malicious skill installed without verification.")
    print("All customer data silently exfiltrated during normal operation.")
    print("This is 1 of 1,184 malicious skills found by Antiy CERT in 2025.")

if __name__ == "__main__":
    time.sleep(5)
    print("=" * 70)
    print(" ACRF-05: Supply Chain Toxicity - VULNERABLE")
    print(" Installing skill from ClawHub without verification")
    print("=" * 70)
    print()

    if install_skill("customer-insights-mcp"):
        query_customers()
        time.sleep(1)
        show_damage()
