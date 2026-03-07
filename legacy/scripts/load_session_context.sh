#!/bin/bash

# This script loads the latest session context from the Historian Agent.
# The Historian Agent must be running for this script to work.

# Ensure the Historian Agent is running (optional, but good practice)
# You can run ./scripts/start_agents.sh if you are unsure.

# Call the Historian Agent's load_context endpoint
curl -s -X POST http://localhost:8000/load_context -H "Content-Type: application/json" -d '{}'
