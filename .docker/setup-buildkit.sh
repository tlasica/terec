#!/bin/bash

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Create and use BuildKit builder
if ! docker buildx ls | grep -q mybuilder; then
    docker buildx create --name mybuilder --driver docker-container --bootstrap
fi
docker buildx inspect --bootstrap

# Set default builder
docker buildx use mybuilder

echo "BuildKit setup complete!"
