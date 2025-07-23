#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment
source .venv/bin/activate

# Base port for agents
PORT=8000

# File to store PIDs
PID_FILE=".agent_pids"
> $PID_FILE # Clear the PID file

# Find all agent directories (containing requirements.txt)
for agent_dir in $(find . -mindepth 2 -name requirements.txt -printf '%h\n'); do
    agent_name=$(basename $agent_dir)
    echo "Starting $agent_name on port $PORT..."

    # Start the agent in the background using nohup to prevent hanging
    nohup uvicorn --host 0.0.0.0 --port $PORT "${agent_name}.main:app" > "logs/${agent_name}.log" 2>&1 &
    
    # Save the PID
    echo $! >> $PID_FILE

    # Increment the port for the next agent
    PORT=$((PORT + 1))
done

echo "All agents started. Logs are in the 'logs' directory."
