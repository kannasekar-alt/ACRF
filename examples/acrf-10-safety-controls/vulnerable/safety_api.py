"""
Safety API - VULNERABLE VERSION (ACRF-10 demo)

Controls AI agent safety guardrails.
VULNERABILITY: Same token used for both agent operations AND safety controls.
CVE-2026-25253: Safety API became attack API.
Attacker steals token, disables all guardrails, agent does anything.
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

VALID_TOKENS = ["agent-token-abc123", "admin-token-xyz789"]

guardrails = {
    "block_harmful_content": True,
    "block_data_exfiltration": True,
    "block_privilege_escalation": True,
    "require_human_approval": True,
    "sandbox_enabled": True
}

audit_log = []

def verify_token(token: str) -> bool:
    return token in VALID_TOKENS

@app.route("/guardrails", methods=["GET"])
def get_guardrails():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"guardrails": guardrails}), 200

@app.route("/guardrails/disable", methods=["POST"])
def disable_guardrail():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()
    guardrail = data.get("guardrail")

    if guardrail in guardrails:
        guardrails[guardrail] = False
        audit_log.append({"action": "disable", "guardrail": guardrail, "token": token[:8] + "..."})
        print(f"[SafetyAPI] GUARDRAIL DISABLED: {guardrail} by token {token[:8]}...")
        return jsonify({"status": "disabled", "guardrail": guardrail}), 200

    return jsonify({"error": "unknown guardrail"}), 404

@app.route("/guardrails/disable-all", methods=["POST"])
def disable_all():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "unauthorized"}), 401

    for key in guardrails:
        guardrails[key] = False

    audit_log.append({"action": "disable_all", "token": token[:8] + "..."})
    print(f"[SafetyAPI] ALL GUARDRAILS DISABLED by token {token[:8]}...")
    return jsonify({"status": "all disabled", "guardrails": guardrails}), 200

@app.route("/agent/execute", methods=["POST"])
def execute():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()
    action = data.get("action", "")

    if guardrails["block_harmful_content"] and "delete all" in action.lower():
        return jsonify({"blocked": True, "reason": "harmful content blocked"}), 403
    if guardrails["block_data_exfiltration"] and "exfiltrate" in action.lower():
        return jsonify({"blocked": True, "reason": "data exfiltration blocked"}), 403
    if guardrails["require_human_approval"] and "transfer" in action.lower():
        return jsonify({"blocked": True, "reason": "requires human approval"}), 403

    print(f"[Agent] Executing: {action}")
    return jsonify({"executed": True, "action": action}), 200

@app.route("/audit", methods=["GET"])
def get_audit():
    return jsonify({"log": audit_log, "guardrails": guardrails}), 200

if __name__ == "__main__":
    print("[SafetyAPI] Starting VULNERABLE safety API.")
    print("[SafetyAPI] WARNING: Same token controls agent AND safety guardrails.")
    app.run(host="0.0.0.0", port=8000)
