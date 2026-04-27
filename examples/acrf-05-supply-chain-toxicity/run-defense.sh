#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "ACRF-05 Supply Chain Toxicity Demo - PROTECTED"
echo "   Expected: Malicious skill blocked via hash mismatch. No data exfiltrated."
echo ""
docker compose --profile protected down --remove-orphans 2>/dev/null || true
docker compose --profile protected up --build --abort-on-container-exit
