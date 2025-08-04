#!/bin/bash

# --- Configuration ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
MAX_RETRIES=10
RETRY_DELAY=3
PORT=8000
NETWORK_NAME="gemini-agents-network"
AGENT_PORTS_FILE=".agent_ports_dockerized"
CONTAINER_IDS_FILE=".container_ids_dockerized"

# --- Find available port function ---
find_available_port() {
    local port=$1
    while lsof -i:$port > /dev/null; do
        port=$((port + 1))
    done
    echo $port
}

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

# --- Create Docker Network ---
if ! docker network ls | grep -q $NETWORK_NAME; then
    echo "Creating Docker network: $NETWORK_NAME"
    docker network create $NETWORK_NAME
fi



# --- Agent Directories (read from config file) ---
AGENT_CONFIG_FILE="/home/cortex/agents_tools/scripts/agents.conf"
AGENT_DIRS=()
while IFS= read -r line; do
    # Skip comments and empty lines
    if [[ ! "$line" =~ ^# && -n "$line" ]]; then
        AGENT_DIRS+=("$line")
    fi
done < "$AGENT_CONFIG_FILE"

ROOT_AGENT_DIR="/home/cortex/agents_tools/root_agent"

declare -A AGENT_PORTS_MAP

for agent_dir in "${AGENT_DIRS[@]}"; do
    agent_name=$(basename "$agent_dir")
    image_name="gemini-agent-${agent_name}"
    container_name="${agent_name}-dockerized"

    echo -e "\n--- Processing ${YELLOW}${agent_name}${NC} ---"

    # Stop and remove any existing container with the same name
    if [ "$(docker ps -aq -f name=^\/${container_name}$)" ]; then
        echo "Stopping and removing existing container $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
    fi

    # Build the Docker image
    echo -e "Building image ${YELLOW}$image_name${NC}"
    docker build -t "$image_name" "$agent_dir"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping. Check logs/${agent_name}.log for details.${NC}"
    else
        # Find an available port for the agent
        CURRENT_PORT=$(find_available_port $PORT)
        if [ -z "$CURRENT_PORT" ]; then
            echo -e "${RED}Error: Could not find an available port for ${agent_name}. Skipping. Check logs/${agent_name}.log for details.${NC}"
        else
            PORT=$((CURRENT_PORT + 1))
            AGENT_PORTS_MAP[$agent_name]=$CURRENT_PORT

            echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$CURRENT_PORT${NC}...\n"
            docker run -d --network $NETWORK_NAME -p ${CURRENT_PORT}:8000 --name "$container_name" "$image_name" > "logs/${agent_name}.log" 2>&1

            # Give Docker a moment to start the container
            sleep 2

            # Check if the container is actually running
            if [ "$(docker ps -q -f name=^\/${container_name}$)" ]; then
                echo -e "${GREEN}Container ${container_name} is running.${NC}"
            else
                echo -e "${RED}Container ${container_name} failed to start. Check logs/${agent_name}.log for details.${NC}"
                # Attempt to get logs if container exited immediately
                docker logs "$container_name" >> "logs/${agent_name}.log"
            fi

            container_id=$(docker ps -aq -f name=^/${agent_name}-dockerized$)
            if [ -z "$container_id" ]; then
                echo -e "${RED}Error: Container for $agent_name not found after launch. Check logs/${agent_name}.log for details.${NC}"
            else
                echo "$container_id" >> $CONTAINER_IDS_FILE
                echo "$agent_name:$CURRENT_PORT" >> $AGENT_PORTS_FILE

                echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $CURRENT_PORT.${NC}"

                # Wait for the agent to be healthy
                if ! wait_for_health_check "$agent_name" "$CURRENT_PORT"; then
                    echo -e "${RED}Failed to start ${agent_name}.${NC}"
                    # Attempt to get logs if container exited immediately
                    docker logs "$container_name" >> "logs/${agent_name}.log"
                fi
            fi
        fi
    fi
done


# Process root_agent last
if [ -n "$ROOT_AGENT_DIR" ]; then
    agent_name=$(basename "$ROOT_AGENT_DIR")
    image_name="gemini-agent-${agent_name}"
    container_name="${agent_name}-dockerized"

    echo -e "\n--- Processing ${YELLOW}${agent_name}${NC} (Root Agent) ---"

    # Stop and remove any existing container with the same name
    if [ "$(docker ps -aq -f name=^\/${container_name}$)" ]; then
        echo "Stopping and removing existing container $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
    fi

    # Build the Docker image
    echo -e "Building image ${YELLOW}$image_name${NC}"
    docker build -t "$image_name" "$ROOT_AGENT_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping. Check logs/${agent_name}.log for details.${NC}"
    else
        # Construct AGENT_HOSTS for root_agent using the collected ports
        AGENT_HOSTS=""
        for other_agent_name in "${!AGENT_PORTS_MAP[@]}"; do
            AGENT_HOSTS+="-e ${other_agent_name^^}_HOST=http://${other_agent_name}-dockerized:${AGENT_PORTS_MAP[$other_agent_name]} "
        done

        # Find an available port for the root agent
        CURRENT_ROOT_PORT=$(find_available_port $PORT)
        if [ -z "$CURRENT_ROOT_PORT" ]; then
            echo -e "${RED}Error: Could not find an available port for ${agent_name}. Skipping. Check logs/${agent_name}.log for details.${NC}"
        else
            PORT=$CURRENT_ROOT_PORT # Update PORT for the next search (though root is last)

            echo -e "Running container ${YELLOW}$container_name${NC} on port ${YELLOW}$CURRENT_ROOT_PORT${NC}...\n"
            docker run -d --network $NETWORK_NAME -p ${CURRENT_ROOT_PORT}:8000 $AGENT_HOSTS --name "$container_name" "$image_name" > "logs/${agent_name}.log" 2>&1

            # Give Docker a moment to start the container
            sleep 2

            # Check if the container is actually running
            if [ "$(docker ps -q -f name=^\/${container_name}$)" ]; then
                echo -e "${GREEN}Container ${container_name} is running.${NC}"
            else
                echo -e "${RED}Container ${container_name} failed to start. Check logs/${agent_name}.log for details.${NC}"
                # Attempt to get logs if container exited immediately
                docker logs "$container_name" >> "logs/${agent_name}.log"
            fi

            container_id=$(docker ps -aq -f name=^/${agent_name}-dockerized$)
            if [ -z "$container_id" ]; then
                echo -e "${RED}Error: Container for $agent_name not found after launch. Check logs/${agent_name}.log for details.${NC}"
            else
                echo "$container_id" >> $CONTAINER_IDS_FILE
                echo "$agent_name:$CURRENT_ROOT_PORT" >> $AGENT_PORTS_FILE

                echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $CURRENT_ROOT_PORT.${NC}"

                # Wait for the agent to be healthy
                if ! wait_for_health_check "$agent_name" "$CURRENT_ROOT_PORT"; then
                    echo -e "${RED}Failed to start ${agent_name}.${NC}"
                    # Attempt to get logs if container exited immediately
                    docker logs "$container_name" >> "logs/${agent_name}.log"
                fi
            fi
            PORT=$((CURRENT_ROOT_PORT + 1)) # Update PORT for the next search (though root is last)
        fi
    fi
fi


echo -e "\n${GREEN}✅ All Dockerized agents processed. Check logs in /home/cortex/agents_tools/logs for details.${NC}"