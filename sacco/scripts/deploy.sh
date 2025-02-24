#!/bin/bash

# Build and start the containers
docker-compose up --build -d

# Wait for the containers to start
echo "Waiting for containers to start..."
sleep 30s

# Initialize the MSSQL database
echo "Initializing the MSSQL database..."
docker exec -it mssql_db /bin/bash /app/scripts/init_db.sh

# Show running containers
docker ps
