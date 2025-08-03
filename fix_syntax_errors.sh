#!/bin/bash
sed -i 's/container_namefi$/container_name$/g' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
sed -i 's/REDError: Container for $agent_name not found after launch. Check Docker logs.${NCfi/RED}Error: Container for $agent_name not found after launch. Check Docker logs.${NC}/g' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
