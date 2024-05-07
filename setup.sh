#!/bin/bash

#Update package list
sudo apt-get update

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    sudo apt-get install -y docker
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing Docker Compose..."
    sudo apt-get install -y docker-compose
    echo "Docker Compose installed successfully."
else
    echo "Docker Compose is already installed."
fi


# Check if jq is installed
if command -v jq &> /dev/null; then
    echo "jq is already installed."
else
    # Install jq
    sudo apt-get install -y jq
    echo "jq installed successfully."
fi


# Check if ngrok is installed
if command -v ngrok &> /dev/null; then
    echo "ngrok is already installed."
else
    # Install ngrok
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update
    sudo apt install ngrok
    echo "ngrok installed successfully."
fi
