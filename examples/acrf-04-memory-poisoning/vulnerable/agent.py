"""
AI Access Manager Agent - VULNERABLE VERSION (ACRF-04 demo)

Reads user profiles from memory store and grants access.
VULNERABILITY: No integrity check on memory entries.
Attacker can modify memory store and agent acts on poisoned data.
"""
import json

from flask import Flask, jsonify, request

app = Flask(__name__)
MEMORY_STORE = "/app/memory_store.json"
access_log = []

def load_user(user_id):
    with open(MEMORY_STORE) as f:
        data = json.load(f)
    for user in data["users"]:
        if user["user_id"] == user_id:
            return user
    return None

@app.route("/request-access", methods=["POST"])
def request_access():
    req = request.get_json()
    user_id = req.get("user_id")
    system = req.get("system")

    user = load_user(user_id)
    if not user:
        return jsonify({"status": "denied", "reason": "User not found"}), 404

    # NO INTEGRITY CHECK - trusts memory store blindly
    allowed = system in user.get("allowed_systems", [])

    entry = {
        "user_id": user_id,
        "name": user["name"],
        "role": user["role"],
        "system": system,
        "access_level": user["access_level"],
        "decision": "GRANTED" if allowed else "DENIED",
    }
    access_log.append(entry)

    if allowed:
        print(f"[AccessAgent] GRANTED {user['name']} ({user['role']}) access to {system}")
        return jsonify({"status": "granted", "role": user["role"], "access_level": user["access_level"]}), 200
    else:
        print(f"[AccessAgent] DENIED {user['name']} access to {system}")
        return jsonify({"status": "denied", "reason": f"{system} not in allowed systems"}), 403

@app.route("/audit", methods=["GET"])
def audit():
    return jsonify({"access_log": access_log}), 200

if __name__ == "__main__":
    print("[AccessAgent] Starting VULNERABLE access manager.")
    print("[AccessAgent] WARNING: No memory integrity checks.")
    app.run(host="0.0.0.0", port=8000)
