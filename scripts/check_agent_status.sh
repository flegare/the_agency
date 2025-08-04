#!/bin/bash

# --- Configuration ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
MAX_RETRIES=10
RETRY_DELAY=3

# --- Health Check Function ---
wait_for_health_check() {
    local agent_name=$1
    local port=$2
    echo -n "Checking health of ${YELLOW}${agent_name}${NC} on port ${YELLOW}${port}${NC}..."
    for ((i=1; i<=MAX_RETRIES; i++)); do
        if curl -sf "http://localhost:${port}/health" > /dev/null; then
            echo -e "${GREEN} HEALTHY${NC}"
            return 0
        fi
        if [ $i -lt $MAX_RETRIES ]; then
            echo -n "."
            sleep $RETRY_DELAY
        fi
    done
    echo -e "${RED} UNHEALTHY${NC}"
    return 1
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
    wait_for_health_check "$agent_name" "$port"
done < "$AGENT_PORTS_FILE"

echo -e "\n${GREEN}✅ Agent status check complete.${NC}"