#!/usr/bin/env bash
# Claude Code wrapper for CHAI harness
# Reads the session prompt file and executes Claude Code

set -euo pipefail

PROMPT_FILE="${1:-}"
PROJECT_PATH="${2:-.}"

if [[ -z "$PROMPT_FILE" ]]; then
    echo "Usage: run_agent.sh <prompt_file> <project_path>"
    exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Prompt file not found: $PROMPT_FILE"
    exit 1
fi

# Read the prompt content and execute Claude Code in non-interactive mode
# Using -p for print mode (non-interactive) with --dangerously-skip-permissions
claude -p "$(cat "$PROMPT_FILE")" \
    --project "$PROJECT_PATH" \
    --dangerously-skip-permissions \
    --no-session-persistence
