# Start from a specific Python 3.8 image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your chatbot files into the container
COPY . .

# Install Rasa and its dependencies
RUN pip install --no-cache-dir rasa==3.6.0

# The entrypoint is the main command to execute
ENTRYPOINT ["rasa"]