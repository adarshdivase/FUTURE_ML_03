#!/bin/bash
echo "Starting Rasa NLU shell for testing intent recognition..."

# Disable telemetry
export RASA_TELEMETRY_ENABLED=false

# Suppress TensorFlow warnings
export TF_CPP_MIN_LOG_LEVEL=2

# Start NLU shell
rasa shell nlu
