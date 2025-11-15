#!/bin/bash
set -e

# Entrypoint script for OnboardingAgent Docker container

# Check if .env file exists and load it
if [ -f "/app/.env" ]; then
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

# Execute the command
exec "$@"
