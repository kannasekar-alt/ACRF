#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "ACRF-10 Safety Controls Not Self-Protecting Demo - VULNERABLE"
echo "   Expected: Stolen token disables all guardrails. Agent does anything."
echo ""
docker compose --profile vulnerable down --remove-orphans 2>/dev/null || true
docker compose --profile vulnerable up --build --abort-on-container-exit
