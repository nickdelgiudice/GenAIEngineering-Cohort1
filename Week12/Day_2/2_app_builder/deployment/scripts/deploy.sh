#!/bin/bash

# Load environment variables
source .env

# Pull the latest docker image
echo "Pulling the latest image..."
docker pull taskmaster_pro_app:latest

# Stop the existing container
echo "Stopping existing container..."
docker-compose -f docker-compose.prod.yml down

# Start the new container
echo "Starting the new container..."
docker-compose -f docker-compose.prod.yml up -d

# Cleanup
echo "Cleaning up unused images..."
docker image prune -f