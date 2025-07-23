#!/bin/bash

echo "Stopping all running uvicorn agent processes..."

# Find and kill all uvicorn processes related to our agents.
# The -f flag matches against the full command line, ensuring we only kill our agent servers.
pkill -f "uvicorn --host 0.0.0.0"

# Clean up the old PID file if it exists
if [ -f ".agent_pids" ]; then
    rm .agent_pids
fi

echo "All agent processes have been terminated."