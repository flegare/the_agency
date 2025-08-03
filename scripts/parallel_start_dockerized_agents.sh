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
            docker run -d --network $NETWORK_NAME -p ${CURRENT_ROOT_PORT}:8000 $AGENT_HOSTS --name "$container_name" "$image_name" > /dev/null 2>&1 &
            ROOT_AGENT_PID=$! # Store PID of the docker run command

            # Wait for root agent to finish launching and check health
            wait $ROOT_AGENT_PID
            if [ $? -ne 0 ]; then
                echo -e "${RED}Error: Docker container failed to launch for $agent_name. Check logs/${agent_name}.log for details.${NC}"
            else
                container_id=$(docker ps -aq -f name=^/${agent_name}-dockerized$)
                if [ -z "$container_id" ]; then
                    echo -e "${RED}Error: Container for $agent_name not found after launch. Check logs/${agent_name}.log for details.${NC}"
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
            fi
            PORT=$((CURRENT_ROOT_PORT + 1)) # Update PORT for the next search (though root is last)
        fi
    fi
fi


echo -e "
${GREEN}✅ All Dockerized agents processed. Check logs in /home/cortex/agents_tools/logs for details.${NC}"