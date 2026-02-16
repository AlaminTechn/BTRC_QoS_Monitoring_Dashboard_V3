#!/bin/bash
# Metabase User Initialization Script
# Runs automatically after Metabase starts

set -e

echo "=================================="
echo "Metabase User Initialization"
echo "=================================="

# Wait for Metabase to be fully ready
echo "Waiting for Metabase to be ready..."
sleep 60  # Give Metabase time to fully start

# Run Python initialization script
echo "Running user setup script..."
python3 /scripts/init_users_permissions.py

echo "✅ User initialization complete!"
