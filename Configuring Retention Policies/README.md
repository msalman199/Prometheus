<div align="center">

# 📦 Configuring Retention Policies in Prometheus

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node_Exporter-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![systemd](https://img.shields.io/badge/systemd-000000?style=for-the-badge&logo=linux&logoColor=white)
![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-yellow?style=for-the-badge)

**Learn to configure, test, and monitor time-based and size-based retention policies for Prometheus time-series data.**

</div>

---

## 📖 Table of Contents

- [🎯 Learning Objectives](#-learning-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🔑 Key Concepts](#-key-concepts)
- [🚀 Task 1: Configure Retention Policies for Time-Series Data](#-task-1-configure-retention-policies-for-time-series-data)
- [📊 Task 2: Test Data Retention and Monitor Disk Usage](#-task-2-test-data-retention-and-monitor-disk-usage)
- [🛠️ Troubleshooting Common Issues](#️-troubleshooting-common-issues)
- [🏆 Best Practices for Production](#-best-practices-for-production)
- [✅ Conclusion](#-conclusion)

---

## 🎯 Learning Objectives

By the end of this lab, students will be able to:

| # | Objective |
|---|-----------|
| 1 | Understand the importance of data retention policies in monitoring systems |
| 2 | Configure time-based retention policies in Prometheus |
| 3 | Set up size-based retention limits to manage disk usage |
| 4 | Monitor and verify retention policy effectiveness |
| 5 | Implement best practices for storage management in production environments |
| 6 | Troubleshoot common retention policy issues |

## 📋 Prerequisites

| # | Requirement |
|---|-------------|
| 1 | Basic understanding of Linux command line operations |
| 2 | Familiarity with YAML configuration files |
| 3 | Basic knowledge of monitoring concepts and time-series data |
| 4 | Understanding of disk space management concepts |
| 5 | Completion of previous Prometheus labs or equivalent experience |

## 🖥️ Lab Environment

> Al Nafi provides Linux-based cloud machines for this lab. Simply click **Start Lab** to access your dedicated environment. The provided Linux machine is bare metal with no pre-installed tools — you will install all required software during the lab exercises.
>
> All tasks are performed on a single Linux machine. No additional virtual machines or remote hosts are required.

## 🔑 Key Concepts

| Concept | Description |
|---------|-------------|
| **Time-based Retention** | `--storage.tsdb.retention.time` — automatically deletes data older than the configured duration (e.g. `7d`, `30d`) |
| **Size-based Retention** | `--storage.tsdb.retention.size` — caps total TSDB storage, deleting the oldest blocks once the limit is reached |
| **TSDB (Time Series Database)** | Prometheus's on-disk storage engine, organized into immutable time-windowed blocks |
| **WAL (Write-Ahead Log)** | In-memory head block's durability log, flushed to disk blocks during compaction |
| **`--web.enable-lifecycle`** | Enables the `/-/reload` API endpoint for hot-reloading configuration without a restart |
| **Compaction** | The background process that merges and prunes TSDB blocks, enforcing retention limits |
| **Node Exporter** | Prometheus exporter that exposes host-level Linux metrics (CPU, memory, disk, network) |

---

## 🚀 Task 1: Configure Retention Policies for Time-Series Data

### Subtask 1.1: Install and Set Up Prometheus

**Step 1: Update the system and install required packages** 📦

```bash
sudo apt update
sudo apt install -y wget curl tar
```

**Step 2: Create a dedicated user for Prometheus** ⚙️

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

**Step 3: Download and install Prometheus** 📦

```bash
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz
tar xvf prometheus-2.47.0.linux-amd64.tar.gz
cd prometheus-2.47.0.linux-amd64
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

### Subtask 1.2: Create Basic Prometheus Configuration

**Step 1: Create the main Prometheus configuration file** ⚙️

```bash
sudo tee /etc/prometheus/prometheus.yml > /dev/null <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF
```

**Step 2: Set proper ownership for the configuration file** ⚙️

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

### Subtask 1.3: Install Node Exporter for Metrics Generation

**Step 1: Download and install Node Exporter** 📦

```bash
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
cd node_exporter-1.6.1.linux-amd64
sudo cp node_exporter /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/node_exporter
```

**Step 2: Create systemd service for Node Exporter** ⚙️

```bash
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF
```

### Subtask 1.4: Configure Time-Based Retention Policy

**Step 1: Create a Prometheus systemd service with retention settings** ⚙️

```bash
sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle \
    --storage.tsdb.retention.time=7d \
    --storage.tsdb.retention.size=1GB

[Install]
WantedBy=multi-user.target
EOF
```

> **Key Configuration Parameters Explained**
> - `--storage.tsdb.retention.time=7d` — Keeps data for 7 days
> - `--storage.tsdb.retention.size=1GB` — Limits total storage to 1GB
> - `--web.enable-lifecycle` — Allows configuration reloads via API

**Step 2: Start the services** ▶️

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
sudo systemctl enable prometheus
sudo systemctl start prometheus
```

**Step 3: Verify services are running** 🔍

```bash
sudo systemctl status prometheus
sudo systemctl status node_exporter
```

### Subtask 1.5: Test Different Retention Configurations

**Step 1: Create a script to test various retention settings** 🧪

```bash
tee ~/test_retention.sh > /dev/null <<'EOF'
#!/bin/bash

echo "Testing different retention configurations..."

# Function to update Prometheus retention settings
update_retention() {
    local time_retention=$1
    local size_retention=$2

    echo "Updating retention: time=${time_retention}, size=${size_retention}"

    sudo systemctl stop prometheus

    # Update the service file
    sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOL
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \\
    --config.file /etc/prometheus/prometheus.yml \\
    --storage.tsdb.path /var/lib/prometheus/ \\
    --web.console.templates=/etc/prometheus/consoles \\
    --web.console.libraries=/etc/prometheus/console_libraries \\
    --web.listen-address=0.0.0.0:9090 \\
    --web.enable-lifecycle \\
    --storage.tsdb.retention.time=${time_retention} \\
    --storage.tsdb.retention.size=${size_retention}

[Install]
WantedBy=multi-user.target
EOL

    sudo systemctl daemon-reload
    sudo systemctl start prometheus
    sleep 10
}

# Test configuration 1: Short retention for testing
update_retention "2h" "500MB"
echo "Configuration 1 applied: 2 hours, 500MB"

# Wait and check
sleep 5
curl -s http://localhost:9090/api/v1/status/config | jq .

echo "Press Enter to continue to next configuration..."
read

# Test configuration 2: Medium retention
update_retention "1d" "1GB"
echo "Configuration 2 applied: 1 day, 1GB"

sleep 5
curl -s http://localhost:9090/api/v1/status/config | jq .

echo "Press Enter to continue to final configuration..."
read

# Test configuration 3: Production-like retention
update_retention "15d" "5GB"
echo "Configuration 3 applied: 15 days, 5GB"

sleep 5
curl -s http://localhost:9090/api/v1/status/config | jq .

echo "Retention testing complete!"
EOF

chmod +x ~/test_retention.sh
```

**Step 2: Install jq for JSON parsing** 📦

```bash
sudo apt install -y jq
```

**Step 3: Run the retention test script** ▶️

```bash
~/test_retention.sh
```

---

## 📊 Task 2: Test Data Retention and Monitor Disk Usage

### Subtask 2.1: Create Data Generation Script

**Step 1: Create a script to generate sample metrics** 🧪

```bash
tee ~/generate_metrics.sh > /dev/null <<'EOF'
#!/bin/bash

echo "Starting metric generation for retention testing..."

# Create a simple HTTP server that exposes custom metrics
tee ~/custom_metrics.py > /dev/null <<'EOL'
#!/usr/bin/env python3
import http.server
import socketserver
import time
import random
from datetime import datetime

class MetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            # Generate sample metrics
            timestamp = int(time.time())
            cpu_usage = random.uniform(10, 90)
            memory_usage = random.uniform(20, 80)
            disk_io = random.randint(100, 1000)
            network_bytes = random.randint(1000, 10000)

            metrics = f"""# HELP custom_cpu_usage CPU usage percentage
# TYPE custom_cpu_usage gauge
custom_cpu_usage {cpu_usage}

# HELP custom_memory_usage Memory usage percentage
# TYPE custom_memory_usage gauge
custom_memory_usage {memory_usage}

# HELP custom_disk_io Disk I/O operations
# TYPE custom_disk_io counter
custom_disk_io {disk_io}

# HELP custom_network_bytes Network bytes transferred
# TYPE custom_network_bytes counter
custom_network_bytes {network_bytes}

# HELP custom_request_duration Request duration in seconds
# TYPE custom_request_duration histogram
custom_request_duration_bucket{{le="0.1"}} {random.randint(10, 50)}
custom_request_duration_bucket{{le="0.5"}} {random.randint(50, 100)}
custom_request_duration_bucket{{le="1.0"}} {random.randint(100, 150)}
custom_request_duration_bucket{{le="+Inf"}} {random.randint(150, 200)}
custom_request_duration_sum {random.uniform(10, 100)}
custom_request_duration_count {random.randint(100, 500)}
"""
            self.wfile.write(metrics.encode())
        else:
            self.send_response(404)
            self.end_headers()

PORT = 8080
with socketserver.TCPServer(("", PORT), MetricsHandler) as httpd:
    print(f"Serving metrics on port {PORT}")
    httpd.serve_forever()
EOL

chmod +x ~/custom_metrics.py

# Install Python3 if not available
sudo apt install -y python3

echo "Starting custom metrics server on port 8080..."
python3 ~/custom_metrics.py &
METRICS_PID=$!

echo "Custom metrics server started with PID: $METRICS_PID"
echo "You can stop it later with: kill $METRICS_PID"
echo "Metrics available at: http://localhost:8080/metrics"
EOF

chmod +x ~/generate_metrics.sh
```

**Step 2: Update Prometheus configuration to scrape custom metrics** ⚙️

```bash
sudo tee /etc/prometheus/prometheus.yml > /dev/null <<EOF
global:
  scrape_interval: 5s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'custom_metrics'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 2s
EOF

sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

**Step 3: Reload Prometheus configuration** ▶️

```bash
curl -X POST http://localhost:9090/-/reload
```

### Subtask 2.2: Monitor Storage Usage and Retention

**Step 1: Create a comprehensive monitoring script** 📈

```bash
tee ~/monitor_retention.sh > /dev/null <<'EOF'
#!/bin/bash

echo "=== Prometheus Retention Monitoring Script ==="
echo "Starting monitoring at $(date)"
echo

# Function to display storage information
show_storage_info() {
    echo "--- Storage Information ---"
    echo "Prometheus data directory size:"
    du -sh /var/lib/prometheus/
    echo

    echo "Detailed breakdown:"
    du -h /var/lib/prometheus/* 2>/dev/null | head -10
    echo

    echo "Available disk space:"
    df -h /var/lib/prometheus/
    echo
}

# Function to show retention settings
show_retention_settings() {
    echo "--- Current Retention Settings ---"
    ps aux | grep prometheus | grep -v grep | grep -o '\--storage\.tsdb\.retention\.[^ ]*'
    echo
}

# Function to show TSDB stats
show_tsdb_stats() {
    echo "--- TSDB Statistics ---"
    curl -s http://localhost:9090/api/v1/status/tsdb | jq '.data' 2>/dev/null || echo "Could not fetch TSDB stats"
    echo
}

# Function to show oldest and newest data
show_data_range() {
    echo "--- Data Time Range ---"

    # Get the oldest timestamp
    oldest=$(curl -s "http://localhost:9090/api/v1/query?query=prometheus_tsdb_symbol_table_size_bytes" | jq -r '.data.result[0].value[0]' 2>/dev/null)
    if [ "$oldest" != "null" ] && [ -n "$oldest" ]; then
        echo "Sample timestamp: $(date -d @$oldest 2>/dev/null || echo 'Invalid timestamp')"
    fi

    # Show current time
    echo "Current time: $(date)"
    echo
}

# Main monitoring loop
monitor_loop() {
    local duration=${1:-300}  # Default 5 minutes
    local interval=${2:-30}   # Default 30 seconds

    echo "Monitoring for $duration seconds with $interval second intervals..."
    echo "Press Ctrl+C to stop monitoring"
    echo

    local end_time=$(($(date +%s) + duration))

    while [ $(date +%s) -lt $end_time ]; do
        echo "=== Monitoring Update: $(date) ==="
        show_storage_info
        show_retention_settings
        show_tsdb_stats
        show_data_range

        echo "--- Recent Log Entries ---"
        sudo journalctl -u prometheus --since "1 minute ago" --no-pager -n 5 2>/dev/null || echo "No recent log entries"
        echo

        echo "Sleeping for $interval seconds..."
        echo "=================================================="
        echo

        sleep $interval
    done
}

# Check if arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [duration_seconds] [interval_seconds]"
    echo "Example: $0 600 60  # Monitor for 10 minutes with 1-minute intervals"
    echo
    echo "Running with default settings (5 minutes, 30-second intervals)..."
    echo
    monitor_loop
else
    monitor_loop $1 $2
fi
EOF

chmod +x ~/monitor_retention.sh
```

**Step 2: Start the metrics generation** ▶️

```bash
~/generate_metrics.sh
```

**Step 3: Begin monitoring retention behavior** 📈

```bash
~/monitor_retention.sh 600 60
```

### Subtask 2.3: Test Retention Policy Effectiveness

**Step 1: Create a retention testing script** 🧪

```bash
tee ~/test_retention_effectiveness.sh > /dev/null <<'EOF'
#!/bin/bash

echo "=== Testing Retention Policy Effectiveness ==="

# Function to force data generation
generate_intensive_data() {
    echo "Generating intensive data to test retention..."

    # Create multiple metric generators
    for i in {1..5}; do
        tee ~/metrics_generator_$i.py > /dev/null <<EOL
#!/usr/bin/env python3
import http.server
import socketserver
import time
import random
import threading

class MetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            metrics = ""
            # Generate many metrics to increase data volume
            for j in range(100):
                value = random.uniform(0, 100)
                metrics += f"test_metric_{j}_generator_{i} {value}\n"

            self.wfile.write(metrics.encode())
        else:
            self.send_response(404)
            self.end_headers()

PORT = 808$i
try:
    with socketserver.TCPServer(("", PORT), MetricsHandler) as httpd:
        print(f"Generator $i serving on port {PORT}")
        httpd.serve_forever()
except Exception as e:
    print(f"Error starting generator $i: {e}")
EOL

        chmod +x ~/metrics_generator_$i.py
        python3 ~/metrics_generator_$i.py &
        echo "Started generator $i with PID $!"
    done
}

# Function to update Prometheus config for intensive scraping
update_prometheus_config() {
    echo "Updating Prometheus configuration for intensive data collection..."

    sudo tee /etc/prometheus/prometheus.yml > /dev/null <<EOF
global:
  scrape_interval: 1s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 1s

  - job_name: 'custom_metrics'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 1s

  - job_name: 'intensive_metrics'
    static_configs:
      - targets: ['localhost:8081', 'localhost:8082', 'localhost:8083', 'localhost:8084', 'localhost:8085']
    scrape_interval: 1s
EOF

    sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
    curl -X POST http://localhost:9090/-/reload
}

# Function to set aggressive retention for testing
set_test_retention() {
    echo "Setting aggressive retention policy for testing..."

    sudo systemctl stop prometheus

    sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \\
    --config.file /etc/prometheus/prometheus.yml \\
    --storage.tsdb.path /var/lib/prometheus/ \\
    --web.console.templates=/etc/prometheus/consoles \\
    --web.console.libraries=/etc/prometheus/console_libraries \\
    --web.listen-address=0.0.0.0:9090 \\
    --web.enable-lifecycle \\
    --storage.tsdb.retention.time=30m \\
    --storage.tsdb.retention.size=100MB

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl start prometheus

    echo "Retention set to 30 minutes or 100MB maximum"
}

# Function to monitor retention in action
monitor_retention_action() {
    echo "Monitoring retention policy in action..."
    echo "This will run for 45 minutes to observe data cleanup"

    for i in {1..45}; do
        echo "--- Minute $i ---"
        echo "Storage size: $(du -sh /var/lib/prometheus/ | cut -f1)"
        echo "Block count: $(ls -1 /var/lib/prometheus/ | wc -l)"

        # Check for cleanup activity
        if [ $i -gt 30 ]; then
            echo "Should see retention cleanup after 30 minutes..."
        fi

        sleep 60
    done
}

# Main execution
echo "Starting retention effectiveness test..."
echo "This test will:"
echo "1. Generate intensive metrics data"
echo "2. Set aggressive retention policies"
echo "3. Monitor cleanup behavior"
echo

read -p "Press Enter to continue or Ctrl+C to cancel..."

set_test_retention
sleep 10
update_prometheus_config
sleep 5
generate_intensive_data
sleep 10

echo "All components started. Beginning monitoring..."
monitor_retention_action
EOF

chmod +x ~/test_retention_effectiveness.sh
```

**Step 2: Run the retention effectiveness test** ▶️

```bash
~/test_retention_effectiveness.sh
```

### Subtask 2.4: Create Retention Monitoring Dashboard

**Step 1: Create a script to display retention metrics** 📈

```bash
tee ~/retention_dashboard.sh > /dev/null <<'EOF'
#!/bin/bash

# Function to display header
show_header() {
    clear
    echo "========================================================"
    echo "           PROMETHEUS RETENTION DASHBOARD"
    echo "========================================================"
    echo "Last updated: $(date)"
    echo
}

# Function to show key metrics
show_key_metrics() {
    echo "--- KEY RETENTION METRICS ---"

    # Storage usage
    local storage_size=$(du -sh /var/lib/prometheus/ 2>/dev/null | cut -f1)
    echo "Total storage used: $storage_size"

    # Number of blocks
    local block_count=$(ls -1 /var/lib/prometheus/ 2>/dev/null | grep -E '^[0-9]' | wc -l)
    echo "Number of data blocks: $block_count"

    # Oldest block
    local oldest_block=$(ls -1t /var/lib/prometheus/ 2>/dev/null | grep -E '^[0-9]' | tail -1)
    if [ -n "$oldest_block" ]; then
        local oldest_time=$(stat -c %Y "/var/lib/prometheus/$oldest_block" 2>/dev/null)
        if [ -n "$oldest_time" ]; then
            echo "Oldest data block: $(date -d @$oldest_time)"
        fi
    fi

    # Current retention settings
    echo "Current retention settings:"
    ps aux | grep prometheus | grep -v grep | grep -o '\--storage\.tsdb\.retention\.[^ ]*' | sed 's/^/  /'
    echo
}

# Function to show TSDB health
show_tsdb_health() {
    echo "--- TSDB HEALTH ---"

    # Try to get TSDB stats
    local tsdb_stats=$(curl -s http://localhost:9090/api/v1/status/tsdb 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$tsdb_stats" ]; then
        echo "TSDB Status: Healthy"
        echo "$tsdb_stats" | jq -r '.data.headStats | "Head samples: \(.numSeries) series, \(.numSamples) samples"' 2>/dev/null || echo "Could not parse head stats"
    else
        echo "TSDB Status: Unable to connect"
    fi
    echo
}

# Function to show recent activity
show_recent_activity() {
    echo "--- RECENT ACTIVITY ---"

    # Recent Prometheus logs
    echo "Recent Prometheus logs:"
    sudo journalctl -u prometheus --since "5 minutes ago" --no-pager -n 3 2>/dev/null | tail -3 | sed 's/^/  /' || echo "  No recent logs available"
    echo
}

# Function to show disk space
show_disk_space() {
    echo "--- DISK SPACE ---"
    df -h /var/lib/prometheus/ | tail -1 | awk '{print "Used: " $3 " / " $2 " (" $5 " full)"}'
    echo
}

# Function to show recommendations
show_recommendations() {
    echo "--- RECOMMENDATIONS ---"

    local storage_size_bytes=$(du -sb /var/lib/prometheus/ 2>/dev/null | cut -f1)
    local storage_mb=$((storage_size_bytes / 1024 / 1024))

    if [ $storage_mb -gt 500 ]; then
        echo "⚠ Storage usage is high ($storage_mb MB). Consider:"
        echo "  - Reducing retention time"
        echo "  - Increasing retention size limit"
        echo "  - Reducing scrape frequency"
    elif [ $storage_mb -lt 50 ]; then
        echo "✓ Storage usage is optimal ($storage_mb MB)"
    else
        echo "ℹ Storage usage is moderate ($storage_mb MB)"
    fi
    echo
}

# Main dashboard loop
run_dashboard() {
    local refresh_interval=${1:-30}

    echo "Starting retention dashboard (refresh every $refresh_interval seconds)"
    echo "Press Ctrl+C to exit"
    sleep 2

    while true; do
        show_header
        show_key_metrics
        show_tsdb_health
        show_recent_activity
        show_disk_space
        show_recommendations

        echo "Next refresh in $refresh_interval seconds..."
        sleep $refresh_interval
    done
}

# Check arguments
if [ "$1" = "--once" ]; then
    show_header
    show_key_metrics
    show_tsdb_health
    show_recent_activity
    show_disk_space
    show_recommendations
else
    run_dashboard ${1:-30}
fi
EOF

chmod +x ~/retention_dashboard.sh
```

**Step 2: Run the retention dashboard** ▶️

```bash
~/retention_dashboard.sh
```

---

## 🛠️ Troubleshooting Common Issues

<details>
<summary><strong>Issue 1: Prometheus Not Starting</strong></summary>

**Symptoms:** Service fails to start or immediately stops

**Solution:**

```bash
# Check service status
sudo systemctl status prometheus

# Check logs
sudo journalctl -u prometheus -f

# Verify configuration
/usr/local/bin/promtool check config /etc/prometheus/prometheus.yml

# Check permissions
sudo chown -R prometheus:prometheus /var/lib/prometheus/
sudo chown -R prometheus:prometheus /etc/prometheus/
```

</details>

<details>
<summary><strong>Issue 2: Retention Not Working</strong></summary>

**Symptoms:** Old data not being cleaned up

**Solution:**

```bash
# Verify retention settings
ps aux | grep prometheus | grep retention

# Check TSDB compaction
curl -s http://localhost:9090/api/v1/status/tsdb | jq '.data'

# Force compaction (if needed)
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot
```

</details>

<details>
<summary><strong>Issue 3: High Disk Usage</strong></summary>

**Symptoms:** Disk space filling up despite retention policies

**Solution:**

```bash
# Check actual storage usage
du -sh /var/lib/prometheus/

# Identify large files
find /var/lib/prometheus/ -type f -size +10M -exec ls -lh {} \;

# Clean up if necessary
sudo systemctl stop prometheus
sudo rm -rf /var/lib/prometheus/wal/
sudo systemctl start prometheus
```

</details>

---

## 🏆 Best Practices for Production

### Retention Policy Guidelines

**Time-based retention** — set based on business requirements:
- Development: 7-15 days
- Production: 30-90 days
- Long-term storage: Use remote storage

**Size-based retention** — set as a safety net:
- Calculate based on available disk space
- Leave 20-30% buffer for system operations

**Monitoring retention effectiveness:**
- Set up alerts for high disk usage
- Monitor data cleanup frequency
- Track storage growth trends

### Configuration Examples

**Development Environment:**
```bash
--storage.tsdb.retention.time=7d
--storage.tsdb.retention.size=1GB
```

**Production Environment:**
```bash
--storage.tsdb.retention.time=30d
--storage.tsdb.retention.size=10GB
```

**High-Volume Environment:**
```bash
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=50GB
```

---

## ✅ Conclusion

### Key Accomplishments

In this lab, you have successfully:

- ✅ Configured time-based retention policies in Prometheus to automatically manage data lifecycle based on age
- ✅ Implemented size-based retention limits to prevent disk space exhaustion
- ✅ Created comprehensive monitoring tools to track retention policy effectiveness
- ✅ Tested retention behavior under various load conditions
- ✅ Developed troubleshooting skills for common retention-related issues

### Real-World Applications

Proper retention policy configuration is crucial for production monitoring systems because it:

- Prevents disk space exhaustion that could crash your monitoring infrastructure
- Optimizes query performance by limiting the amount of data Prometheus needs to search
- Reduces storage costs in cloud environments where storage is billed by usage
- Ensures compliance with data retention regulations in regulated industries
- Maintains system stability by preventing resource exhaustion

### Key Takeaways

- Always set both time and size-based retention as safety measures
- Monitor retention effectiveness regularly to ensure policies are working
- Consider your query patterns when setting retention periods
- Plan for data growth and adjust retention policies accordingly
- Use remote storage solutions for long-term data archival needs

The skills learned in this lab are essential for maintaining healthy, efficient Prometheus deployments in production environments where data volume and storage management are critical concerns.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al_Nafi-Cybersecurity_Training-blueviolet?style=for-the-badge)

</div>
