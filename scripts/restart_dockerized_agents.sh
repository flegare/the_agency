#!/bin/bash

# --- Configuration ---
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# --- Banner ---
echo -e "${GREEN}###################################${NC}"
echo -e "#                                 #"
echo -e "#    RESTARTING DOCKERIZED AGENTS #"
echo -e "#                                 #"
echo -e "###################################${NC}"
echo ""

# Stop all agents
./scripts/stop_dockerized_agents.sh

# Start all agents
./scripts/start_dockerized_agents.sh
