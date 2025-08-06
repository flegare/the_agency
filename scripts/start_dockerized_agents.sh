#!/bin/bash

# --- Co        figuration ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Health Check Function ---
wait_for_health_check() {
    local agent_name=$1
    local port=$2
    local retries=15
    local wait_time=10

    echo "Waiting for $agent_name to be healthy on port $port..."

    for ((i=0; i<retries; i++)); do
        if curl -sf "http://localhost:${port}/health" > /dev/null; then
            echo -e "${GREEN}${agent_name} is healthy.${NC}"
            return 0
        fi
        echo "Attempt $((i+1))/$retries: $agent_name not ready yet. Waiting ${wait_time}s..."
        sleep $wait_time
    done

    echo -e "${RED}Error: Timed out waiting for $agent_name to become healthy.${NC}"
    echo "Dumping logs for container ${agent_name}-dockerized:"
    docker logs "${agent_name}-dockerized"
    return 1
}

# --- Banner ---
# Define colors for output
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
NC="\033[0m" # No Color

echo -e "${GREEN}###################################${NC}"
echo -e "${GREEN}#                                 #${NC}"
echo -e "${GREEN}#     STARTING DOCKERIZED AGENTS  #${NC}"
echo -e "${GREEN}#                                 #${NC}"
echo -e "${GREEN}###################################${NC}"
echo ""

# --- Script Logic ---
mkdir -p logs

# Stop and remove all existing gemini-agent-* containers
echo -e "${YELLOW}Stopping and removing all existing gemini-agent-* containers...${NC}"
docker ps -aq -f name=^/gemini-agent- | xargs docker stop > /dev/null 2>&1
docker ps -aq -f name=^/gemini-agent- | xargs docker rm > /dev/null 2>&1

# Prune all stopped containers and unused networks to free up ports
echo -e "${YELLOW}Pruning stopped containers and unused networks...${NC}"
docker container prune -f > /dev/null
docker network prune -f > /dev/null
echo -e "${GREEN}Cleaned up existing containers and networks.${NC}"

# Create a custom Docker network for inter-agent communication
NETWORK_NAME="gemini_agents_network"
if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
    docker network create $NETWORK_NAME > /dev/null
fi

# File to store container IDs
CONTAINER_IDS_FILE=".agent_container_ids"
> $CONTAINER_IDS_FILE # Clear the file

# File to store agent names and ports
AGENT_PORTS_FILE=".agent_ports_dockerized"
> $AGENT_PORTS_FILE # Clear the file

# Associative array to store agent_name:port
declare -A AGENT_PORTS_MAP

# Read agent configurations from agents.conf
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^\s*# ]] || [[ -z "$line" ]]; then
        continue
    fi

    # Parse agent path and port
    AGENT_PATH=$(echo "$line" | awk '{print $1}')
    PORT=$(echo "$line" | awk '{print $2}')
    
    agent_name=$(basename "$AGENT_PATH")
    image_name="gemini-agent-${agent_name}"
    container_name="${agent_name}-dockerized"

    echo -e "\n--- Processing ${YELLOW}$agent_name${NC} ---"

    # Stop and remove any existing container with the same name
    if [ "$(docker ps -aq -f name=^/${container_name}$)" ]; then
        echo "Stopping and removing existing container $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
    fi

    # Build the Docker image
    echo -e "Building image ${YELLOW}$image_name${NC}..."
    docker build -t "$image_name" "$AGENT_PATH"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping.${NC}"
        continue # Skip to next agent if build fails
    fi

    # Run the Docker container
    echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$PORT${NC}..."
    container_id=$(docker run -d --network $NETWORK_NAME -p ${PORT}:8000 --name "$container_name" "$image_name")
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker container failed to start for $agent_name. Skipping.${NC}"
        continue # Skip to next agent if run fails
    fi

    echo "$container_id" >> $CONTAINER_IDS_FILE
    echo "$agent_name:$PORT" >> $AGENT_PORTS_FILE
    AGENT_PORTS_MAP["$agent_name"]="$PORT" # Store agent name and its assigned port

    echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $PORT.${NC}"

    # Wait for the agent to be healthy
    if ! wait_for_health_check "$agent_name" "$PORT"; then
        echo -e "${RED}Failed to start ${agent_name}. Continuing with next agent.${NC}"
    fi
done < "scripts/agents.conf"

# Restart root_agent with agent hosts
if [[ -v AGENT_PORTS_MAP["root_agent"] ]]; then
    agent_name="root_agent"
    port=${AGENT_PORTS_MAP["root_agent"]}
    image_name="gemini-agent-${agent_name}"
    container_name="${agent_name}-dockerized"

    echo -e "\n--- Restarting ${YELLOW}$agent_name${NC} with other agent hosts ---"

    # Stop the running root_agent container
    echo "Stopping existing container $container_name..."
    docker stop "$container_name" > /dev/null
    docker rm "$container_name" > /dev/null

    # Construct AGENT_HOSTS for root_agent using the collected ports
    AGENT_HOSTS=""
    for other_agent_name in "${!AGENT_PORTS_MAP[@]}"; do
        if [ "$other_agent_name" != "root_agent" ]; then
            AGENT_HOSTS+="-e ${other_agent_name^^}_HOST=http://${other_agent_name}-dockerized:8000 "
        fi
    done

    # Run the Docker container
    echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$port${NC}..."
    container_id=$(docker run -d --network $NETWORK_NAME -p ${port}:8000 $AGENT_HOSTS --name "$container_name" "$image_name")
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker container failed to start for $agent_name.${NC}"
    else
        echo "$container_id" >> $CONTAINER_IDS_FILE
        echo "$agent_name:$port" >> $AGENT_PORTS_FILE

        echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $port.${NC}"

        # Wait for the agent to be healthy
        if ! wait_for_health_check "$agent_name" "$port"; then
            echo -e "${RED}Failed to start ${agent_name}.${NC}"
        fi
    fi
fi



echo -e "\n${GREEN}✅ All Dockerized agents processed. Check logs for details.${NC}"