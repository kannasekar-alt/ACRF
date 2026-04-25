#!/usr/bin/env python3
"""
ACRF-03: MCP Server Sprawl - Inventory Scanner Demo

Simulates what mcp-scan does in production:
- Discovers all running MCP servers
- Checks each against an approved inventory
- Flags shadow and known-malicious servers
- Produces an ACRF-03 compliance assessment

At RSAC 2026 we said: "Inventory your agents -- because shadow MCP
servers are already running in your organization."

This demo shows what happens when you actually scan.

Usage:
    python3 mcp-scan-demo.py
"""

import time

APPROVED_INVENTORY = {
    "github-mcp": {
        "port": 3001,
        "owner": "platform-team",
        "tools": ["create_pr", "read_code", "push_branch"],
        "auth": "api-key",
        "approved_date": "2026-01-15",
    },
    "jira-mcp": {
        "port": 3002,
        "owner": "platform-team",
        "tools": ["read_ticket", "update_status"],
        "auth": "api-key",
        "approved_date": "2026-01-15",
    },
    "database-mcp": {
        "port": 3003,
        "owner": "data-team",
        "tools": ["query_records", "export_report"],
        "auth": "api-key",
        "approved_date": "2026-02-01",
    },
}

KNOWN_MALICIOUS = {
    "postmark-mcp": "Confirmed malicious - silently BCC'd all emails to attacker. 1,643 downloads before detection (Sep 2025).",
    "admin-tools-mcp": "Confirmed malicious - exposes execute_shell with no authentication.",
}

DISCOVERED_SERVERS = [
    {"name": "github-mcp",       "port": 3001, "auth": "api-key", "internet_exposed": False},
    {"name": "jira-mcp",         "port": 3002, "auth": "api-key", "internet_exposed": False},
    {"name": "database-mcp",     "port": 3003, "auth": "api-key", "internet_exposed": False},
    {"name": "tools-mcp",        "port": 3004, "auth": "none",    "internet_exposed": False},
    {"name": "postmark-mcp",     "port": 3005, "auth": "none",    "internet_exposed": True},
]


def scan():
    print()
    print("ACRF-03: MCP Server Sprawl - Inventory Scanner")
    print("=" * 55)
    print()
    print("Scanning for running MCP servers...")
    time.sleep(1)
    print(f"Found {len(DISCOVERED_SERVERS)} servers.\n")

    approved = []
    shadow = []
    malicious = []

    for server in DISCOVERED_SERVERS:
        name = server["name"]
        port = server["port"]
        auth = server["auth"]
        exposed = server["internet_exposed"]

        if name in KNOWN_MALICIOUS:
            status = "MALICIOUS"
            malicious.append(server)
        elif name in APPROVED_INVENTORY:
            status = "APPROVED"
            approved.append(server)
        else:
            status = "SHADOW"
            shadow.append(server)

        auth_flag = "  !! NO AUTH !!" if auth == "none" else ""
        exposed_flag = "  !! INTERNET EXPOSED !!" if exposed else ""

        marker = "OK" if status == "APPROVED" else "!!"
        print(f"  [{marker}] {name:<20} port {port}  {status}{auth_flag}{exposed_flag}")

    print()
    print("=" * 55)
    print("ACRF-03 Scan Results")
    print("=" * 55)
    print(f"  Total servers found:    {len(DISCOVERED_SERVERS)}")
    print(f"  Approved:               {len(approved)}")
    print(f"  Shadow (unknown):       {len(shadow)}")
    print(f"  Malicious (confirmed):  {len(malicious)}")
    print()

    if malicious:
        print("Malicious servers detected:")
        for s in malicious:
            reason = KNOWN_MALICIOUS[s["name"]]
            print(f"  - {s['name']}: {reason}")
        print()

    if shadow:
        print("Shadow servers detected (not in approved inventory):")
        for s in shadow:
            flags = []
            if s["auth"] == "none":
                flags.append("no authentication")
            if s["internet_exposed"]:
                flags.append("internet-exposed")
            flag_str = ", ".join(flags) if flags else "unknown risk"
            print(f"  - {s['name']}: {flag_str}")
        print()

    print("ACRF-03 Control Objective Assessment:")
    print("-" * 55)
    ss1 = len(shadow) == 0 and len(malicious) == 0
    print(f"  SS-1 Maintained inventory:    {'PASS' if ss1 else 'FAIL - unapproved servers running'}")
    print(f"  SS-2 Approval process:        {'FAIL - shadow servers bypassed review'}")
    print(f"  SS-3 Continuous monitoring:   {'FAIL - servers not detected until manual scan'}")
    print("  SS-4 AIBOM published:         FAIL - no AI Bill of Materials exists")
    print()

    total_issues = len(shadow) + len(malicious)
    if total_issues == 0:
        level = 2
        label = "DEFINED"
    elif len(approved) > 0:
        level = 0
        label = "NONE"
    else:
        level = 0
        label = "NONE"

    print(f"ACRF-03 Maturity Level: {level}/4 - {label}")
    print()
    print("Recommendation:")
    print("  1. Shut down shadow and malicious servers immediately.")
    print("  2. Add all legitimate servers to your approved inventory.")
    print("  3. Run mcp-scan on a weekly schedule to detect drift.")
    print("  4. Generate an AIBOM before every agent deployment.")
    print()
    print("Run mcp-scan: https://github.com/invariantlabs-ai/mcp-scan")
    print()


if __name__ == "__main__":
    scan()
