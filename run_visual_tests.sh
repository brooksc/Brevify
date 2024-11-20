#!/bin/bash

# Create temporary files for outputs
TEST_OUTPUT="/tmp/test.out"
OLLAMA_LOG_FILE="/tmp/ollama_test.log"
ANALYSIS_OUTPUT="/tmp/analysis.out"

# Count initial lines in Ollama log
OLLAMA_LOG="$HOME/.ollama/logs/server.log"
INITIAL_LINES=$(wc -l < "$OLLAMA_LOG")

# Run pytest with sequential tests only
echo "Running visual analysis tests..."
PYTHONPATH=/Users/brooksc/Library/CloudStorage/Dropbox/py/Brevify pytest -v -s -m sequential tests/frontend/test_visual_analysis.py 2>&1 | tee $TEST_OUTPUT

# Get the pytest exit code
TEST_EXIT_CODE=${PIPESTATUS[0]}

echo -e "\nNew Ollama Server Logs:"
echo "=========================="
# Get only the new lines added during this test run
tail -n "+$((INITIAL_LINES + 1))" "$OLLAMA_LOG"
echo -e "\n==========================\n"

# Extract and display screenshot locations
echo -e "\nScreenshot Locations:"
grep "Saved .* screenshot to:" $TEST_OUTPUT | sed 's/^/- /'

echo -e "\nFiles saved:"
echo "- Test output: $TEST_OUTPUT"
echo "- Ollama logs: $OLLAMA_LOG_FILE"
echo "- Light mode screenshot: /tmp/brevify_light_mode.png"
echo "- Dark mode screenshot: /tmp/brevify_dark_mode.png"

# Exit with the original pytest exit code
exit $TEST_EXIT_CODE
