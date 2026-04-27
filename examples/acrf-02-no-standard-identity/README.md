# ACRF-02: No Standard Agent Identity

A runnable demonstration of agent identity lifecycle risk - with a working defense.

**ACRF Risk:** 02
**AIVSS Severity:** High (8.2)
**OWASP Agentic:** ASI03 Identity and Privilege Failures
**OWASP MCP:** MCP01 Token Mismanagement

---

## The IAM connection

In traditional IAM, service account sprawl is one of the most common
audit findings. Accounts created for automated processes. Never reviewed.
Never rotated. Never decommissioned. Each one a liability waiting to be exploited.

AI agents have the same problem - but worse.
Most organizations give all their agents a single shared token.
No per-agent identity. No scope. No expiry. No revocation.

When an agent is retired, the token stays active.
When an attacker finds it, they can impersonate any agent in the system.

This demo shows what that looks like - and how per-agent scoped tokens stop it.

---

## Your instinct from RSAC 2026

"Who has accountability?"

That is ACRF-02 in one question.

With shared tokens - nobody has accountability.
The audit log shows the same token on every call.
You cannot tell which agent made which decision.
You cannot prove which agent executed which trade.
You cannot revoke one agent without revoking all of them.

Per-agent identity fixes all of this.

---

## What this demo shows

A financial platform with four agents:
- orchestrator-agent - coordinates the others
- pricing-agent - reads market data only
- trade-agent - executes trades
- data-agent - retired 90 days ago

### Mode 1 - Vulnerable

All four agents share one token: shared-service-token-acrf02-2026

The data-agent was retired but its token was never revoked.
An attacker finds the token in an old deployment config.
Uses it to read pricing data AND execute a SELL order for 10,000 shares.

The audit log is useless - every entry shows the same token prefix.
You cannot tell which calls were legitimate and which were the attacker.

**Result:** Retired agent token used to execute unauthorized trades.
Audit log provides no accountability. This is service account sprawl
for AI agents.

### Mode 2 - Protected

Each agent has its own scoped token:
- pricing-agent: can only call pricing endpoints
- trade-agent: can call pricing and trade endpoints
- data-agent: token marked revoked at decommission time

When the attacker uses the retired data-agent token:
- Token revocation checked immediately
- Access denied with reason: "Agent decommissioned 90 days ago"
- Every audit entry shows exact agent identity
- Pricing agent cannot execute trades even with its valid token

**Result:** Attack blocked. Revocation works. Scope enforced.
Audit log shows clear per-agent accountability on every call.

---

## Prerequisites

- Docker 20+
- Docker Compose 2+
- 2 GB free RAM

No Python install needed. Everything runs in containers.

---

## Running the demo

Attack - shared token, no revocation:

    ./run-attack.sh

Expected output:
    Legitimate agents work normally
    Attacker uses retired token: GRANTED
    Audit log: all entries show same token - no accountability

Defense - per-agent scoped tokens with revocation:

    ./run-defense.sh

Expected output:
    Legitimate agents work normally
    Attacker uses retired token: DENIED
    Reason: Token revoked: Agent decommissioned 90 days ago
    Audit log: clear per-agent identity on every call

---

## How the defense works

1. Per-agent tokens - each agent gets its own unique token at provisioning
2. Scoped access - pricing-agent token only works on pricing endpoints
3. Token expiry - tokens have a defined lifetime tied to the task window
4. Revocation - when data-agent is decommissioned, token marked revoked immediately
5. Audit trail - every request logged with verified agent identity, not just a name

The attacker cannot use the retired token because revocation is checked
before any access is granted. Scope prevents even valid tokens from
calling endpoints outside their permitted range.

---

## Built with

- Python 3.11
- Flask 3.0 - API gateway simulation
- requests 2.31 - inter-container communication
- Docker + Docker Compose - isolated vulnerable and protected environments

No external auth library needed. The pattern is simple enough to implement
in pure Python to show the concepts clearly.

---

## Security patterns implemented

- Per-agent token identity (replaces shared service account)
- Scope enforcement per endpoint (least privilege)
- Token revocation at decommission time (lifecycle management)
- Deny-by-default on revoked or expired tokens
- Audit log with verified agent identity on every call

---

## How RBAC and ABAC apply here

**RBAC (Role-Based Access Control):**
Each agent has a role that determines which endpoints it can call.
pricing-agent role: pricing:read only
trade-agent role: pricing:read + trade:execute
data-agent role: revoked - no access

An agent cannot call an endpoint outside its role.
Even if the token is valid, scope mismatch means access denied.

**ABAC (Attribute-Based Access Control):**
Access decisions use multiple token attributes:
- status: is the token active or revoked?
- expires_at: has the token lifetime elapsed?
- scopes: does this token permit this specific endpoint?
- agent_id: which agent does this token belong to?

All four attributes must pass. A valid but out-of-scope token is denied.
A scoped but revoked token is denied. One failed attribute blocks all access.

This mirrors how SailPoint and CyberArk manage privileged service accounts:
identity + role + lifecycle + revocation all enforced together.

---

## What the cybersecurity community can take from this

Service account sprawl is a top IAM audit finding.
The fix is well understood: individual accounts, scoped permissions,
lifecycle management, immediate revocation on decommission.

AI agents need the same treatment.

The contractor keycard analogy from RSAC 2026:
"A contractor finishes the job and leaves. Their building keycard is never
deactivated. Six months later someone finds it and walks back in.
That is ACRF-02."

The fix is not complicated. It is the same discipline IAM teams
already apply to human identities and service accounts:

- Every agent gets its own identity (not shared tokens)
- Scope is limited to what that agent actually needs
- Tokens expire when the task or session ends
- Decommission triggers immediate revocation

If your organization uses SailPoint or Okta to govern human identities,
apply the same governance model to your AI agents.
The tools exist. The process is the same. The stakes are higher.

---

## ACRF-02 maturity levels

    Level 0 - NONE      Agents share credentials. No individual identity.
    Level 1 - INITIAL   Agents have distinct verifiable identities (SI-1).
    Level 2 - DEFINED   Tokens are scoped per agent (SI-1, SI-2).
    Level 3 - MANAGED   Identity material rotated and revocable (SI-1, SI-2, SI-3).
    Level 4 - OPTIMIZED Agent identity distinguished from user identity in all logs (SI-1 through SI-4).

This demo implements Level 3 - per-agent tokens with scope and revocation.

---

## Control objectives addressed

    SI-1  Every agent has a cryptographically verifiable identity distinct from user identity
    SI-2  Tokens scoped per agent - one agent token cannot be used by another agent
    SI-3  Identity material rotatable and revocable without impacting other agents

Planned for future versions:

    SI-4  Agent identity consistently distinguished from user identity in all audit records

---

## Attribution

Part of the ACRF framework: https://github.com/kannasekar-alt/ACRF
Presented at RSA Conference 2026.

Authors: Ravi Karthick Sankara Narayanan and Kanna Sekar

Licensed under Apache 2.0.
