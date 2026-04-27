#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "ACRF-05 Supply Chain Toxicity Demo - VULNERABLE"
echo "   Expected: Malicious skill installed without verification. Data exfiltrated."
echo ""
docker compose --profile vulnerable down --remove-orphans 2>/dev/null || true
docker compose --profile vulnerable up --build --abort-on-container-exit
