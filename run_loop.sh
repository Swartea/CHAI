#!/bin/bash
# Auto-run harness in loop until all features complete or blocked

cd "$(dirname "$0")"

AGENT_CMD="/Users/swarteachou/Desktop/CHAI/run_agent.sh \"{prompt_path}\""
export AGENT_HARNESS_AGENT_COMMAND="$AGENT_CMD"

HARNESS_DIR="/Users/swarteachou/Desktop/wuxian/agent_harness"
REPO_PATH="/Users/swarteachou/Desktop/CHAI"

echo "========================================"
echo "Auto Harness Loop Started at $(date)"
echo "========================================"

while true; do
    echo "----------------------------------------"
    echo "Running session at $(date)"
    echo "----------------------------------------"

    OUTPUT=$(cd "$HARNESS_DIR" && python3 main.py run --repo-path "$REPO_PATH" 2>&1)
    echo "$OUTPUT"

    # Check for complete OR completed (output format: "session_id: status feature_id")
    if echo "$OUTPUT" | grep -qE "^[^:]+: (complete|completed) "; then
        # Check if actually done (no remaining features)
        # grep returns exit code 0 if found, 1 if not found
        if grep -q '"passes": false' "$REPO_PATH/feature_list.json" 2>/dev/null; then
            :  # There are remaining features, continue
        else
            echo "========================================"
            echo "ALL FEATURES COMPLETED at $(date)!"
            echo "========================================"
            break
        fi
    fi

    # Check for blocked
    if echo "$OUTPUT" | grep -q "status=blocked"; then
        echo "========================================"
        echo "BLOCKED - Baseline broken, needs manual intervention"
        echo "========================================"
        break
    fi

    echo "Sleeping 5 seconds before next session..."
    sleep 5
done

echo "Loop ended at $(date)"
