#!/bin/bash

# Ensure Docker and Docker-compose are installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Docker is not installed, installing Docker..."
  # Add steps to install Docker here
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo "Docker-compose is not installed, installing Docker-compose..."
  # Add steps to install Docker-compose here
fi

# Build Docker images and start the development environment
echo "Building Docker Images..."
docker-compose up --build

# Provide initial setup feedback
echo "Development setup is complete. Access the app at http://localhost:8000"