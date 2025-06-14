#!/bin/bash

# Start PostgreSQL development server in foreground
# Press Ctrl+C to stop
# To restart from scratch (fresh database): docker-compose down -v

echo "Starting PostgreSQL development server..."
echo "Database: lczero_dev_portal"
echo "Host: localhost:5432"
echo "User: lczero_dev"
echo "Password: dev_password"
echo ""
echo "Press Ctrl+C to stop"

docker-compose up