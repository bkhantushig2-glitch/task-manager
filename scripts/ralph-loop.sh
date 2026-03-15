#!/usr/bin/env bash
# Ralph Loop Runner (Karpathy-friendly)
# Runs Claude Code in fresh-context iterations and stops when verification state is complete.
set -euo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
CYAN=$'\033[0;36m'
NC=$'\033[0m'

MAX_ITERATIONS=20
DELAY=3
TIMEOUT_WARN=600
CHECK_PRD=""
CHECK_GOALS=""
CHECK_FILE=""
PROMPT_FILE=""
LOG_DIR="$HOME/.ralph/logs"
mkdir -p "$LOG_DIR"

usage() {
  cat <<'USAGE'
Ralph Loop Runner

Usage:
  ralph-loop.sh <prompt.md> [options]

Options:
  -m, --max <n>         Maximum iterations (default: 20, 0 = unlimited)
  -d, --delay <seconds> Delay between iterations (default: 3)
  --check-prd <file>    Stop when all prd.json tasks are complete (no "passes": false)
  --check-goals <file>  Stop when all goals.json goals have status "passed"
  --check-file <file>   Stop when file contains RALPH_COMPLETE
  -h, --help            Show help

Examples:
  ./scripts/ralph-loop.sh ralph/prompt.md --check-goals ralph/goals.json
  ./scripts/ralph-loop.sh ralph/prompt.md --check-prd ralph/prd.json --max 50
USAGE
}

log() { echo -e "${BLUE}[ralph]${NC} $1"; }
success() { echo -e "${GREEN}[ralph]${NC} $1"; }
warn() { echo -e "${YELLOW}[ralph]${NC} $1"; }
fail() { echo -e "${RED}[ralph]${NC} $1"; }

format_elapsed() {
  local secs=$1
  printf "%02d:%02d" "$((secs / 60))" "$((secs % 60))"
}

check_goals_complete() {
  local file="$1"
  python3 - "$file" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

goals = data.get('goals', [])
if not goals:
    raise SystemExit(1)

pending = [g for g in goals if g.get('status') != 'passed']
raise SystemExit(0 if not pending else 1)
PY
}

check_complete() {
  if [[ -n "$CHECK_PRD" ]] && [[ -f "$CHECK_PRD" ]]; then
    if ! rg -q '"passes"\s*:\s*false' "$CHECK_PRD"; then
      success "All PRD tasks complete."
      return 0
    fi
  fi

  if [[ -n "$CHECK_GOALS" ]] && [[ -f "$CHECK_GOALS" ]]; then
    if check_goals_complete "$CHECK_GOALS"; then
      success "All goals are passed."
      return 0
    fi
  fi

  if [[ -n "$CHECK_FILE" ]] && [[ -f "$CHECK_FILE" ]]; then
    if rg -q 'RALPH_COMPLETE' "$CHECK_FILE"; then
      success "Completion marker found."
      return 0
    fi
  fi

  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -m|--max)
      MAX_ITERATIONS="$2"
      shift 2
      ;;
    -d|--delay)
      DELAY="$2"
      shift 2
      ;;
    --check-prd)
      CHECK_PRD="$2"
      shift 2
      ;;
    --check-goals)
      CHECK_GOALS="$2"
      shift 2
      ;;
    --check-file)
      CHECK_FILE="$2"
      shift 2
      ;;
    -* )
      fail "Unknown option: $1"
      usage
      exit 1
      ;;
    *)
      if [[ -z "$PROMPT_FILE" ]]; then
        PROMPT_FILE="$1"
      else
        fail "Unexpected argument: $1"
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$PROMPT_FILE" ]]; then
  fail "No prompt file supplied."
  usage
  exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  fail "Prompt file not found: $PROMPT_FILE"
  exit 1
fi

PROMPT_FILE="$(realpath "$PROMPT_FILE")"

if ! command -v claude >/dev/null 2>&1; then
  fail "claude CLI not found in PATH."
  exit 1
fi

if [[ -n "$CHECK_GOALS" ]] && [[ ! -f "$CHECK_GOALS" ]]; then
  warn "Goals file not found yet: $CHECK_GOALS"
fi
if [[ -n "$CHECK_PRD" ]] && [[ ! -f "$CHECK_PRD" ]]; then
  warn "PRD file not found yet: $CHECK_PRD"
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  warn "Current directory is not a git repository."
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}         ${YELLOW}Ralph Loop${NC} - Fresh Context Per Iteration         ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
log "Prompt: $PROMPT_FILE"
log "Max iterations: $(if [[ "$MAX_ITERATIONS" -eq 0 ]]; then echo unlimited; else echo "$MAX_ITERATIONS"; fi)"
[[ -n "$CHECK_GOALS" ]] && log "Goal check: $CHECK_GOALS"
[[ -n "$CHECK_PRD" ]] && log "PRD check: $CHECK_PRD"
[[ -n "$CHECK_FILE" ]] && log "Marker check: $CHECK_FILE"
log "Logs: $LOG_DIR"
warn "Ctrl+C to stop"

ITERATION=0
START_TIME=$(date +%s)

while true; do
  ITERATION=$((ITERATION + 1))

  if [[ "$MAX_ITERATIONS" -gt 0 ]] && [[ "$ITERATION" -gt "$MAX_ITERATIONS" ]]; then
    warn "Reached max iterations ($MAX_ITERATIONS)."
    break
  fi

  if [[ "$ITERATION" -gt 1 ]] && check_complete; then
    break
  fi

  LOG_FILE="$LOG_DIR/$(date '+%Y-%m-%d_%H%M%S')_iter${ITERATION}.log"
  ITER_START=$SECONDS

  echo ""
  echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
  echo -e "${GREEN} ITERATION $ITERATION${NC} - $(date '+%Y-%m-%d %H:%M:%S')"
  echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"

  (
    sleep "$TIMEOUT_WARN"
    echo -e "${YELLOW}[ralph] Iteration $ITERATION is still running after 10 minutes.${NC}"
    while true; do
      sleep 300
      echo -e "${YELLOW}[ralph] Iteration $ITERATION still running...${NC}"
    done
  ) &
  TIMER_PID=$!

  trap 'kill $TIMER_PID 2>/dev/null || true' EXIT

  set +e
  cat "$PROMPT_FILE" | claude -p --dangerously-skip-permissions 2>&1 | tee "$LOG_FILE"
  EXIT_CODE=${PIPESTATUS[1]}
  set -e

  kill "$TIMER_PID" 2>/dev/null || true
  trap - EXIT

  ITER_ELAPSED=$((SECONDS - ITER_START))
  ITER_TIME=$(format_elapsed "$ITER_ELAPSED")

  echo ""
  echo -e "${GREEN}[${ITER_TIME}]${NC} Iteration $ITERATION finished (exit: $EXIT_CODE)"
  log "Saved log: $LOG_FILE"

  if check_complete; then
    break
  fi

  if [[ "$DELAY" -gt 0 ]]; then
    log "Sleeping ${DELAY}s before next iteration..."
    sleep "$DELAY"
  fi
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                          LOOP COMPLETE${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
success "Iterations: $ITERATION"
success "Duration: $((DURATION / 60))m $((DURATION % 60))s"
success "Logs: $LOG_DIR"

if git rev-parse --git-dir >/dev/null 2>&1; then
  log "Recent commits:"
  git log --oneline -5 || true
fi
