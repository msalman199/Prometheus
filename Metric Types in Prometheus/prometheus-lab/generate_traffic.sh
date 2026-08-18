#!/bin/bash

echo "Generating traffic to sample application..."

while true; do
    # Generate random requests
    curl -s http://localhost:8000/ > /dev/null
    sleep 1
    
    curl -s http://localhost:8000/api/data > /dev/null
    sleep 2
    
    # Occasionally hit error endpoint
    if [ $((RANDOM % 10)) -eq 0 ]; then
        curl -s http://localhost:8000/api/error > /dev/null
    fi
    
    sleep 1
done
