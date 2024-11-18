#!/bin/bash

# Set error handling
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Add project root to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Print section header
print_header() {
    echo
    echo "================================"
    echo "$1"
    echo "================================"
    echo
}

# Run frontend tests
run_frontend_tests() {
    print_header "Running Frontend Tests"
    if [ -f "package.json" ]; then
        echo "Running frontend tests..."
        /opt/homebrew/Cellar/node/23.2.0_1/libexec/bin/npm test
    fi
}

# Run backend tests
run_backend_tests() {
    print_header "Running Backend Tests"
    echo "Running Python backend tests..."
    python -m pytest tests/backend/test_youtube_api.py -v
}

# Main execution
print_header "Starting Test Suite"

# Run tests
run_frontend_tests
run_backend_tests

print_header "All Tests Completed"
