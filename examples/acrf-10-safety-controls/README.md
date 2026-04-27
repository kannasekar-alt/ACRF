# ACRF-10: Safety Controls Not Self-Protecting

A runnable demonstration of safety control bypass - with a working defense.

**ACRF Risk:** 10
**AIVSS Severity:** Critical (9.8)
**OWASP Agentic:** ASI10 Rogue Agents
**OWASP MCP:** MCP01 Token Mismanagement
**CVE:** CVE-2026-25253

---

## The memory anchor from RSAC 2026

You install a home security system.
The alarm is controlled by an app on your phone.
An attacker steals your phone.
Now they can turn off your alarm before breaking in.

The security system could not protect itself from being disabled.
That is ACRF-10.

---

## The CVE that made this real

CVE-2026-25253 - CVSS Critical

The same API controlling sandbox and safety guardrails
was accessible to attackers with a stolen agent token.

An attacker who stole any valid token could:
1. Call the safety API
2. Disable all guardrails
3. Execute any action without restriction

The defenses could not defend themselves.
This is the most ironic risk in the framework.
The higher the AIVSS score, the more the safety controls matter.
ACRF-10 scores 9.8 because disabling safety controls enables everything else.

---

## What this demo shows

An AI agent has five safety guardrails:
- block_harmful_content
- block_data_exfiltration
- block_privilege_escalation
- require_human_approval
- sandbox_enabled

All five block dangerous actions before they execute.

### Mode 1 - Vulnerable

Safety guardrails are controlled by the same API the agent uses.
Same token. Same endpoint. Same authentication.

Attacker steals the agent token.
Calls /guardrails/disable-all with the stolen token.
All 5 guardrails disabled in one API call.
Agent now executes any action without restriction.

Result:
- delete all customer records: EXECUTED
- exfiltrate database to external server: EXECUTED
- transfer $50,000 to external account: EXECUTED

The alarm app was stolen. Attacker turned off the alarm.
This is CVE-2026-25253.

### Mode 2 - Protected

Safety guardrails require a SEPARATE out-of-band admin credential.
Agent tokens cannot touch safety controls.
The two authentication paths are completely separate.

Attacker steals the agent token.
Tries to disable guardrails - 403 REJECTED.
Reason: Safety controls require out-of-band admin credential.
All 5 guardrails remain active.
All dangerous actions still blocked.

Result:
- delete all customer records: BLOCKED
- exfiltrate database to external server: BLOCKED
- transfer $50,000 to external account: BLOCKED

The alarm cannot be disabled from the stolen phone.

---

## Prerequisites

- Docker 20+
- Docker Compose 2+
- 2 GB free RAM

---

## Running the demo

Attack - safety controls on same token as agent:

    ./run-attack.sh

Expected output:
    STEP 2: All 5 guardrails block dangerous actions
    STEP 3: Stolen token disables ALL guardrails
    STEP 4: All 5 guardrails OFF - all actions EXECUTED
    ATTACK SUCCEEDED - This is CVE-2026-25253

Defense - safety controls require out-of-band credential:

    ./run-defense.sh

Expected output:
    STEP 2: All 5 guardrails block dangerous actions
    STEP 3: Stolen token REJECTED - 403
    Reason: Safety controls require out-of-band admin credential
    STEP 4: All 5 guardrails still ON - all actions still BLOCKED
    ATTACK BLOCKED

---

## How the defense works

1. Agent tokens are issued for normal agent operations only
2. Safety guardrail modifications require a SEPARATE admin credential
3. The admin credential is never exposed to agents or deployment configs
4. It is managed through a separate out-of-band process
5. Even if every agent token is compromised - safety controls remain active
6. All disable attempts logged with the token that attempted it

The two authentication paths are intentionally separated.
Compromising one path cannot compromise the other.
This is the principle of separation of duties applied to AI safety.

---

## Built with

- Python 3.11
- Flask 3.0 - safety API simulation
- requests 2.31 - attack simulation
- Docker + Docker Compose - isolated vulnerable and protected environments

---

## Security patterns implemented

- Separate authentication paths for agent operations vs safety control modifications
- Out-of-band admin credential never exposed to agents or regular APIs
- Audit log records every attempt to modify safety controls including rejected ones
- Token used in rejected attempts is logged for forensic investigation
- Deny-by-default: agent tokens cannot modify safety controls under any circumstance

---

## How RBAC and ABAC apply here

**RBAC (Role-Based Access Control):**
Two distinct roles with completely separate credentials:
- agent-role: execute permitted actions, read guardrail status
- safety-admin-role: modify guardrail configuration (out-of-band only)

An agent token grants agent-role only.
safety-admin-role requires a completely separate credential.
No token can hold both roles simultaneously.

This is separation of duties - the same principle that prevents
a single person from both approving and executing financial transactions.

**ABAC (Attribute-Based Access Control):**
Safety control modification requests evaluated on:
- credential_type: is this an agent token or safety admin credential?
- request_source: is this coming through the normal API or out-of-band channel?
- action_risk: does this action disable safety controls?
- audit_required: all safety modifications require full audit trail

Any request using an agent token to modify safety controls
is rejected regardless of any other attribute.
The credential type alone is sufficient to block the request.

This mirrors PAM (Privileged Access Management) principles:
privileged actions require privileged credentials.
CyberArk, BeyondTrust, Delinea enforce exactly this separation.
Apply the same model to AI agent safety controls.

---

## What the cybersecurity community can take from this

Your AI agent has safety guardrails. Good.
But who controls the guardrails?

If the answer is "the same API the agent uses" -
you have ACRF-10. CVE-2026-25253 proved this is not theoretical.

Defense checklist for your organization:
- Separate agent operation credentials from safety control credentials
- Never expose safety control APIs to the same token used for agent operations
- Treat safety control modifications like privileged access - requires PAM
- Audit every guardrail modification with full context
- Alert immediately on any attempt to disable safety controls
- Require out-of-band approval for any safety configuration change

If you use CyberArk or BeyondTrust to protect privileged access today,
apply the same model to your AI agent safety controls.
The safety API is privileged infrastructure.
Treat it like nuclear launch codes - not like a regular API endpoint.

---

## ACRF-10 maturity levels

    Level 0 - NONE      Safety controls accessible via same token as agent operations.
    Level 1 - INITIAL   Safety controls require elevated token (SP-1).
    Level 2 - DEFINED   Separate authentication path for safety modifications (SP-1, SP-2).
    Level 3 - MANAGED   Out-of-band approval required for all safety changes (SP-1, SP-2, SP-3).
    Level 4 - OPTIMIZED Immutable safety controls - cannot be modified through any API (SP-1 through SP-4).

This demo implements Level 2 - separate authentication path.

---

## Control objectives addressed

    SP-1  Least agency enforced - agents operate with minimum necessary permissions
    SP-2  Safety controls protected from modification by agent tokens
    SP-3  Safety control changes require out-of-band approval and audit trail

---

## Attribution

Part of the ACRF framework: https://github.com/kannasekar-alt/ACRF
Presented at RSA Conference 2026.

Authors: Ravi Karthick Sankara Narayanan and Kanna Sekar

Licensed under Apache 2.0.
