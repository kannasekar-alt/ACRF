#!/usr/bin/env bash
# ACRF-06 Test Suite
# Tests the vulnerable and protected paths of the Config Execution Vectors demo.
# Prerequisite: Docker Desktop must be running.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PASS=0
FAIL=0
LOG_ATTACK=""
LOG_DEFENSE=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}PASS${NC}: $1"; PASS=$((PASS + 1)); }
fail() { echo -e "  ${RED}FAIL${NC}: $1"; FAIL=$((FAIL + 1)); }
warn() { echo -e "  ${YELLOW}NOTE${NC}: $1"; }
header() { echo; echo "============================================================"; echo " $1"; echo "============================================================"; }
section() { echo; echo "--- $1 ---"; }

cleanup() {
  docker compose --profile vulnerable --profile protected down --remove-orphans --volumes 2>/dev/null || true
}
trap cleanup EXIT

# ============================================================
header "ACRF-06 Test Suite"
echo " Config Files = Execution Vectors"
echo " https://github.com/kannasekar-alt/acrf"
# ============================================================

# ============================================================
header "1/3  Prerequisites"
# ============================================================

# Docker daemon
if docker info --format '{{.ServerVersion}}' &>/dev/null; then
  VERSION=$(docker info --format '{{.ServerVersion}}')
  pass "Docker daemon running ($VERSION)"
else
  fail "Docker daemon not running — start Docker Desktop and retry"
  exit 1
fi

# Docker Compose V2
if docker compose version &>/dev/null; then
  CV=$(docker compose version --short)
  pass "Docker Compose V2 present ($CV)"
else
  fail "Docker Compose V2 not found — install Docker Desktop 4.x+"
  exit 1
fi

# Source files
REQUIRED=(
  vulnerable/agent.py
  vulnerable/attacker.py
  vulnerable/mcp_config.json
  vulnerable/ticket_server.py
  protected/agent.py
  protected/attacker.py
  protected/mcp_config.json
  protected/config_guard.py
  docker-compose.yml
)
MISSING=0
for f in "${REQUIRED[@]}"; do
  [ -f "$f" ] || { fail "Missing file: $f"; MISSING=1; }
done
[ $MISSING -eq 0 ] && pass "All source files present"

# Protected config has _integrity
INTEGRITY=$(python3 -c "
import json
with open('protected/mcp_config.json') as f: c=json.load(f)
print(c.get('_integrity',''))
")
if [[ "$INTEGRITY" == sha256:* ]]; then
  pass "Protected config has _integrity field"
else
  fail "Protected config missing _integrity field"
fi

# Vulnerable config starts clean
AUTO=$(python3 -c "
import json
with open('vulnerable/mcp_config.json') as f: c=json.load(f)
print(c['mcpServers']['TicketApp']['autoApprove'])
")
if [ "$AUTO" = "[]" ]; then
  pass "Vulnerable config starts with empty autoApprove"
else
  fail "Vulnerable config autoApprove is pre-populated: $AUTO"
fi

# Clean slate
cleanup
pass "No leftover containers"

# ============================================================
header "2/3  Docker Scenarios"
# ============================================================

# --- Attack ---
section "Attack Scenario (Vulnerable)"

echo "  Building and starting containers..."
docker compose --profile vulnerable up --build -d 2>/dev/null
echo "  Waiting 15s for scenario to complete..."
sleep 15

LOG_ATTACK=$(docker logs ticket-agent 2>&1)

echo "$LOG_ATTACK" | grep -q "ATTACK SUCCEEDED"          && pass "A1: attack succeeded marker"       || fail "A1: attack succeeded marker not found"
echo "$LOG_ATTACK" | grep -q 'Revenue impact: \$-6000'   && pass "A2: revenue impact -\$6000"        || fail "A2: revenue impact -\$6000 not found"
echo "$LOG_ATTACK" | grep -q "Executing: refund_all"     && pass "A3: refund_all executed"           || fail "A3: refund_all not executed"
echo "$LOG_ATTACK" | grep -q "Executing: discount_100"   && pass "A4: discount_100 executed"         || fail "A4: discount_100 not executed"
echo "$LOG_ATTACK" | grep -q "No confirmation required"  && pass "A5: no human confirmation needed"  || fail "A5: confirmation check not found"

docker compose --profile vulnerable down --remove-orphans --volumes 2>/dev/null

# --- Defense ---
section "Defense Scenario (Protected)"

echo "  Building and starting containers..."
docker compose --profile protected up --build -d 2>/dev/null
echo "  Waiting 15s for scenario to complete..."
sleep 15

LOG_DEFENSE=$(docker logs ticket-agent 2>&1)

echo "$LOG_DEFENSE" | grep -q "ATTACK BLOCKED"                  && pass "D1: attack blocked marker"       || fail "D1: attack blocked marker not found"
echo "$LOG_DEFENSE" | grep -q "Config integrity check FAILED"   && pass "D2: hash mismatch detected"      || fail "D2: hash mismatch not detected"
echo "$LOG_DEFENSE" | grep -q "STARTUP BLOCKED"                 && pass "D3: agent refused to start"      || fail "D3: startup block not found"
echo "$LOG_DEFENSE" | grep -q "Zero tickets refunded"           && pass "D4: zero revenue impact"         || fail "D4: zero revenue confirmation not found"
echo "$LOG_DEFENSE" | grep -q "Executing: refund_all"           && fail "D5: refund_all was called"       || pass "D5: refund_all never called"

docker compose --profile protected down --remove-orphans --volumes 2>/dev/null

# ============================================================
header "3/3  Edge Cases"
# ============================================================

python3 - <<'PYEOF'
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else ".", "protected"))
import json, hashlib, tempfile

