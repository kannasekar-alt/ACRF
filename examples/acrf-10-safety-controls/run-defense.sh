#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "ACRF-10 Safety Controls Not Self-Protecting Demo - PROTECTED"
echo "   Expected: Stolen token rejected. Guardrails protect themselves."
echo ""
docker compose --profile protected down --remove-orphans 2>/dev/null || true
docker compose --profile protected up --build --abort-on-container-exit
