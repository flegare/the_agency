#!/bin/bash

# --- Configuration ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
MAX_RETRIES=10
RETRY_DELAY=3
PORT=30000 # Start port for agents
NETWORK_NAME="gemini-agents-network"
AGENT_PORTS_FILE=".agent_ports_dockerized"
CONTAINER_IDS_FILE="/home/cortex/agents_tools/.agent_container_ids"
> $CONTAINER_IDS_FILE # Clear the file


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
declare -A AGENT_PORTS_MAP

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

    echo -e "\n--- Processing ${YELLOW}${agent_name}${NC} ---"

    # Stop and remove any existing container with the same name
    if [ "$(docker ps -aq -f name=^/${container_name}$)" ]; then
        echo "Stopping and removing existing container $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
        sleep 3 # Give OS time to release port
    fi

    # Build the Docker image
    echo -e "Building image ${YELLOW}$image_name${NC}"
    docker build -t "$image_name" "$AGENT_PATH"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping. Check logs/${agent_name}.log for details.${NC}"
    else
        AGENT_PORTS_MAP[$agent_name]=$PORT

        # Attempt to run the container with retries
        run_attempts=0
        container_id=""
        while [ "$run_attempts" -lt 5 ]; do
            run_attempts=$((run_attempts + 1))
            echo -e "Attempt ${run_attempts}/5: Running command: docker run -d --network \"$NETWORK_NAME\" -p \"${PORT}:8000\" --name \"$container_name\" \"$image_name\""
            
            # Try to run the container, capture its ID or error
            if [ "$agent_name" == "name_generator_agent" ]; then
                # Use --add-host to make host.docker.internal resolve to the host's gateway
                container_id=$(docker run -d --network "$NETWORK_NAME" -p "${PORT}:8000" --add-host=host.docker.internal:host-gateway --name "$container_name" "$image_name" 2>&1)
            else
                container_id=$(docker run -d --network "$NETWORK_NAME" -p "${PORT}:8000" --name "$container_name" "$image_name" 2>&1)
            fi
            run_status=$?
            run_status=$?

            echo "Docker run exit status: $run_status"
            echo "Docker run raw output \(container_id or error\): $container_id"

            # Give Docker a moment to start the container
            sleep 5

            if [ "$run_status" -eq 0 ] && [ -n "$container_id" ] && docker ps -q --filter "id=$container_id" > /dev/null; then
                echo -e "${GREEN}Container ${container_name} is running.${NC}\n"
                break # Container started successfully
            else
                echo -e "${RED}Container ${container_name} failed to start on attempt ${run_attempts}. Retrying... Check logs/${agent_name}.log for details.${NC}\n"
                # Output docker run error to log
                echo "Docker run output (attempt ${run_attempts}): ${container_id}" >> "logs/${agent_name}.log"
                # Clean up any partially created container
                docker rm "$container_name" > /dev/null 2>&1 || true # Use || true to prevent script from exiting if rm fails
                sleep 2 # Wait before retrying
            fi
        done

        if [ "$run_attempts" -eq 5 ] && [ -z "$container_id" ]; then
            echo -e "${RED}Error: Container ${container_name} failed to start after multiple retries. Skipping. Check logs/${agent_name}.log for details.${NC}\n"
            continue # Skip to next agent
        fi

        # This block is executed only if container_started is true (from the break above)
        if [ -z "$container_id" ]; then # This check should ideally not be needed if break works
            echo -e "${RED}Error: Container for $agent_name not found after launch. Check logs/${agent_name}.log for details.${NC}"
        else
            echo "$container_id" >> $CONTAINER_IDS_FILE
            echo "$agent_name:$PORT" >> $AGENT_PORTS_FILE

            echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $PORT.${NC}"

            # Wait for the agent to be healthy
            if ! wait_for_health_check "$agent_name" "$PORT"; then
                echo -e "${RED}Failed to start ${agent_name}.${NC}"
                # Attempt to get logs if container exited immediately
                docker logs "$container_name" >> "logs/${agent_name}.log"
            fi
        fi
    fi
done < "$AGENT_CONFIG_FILE"



