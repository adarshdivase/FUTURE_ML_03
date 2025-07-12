#!/bin/bash
echo "Starting Rasa training..."

# Disable telemetry for faster training
export RASA_TELEMETRY_ENABLED=false

# Train the model
rasa train --verbose

echo "Training completed!"
echo "To test your bot, run: rasa shell"
