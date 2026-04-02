#!/usr/bin/env bash
# Claude Code wrapper for CHAI harness
# Reads the session prompt file and executes Claude Code

set -euo pipefail

PROMPT_FILE="${1:-}"

if [[ -z "$PROMPT_FILE" ]]; then
    echo "Usage: run_agent.sh <prompt_file>"
    exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Prompt file not found: $PROMPT_FILE"
    exit 1
fi

# Read the prompt content and execute Claude Code in non-interactive mode
# Claude Code runs in current working directory (set by harness via cwd parameter)
claude -p "$(cat "$PROMPT_FILE")" \
    --dangerously-skip-permissions \
    --no-session-persistence
