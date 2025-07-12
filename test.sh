#!/bin/bash
echo "Starting Rasa shell..."

# Disable telemetry
export RASA_TELEMETRY_ENABLED=false

# Start interactive shell
rasa shell
