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

# Function to find an available port
find_available_port() {
    local start_port=$1
    local current_port=$start_port
    while true; do
        if ! lsof -i :$current_port -t > /dev/null; then
            echo $current_port
            return 0
        fi
        current_port=$((current_port + 1))
    done
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

# Base port for agents
PORT=7999

# File to store container IDs
CONTAINER_IDS_FILE=".agent_container_ids"
> $CONTAINER_IDS_FILE # Clear the file

# File to store agent names and ports
AGENT_PORTS_FILE=".agent_ports_dockerized"
> $AGENT_PORTS_FILE # Clear the file

# Collect all agent directories, separating the root_agent
ALL_AGENT_DIRS=()
ROOT_AGENT_DIR=""

# Collect all agent directories
AGENT_DIRS_RAW=$(find . -mindepth 2 -name Dockerfile -printf '%h\n' | sort)

# Filter agent directories based on TARGET_AGENT
for agent_dir in $AGENT_DIRS_RAW; do
    agent_name=$(basename $agent_dir)
    if [ -n "$TARGET_AGENT" ] && [ "$agent_name" != "$TARGET_AGENT" ]; then
        continue
    fi

    if [ "$agent_name" == "root_agent" ]; then
        ROOT_AGENT_DIR="$agent_dir"
    else
        ALL_AGENT_DIRS+=("$agent_dir")
    fi
done


declare -A AGENT_PORTS_MAP # Associative array to store agent_name:port

# Process non-root agents first
for agent_dir in "${ALL_AGENT_DIRS[@]}"; do
    agent_name=$(basename "$agent_dir")
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
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping.${NC}"
        continue # Skip to next agent if build fails
    fi

    # Find an available port for the current agent
    CURRENT_PORT=$(find_available_port $PORT)
    if [ -z "$CURRENT_PORT" ]; then
        echo -e "${RED}Error: Could not find an available port for ${agent_name}. Skipping.${NC}"
        continue
    fi
    # Run the Docker container
    echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$CURRENT_PORT${NC}..."
    container_id=$(docker run -d --network $NETWORK_NAME -p ${CURRENT_PORT}:8000 --name "$container_name" "$image_name")
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker container failed to start for $agent_name. Skipping.${NC}"
        PORT=$((CURRENT_PORT + 1)) # Update PORT even if run fails
        continue # Skip to next agent if run fails
    fi

    echo "$container_id" >> $CONTAINER_IDS_FILE
    echo "$agent_name:$CURRENT_PORT" >> $AGENT_PORTS_FILE
    AGENT_PORTS_MAP["$agent_name"]="$CURRENT_PORT" # Store agent name and its assigned port

    echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $CURRENT_PORT.${NC}"

    # Give the container a moment to start its internal server
    sleep 10

    # Wait for the agent to be healthy
    if ! wait_for_health_check "$agent_name" "$CURRENT_PORT"; then
        echo -e "${RED}Failed to start ${agent_name}. Continuing with next agent.${NC}"
    fi
    PORT=$((CURRENT_PORT + 1)) # Update PORT for the next search
done

# Process root_agent last
if [ -n "$ROOT_AGENT_DIR" ]; then
    agent_name=$(basename "$ROOT_AGENT_DIR")
    image_name="gemini-agent-${agent_name}"
    container_name="${agent_name}-dockerized"

    echo -e "\n--- Processing ${YELLOW}$agent_name${NC} (Root Agent) ---"

    # Stop and remove any existing container with the same name
    if [ "$(docker ps -aq -f name=^/${container_name}$)" ]; then
        echo "Stopping and removing existing container $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
    fi

    # Build the Docker image
    echo -e "Building image ${YELLOW}$image_name${NC}..."
    docker build -t "$image_name" "$ROOT_AGENT_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping.${NC}"
    else
        # Construct AGENT_HOSTS for root_agent using the collected ports
        AGENT_HOSTS=""
        for other_agent_name in "${!AGENT_PORTS_MAP[@]}"; do
            AGENT_HOSTS+="-e ${other_agent_name^^}_HOST=http://${other_agent_name}-dockerized:${AGENT_PORTS_MAP[$other_agent_name]} "
        done

        # Find an available port for the root agent
        CURRENT_ROOT_PORT=$(find_available_port $PORT)
        if [ -z "$CURRENT_ROOT_PORT" ]; then
            echo -e "${RED}Error: Could not find an available port for ${agent_name}. Skipping.${NC}"
        else
            PORT=$CURRENT_ROOT_PORT # Update PORT for the next search (though root is last)

            echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$CURRENT_ROOT_PORT${NC}..."
            container_id=$(docker run -d --network $NETWORK_NAME -p ${CURRENT_ROOT_PORT}:8000 $AGENT_HOSTS --name "$container_name" "$image_name")
            if [ $? -ne 0 ]; then
                echo -e "${RED}Error: Docker container failed to start for $agent_name.${NC}"
            else
                echo "$container_id" >> $CONTAINER_IDS_FILE
                echo "$agent_name:$CURRENT_ROOT_PORT" >> $AGENT_PORTS_FILE

                echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $CURRENT_ROOT_PORT.${NC}"

                # Give the container a moment to start its internal server
                sleep 10

                # Wait for the agent to be healthy
                if ! wait_for_health_check "$agent_name" "$CURRENT_ROOT_PORT"; then
                    echo -e "${RED}Failed to start ${agent_name}.${NC}"
                fi
            fi
            PORT=$((CURRENT_ROOT_PORT + 1)) # Update PORT for the next search (though root is last)
        fi
    fi
fi


echo -e "\n${GREEN}✅ All Dockerized agents processed. Check logs for details.${NC}"