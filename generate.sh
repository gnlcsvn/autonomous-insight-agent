#!/usr/bin/env bash
# Daily insight draft factory: scout -> research -> verify -> write -> gate (-> critic).
# Deterministic flow; LLM does the stages, code controls the pipeline and the gate.
# Usage: ./generate.sh [RUN_ID]    (RUN_ID defaults to today's date)
set -uo pipefail
cd "$(dirname "$0")"

# Never use the premium 1M-context window in unattended runs: stay on standard 200k
# (Claude Code auto-compacts instead). Fixes "Usage credits required for 1M context".
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1

CLAUDE="${CLAUDE_BIN:-/home/gianluca/.local/bin/claude}"
RUN_ID="${1:-$(date +%F)}"
RUN_DATE="$RUN_ID"
DATE_HUMAN="$(date -d "$RUN_ID" "+%b %-d, %Y" 2>/dev/null || echo "$RUN_ID")"
SLUG=""

RUN_DIR="runs/$RUN_ID"
mkdir -p "$RUN_DIR"
LOG="$RUN_DIR/log.txt"
echo "=== run $RUN_ID @ $(date) ===" | tee -a "$LOG"

# Models: cheaper for scout/research/write/critic, strong for verification.
M_SCOUT=sonnet; M_RESEARCH=sonnet; M_VERIFY=opus; M_WRITE=sonnet; M_CRITIC=sonnet
TOOLS="Read,Write,Edit,WebSearch,WebFetch,Glob,Grep"

jget() { python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d$2)" "$1" 2>/dev/null; }

# Halt the pipeline if a stage did not produce its expected artifact (a stage can
# error yet exit 0; don't let a silent failure flow downstream).
require_file() {
  if [ ! -s "$1" ]; then
    echo "ABORT: expected artifact '$1' missing after $2 stage (likely an API/tool error; see log)." | tee -a "$LOG"
    exit 2
  fi
}

run_stage() {
  local name="$1" model="$2" maxturns="$3" promptfile="$4" prompt
  prompt="$(sed -e "s|{{RUN_ID}}|$RUN_ID|g" -e "s|{{RUN_DATE}}|$RUN_DATE|g" \
                -e "s|{{DATE_HUMAN}}|$DATE_HUMAN|g" -e "s|{{SLUG}}|$SLUG|g" "$promptfile")"
  prompt="$prompt

RUN CONTEXT: RUN_ID=$RUN_ID  RUN_DATE=$RUN_DATE  DATE_HUMAN=$DATE_HUMAN  SLUG=${SLUG:-<set after scout>}
Working directory is the project root. Use the exact relative paths above. Write only the specified files."
  echo "[$(date +%T)] >>> $name (model=$model, max-turns=$maxturns)" | tee -a "$LOG"
  "$CLAUDE" --model "$model" -p "$prompt" \
    --permission-mode acceptEdits --allowedTools "$TOOLS" --max-turns "$maxturns" \
    >>"$LOG" 2>&1
  echo "[$(date +%T)] <<< $name done (exit $?)" | tee -a "$LOG"
}

# 1) Scout
run_stage scout "$M_SCOUT" 18 prompts/1-scout.md
TOPIC_SLUG="$(jget "$RUN_DIR/topic.json" "['slug']")"
if [ -z "$TOPIC_SLUG" ] || [ "$TOPIC_SLUG" = "none" ]; then
  echo "No topic found today; nothing to draft." | tee -a "$LOG"; exit 0
fi
SLUG="$RUN_ID-$TOPIC_SLUG"
echo "topic: $SLUG" | tee -a "$LOG"

# 2) Research  3) Verify
run_stage research "$M_RESEARCH" 30 prompts/2-research.md
require_file "$RUN_DIR/claims.json" research
run_stage verify   "$M_VERIFY"   30 prompts/3-verify.md
require_file "$RUN_DIR/verified.json" verify

# 4) Write
run_stage write "$M_WRITE" 24 prompts/4-write.md

# 5) Gate (code). Critic only on a fixable failure.
python3 scripts/gate.py "$RUN_ID" "$SLUG" || true
PASSED="$(jget "$RUN_DIR/gate.json" "['passed']")"
HELD="$(jget "$RUN_DIR/gate.json" "['held']")"
if [ "$PASSED" != "True" ] && [ "$HELD" != "True" ]; then
  echo "gate failed; one grounded critic pass" | tee -a "$LOG"
  run_stage critic "$M_CRITIC" 16 prompts/5-critic.md
  python3 scripts/gate.py "$RUN_ID" "$SLUG" || true
fi

# Record the topic so future runs don't repeat it (unless it was held/abstained).
if [ "$(jget "$RUN_DIR/gate.json" "['held']")" != "True" ]; then
  python3 - "$SLUG" "$RUN_ID" <<'PY'
import json, sys, pathlib
slug, run_id = sys.argv[1], sys.argv[2]
p = pathlib.Path("state/used-topics.json")
d = json.loads(p.read_text()) if p.exists() else {"used": []}
title = ""
try:
    title = json.loads(pathlib.Path(f"public/drafts/{slug}/meta.json").read_text()).get("title", "")
except Exception:
    pass
if not any(u.get("slug") == slug for u in d.get("used", [])):
    d.setdefault("used", []).append({"slug": slug, "title": title, "status": "draft", "date": run_id})
    p.write_text(json.dumps(d, indent=2))
    print("used-topics += " + slug)
PY
fi

# Rebuild the review-queue grid
python3 scripts/build-index.py | tee -a "$LOG"
echo "=== run $RUN_ID complete: $SLUG (passed=$(jget "$RUN_DIR/gate.json" "['passed']"), confidence=$(jget "$RUN_DIR/gate.json" "['confidence']")) ===" | tee -a "$LOG"
