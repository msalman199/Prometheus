<div align="center">

# 🔌 Using Exporters with Prometheus

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Blackbox Exporter](https://img.shields.io/badge/Blackbox%20Exporter-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

**A hands-on lab integrating Node Exporter, MySQL Exporter, and Blackbox Exporter with Prometheus to build comprehensive system, database, and endpoint monitoring dashboards.**

</div>

---

## 📑 Table of Contents

- [🎯 Lab Objectives](#-lab-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🧩 Key Concepts](#-key-concepts)
- [🖧 Task 1: Install and Configure Node Exporter](#-task-1-install-and-configure-node-exporter)
- [📊 Task 2: Monitor System Performance Metrics](#-task-2-monitor-system-performance-metrics)
- [🗄️ Task 3: Configure MySQL Exporter for Database Monitoring](#️-task-3-configure-mysql-exporter-for-database-monitoring)
- [📈 Task 4: Create Comprehensive Monitoring Queries](#-task-4-create-comprehensive-monitoring-queries)
- [✅ Task 5: Verification and Testing](#-task-5-verification-and-testing)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🏁 Conclusion](#-conclusion)

---

## 🎯 Lab Objectives

By the end of this lab, you will be able to:

| # | Objective |
|---|-----------|
| 1 | Install and configure Node Exporter to collect system metrics |
| 2 | Set up MySQL Exporter for database monitoring |
| 3 | Configure Blackbox Exporter for endpoint monitoring |
| 4 | Integrate multiple exporters with Prometheus |
| 5 | Create comprehensive monitoring dashboards using various exporter metrics |
| 6 | Understand the architecture and communication between Prometheus and exporters |

## 📋 Prerequisites

Before starting this lab, you should have:

- ✅ Basic understanding of Linux command line operations
- ✅ Familiarity with YAML configuration files
- ✅ Basic knowledge of Prometheus concepts from previous labs
- ✅ Understanding of system monitoring fundamentals
- ✅ Basic MySQL database knowledge

## 🖥️ Lab Environment

> **☁️ Al Nafi Cloud Machine**
> Al Nafi provides Linux-based cloud machines for this lab. Simply click **Start Lab** to access your dedicated Linux machine. The provided machine is bare metal with no pre-installed tools — you will install all required components during the lab exercises.
>
> **⚠️ Important Note:** All tasks in this lab are performed on a **single Linux machine**. No additional machines or remote hosts are required.

## 🧩 Key Concepts

| Concept | Description |
|---------|-------------|
| **Exporter** | A small service that translates metrics from a third-party system (OS, database, endpoint) into the Prometheus exposition format at a `/metrics` HTTP endpoint |
| **Node Exporter** | Exposes hardware and OS-level metrics (CPU, memory, disk, network) from Unix systems |
| **MySQL Exporter (`mysqld_exporter`)** | Connects to a MySQL instance with a dedicated monitoring user and exposes connection, query, and performance metrics |
| **Blackbox Exporter** | A "prober" exporter — it doesn't expose its own state, but actively probes remote targets (HTTP, TCP, ICMP) on Prometheus's behalf |
| **Probe Relabeling Pattern** | The `metrics_path: /probe` + `params.module` + `relabel_configs` pattern that lets Prometheus scrape Blackbox Exporter *about* a target instead of scraping the target directly |
| **Dedicated System User** | Each exporter runs under its own `--no-create-home --shell /bin/false` system account, following least-privilege service hygiene |
| **Multi-Exporter Architecture** | A single Prometheus instance can scrape many independent exporters concurrently, each contributing a different observability dimension |

---

## 🖧 Task 1: Install and Configure Node Exporter

### 📦 Subtask 1.1: Download and Install Node Exporter

Node Exporter is a Prometheus exporter that collects hardware and OS metrics from Unix systems.

**Step 1: Update the system packages**

```bash
sudo apt update && sudo apt upgrade -y
```

**Step 2: Create a dedicated user for Node Exporter**

```bash
sudo useradd --no-create-home --shell /bin/false node_exporter
```

**Step 3: Download Node Exporter**

```bash
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
```

**Step 4: Extract and install Node Exporter**

```bash
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

### ⚙️ Subtask 1.2: Create Node Exporter Service

**Step 1: Create a systemd service file**

```bash
sudo nano /etc/systemd/system/node_exporter.service
```

**Step 2: Add the following configuration to the service file**

```ini
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter --collector.systemd

[Install]
WantedBy=multi-user.target
```

**Step 3: Enable and start Node Exporter service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

**Step 4: Verify Node Exporter is running**

```bash
sudo systemctl status node_exporter
curl http://localhost:9100/metrics | head -20
```

### 🛠️ Subtask 1.3: Install and Configure Prometheus

**Step 1: Create Prometheus user**

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

**Step 2: Create directories for Prometheus**

```bash
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

**Step 3: Download and install Prometheus**

```bash
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvf prometheus-2.45.0.linux-amd64.tar.gz
sudo cp prometheus-2.45.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.45.0.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

**Step 4: Create Prometheus configuration file**

```bash
sudo nano /etc/prometheus/prometheus.yml
```

**Step 5: Add the following configuration**

```yaml
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
```

**Step 6: Set proper ownership**

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

**Step 7: Create Prometheus systemd service**

```bash
sudo nano /etc/systemd/system/prometheus.service
```

**Step 8: Add service configuration**

```ini
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
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
```

**Step 9: Start Prometheus service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus
```

---

## 📊 Task 2: Monitor System Performance Metrics

### 🔍 Subtask 2.1: Explore Node Exporter Metrics

**Step 1: Access Node Exporter metrics endpoint**

```bash
curl http://localhost:9100/metrics | grep -E "node_cpu|node_memory|node_disk"
```

**Step 2: Check specific CPU metrics**

```bash
curl -s http://localhost:9100/metrics | grep "node_cpu_seconds_total" | head -10
```

**Step 3: Check memory metrics**

```bash
curl -s http://localhost:9100/metrics | grep -E "node_memory_(MemTotal|MemFree|MemAvailable)"
```

**Step 4: Check disk metrics**

```bash
curl -s http://localhost:9100/metrics | grep -E "node_disk_(read_bytes|written_bytes)_total"
```

### 📈 Subtask 2.2: Query Metrics in Prometheus

**Step 1: Access Prometheus web interface**

Open a web browser and navigate to `http://your-server-ip:9090`

**Step 2: Execute basic queries for system monitoring**

Try these queries in the Prometheus query interface:

```promql
# CPU Usage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk Usage
100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes)

# Network Traffic
rate(node_network_receive_bytes_total[5m])
```

**Step 3: Create a simple monitoring script**

```bash
nano system_monitor.sh
```

Add the following content:

```bash
#!/bin/bash

echo "=== System Monitoring Report ==="
echo "Timestamp: $(date)"
echo ""

# 💻 CPU Usage
echo "CPU Metrics:"
curl -s 'http://localhost:9090/api/v1/query?query=100%20-%20(avg%20by%20(instance)%20(rate(node_cpu_seconds_total{mode="idle"}[5m]))%20*%20100)' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'CPU Usage: {float(data[\"data\"][\"result\"][0][\"value\"][1]):.2f}%')" 2>/dev/null || echo "CPU data not available"

# 🧠 Memory Usage
echo "Memory Metrics:"
curl -s 'http://localhost:9090/api/v1/query?query=(1%20-%20(node_memory_MemAvailable_bytes%20/%20node_memory_MemTotal_bytes))%20*%20100' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Memory Usage: {float(data[\"data\"][\"result\"][0][\"value\"][1]):.2f}%')" 2>/dev/null || echo "Memory data not available"

echo ""
echo "=== End Report ==="
```

**Step 4: Make the script executable and run it**

```bash
chmod +x system_monitor.sh
./system_monitor.sh
```

---

## 🗄️ Task 3: Configure MySQL Exporter for Database Monitoring

### 🐬 Subtask 3.1: Install and Configure MySQL

**Step 1: Install MySQL server**

```bash
sudo apt install mysql-server -y
```

**Step 2: Start and enable MySQL service**

```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Step 3: Secure MySQL installation**

```bash
sudo mysql_secure_installation
```

> Follow the prompts and set a root password when asked.

**Step 4: Create a database and user for monitoring**

```bash
sudo mysql -u root -p
```

Execute the following SQL commands:

```sql
CREATE DATABASE testdb;
CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'exporterpassword';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 📡 Subtask 3.2: Install and Configure MySQL Exporter

**Step 1: Create MySQL Exporter user**

```bash
sudo useradd --no-create-home --shell /bin/false mysql_exporter
```

**Step 2: Download MySQL Exporter**

```bash
cd /tmp
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.0/mysqld_exporter-0.15.0.linux-amd64.tar.gz
```

**Step 3: Extract and install MySQL Exporter**

```bash
tar xvf mysqld_exporter-0.15.0.linux-amd64.tar.gz
sudo cp mysqld_exporter-0.15.0.linux-amd64/mysqld_exporter /usr/local/bin/
sudo chown mysql_exporter:mysql_exporter /usr/local/bin/mysqld_exporter
```

**Step 4: Create MySQL Exporter configuration file**

```bash
sudo nano /etc/mysql_exporter.cnf
```

Add the following configuration:

```ini
[client]
user=exporter
password=exporterpassword
host=localhost
port=3306
```

**Step 5: Set proper permissions**

```bash
sudo chown mysql_exporter:mysql_exporter /etc/mysql_exporter.cnf
sudo chmod 600 /etc/mysql_exporter.cnf
```

**Step 6: Create MySQL Exporter systemd service**

```bash
sudo nano /etc/systemd/system/mysql_exporter.service
```

Add the following configuration:

```ini
[Unit]
Description=MySQL Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=mysql_exporter
Group=mysql_exporter
Type=simple
ExecStart=/usr/local/bin/mysqld_exporter --config.my-cnf=/etc/mysql_exporter.cnf
Restart=always

[Install]
WantedBy=multi-user.target
```

**Step 7: Start MySQL Exporter service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable mysql_exporter
sudo systemctl start mysql_exporter
sudo systemctl status mysql_exporter
```

**Step 8: Verify MySQL Exporter is working**

```bash
curl http://localhost:9104/metrics | grep mysql | head -10
```

### 🕳️ Subtask 3.3: Configure Blackbox Exporter

**Step 1: Create Blackbox Exporter user**

```bash
sudo useradd --no-create-home --shell /bin/false blackbox_exporter
```

**Step 2: Download Blackbox Exporter**

```bash
cd /tmp
wget https://github.com/prometheus/blackbox_exporter/releases/download/v0.24.0/blackbox_exporter-0.24.0.linux-amd64.tar.gz
```

**Step 3: Extract and install Blackbox Exporter**

```bash
tar xvf blackbox_exporter-0.24.0.linux-amd64.tar.gz
sudo cp blackbox_exporter-0.24.0.linux-amd64/blackbox_exporter /usr/local/bin/
sudo chown blackbox_exporter:blackbox_exporter /usr/local/bin/blackbox_exporter
```

**Step 4: Create Blackbox Exporter configuration directory**

```bash
sudo mkdir /etc/blackbox_exporter
sudo chown blackbox_exporter:blackbox_exporter /etc/blackbox_exporter
```

**Step 5: Create Blackbox Exporter configuration file**

```bash
sudo nano /etc/blackbox_exporter/blackbox.yml
```

Add the following configuration:

```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []
      method: GET
      follow_redirects: true
      preferred_ip_protocol: "ip4"

  tcp_connect:
    prober: tcp
    timeout: 5s

  icmp:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
```

**Step 6: Set proper ownership**

```bash
sudo chown blackbox_exporter:blackbox_exporter /etc/blackbox_exporter/blackbox.yml
```

**Step 7: Create Blackbox Exporter systemd service**

```bash
sudo nano /etc/systemd/system/blackbox_exporter.service
```

Add the following configuration:

```ini
[Unit]
Description=Blackbox Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=blackbox_exporter
Group=blackbox_exporter
Type=simple
ExecStart=/usr/local/bin/blackbox_exporter --config.file=/etc/blackbox_exporter/blackbox.yml
Restart=always

[Install]
WantedBy=multi-user.target
```

**Step 8: Start Blackbox Exporter service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable blackbox_exporter
sudo systemctl start blackbox_exporter
sudo systemctl status blackbox_exporter
```

**Step 9: Test Blackbox Exporter**

```bash
curl "http://localhost:9115/probe?target=google.com&module=http_2xx" | grep probe_success
```

### 🔄 Subtask 3.4: Update Prometheus Configuration

**Step 1: Update Prometheus configuration to include all exporters**

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Replace the content with:

```yaml
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

  - job_name: 'mysql_exporter'
    static_configs:
      - targets: ['localhost:9104']

  - job_name: 'blackbox_http'
    metrics_path: /probe
    params:
      module: [http_2xx]           # 🌐 which Blackbox module to use
    static_configs:
      - targets:
        - http://google.com
        - http://github.com
        - http://localhost:9090
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115   # 🕳️ actually scrape Blackbox, not the target

  - job_name: 'blackbox_tcp'
    metrics_path: /probe
    params:
      module: [tcp_connect]
    static_configs:
      - targets:
        - localhost:3306
        - localhost:9090
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
```

**Step 2: Restart Prometheus to apply new configuration**

```bash
sudo systemctl restart prometheus
sudo systemctl status prometheus
```

**Step 3: Verify all targets are being scraped**

```bash
curl http://localhost:9090/api/v1/targets | python3 -m json.tool
```

---

## 📈 Task 4: Create Comprehensive Monitoring Queries

### 🗃️ Subtask 4.1: Database Monitoring Queries

**Step 1: Create a script to test MySQL monitoring**

```bash
nano mysql_monitor.sh
```

Add the following content:

```bash
#!/bin/bash

echo "=== MySQL Monitoring Report ==="
echo "Timestamp: $(date)"
echo ""

# 🔌 MySQL Connection Status
echo "MySQL Connections:"
curl -s 'http://localhost:9090/api/v1/query?query=mysql_global_status_threads_connected' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Active Connections: {data[\"data\"][\"result\"][0][\"value\"][1]}')" 2>/dev/null || echo "MySQL connection data not available"

# ⏱️ MySQL Uptime
echo "MySQL Uptime:"
curl -s 'http://localhost:9090/api/v1/query?query=mysql_global_status_uptime' | \
python3 -c "import sys, json; data=json.load(sys.stdin); uptime=int(float(data[\"data\"][\"result\"][0][\"value\"][1])); print(f'Uptime: {uptime//3600}h {(uptime%3600)//60}m {uptime%60}s')" 2>/dev/null || echo "MySQL uptime data not available"

echo ""
echo "=== End MySQL Report ==="
```

**Step 2: Make executable and run**

```bash
chmod +x mysql_monitor.sh
./mysql_monitor.sh
```

### 🌐 Subtask 4.2: Network Connectivity Monitoring

**Step 1: Create a connectivity monitoring script**

```bash
nano connectivity_monitor.sh
```

Add the following content:

```bash
#!/bin/bash

echo "=== Connectivity Monitoring Report ==="
echo "Timestamp: $(date)"
echo ""

# 🌐 Check HTTP endpoints
echo "HTTP Endpoint Status:"
targets=("http://google.com" "http://github.com" "http://localhost:9090")

for target in "${targets[@]}"; do
    status=$(curl -s "http://localhost:9090/api/v1/query?query=probe_success{instance=\"$target\"}" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['result'][0]['value'][1] if data['data']['result'] else '0')" 2>/dev/null)
    
    if [ "$status" = "1" ]; then
        echo "$target: UP"
    else
        echo "$target: DOWN"
    fi
done

echo ""
echo "TCP Port Status:"
tcp_targets=("localhost:3306" "localhost:9090")

for target in "${tcp_targets[@]}"; do
    status=$(curl -s "http://localhost:9090/api/v1/query?query=probe_success{instance=\"$target\",job=\"blackbox_tcp\"}" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['result'][0]['value'][1] if data['data']['result'] else '0')" 2>/dev/null)
    
    if [ "$status" = "1" ]; then
        echo "$target: OPEN"
    else
        echo "$target: CLOSED"
    fi
done

echo ""
echo "=== End Connectivity Report ==="
```

**Step 2: Make executable and run**

```bash
chmod +x connectivity_monitor.sh
./connectivity_monitor.sh
```

### 📺 Subtask 4.3: Create a Comprehensive Monitoring Dashboard Script

**Step 1: Create a complete monitoring dashboard**

```bash
nano monitoring_dashboard.sh
```

Add the following content:

```bash
#!/bin/bash

clear
echo "=========================================="
echo "    COMPREHENSIVE MONITORING DASHBOARD    "
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# 💻 System Metrics
echo "--- SYSTEM METRICS ---"
echo "CPU Usage:"
cpu_usage=$(curl -s 'http://localhost:9090/api/v1/query?query=100%20-%20(avg%20by%20(instance)%20(rate(node_cpu_seconds_total{mode="idle"}[5m]))%20*%20100)' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{float(data[\"data\"][\"result\"][0][\"value\"][1]):.2f}%')" 2>/dev/null || echo "N/A")
echo "  Current: $cpu_usage"

echo "Memory Usage:"
mem_usage=$(curl -s 'http://localhost:9090/api/v1/query?query=(1%20-%20(node_memory_MemAvailable_bytes%20/%20node_memory_MemTotal_bytes))%20*%20100' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{float(data[\"data\"][\"result\"][0][\"value\"][1]):.2f}%')" 2>/dev/null || echo "N/A")
echo "  Current: $mem_usage"

echo "Load Average:"
load_avg=$(curl -s 'http://localhost:9090/api/v1/query?query=node_load1' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{float(data[\"data\"][\"result\"][0][\"value\"][1]):.2f}')" 2>/dev/null || echo "N/A")
echo "  1-minute: $load_avg"

echo ""

# 🗄️ Database Metrics
echo "--- DATABASE METRICS ---"
mysql_connections=$(curl -s 'http://localhost:9090/api/v1/query?query=mysql_global_status_threads_connected' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(data[\"data\"][\"result\"][0][\"value\"][1])" 2>/dev/null || echo "N/A")
echo "MySQL Connections: $mysql_connections"

mysql_queries=$(curl -s 'http://localhost:9090/api/v1/query?query=rate(mysql_global_status_queries[5m])' | \
python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{float(data[\"data\"][\"result\"][0][\"value\"][1]):.2f}/sec')" 2>/dev/null || echo "N/A")
echo "MySQL Queries/sec: $mysql_queries"

echo ""

# 🛎️ Service Status
echo "--- SERVICE STATUS ---"
services=("prometheus" "node_exporter" "mysql_exporter" "blackbox_exporter" "mysql")

for service in "${services[@]}"; do
    status=$(systemctl is-active $service 2>/dev/null)
    if [ "$status" = "active" ]; then
        echo "$service: RUNNING"
    else
        echo "$service: STOPPED"
    fi
done

echo ""

# 🌐 Connectivity Status
echo "--- CONNECTIVITY STATUS ---"
http_targets=("http://google.com" "http://github.com")

for target in "${http_targets[@]}"; do
    status=$(curl -s "http://localhost:9090/api/v1/query?query=probe_success{instance=\"$target\"}" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['result'][0]['value'][1] if data['data']['result'] else '0')" 2>/dev/null)
    
    if [ "$status" = "1" ]; then
        echo "$target: REACHABLE"
    else
        echo "$target: UNREACHABLE"
    fi
done

echo ""
echo "=========================================="
echo "Dashboard refresh: ./monitoring_dashboard.sh"
echo "Prometheus Web UI: http://localhost:9090"
echo "=========================================="
```

**Step 2: Make executable and run**

```bash
chmod +x monitoring_dashboard.sh
./monitoring_dashboard.sh
```

---

## ✅ Task 5: Verification and Testing

### 🔎 Subtask 5.1: Verify All Exporters are Working

**Step 1: Check all exporter endpoints**

```bash
echo "Checking Node Exporter..."
curl -s http://localhost:9100/metrics | grep "node_cpu_seconds_total" | wc -l

echo "Checking MySQL Exporter..."
curl -s http://localhost:9104/metrics | grep "mysql_up"

echo "Checking Blackbox Exporter..."
curl -s http://localhost:9115/metrics | grep "blackbox_exporter_build_info"
```

**Step 2: Verify Prometheus targets**

```bash
curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
for target in data['data']['activeTargets']:
    print(f\"Job: {target['job']}, Instance: {target['instance']}, Health: {target['health']}\")
"
```

### 🏋️ Subtask 5.2: Generate Test Load and Monitor

**Step 1: Create a load generation script**

```bash
nano generate_load.sh
```

Add the following content:

```bash
#!/bin/bash

echo "Generating system load for monitoring test..."

# 💻 CPU load
echo "Starting CPU load..."
for i in {1..4}; do
    yes > /dev/null &
done

# 🧠 Memory load
echo "Starting memory load..."
stress-ng --vm 1 --vm-bytes 512M --timeout 60s &

# 💽 Disk I/O load
echo "Starting disk I/O load..."
dd if=/dev/zero of=/tmp/testfile bs=1M count=100 &

echo "Load generation started. Monitor for 60 seconds..."
echo "Use Ctrl+C to stop early or wait for automatic cleanup."

sleep 60

# 🧹 Cleanup
echo "Cleaning up..."
killall yes 2>/dev/null
killall stress-ng 2>/dev/null
rm -f /tmp/testfile

echo "Load generation completed."
```

**Step 2: Install stress-ng for load testing**

```bash
sudo apt install stress-ng -y
```

**Step 3: Make the script executable**

```bash
chmod +x generate_load.sh
```

**Step 4: Run load generation in background and monitor**

```bash
# Start monitoring dashboard in one terminal
./monitoring_dashboard.sh

# In another terminal or after noting initial values, run:
# ./generate_load.sh
```

### 🐬 Subtask 5.3: Test Database Monitoring

**Step 1: Create database activity**

```bash
mysql -u root -p -e "
USE testdb;
CREATE TABLE test_table (id INT AUTO_INCREMENT PRIMARY KEY, data VARCHAR(255));
INSERT INTO test_table (data) VALUES ('test1'), ('test2'), ('test3');
SELECT * FROM test_table;
"
```

**Step 2: Monitor database metrics**

```bash
./mysql_monitor.sh
```

---

## 🛠️ Troubleshooting

<details>
<summary><strong>Issue 1: Exporter service fails to start</strong></summary>

**Solution:**

- Check service logs using `sudo journalctl -u service_name -f`
- Verify user permissions and file ownership
- Ensure configuration files are properly formatted

</details>

<details>
<summary><strong>Issue 2: Prometheus cannot scrape targets</strong></summary>

**Solution:**

- Check firewall settings: `sudo ufw status`
- Verify target endpoints are accessible: `curl http://localhost:port/metrics`
- Check Prometheus configuration syntax: `promtool check config /etc/prometheus/prometheus.yml`

</details>

<details>
<summary><strong>Issue 3: MySQL Exporter authentication fails</strong></summary>

**Solution:**

- Verify MySQL user permissions: `SHOW GRANTS FOR 'exporter'@'localhost';`
- Check MySQL Exporter configuration file permissions
- Test MySQL connection manually: `mysql -u exporter -p`

</details>

<details>
<summary><strong>Issue 4: Blackbox Exporter probe failures</strong></summary>

**Solution:**

- Check network connectivity to target hosts
- Verify Blackbox Exporter configuration syntax
- Test probe manually: `curl "http://localhost:9115/probe?target=google.com&module=http_2xx"`

</details>

<details>
<summary><strong>Issue 5: High resource usage</strong></summary>

**Solution:**

- Adjust scrape intervals in Prometheus configuration
- Reduce retention time: add `--storage.tsdb.retention.time=7d` to the Prometheus service
- Monitor system resources: `htop` or `./monitoring_dashboard.sh`

</details>

---

## 🏁 Conclusion

In this comprehensive lab, you have successfully:

### 🎯 Key Accomplishments

- ✅ Installed and configured Node Exporter to collect detailed system metrics including CPU, memory, disk, and network statistics
- ✅ Set up MySQL Exporter for comprehensive database monitoring, tracking connections, queries, and performance metrics
- ✅ Implemented Blackbox Exporter for endpoint monitoring, testing HTTP connectivity and TCP port availability
- ✅ Integrated multiple exporters with Prometheus using proper configuration and service management
- ✅ Created monitoring scripts and dashboards to visualize and analyze metrics from all exporters
- ✅ Learned troubleshooting techniques for common exporter and Prometheus integration issues

This lab demonstrates the power of Prometheus exporters in creating a comprehensive monitoring solution. The combination of system metrics from Node Exporter, database metrics from MySQL Exporter, and connectivity metrics from Blackbox Exporter provides complete visibility into your infrastructure.

### 📌 Key Takeaways

- Exporters extend Prometheus capabilities to monitor specific services and systems
- Proper configuration and service management are crucial for reliable monitoring
- Multiple exporters can work together to provide comprehensive observability
- Regular monitoring and alerting help maintain system health and performance

### 🚀 Next Steps

- Explore additional exporters for other services (Redis, PostgreSQL, Apache, etc.)
- Implement alerting rules based on exporter metrics
- Create custom exporters for application-specific monitoring
- Integrate with visualization tools like Grafana for advanced dashboards

The monitoring infrastructure you've built in this lab forms the foundation for production-ready observability systems that can scale to monitor complex, distributed applications and infrastructure.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al%20Nafi-Cybersecurity%20Training-blueviolet?style=for-the-badge)

</div>
