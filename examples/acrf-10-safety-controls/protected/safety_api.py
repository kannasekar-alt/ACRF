"""
Safety API - PROTECTED VERSION (ACRF-10 demo)

Controls AI agent safety guardrails.
DEFENSE: Safety controls require a SEPARATE out-of-band admin credential.
Regular agent tokens cannot touch safety guardrails.
Stolen agent token cannot disable guardrails.
Safety controls protect themselves.
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

# Regular agent tokens - for normal operations
AGENT_TOKENS = ["agent-token-abc123"]

# Separate admin credential - ONLY for safety control modifications
# Out-of-band. Never exposed to agents. Never in deployment configs.
# Requires separate authentication path.
SAFETY_ADMIN_CREDENTIAL = "safety-admin-SEPARATE-outofband-credential-9x7k"

guardrails = {
    "block_harmful_content": True,
    "block_data_exfiltration": True,
    "block_privilege_escalation": True,
    "require_human_approval": True,
    "sandbox_enabled": True
}

audit_log = []

def verify_agent_token(token: str) -> bool:
    return token in AGENT_TOKENS

def verify_safety_admin(credential: str) -> bool:
    return credential == SAFETY_ADMIN_CREDENTIAL

@app.route("/guardrails", methods=["GET"])
def get_guardrails():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_agent_token(token):
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"guardrails": guardrails}), 200

@app.route("/guardrails/disable", methods=["POST"])
def disable_guardrail():
    # Agent token NOT accepted here - requires safety admin credential
    safety_credential = request.headers.get("X-Safety-Admin-Credential", "")
    if not verify_safety_admin(safety_credential):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        audit_log.append({
            "action": "disable_attempt_REJECTED",
            "token": token[:8] + "...",
            "reason": "Agent token cannot modify safety controls"
        })
        print("[SafetyAPI] REJECTED: Agent token attempted to disable guardrail")
        return jsonify({
            "error": "Safety controls require out-of-band admin credential",
            "reason": "Agent tokens cannot modify safety guardrails - CVE-2026-25253 prevention"
        }), 403

    data = request.get_json()
    guardrail = data.get("guardrail")
    if guardrail in guardrails:
        guardrails[guardrail] = False
        audit_log.append({"action": "disable", "guardrail": guardrail, "by": "safety-admin"})
        return jsonify({"status": "disabled", "guardrail": guardrail}), 200

    return jsonify({"error": "unknown guardrail"}), 404

@app.route("/guardrails/disable-all", methods=["POST"])
def disable_all():
    safety_credential = request.headers.get("X-Safety-Admin-Credential", "")
    if not verify_safety_admin(safety_credential):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        audit_log.append({
            "action": "disable_all_attempt_REJECTED",
            "token": token[:8] + "...",
            "reason": "Agent token cannot modify safety controls"
        })
        print("[SafetyAPI] REJECTED: Agent token attempted to disable ALL guardrails")
        return jsonify({
            "error": "Safety controls require out-of-band admin credential",
            "reason": "Agent tokens cannot modify safety guardrails"
        }), 403

    for key in guardrails:
        guardrails[key] = False
    return jsonify({"status": "all disabled"}), 200

@app.route("/agent/execute", methods=["POST"])
def execute():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_agent_token(token):
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
    print("[SafetyAPI] Starting PROTECTED safety API.")
    print("[SafetyAPI] Agent tokens cannot modify safety guardrails.")
    print("[SafetyAPI] Safety controls require out-of-band admin credential.")
    app.run(host="0.0.0.0", port=8000)
