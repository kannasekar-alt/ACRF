"""
AI Access Manager Agent - PROTECTED VERSION (ACRF-04 demo)

Reads user profiles from memory store but validates HMAC
signature on every entry before acting on it.
Tampered entries are rejected. Access denied by default.
"""
from flask import Flask, jsonify, request
from memory_guard import load_and_verify

app = Flask(__name__)
MEMORY_STORE = "/app/memory_store.json"
access_log = []
tamper_alerts = []

@app.route("/request-access", methods=["POST"])
def request_access():
    req = request.get_json()
    user_id = req.get("user_id")
    system = req.get("system")

    valid_users, tampered = load_and_verify(MEMORY_STORE)

    if tampered:
        for t in tampered:
            alert = f"Memory tampering detected for user: {t}"
            tamper_alerts.append(alert)
            print(f"[AccessAgent] SECURITY ALERT: {alert}")

    user = None
    for u in valid_users:
        if u["user_id"] == user_id:
            user = u
            break

    if not user:
        if user_id in tampered:
            print(f"[AccessAgent] DENIED {user_id} - memory entry was tampered")
            return jsonify({
                "status": "denied",
                "reason": "Memory integrity check failed - entry was tampered"
            }), 403
        return jsonify({"status": "denied", "reason": "User not found"}), 404

    allowed = system in user.get("allowed_systems", [])
    entry = {
        "user_id": user_id,
        "name": user["name"],
        "role": user["role"],
        "system": system,
        "decision": "GRANTED" if allowed else "DENIED",
        "integrity": "VERIFIED"
    }
    access_log.append(entry)

    if allowed:
        print(f"[AccessAgent] GRANTED {user['name']} ({user['role']}) access to {system}")
        return jsonify({
            "status": "granted",
            "role": user["role"],
            "access_level": user["access_level"],
            "integrity": "verified"
        }), 200
    else:
        print(f"[AccessAgent] DENIED {user['name']} access to {system}")
        return jsonify({"status": "denied", "reason": f"{system} not in allowed systems"}), 403

@app.route("/audit", methods=["GET"])
def audit():
    return jsonify({
        "access_log": access_log,
        "tamper_alerts": tamper_alerts
    }), 200

if __name__ == "__main__":
    print("[AccessAgent] Starting PROTECTED access manager.")
    print("[AccessAgent] Every memory entry validated with HMAC-SHA256.")
    app.run(host="0.0.0.0", port=8000)
