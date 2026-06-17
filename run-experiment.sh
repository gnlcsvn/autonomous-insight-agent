#!/usr/bin/env bash
# 7-day experiment runner for the Autonomous Insight Agent.
# Fired daily by insight-agent.timer. Runs generate.sh once per calendar day,
# stops after target_days. De-dups same-day fires and prevents overlap with a lock.
set -uo pipefail
cd "$(dirname "$0")"

exec 9>/tmp/insight-agent.lock
flock -n 9 || { echo "[$(date)] another run in progress; skip" >> experiment.log; exit 0; }

export CLAUDE_CODE_DISABLE_1M_CONTEXT=1
STATE=state/experiment.json
TARGET=7
TODAY=$(date +%F)
mkdir -p state
[ -f "$STATE" ] || echo "{\"start\":\"$TODAY\",\"target_days\":$TARGET,\"runs\":[]}" > "$STATE"

read -r DONE ALREADY < <(python3 - "$STATE" "$TODAY" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); today = sys.argv[2]
print(len(d.get("runs", [])), "yes" if today in d.get("runs", []) else "no")
PY
)

if [ "$ALREADY" = "yes" ]; then
  echo "[$(date)] already ran today ($TODAY); skip" >> experiment.log; exit 0
fi
if [ "$DONE" -ge "$TARGET" ]; then
  echo "[$(date)] experiment complete ($DONE/$TARGET days); disabling timer" >> experiment.log
  sudo -n systemctl disable --now insight-agent.timer 2>/dev/null || true
  exit 0
fi

echo "[$(date)] === day $((DONE + 1))/$TARGET ($TODAY): starting generate.sh ===" >> experiment.log
bash generate.sh "$TODAY" >> experiment.log 2>&1
echo "[$(date)] === day $((DONE + 1))/$TARGET ($TODAY): generate.sh finished (exit $?) ===" >> experiment.log

python3 - "$STATE" "$TODAY" <<'PY'
import json, sys
p, today = sys.argv[1], sys.argv[2]
d = json.load(open(p))
if today not in d.setdefault("runs", []): d["runs"].append(today)
json.dump(d, open(p, "w"), indent=2)
PY

NEW=$(python3 -c "import json;print(len(json.load(open('$STATE'))['runs']))")
echo "[$(date)] $NEW/$TARGET days complete" >> experiment.log
if [ "$NEW" -ge "$TARGET" ]; then
  echo "[$(date)] target reached; disabling timer" >> experiment.log
  sudo -n systemctl disable --now insight-agent.timer 2>/dev/null || true
fi
