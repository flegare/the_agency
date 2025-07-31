#!/bin/bash

# --- Configuration ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Health Check Function ---
wait_for_health_check() {
    local agent_name=$1
    local port=$2
    local retries=10
    local wait_time=3

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
echo -e "${GREEN}###################################${NC}"
echo -e "${GREEN}#                                 #${NC}"
echo -e "${GREEN}#     STARTING DOCKERIZED AGENTS  #${NC}"
echo -e "#                                 #${NC}"
echo -e "${GREEN}###################################${NC}"
echo ""

# --- Script Logic ---
mkdir -p logs

# Create a custom Docker network for inter-agent communication
NETWORK_NAME="gemini_agents_network"
if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
    docker network create $NETWORK_NAME > /dev/null
fi

# Base port for agents
PORT=8000

# File to store container IDs
CONTAINER_IDS_FILE=".agent_container_ids"
> $CONTAINER_IDS_FILE # Clear the file

# File to store agent names and ports
AGENT_PORTS_FILE=".agent_ports_dockerized"
> $AGENT_PORTS_FILE # Clear the file

# Find all agent directories (containing a Dockerfile)
for agent_dir in $(find . -mindepth 2 -name Dockerfile -printf '%h\n' | sort); do
    agent_name=$(basename $agent_dir)
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
    docker build -t "$image_name" "$agent_dir"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name.${NC}"
        continue
    fi

    # Run the Docker container
    echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$PORT${NC}..."
    
    # Collect all agent container names to pass to the root_agent
    AGENT_HOSTS=""
    if [ "$agent_name" == "root_agent" ]; then
        # Pre-collect all agent names for the root_agent
        for other_agent_dir in $(find . -mindepth 2 -name Dockerfile -printf '%h\n' | sort); do
            other_agent_name=$(basename $other_agent_dir)
            if [ "$other_agent_name" != "root_agent" ]; then
                AGENT_HOSTS+="-e ${other_agent_name^^}_HOST=${other_agent_name}-dockerized "
            fi
        done
        container_id=$(docker run -d --network $NETWORK_NAME -p ${PORT}:8000 $AGENT_HOSTS --name "$container_name" "$image_name")
    else
        container_id=$(docker run -d --network $NETWORK_NAME -p ${PORT}:8000 --name "$container_name" "$image_name")
    fi
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker container failed to start for $agent_name.${NC}"
        continue
    fi

    echo "$container_id" >> $CONTAINER_IDS_FILE
    echo "$agent_name:$PORT" >> $AGENT_PORTS_FILE

    echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $PORT.${NC}"

    # Give the container a moment to start its internal server
    sleep 5

    # Wait for the agent to be healthy
    if ! wait_for_health_check "$agent_name" "$PORT"; then
        echo -e "${RED}Failed to start ${agent_name}. Continuing with next agent.${NC}"
    fi

    # Increment the port for the next agent
    PORT=$((PORT + 1))
done

echo -e "\n${GREEN}✅ All Dockerized agents processed. Check logs for details.${NC}"
