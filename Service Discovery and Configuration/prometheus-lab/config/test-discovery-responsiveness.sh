#!/bin/bash

echo "Testing service discovery responsiveness..."

# Get initial target count
INITIAL_COUNT=$(curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(len(data['data']['activeTargets']))
")

echo "Initial target count: $INITIAL_COUNT"

# Create a new service
kubectl create deployment test-discovery --image=nginx:alpine -n demo-apps
kubectl expose deployment test-discovery --port=80 --target-port=80 -n demo-apps
kubectl annotate service test-discovery prometheus.io/scrape=true -n demo-apps
kubectl annotate service test-discovery prometheus.io/port=80 -n demo-apps

echo "Created new service, waiting for discovery..."

# Wait and check for new targets
for i in {1..10}; do
    sleep 15
    NEW_COUNT=$(curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(len(data['data']['activeTargets']))
")
    echo "Attempt $i: Target count is now $NEW_COUNT"
    
    if [ "$NEW_COUNT" -gt "$INITIAL_COUNT" ]; then
        echo "SUCCESS: New service discovered!"
        break
    fi
done
