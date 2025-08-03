#!/bin/bash
sed -i 's/container_namefi$/container_name$/g' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
sed -i 's/Check Docker logs.${NC/Check Docker logs.${NC}"/' /home/cortex/agents_tools/scripts/parallel_start_dockerized_agents.sh
