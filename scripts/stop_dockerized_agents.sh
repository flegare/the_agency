#!/bin/bash

# --- Configuration ---
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Banner ---
echo -e "${RED}###################################${NC}"
echo -e "#                                 #"
echo -e "#     STOPPING DOCKERIZED AGENTS  #"
echo -e "#                                 #"
echo -e "###################################${NC}"
echo ""

# --- Script Logic ---
CONTAINER_IDS_FILE=".agent_container_ids"

if [ -f "$CONTAINER_IDS_FILE" ]; then
    echo -e "🛑 Stopping and removing Dockerized agent containers..."
    while IFS= read -r container_id;
    do
        if [ -n "$container_id" ]; then
            echo -e "Stopping and removing container ${YELLOW}$container_id${NC}..."
            docker stop $container_id > /dev/null 2>&1
            docker rm $container_id > /dev/null 2>&1
        fi
    done < "$CONTAINER_IDS_FILE"
    rm "$CONTAINER_IDS_FILE"
else
    echo -e "${YELLOW}No .agent_container_ids file found. No Dockerized agents to stop.${NC}"
fi

# Also try to stop any containers with the naming convention
echo -e "Attempting to stop any remaining 'gemini-agent-' containers..."



# Clean up the agent_ports_dockerized file
AGENT_PORTS_FILE=".agent_ports_dockerized"
if [ -f "$AGENT_PORTS_FILE" ]; then
    rm "$AGENT_PORTS_FILE"
fi

echo -e "
${RED}✅ All Dockerized agent processes have been terminated and cleaned up.${NC}"

# Remove the custom Docker network
docker network rm $NETWORK_NAME > /dev/null 2>&1

# Remove the custom Docker network
docker network rm $NETWORK_NAME > /dev/null 2>&1
