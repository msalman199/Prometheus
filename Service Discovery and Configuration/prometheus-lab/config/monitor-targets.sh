#!/bin/bash

echo "Monitoring Prometheus targets for changes..."
echo "Press Ctrl+C to stop"

while true; do
    echo "=== $(date) ==="
    echo "Total targets discovered:"
    curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
active_targets = data['data']['activeTargets']
print(f'Active targets: {len(active_targets)}')
for target in active_targets:
    labels = target.get('labels', {})
    job = labels.get('job', 'unknown')
    instance = labels.get('instance', 'unknown')
    namespace = labels.get('kubernetes_namespace', 'N/A')
    print(f'  - Job: {job}, Instance: {instance}, Namespace: {namespace}')
"
    echo ""
    sleep 30
done
