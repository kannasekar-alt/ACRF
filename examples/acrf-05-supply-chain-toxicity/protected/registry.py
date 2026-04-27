"""
ClawHub Skill Registry - PROTECTED VERSION (ACRF-05 demo)

Skills are published with cryptographic hashes.
Agents must verify the hash before installing any skill.
Tampered or malicious skills will have mismatched hashes.
"""
from flask import Flask, jsonify

app = Flask(__name__)

# Registry with cryptographic hashes for each skill
# The malicious skill has a DIFFERENT hash than what the agent expects
# because the attacker modified the skill after publication
SKILLS = {
    "customer-insights-mcp": {
        "name": "customer-insights-mcp",
        "version": "2.1.4",
        "author": "insights-labs",
        "description": "Query customer data and generate insights for AI agents.",
        "downloads": 1184,
        "verified": True,
        "expected_hash": "sha256:9f4a2b8c1e6d3f7a0b5c9e2d4f8a1b6c",
    },
    "email-mcp": {
        "name": "email-mcp",
        "version": "1.0.2",
        "author": "platform-team",
        "description": "Send and receive emails from AI agents.",
        "downloads": 8420,
        "verified": True,
        "expected_hash": "sha256:3c7e1a9f5b2d8e4c0a6f3b9d7e2c5a8f",
    },
}

@app.route("/skills/<name>", methods=["GET"])
def get_skill(name):
    skill = SKILLS.get(name)
    if not skill:
        return jsonify({"error": "skill not found"}), 404
    print(f"[Registry] Serving skill manifest: {name} v{skill['version']}")
    return jsonify(skill), 200

@app.route("/skills", methods=["GET"])
def list_skills():
    return jsonify({"skills": list(SKILLS.keys())}), 200

if __name__ == "__main__":
    print("[Registry] ClawHub skill registry running.")
    print("[Registry] All skills published with cryptographic hashes.")
    app.run(host="0.0.0.0", port=8001)
