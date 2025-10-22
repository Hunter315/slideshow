#!/bin/bash
# Deployment script for Raspberry Pi Zero W
# This script should be copied to the Pi along with the bundled application

# Create necessary directories
mkdir -p uploads
mkdir -p node_modules/better-sqlite3

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed!"
    echo "Installing Node.js (this may take a while on Pi Zero W)..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "Setup complete!"
echo "To run the server: node server-bundle.js"
