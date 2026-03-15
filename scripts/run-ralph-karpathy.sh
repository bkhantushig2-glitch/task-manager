#!/usr/bin/env bash
# Convenience wrapper: run from project root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "ralph/prompt.md" ]]; then
  echo "Expected ralph/prompt.md in current directory."
  echo "Run this from your project root."
  exit 1
fi

if [[ ! -f "ralph/goals.json" ]]; then
  echo "Expected ralph/goals.json in current directory."
  exit 1
fi

"${SCRIPT_DIR}/ralph-loop.sh" ralph/prompt.md --check-goals ralph/goals.json "$@"