# Process root_agent last
if [[ -v AGENT_PORTS_MAP["root_agent"] ]]; then
    agent_name="root_agent"
    port=${AGENT_PORTS_MAP["root_agent"]}
    agent_dir="/home/cortex/agents_tools/agents/core/root_agent"
    image_name="gemini-agent-${agent_name}"
    container_name="${agent_name}-dockerized"

    echo -e "\n--- Processing ${YELLOW}${agent_name}${NC} (Root Agent) ---"

    # Stop and remove any existing container with the same name
    if [ "$(docker ps -aq -f name=^/${container_name}$)" ]; then
        echo "Stopping and removing existing container $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
        sleep 3 # Give OS time to release port
    fi

    # Build the Docker image
    echo -e "Building image ${YELLOW}$image_name${NC}"
    docker build -t "$image_name" "$agent_dir"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Docker image build failed for $agent_name. Skipping. Check logs/${agent_name}.log for details.${NC}"
    else
        # Construct AGENT_HOSTS for root_agent using the collected ports
        AGENT_HOSTS=""
        for other_agent_name in "${!AGENT_PORTS_MAP[@]}"; do
            if [ "$other_agent_name" != "root_agent" ]; then
                AGENT_HOSTS+="-e ${other_agent_name^^}_HOST=http://${other_agent_name}-dockerized:8000 "
            fi
        done

        # Attempt to run the container with retries
        run_attempts=0
        container_id=""
        while [ "$run_attempts" -lt 5 ]; do
            run_attempts=$((run_attempts + 1))
            echo -e "Attempt ${run_attempts}/5: Running command: docker run -d --network \"$NETWORK_NAME\" -p \"${port}:8000\" $AGENT_HOSTS --name \"$container_name\" \"$image_name\""
            
            # Try to run the container, capture its ID or error
            container_id=$(docker run -d --network "$NETWORK_NAME" -p "${port}:8000" $AGENT_HOSTS --name "$container_name" "$image_name" 2>&1)
            run_status=$?

            echo "Docker run exit status: $run_status"
            echo "Docker run raw output \(container_id or error\): $container_id"

            # Give Docker a moment to start the container
            sleep 5

            if [ "$run_status" -eq 0 ] && [ -n "$container_id" ] && docker ps -q --filter "id=$container_id" > /dev/null; then
                echo -e "${GREEN}Container ${container_name} is running.${NC}\n"
                break # Container started successfully
            else
                echo -e "${RED}Container ${container_name} failed to start on attempt ${run_attempts}. Retrying... Check logs/${agent_name}.log for details.${NC}\n"
                # Output docker run error to log
                echo "Docker run output (attempt ${run_attempts}): ${container_id}" >> "logs/${agent_name}.log"
                # Clean up any partially created container
                docker rm "$container_name" > /dev/null 2>&1 || true # Use || true to prevent script from exiting if rm fails
                sleep 2 # Wait before retrying
            fi
        done

        if [ "$run_attempts" -eq 5 ] && [ -z "$container_id" ]; then
            echo -e "${RED}Error: Container %s failed to start after multiple retries. Skipping. Check logs/%s.log for details.${NC}\n" "$container_name" "$agent_name"
        else
            # This block is executed only if container_started is true (from the break above)
            if [ -z "$container_id" ]; then # This check should ideally not be needed if break works
                echo -e "${RED}Error: Container for $agent_name not found after launch. Check logs/${agent_name}.log for details.${NC}"
            else
                echo "$container_id" >> $CONTAINER_IDS_FILE
                echo "$agent_name:$port" >> $AGENT_PORTS_FILE

                echo -e "${GREEN}Started ${agent_name} (Container ID: ${container_id:0:12}) on port $port.${NC}"

                # Wait for the agent to be healthy
                if ! wait_for_health_check "$agent_name" "$port"; then
                    echo -e "${RED}Failed to start ${agent_name}.${NC}"
                    # Attempt to get logs if container exited immediately
                    docker logs "$container_name" >> "logs/${agent_name}.log"
                fi
            fi
        fi
    fi
fi



echo -e "\n${GREEN}✅ All Dockerized agents processed. Check logs in /home/cortex/agents_tools/logs for details.${NC}"
