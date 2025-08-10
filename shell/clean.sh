#!/bin/bash

echo "Stopping all running containers..."
docker ps -q | xargs -r docker stop

echo "Removing all containers..."
docker ps -a -q | xargs -r docker rm

echo "Removing all unused images..."
docker images -q | xargs -r docker rmi -f

echo "Removing all unused volumes..."
docker volume ls -q | xargs -r docker volume rm

echo "Cleaning up build cache..."
docker builder prune -f

echo "Docker cleanup complete."
docker system df