#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "ACRF-04 Memory Poisoning Demo - PROTECTED"
echo "   Expected: Memory tampering detected. Access denied. Alert raised."
echo ""
docker compose --profile protected down --remove-orphans 2>/dev/null || true
docker compose --profile protected up --build --abort-on-container-exit
