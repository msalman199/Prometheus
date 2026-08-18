#!/bin/bash
echo "Starting CPU stress test..."
for i in {1..4}; do
    yes > /dev/null &
done
echo "CPU stress test started. Run 'killall yes' to stop."
