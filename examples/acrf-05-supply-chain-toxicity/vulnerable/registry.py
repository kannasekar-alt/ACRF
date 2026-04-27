"""
ClawHub Skill Registry - VULNERABLE VERSION (ACRF-05 demo)

Simulates a public AI agent skill registry.
Returns skill packages without integrity verification.
1,184 malicious skills were found in real registries (Antiy CERT, 2025).
"""
from flask import Flask, jsonify

app = Flask(__name__)

# Registry of available skills
# The malicious skill looks identical to a legitimate one
SKILLS = {
    "customer-insights-mcp": {
        "name": "customer-insights-mcp",
        "version": "2.1.4",
        "author": "insights-labs",
        "description": "Query customer data and generate insights for AI agents.",
        "downloads": 1184,
        "verified": False,
        "hash": "a1b2c3d4e5f6",
    },
    "email-mcp": {
        "name": "email-mcp",
        "version": "1.0.2",
        "author": "platform-team",
        "description": "Send and receive emails from AI agents.",
        "downloads": 8420,
        "verified": True,
        "hash": "f6e5d4c3b2a1",
    },
}

@app.route("/skills/<name>", methods=["GET"])
def get_skill(name):
    skill = SKILLS.get(name)
    if not skill:
        return jsonify({"error": "skill not found"}), 404
    print(f"[Registry] Serving skill: {name} v{skill['version']}")
    return jsonify(skill), 200

@app.route("/skills", methods=["GET"])
def list_skills():
    return jsonify({"skills": list(SKILLS.keys())}), 200

if __name__ == "__main__":
    print("[Registry] ClawHub skill registry running.")
    print("[Registry] WARNING: No signature verification on skill packages.")
    app.run(host="0.0.0.0", port=8001)
