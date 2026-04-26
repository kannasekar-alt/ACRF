#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "ACRF-04 Memory Poisoning Demo - VULNERABLE"
echo "   Expected: Attacker poisons memory store. Agent grants unauthorized access."
echo ""
docker compose --profile vulnerable down --remove-orphans 2>/dev/null || true
docker compose --profile vulnerable up --build --abort-on-container-exit
