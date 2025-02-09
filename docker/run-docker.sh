#!/bin/bash

# Name of the Docker image
IMAGE_NAME="ubuntu-jammy-python3-git"

# Build the Docker image
echo "Building the Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# Run the Docker container
echo "Running the Docker container from image: $IMAGE_NAME"
docker run -it --rm $IMAGE_NAME
