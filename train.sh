#!/bin/bash
echo "Starting Rasa training..."

# Disable telemetry for faster training
export RASA_TELEMETRY_ENABLED=false

# Suppress TensorFlow warnings
export TF_CPP_MIN_LOG_LEVEL=2

# Train the model
echo "Training model (this may take a few minutes)..."
rasa train --verbose

echo "Training completed!"
echo "To test your bot, run: rasa shell"
echo "To test NLU only, run: rasa shell nlu"
