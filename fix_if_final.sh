#!/bin/bash
sed -i '/container_id=$(docker ps -aq -f name=^\/${container_name}\$)/,+3s/}/fi/' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
