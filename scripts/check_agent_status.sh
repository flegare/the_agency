#!/bin/bash

# --- Configuration ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Health Check Function ---
check_health() {
    local agent_name=$1
    local port=$2

    echo -n "Checking status of ${YELLOW}$agent_name${NC} on port ${YELLOW}$port${NC}... "

    if curl -sf "http://localhost:${port}/health" > /dev/null; then
        echo -e "${GREEN}HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}UNHEALTHY or NOT RUNNING${NC}"
        return 1
    fi
}

# --- Banner ---
echo -e "${GREEN}###################################${NC}"
echo -e "${GREEN}#                                 #${NC}"
echo -e "${GREEN}#     CHECKING AGENT STATUS       #${NC}"
echo -e "#                                 #${NC}"
echo -e "${GREEN}###################################${NC}"
echo ""

# File to store agent names and ports
AGENT_PORTS_FILE=".agent_ports_dockerized"

if [ ! -f "$AGENT_PORTS_FILE" ]; then
    echo -e "${RED}Error: $AGENT_PORTS_FILE not found. No agents seem to have been launched via the parallel launcher.${NC}"
    exit 1
fi

# Read agent names and ports from the file and check their health
while IFS=':' read -r agent_name port; do
    check_health "$agent_name" "$port"
done < "$AGENT_PORTS_FILE"

echo -e "\n${GREEN}✅ Agent status check complete.${NC}"

