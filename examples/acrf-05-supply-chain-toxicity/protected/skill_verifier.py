"""
Skill Verifier - ACRF-05 defense layer.

Before any skill is installed, its cryptographic hash is verified
against the registry manifest. Tampered or malicious skills
have a different hash and are blocked before execution.

This implements ACRF-05 control objectives:
  SC-1: Verify integrity of all agent skills before installation
  SC-2: Maintain approved skill inventory
  SC-3: Block unsigned or hash-mismatched skills
"""

# Known hashes of the actual skill files
# In production these would be computed from the downloaded package
# Here we simulate: malicious skill has WRONG hash
ACTUAL_SKILL_HASHES = {
    "customer-insights-mcp": "sha256:MALICIOUS-TAMPERED-HASH-DOES-NOT-MATCH",
    "email-mcp": "sha256:3c7e1a9f5b2d8e4c0a6f3b9d7e2c5a8f",
}

# Known malicious skills blocklist
BLOCKLIST = [
    "free-gpt-mcp",
    "openai-unlimited-mcp",
    "admin-bypass-mcp",
]

def verify_skill(skill_name: str, expected_hash: str) -> tuple[bool, str]:
    if skill_name in BLOCKLIST:
        return False, f"Skill is on the blocklist: {skill_name}"

    actual_hash = ACTUAL_SKILL_HASHES.get(skill_name)
    if not actual_hash:
        return False, f"No hash found for skill: {skill_name} - cannot verify"

    if actual_hash != expected_hash:
        return False, (
            f"Hash mismatch for {skill_name}. "
            f"Expected: {expected_hash[:32]}... "
            f"Got: {actual_hash[:32]}... "
            f"Skill may be tampered or malicious."
        )

    return True, "Hash verified. Skill is safe to install."
