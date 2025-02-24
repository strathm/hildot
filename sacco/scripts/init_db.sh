#!/bin/bash

# Wait for the database to be ready
sleep 30s

# Connect to the MSSQL instance and create the database
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -Q "CREATE DATABASE IF NOT EXISTS yourdatabase;"

# Initialize tables and any necessary schema
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d yourdatabase -i /app/scripts/init_schema.sql

echo "MSSQL Database initialized successfully."
