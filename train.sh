#!/bin/bash
# Optimized training script for large datasets

echo "Starting optimized Rasa training..."

# Set environment variables for better performance
export PYTHONPATH="${PYTHONPATH}:."
export OMP_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=true

# Train with optimizations
rasa train     --config config.yml     --domain domain.yml     --data data/     --num-threads 4     --verbose

echo "Training completed!"
echo "To test your bot, run: rasa shell"
