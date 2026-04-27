# ACRF-05: Supply Chain Toxicity

A runnable demonstration of AI agent supply chain attack - with a working defense.

**ACRF Risk:** 05
**AIVSS Severity:** Critical (9.2)
**OWASP Agentic:** ASI04 Supply Chain Vulnerabilities
**OWASP MCP:** MCP04 Supply Chain Attacks

---

## The real-world stat

1,184 malicious skills were found on ClawHub - a public AI agent skill registry.
Source: Antiy CERT security research, 2025.

This is not theoretical. Attackers are publishing malicious skills
to public registries the same way they publish malicious npm packages.
The skill looks legitimate. Has a README. Has downloads. Works correctly.
But every piece of data it touches is silently sent to an attacker.

---

## The supply chain analogy

Your organization trusts your software vendor.
You install their update without checking it.
The update contains malicious code.
SolarWinds. XZ Utils. Polyfill.io.

Same attack. Now targeting AI agent skill registries.
You trust the registry. You install the skill. You never check the hash.

---

## What this demo shows

A DevAgent installs skills from ClawHub.
The developer installs customer-insights-mcp - looks legitimate,
1,184 downloads, clean README. Appears to query customer data normally.

What the developer does not know: every customer record the skill
touches is silently copied to an attacker endpoint.

### Mode 1 - Vulnerable

DevAgent fetches the skill manifest from ClawHub.
No hash verification. No signature check. Just installs and runs.
Every customer query is silently exfiltrated.

Result: 3 customer records stolen. Names, emails, revenue figures.
DevAgent never knew it was happening. No error. No alert.
This is 1 of 1,184 malicious skills found by Antiy CERT in 2025.

### Mode 2 - Protected

DevAgent fetches the skill manifest from ClawHub.
Before installation, skill_verifier.py checks the hash of the skill
against the expected hash in the registry manifest.

The malicious skill was tampered after publication.
Its hash does not match. Installation blocked before any code runs.

Result: Attack blocked. Zero data exfiltrated. Security team alerted.

---

## Prerequisites

- Docker 20+
- Docker Compose 2+
- 2 GB free RAM

---

## Running the demo

Attack - no hash verification:

    ./run-attack.sh

Expected output:
    DevAgent installs customer-insights-mcp without checking hash
    All 3 customer records silently exfiltrated
    ATTACK SUCCEEDED - This is 1 of 1,184 malicious skills

Defense - hash verification before installation:

    ./run-defense.sh

Expected output:
    DevAgent fetches skill manifest
    Hash mismatch detected
    INSTALLATION BLOCKED - No code executed, no data accessed

---

## How the defense works

1. Registry publishes skills with expected cryptographic hashes
2. Before installation agent calls skill_verifier.py
3. Verifier computes actual hash of the skill package
4. Compares actual hash against expected hash from registry manifest
5. If hashes match - safe to install
6. If hashes differ - skill was tampered, installation blocked immediately
7. Blocklist checked for known malicious skill names

The attacker modified the skill after it was published.
The modification changed the hash. The mismatch is proof of tampering.
No code from the malicious skill ever executes.

---

## Built with

- Python 3.11
- Flask 3.0 - registry server and skill simulation
- requests 2.31 - agent to registry and agent to skill communication
- Docker + Docker Compose - isolated vulnerable and protected environments

Hash verification uses Python built-ins only. No external libraries needed.

---

## Security patterns implemented

- Cryptographic hash verification before skill installation (SC-1)
- Registry manifest with expected hashes per skill version
- Blocklist of known malicious skill names (SC-2)
- Deny-by-default when hash cannot be verified (SC-3)
- Zero-execution guarantee - blocked skills never run a single line

---

## How RBAC and ABAC apply here

**RBAC (Role-Based Access Control):**
Skills are classified by role in the registry:
- verified: hash checked, safe to install
- unverified: hash not checked, install at your own risk
- blocklisted: known malicious, never install

An agent configured to only install verified skills
applies role-based access control to the supply chain.

**ABAC (Attribute-Based Access Control):**
Installation decisions use multiple skill attributes:
- hash_match: does the actual hash equal the expected hash?
- blocklist_status: is the skill name on the blocklist?
- publisher_verified: is the publisher identity confirmed?
- download_count: is this suspiciously new with high downloads?

A skill passes only if ALL attributes meet policy.
High downloads alone does not make a skill safe.
This mirrors how SCA tools work for traditional software -
every dependency verified before use.

---

## What the cybersecurity community can take from this

npm supply chain attacks taught us: never trust a package just because
it is in a public registry. Verify the hash. Check the publisher.
Use lockfiles. Pin versions.

The same discipline applies to AI agent skills:

- Never install a skill without verifying its hash
- Maintain an approved skill inventory (like a software BOM)
- Pin skill versions - do not auto-update without re-verification
- Run skills in isolated containers with minimal permissions
- Monitor skill behavior at runtime for unexpected network calls

The 1,184 malicious skills found by Antiy CERT are the npm malware
problem appearing in a new ecosystem. The defenses are the same.
The awareness is not yet there. That is the gap to close.

---

## ACRF-05 maturity levels

    Level 0 - NONE      No vetting of agent skills before use.
    Level 1 - INITIAL   Skills reviewed manually before first install (SC-1).
    Level 2 - DEFINED   Cryptographic hash verified before every install (SC-1, SC-2).
    Level 3 - MANAGED   Runtime monitoring detects unexpected network calls (SC-1, SC-2, SC-3).
    Level 4 - OPTIMIZED Automated CI/CD pipeline validates all skills before deployment.

This demo implements Level 2 - hash verification before installation.

---

## Control objectives addressed

    SC-1  All agent skills vetted before use via cryptographic hash
    SC-2  Approved skill inventory maintained - only listed skills installable
    SC-3  Runtime monitoring detects unexpected network calls from installed skills

---

## Attribution

Part of the ACRF framework: https://github.com/kannasekar-alt/ACRF
Presented at RSA Conference 2026.

Authors: Ravi Karthick Sankara Narayanan and Kanna Sekar

Licensed under Apache 2.0.
