#!/bin/bash
# Metabase User Initialization
# Triggered automatically by Docker after Metabase passes its healthcheck.
# The Python script polls /api/health internally as an extra safety net.

set -e

echo "=================================="
echo "  BTRC Metabase User Initialization"
echo "=================================="

python3 /scripts/init_metabase_users.py

echo "=================================="
echo "  Initialization complete"
echo "=================================="
