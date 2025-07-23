#!/bin/bash

# --- Configuration ---
# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Banner ---
echo -e "${RED}###################################${NC}"
echo -e "${RED}#                                 #${NC}"
echo -e "${RED}#         STOPPING AGENTS         #${NC}"
echo -e "${RED}#                                 #${NC}"
echo -e "${RED}###################################${NC}"
echo ""

# --- Script Logic ---
echo -e "🛑 Stopping all running ${YELLOW}uvicorn${NC} agent processes..."

# Find and kill all uvicorn processes related to our agents.
pkill -f "uvicorn --host 0.0.0.0"

# Clean up the old PID file if it exists
if [ -f ".agent_pids" ]; then
    rm .agent_pids
fi

echo ""
echo -e "${RED}✅ All agent processes have been terminated.${NC}"
