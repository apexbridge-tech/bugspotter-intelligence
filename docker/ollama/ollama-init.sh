#!/bin/bash
set -e

# Start Ollama in the background
/bin/ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama server to start..."
sleep 5  # Give it a moment to start

# Try to list models (this checks if server is ready)
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if ollama list > /dev/null 2>&1; then
        echo "Ollama server is ready!"
        break
    fi
    echo "Waiting for Ollama... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Ollama server failed to start!"
    exit 1
fi

# Pull the model if not already present
MODEL="${OLLAMA_MODEL:-llama3.1:8b}"
echo "Checking if model $MODEL exists..."

if ! ollama list | grep -q "$MODEL"; then
    echo "Pulling model $MODEL (this may take several minutes)..."
    ollama pull "$MODEL"
    echo "Model $MODEL pulled successfully!"
else
    echo "Model $MODEL already exists."
fi

echo "Ollama is ready with model $MODEL"

# Keep the container running
wait