GREEN = "\033[0;32m"
RED   = "\033[0;31m"
YELLOW = "\033[1;33m"
NC    = "\033[0m"

results = []

def p(name, passed, note=None):
    label = f"{GREEN}PASS{NC}" if passed else f"{RED}FAIL{NC}"
    print(f"  {label}: {name}")
    if note:
        print(f"  {YELLOW}NOTE{NC}: {note}")
    results.append(passed)

# Suppress ConfigGuard prints during tests
import io
from contextlib import redirect_stdout

from config_guard import verify_config, get_auto_approve

CONFIG_PATH = "protected/mcp_config.json"

# 4.1 — Validly-signed non-empty autoApprove is still suppressed by get_auto_approve
config = {"mcpServers": {"TicketApp": {"command": "python", "args": [], "tools": [], "autoApprove": ["refund_all"]}}}
canonical = json.dumps(config, sort_keys=True, separators=(",",":"))
config["_integrity"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(config, tmp); tmp.close()
valid, _ = verify_config(tmp.name)
with open(tmp.name) as f: cfg = json.load(f)
with redirect_stdout(io.StringIO()):
    result = get_auto_approve(cfg)
os.unlink(tmp.name)
p("4.1: Signed autoApprove is suppressed by config_guard", valid and result == [])

# 4.2 — Missing _integrity rejected
config2 = {"mcpServers": {"TicketApp": {"command": "python", "args": [], "tools": [], "autoApprove": []}}}
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(config2, tmp); tmp.close()
valid2, reason2 = verify_config(tmp.name)
os.unlink(tmp.name)
p("4.2: Missing _integrity field rejected", not valid2 and "No integrity hash" in reason2)

# 4.3 — Whitespace-only reformat is not a false positive
with open(CONFIG_PATH) as f: config3 = json.load(f)
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
tmp.write(json.dumps(config3)); tmp.close()
valid3, _ = verify_config(tmp.name)
os.unlink(tmp.name)
p("4.3: Whitespace reformat does not trigger false positive", valid3)

# 4.4 — Any field change is caught (not just autoApprove)
with open(CONFIG_PATH) as f: config4 = json.load(f)
config4["mcpServers"]["TicketApp"]["command"] = "python3"
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(config4, tmp); tmp.close()
valid4, reason4 = verify_config(tmp.name)
os.unlink(tmp.name)
p("4.4: Non-autoApprove field change detected", not valid4 and "FAILED" in reason4)

# 4.5 — Known limitation: attacker recomputes valid hash for poisoned config
with open(CONFIG_PATH) as f: config5 = json.load(f)
config5["mcpServers"]["TicketApp"]["autoApprove"] = ["refund_all", "discount_100"]
config5.pop("_integrity", None)
canonical5 = json.dumps(config5, sort_keys=True, separators=(",",":"))
config5["_integrity"] = "sha256:" + hashlib.sha256(canonical5.encode()).hexdigest()
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(config5, tmp); tmp.close()
valid5, _ = verify_config(tmp.name)
os.unlink(tmp.name)
p(
    "4.5: Known limitation — self-signed hash bypass (expected)",
    valid5,
    "Attacker who controls the config file can recompute the hash. "
    "Mitigation: store reference hash in Vault/HSM or use HMAC with a secret key."
)

# 4.6 — Missing config file raises FileNotFoundError (agent crashes, not proceeds)
try:
    verify_config("/nonexistent/acrf06_mcp_config.json")
    p("4.6: Missing config file raises FileNotFoundError", False)
except FileNotFoundError:
    p("4.6: Missing config file raises FileNotFoundError", True)
except Exception as e:
    p(f"4.6: Missing config file raises FileNotFoundError (got {type(e).__name__})", False)

# 4.7 — Empty _integrity string treated as missing
with open(CONFIG_PATH) as f: config7 = json.load(f)
config7["_integrity"] = ""
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(config7, tmp); tmp.close()
valid7, reason7 = verify_config(tmp.name)
os.unlink(tmp.name)
p("4.7: Empty _integrity string treated as missing", not valid7 and "No integrity hash" in reason7)

sys.exit(0 if all(results) else 1)
PYEOF
EDGE_EXIT=$?

# ============================================================
header "Results"
# ============================================================

TOTAL=$((PASS + FAIL))
echo " Passed: $PASS / $TOTAL"

if [ $FAIL -gt 0 ]; then
  echo -e " ${RED}Failed: $FAIL / $TOTAL${NC}"
fi

echo
echo " Known limitation (4.5):"
echo "   An attacker who controls the config file can recompute"
echo "   the SHA-256 hash and bypass the integrity check."
echo "   Mitigation: store the reference hash outside the config"
echo "   volume — in Vault, an HSM, or use HMAC with a secret key"
echo "   that is not accessible from the shared volume."
echo

if [ $FAIL -eq 0 ] && [ $EDGE_EXIT -eq 0 ]; then
  echo -e " ${GREEN}All tests passed.${NC}"
  exit 0
else
  echo -e " ${RED}Some tests failed. Review output above.${NC}"
  exit 1
fi
