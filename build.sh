#!/usr/bin/env bash
# Build script for Render
set -o errexit

pip install -r requirements.txt

# Ensure templates directory exists
if [ ! -d "templates" ]; then
    echo "Error: templates directory not found"
    exit 1
fi

echo "Build completed successfully"