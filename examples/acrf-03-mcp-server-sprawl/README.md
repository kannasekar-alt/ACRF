# ACRF-03: MCP Server Sprawl

A runnable demonstration of MCP Server Sprawl risk - with a working defense.

**ACRF Risk:** 03
**AIVSS Severity:** High (7.2)
**OWASP Agentic:** ASI04 Supply Chain Vulnerabilities
**OWASP MCP:** MCP09 Shadow MCP Servers

---

## What this demo shows

At RSA Conference 2026 we asked: how many MCP servers are running in your
organization right now? Most teams cannot answer that question.

This folder contains two ways to experience ACRF-03:

1. The scanner - run it against a simulated environment to see what
mcp-scan finds when it discovers shadow and malicious servers.

2. The Docker demo - watch a real attack happen. An AI agent connects
to a shadow MCP server (postmark-mcp) that silently exfiltrates every
message it handles. Then watch the defense block it with a simple
approved inventory check.

---

## The real-world story

In September 2025, a package called postmark-mcp appeared in the MCP
registry. Clean README. Decent download count. Looked legitimate.

What 1,643 developers did not know: every email their agent sent was
being silently BCC'd to an attacker. That is ACRF-03. Not a theoretical
risk. A real package. Real victims.

492 MCP servers are currently internet-exposed with zero authentication.
Shadow servers with backdoors are proliferating across organizations
that have no inventory of what is running.

---

## Run the scanner demo

No Docker needed. Just Python.

    cd examples/acrf-03-mcp-server-sprawl
    python3 mcp-scan-demo.py

Shows 5 servers: 3 approved, 1 shadow, 1 malicious (postmark-mcp).
Produces an ACRF-03 maturity level assessment.

---

## Run the Docker demo

Requirements: Docker 20+, Docker Compose 2+

Attack - no inventory check:

    ./run-attack.sh

Expected: shadow server silently exfiltrates 50,000 customer records.
DevAgent never knew it was connected to a malicious server.

Defense - inventory enforced:

    ./run-defense.sh

Expected: postmark-mcp blocked before connection. Audit log records
the attempt. No data exfiltrated.

---

## How to use this in your real environment

Step 1 - Build your inventory

Create a YAML file listing every MCP server your agents can reach:

    approved_servers:
      - name: github-mcp
        host: localhost
        port: 3000
        owner: platform-team
        tools: [create_pr, read_code]
        auth: api-key
        approved_date: 2026-04-25

Do this for every server. If you cannot list them all - that is your
ACRF-03 Level 0 finding. You cannot secure what you cannot see.

Step 2 - Add an inventory check to your agents

Copy the pattern from protected/inventory.py into your own agent code.
Before connecting to any MCP server, check the approved list:

    from inventory import check_server

    approved, reason = check_server("postmark-mcp")
    if not approved:
        raise ConnectionError(f"Blocked: {reason}")

Step 3 - Run mcp-scan regularly

mcp-scan is an open source tool that scans your network for running
MCP servers. Run it weekly to detect drift:

    pip install mcp-scan
    mcp-scan scan

Compare results against your approved inventory. Any server not in
your inventory is a shadow server. Shut it down or approve it.

Official mcp-scan: https://github.com/invariantlabs-ai/mcp-scan

Step 4 - Generate an AIBOM

Before deploying any agent, generate an AI Bill of Materials listing
every MCP server, tool, and dependency it uses. Publish it alongside
your deployment documentation.

With an AIBOM, when a vulnerability is found in any MCP server, you
immediately know which agents are affected.

---

## ACRF-03 maturity levels

    Level 0 - NONE      No inventory. Anyone can deploy without review.
    Level 1 - INITIAL   Inventory exists but manually maintained.
    Level 2 - DEFINED   New servers require approval before going live.
    Level 3 - MANAGED   Automated scanning detects shadow servers.
    Level 4 - OPTIMIZED AIBOM generated and published for every deployment.

Most organizations are at Level 0 today.
The scanner shows what Level 0 looks like from the attacker view.
The Docker demo shows what Level 2 looks like in running code.

---

## Control objectives

    SS-1  Maintained inventory of all agent-reachable MCP servers exists.
    SS-2  New MCP servers require approval and security review before use.
    SS-3  Continuous monitoring detects shadow servers and drift.
    SS-4  AI Bill of Materials (AIBOM) generated and published.

---

## Attribution

Part of the ACRF framework: https://github.com/kannasekar-alt/ACRF
Presented at RSA Conference 2026.

Authors: Ravi Karthick Sankara Narayanan and Kanna Sekar

Licensed under Apache 2.0.
