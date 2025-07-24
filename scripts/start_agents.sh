#!/bin/bash

# --- Configuration ---
# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Banner ---
echo -e "${GREEN}###################################${NC}"
echo -e "${GREEN}#                                 #${NC}"
echo -e "${GREEN}#        STARTING AGENTS          #${NC}"
echo -e "${GREEN}#                                 #${NC}"
echo -e "${GREEN}###################################${NC}"
echo ""

# --- Script Logic ---
# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment
source .venv/bin/activate

# Base port for agents
PORT=8000

# File to store PIDs
PID_FILE=".agent_pids"
> $PID_FILE # Clear the PID file

# Find all agent directories (containing requirements.txt)
for agent_dir in $(find . -mindepth 2 -name requirements.txt -printf '%h\n'); do
    agent_name=$(basename $agent_dir)
    echo -e "🚀 Starting ${YELLOW}$agent_name${NC} on port ${YELLOW}$PORT${NC}..."

    # Start the agent in the background using nohup
    (cd "$agent_dir" && nohup uvicorn main:app --host 0.0.0.0 --port $PORT > "../logs/${agent_name}.log" 2>&1 &)
    
    # Save the PID
    echo $! >> $PID_FILE

    # Increment the port for the next agent
    PORT=$((PORT + 1))
done

echo ""
echo -e "${GREEN}✅ All agents started. Logs are in the 'logs' directory.${NC}"