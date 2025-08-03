#!/bin/bash
sed -i 's/container_namefi$/container_name$/g' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
sed -i 's/REDError/RED}Error/g' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
