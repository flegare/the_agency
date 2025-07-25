#!/bin/bash

# --- Configuration ---
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Banner ---
echo -e "${RED}###################################${NC}"
echo -e "#                                 #"
echo -e "#         STOPPING AGENTS         #"
echo -e "#                                 #"
echo -e "###################################${NC}"
echo ""

# --- Script Logic ---
echo -e "🛑 Stopping all running uvicorn agent processes..."

# Find and kill all uvicorn processes
PIDS=$(lsof -t -i:8000-8005)
if [ -n "$PIDS" ]; then
    kill -9 $PIDS
fi

# Clean up the old PID file if it exists
if [ -f ".agent_pids" ]; then
    rm .agent_pids
fi

echo ""
echo -e "${RED}✅ All agent processes have been terminated.${NC}"