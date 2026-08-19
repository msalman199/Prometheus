# 🚀 Troubleshooting Prometheus

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange?style=for-the-badge\&logo=prometheus)
![Linux](https://img.shields.io/badge/Linux-Administration-FCC624?style=for-the-badge\&logo=linux\&logoColor=black)
![YAML](https://img.shields.io/badge/YAML-Configuration-CB171E?style=for-the-badge\&logo=yaml)
![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?style=for-the-badge\&logo=gnu-bash\&logoColor=white)
![Systemd](https://img.shields.io/badge/Systemd-Service%20Management-000000?style=for-the-badge\&logo=linux)
![Monitoring](https://img.shields.io/badge/Observability-Monitoring-blue?style=for-the-badge)

> 🛠️ A hands-on Prometheus troubleshooting lab covering configuration validation, scraping failures, service debugging, health checks, logging, automated diagnostics, and production troubleshooting techniques.

---

## 📌 Table of Contents

* [🎯 Lab Objectives](#-lab-objectives)
* [📋 Prerequisites](#-prerequisites)
* [🏗️ Lab Environment](#️-lab-environment)
* [🧰 Technology Stack](#-technology-stack)
* [🔭 Lab Architecture](#-lab-architecture)
* [🚀 Task 1 — Prometheus Environment Setup](#-task-1--prometheus-environment-setup)
* [🔎 Task 2 — Promtool Configuration Validation](#-task-2--promtool-configuration-validation)
* [🎯 Task 3 — Troubleshooting Scraping Issues](#-task-3--troubleshooting-scraping-issues)
* [🧪 Task 4 — Advanced Troubleshooting](#-task-4--advanced-troubleshooting)
* [📚 Task 5 — Troubleshooting Documentation](#-task-5--troubleshooting-documentation)
* [🩺 Common Problems and Solutions](#-common-problems-and-solutions)
* [📊 Troubleshooting Workflow](#-troubleshooting-workflow)
* [🔐 Production Best Practices](#-production-best-practices)
* [✅ Validation Checklist](#-validation-checklist)
* [🏁 Conclusion](#-conclusion)

---

# 🎯 Lab Objectives

By completing this lab, you will learn how to:

* 🔍 Use **promtool** to validate Prometheus configuration files.
* 🧩 Identify YAML syntax and configuration errors.
* 🎯 Troubleshoot Prometheus scraping failures.
* 🌐 Diagnose network connectivity problems.
* 📜 Analyze Prometheus systemd logs.
* 🐞 Run Prometheus with debug logging.
* 🔄 Reload configuration without restarting Prometheus.
* 🩺 Perform Prometheus health and readiness checks.
* 📊 Inspect Prometheus target status through its HTTP API.
* 🤖 Build automated Prometheus diagnostic scripts.
* 📝 Document recurring Prometheus problems and solutions.
* 🏭 Apply systematic troubleshooting techniques suitable for production environments.

---

# 📋 Prerequisites

Before beginning the lab, you should have:

* 🐧 Basic Linux command-line knowledge.
* 📄 Familiarity with YAML.
* 📈 Basic Prometheus knowledge.
* 🌐 Understanding of HTTP status codes.
* 🔌 Basic networking knowledge.
* ✏️ Familiarity with `nano` or `vim`.
* 🐚 Basic Bash scripting knowledge.
* ⚙️ Basic understanding of `systemd`.

---

# 🏗️ Lab Environment

The lab is designed for the **Al Nafi Linux cloud environment**.

The machine is intentionally provided without the required monitoring tools so that you can practice the complete installation and troubleshooting process.

### Main Components

| Component     | Purpose                           |
| ------------- | --------------------------------- |
| Prometheus    | Metrics collection and monitoring |
| Promtool      | Configuration and rule validation |
| Node Exporter | Host-level metrics                |
| systemd       | Service management                |
| journalctl    | Log investigation                 |
| curl          | API and endpoint testing          |
| Bash          | Diagnostic automation             |
| YAML          | Prometheus configuration          |

---

# 🧰 Technology Stack

### 📊 Monitoring

![Prometheus](https://img.shields.io/badge/Prometheus-2.45.0-orange?style=flat-square\&logo=prometheus)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-1.6.0-green?style=flat-square)

### 🐧 Operating System

![Linux](https://img.shields.io/badge/Linux-Ubuntu-FCC624?style=flat-square\&logo=linux\&logoColor=black)

### ⚙️ Administration

![Systemd](https://img.shields.io/badge/systemd-Service%20Management-black?style=flat-square)
![Bash](https://img.shields.io/badge/Bash-Automation-4EAA25?style=flat-square\&logo=gnu-bash\&logoColor=white)

---

# 🔭 Lab Architecture

```text
                    ┌──────────────────────────┐
                    │       Prometheus         │
                    │        :9090             │
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
     ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
     │ Prometheus   │    │ Node Exporter│    │ Broken Target│
     │ localhost    │    │    :9100     │    │    :8080     │
     │    :9090     │    │              │    │              │
     └──────────────┘    └──────────────┘    └──────────────┘
                                      
                    ┌──────────────────────────┐
                    │   promtool / journalctl  │
                    │   curl / diagnostic bash  │
                    └──────────────────────────┘
```

The intentionally broken targets are used to demonstrate realistic troubleshooting scenarios.

---

# 🚀 Task 1 — Prometheus Environment Setup

## 1.1 🔧 Update the System

```bash
sudo apt update
```

---

## 1.2 👤 Create the Prometheus User

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

Create the required directories:

```bash
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

---

## 1.3 📥 Download Prometheus

```bash
cd /tmp

wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

tar xvf prometheus-2.45.0.linux-amd64.tar.gz

cd prometheus-2.45.0.linux-amd64
```

Install the binaries:

```bash
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
```

Set ownership:

```bash
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

Copy Prometheus console files:

```bash
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus

sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

Verify the installation:

```bash
prometheus --version
promtool --version
```

---

# ⚙️ 1.4 Create the Initial Configuration

Create:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add:

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

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'broken-target'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 10s
    scrape_timeout: 5s

  - job_name: 'invalid-config'
    static_configs:
      - targets: ['invalid-hostname:9090']
    metrics_path: '/invalid/path'
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

---

# 🖥️ 1.5 Install Node Exporter

Download Node Exporter:

```bash
cd /tmp

wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz

tar xvf node_exporter-1.6.0.linux-amd64.tar.gz

sudo cp node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/

sudo chown prometheus:prometheus /usr/local/bin/node_exporter
```

Create the service:

```bash
sudo nano /etc/systemd/system/node_exporter.service
```

Add:

```ini
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
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

Check:

```bash
sudo systemctl status node_exporter
```

Test:

```bash
curl http://localhost:9100/metrics
```

### ✅ Expected Result

You should receive Prometheus-formatted metrics from Node Exporter.

---

# 🔎 Task 2 — Promtool Configuration Validation

## 2.1 🧪 Validate the Configuration

Run:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

### 💡 Why Use Promtool?

`promtool` helps identify:

* YAML syntax errors.
* Invalid configuration fields.
* Incorrect scrape settings.
* Rule syntax errors.
* Configuration loading problems.

---

# 💥 2.2 Create a Broken YAML Configuration

Create:

```bash
sudo nano /etc/prometheus/broken-syntax.yml
```

Add:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'broken-job'
    static_configs
      - targets: ['localhost:9100'
    scrape_interval: invalid_value
```

Validate:

```bash
promtool check config /etc/prometheus/broken-syntax.yml
```

### 🔍 What to Look For

Promtool should identify problems such as:

* Invalid YAML structure.
* Missing syntax elements.
* Incorrect indentation.
* Invalid configuration values.

---

# ⚠️ 2.3 Test Logical Configuration Errors

Create:

```bash
sudo nano /etc/prometheus/logical-errors.yml
```

Add:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'duplicate-job'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'duplicate-job'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'invalid-timeout'
    static_configs:
      - targets: ['localhost:9091']
    scrape_timeout: 30s
    scrape_interval: 15s
```

Validate:

```bash
promtool check config /etc/prometheus/logical-errors.yml
```

> ⚠️ **Important:** Some semantic or operational problems may not be caught by a basic configuration check. Always validate the behavior of the running Prometheus instance as well.

---

# 📜 2.4 Validate Prometheus Rules

Create:

```bash
sudo mkdir -p /etc/prometheus/rules
sudo nano /etc/prometheus/rules/test-rules.yml
```

Add:

```yaml
groups:
  - name: test-rules
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"

      - alert: InvalidSyntax
        expr: invalid_metric_name{job=}
        for: 2m
```

Check:

```bash
promtool check rules /etc/prometheus/rules/test-rules.yml
```

---

# 🎯 Task 3 — Troubleshooting Scraping Issues

## 3.1 ⚙️ Create the Prometheus systemd Service

Create:

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Add:

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
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable Prometheus:

```bash
sudo systemctl enable prometheus
```

Start:

```bash
sudo systemctl start prometheus
```

Check:

```bash
sudo systemctl status prometheus
```

---

# 📜 3.2 Investigate Prometheus Logs

Follow logs:

```bash
sudo journalctl -u prometheus -f
```

View recent logs:

```bash
sudo journalctl -u prometheus --since "10 minutes ago"
```

Search for errors:

```bash
sudo journalctl -u prometheus --no-pager | grep -i error
```

---

# 🌐 3.3 Check Prometheus API

Check target information:

```bash
curl http://localhost:9090/api/v1/targets
```

Check health:

```bash
curl http://localhost:9090/-/healthy
```

Check readiness:

```bash
curl http://localhost:9090/-/ready
```

---

# 🔌 3.4 Test Individual Targets

### Node Exporter

```bash
curl http://localhost:9100/metrics
```

Expected result:

```text
Prometheus metrics
```

### Broken Target

```bash
curl http://localhost:8080/metrics
```

Expected result:

```text
Connection refused
```

### Invalid Host

```bash
curl http://invalid-hostname:9090/metrics
```

Expected result:

```text
DNS or connection failure
```

---

# 🛠️ 3.5 Fix the Configuration

Create:

```bash
sudo nano /etc/prometheus/prometheus-fixed.yml
```

Add:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'prometheus-self'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s
```

Validate:

```bash
promtool check config /etc/prometheus/prometheus-fixed.yml
```

If valid:

```bash
sudo cp /etc/prometheus/prometheus-fixed.yml /etc/prometheus/prometheus.yml

sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

---

# 🔄 3.6 Reload Prometheus

Because the service was started with:

```text
--web.enable-lifecycle
```

you can reload the configuration:

```bash
curl -X POST http://localhost:9090/-/reload
```

Check the logs:

```bash
sudo journalctl -u prometheus --since "1 minute ago"
```

Verify targets:

```bash
curl -s http://localhost:9090/api/v1/targets
```

---

# 🧪 Task 4 — Advanced Troubleshooting

## 4.1 🐞 Enable Debug Logging

Stop Prometheus:

```bash
sudo systemctl stop prometheus
```

Run it manually:

```bash
sudo -u prometheus /usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --log.level=debug
```

Observe the output.

Stop with:

```text
Ctrl+C
```

Restart normally:

```bash
sudo systemctl start prometheus
```

---

# 🔎 4.2 Test Prometheus Queries

Start Prometheus:

```bash
sudo systemctl start prometheus
```

Wait:

```bash
sleep 10
```

Test an instant query:

```bash
promtool query instant http://localhost:9090 'up'
```

A range query can be tested with:

```bash
promtool query range \
  http://localhost:9090 \
  'up' \
  --start=2023-01-01T00:00:00Z \
  --end=2023-01-01T01:00:00Z
```

> ℹ️ For real investigations, use a time range that overlaps the data currently retained by your Prometheus instance.

---

# 🩺 4.3 Create a Prometheus Health-Check Script

Create:

```bash
nano prometheus-health-check.sh
```

Add:

```bash
#!/bin/bash

echo "=== Prometheus Health Check ==="
echo "Date: $(date)"
echo

echo "1. Checking Prometheus service status:"
systemctl is-active prometheus
echo

echo "2. Checking Prometheus port:"
ss -ltnp | grep :9090 || echo "Port 9090 not listening"
echo

echo "3. Checking Prometheus API health:"
curl -s http://localhost:9090/-/healthy || echo "API health check failed"
echo

echo "4. Checking configuration validity:"
promtool check config /etc/prometheus/prometheus.yml
echo

echo "5. Checking target status:"
curl -s http://localhost:9090/api/v1/targets | \
    python3 -m json.tool 2>/dev/null || \
    echo "Failed to get targets status"
echo

echo "6. Recent error logs:"
journalctl -u prometheus \
    --since "5 minutes ago" \
    --no-pager | \
    grep -i error || \
    echo "No recent errors found"
```

Make executable:

```bash
chmod +x prometheus-health-check.sh
```

Run:

```bash
./prometheus-health-check.sh
```

---

# 💥 4.4 Simulate Common Problems

Create:

```bash
nano simulate-problems.sh
```

Add:

```bash
#!/bin/bash

echo "Simulating common Prometheus problems..."

echo "1. Testing configuration file permissions:"
sudo chmod 600 /etc/prometheus/prometheus.yml

sudo systemctl restart prometheus
sleep 5

sudo systemctl status prometheus

echo "Fixing permissions:"
sudo chmod 644 /etc/prometheus/prometheus.yml

sudo systemctl restart prometheus

echo

echo "2. Checking port conflicts:"
ss -ltnp | grep :9090

echo

echo "3. Testing invalid configuration:"
sudo cp /etc/prometheus/broken-syntax.yml \
    /etc/prometheus/prometheus.yml

promtool check config /etc/prometheus/prometheus.yml

echo "Restoring valid configuration:"

sudo cp /etc/prometheus/prometheus-fixed.yml \
    /etc/prometheus/prometheus.yml

sudo chown prometheus:prometheus \
    /etc/prometheus/prometheus.yml

promtool check config /etc/prometheus/prometheus.yml
```

Make executable:

```bash
chmod +x simulate-problems.sh
```

Run:

```bash
./simulate-problems.sh
```

> ⚠️ **Lab Safety:** This script intentionally changes the Prometheus configuration. Always restore the valid configuration after testing.

---

# 📚 Task 5 — Troubleshooting Documentation

## 5.1 📝 Create a Troubleshooting Guide

Create:

```bash
nano prometheus-troubleshooting-guide.md
```

Use the following structure:

```markdown
# Prometheus Troubleshooting Guide

## 1. Configuration Problems

### Symptoms

- Prometheus fails to start.
- Configuration parsing errors appear in logs.

### Checks

promtool check config /etc/prometheus/prometheus.yml

### Resolution

- Correct YAML syntax.
- Check indentation.
- Validate configuration fields.
- Verify file permissions.
- Reload Prometheus after changes.

---

## 2. Target Scraping Problems

### Symptoms

- Target appears DOWN.
- No metrics are collected.

### Checks

curl http://target:port/metrics

### Resolution

- Verify target service is running.
- Check network connectivity.
- Check firewall rules.
- Verify metrics endpoint.
- Verify target hostname and port.

---

## 3. Permission Problems

### Symptoms

- Permission denied messages.
- Prometheus cannot read configuration.
- Prometheus cannot write TSDB data.

### Resolution

Check:

ls -la /etc/prometheus/prometheus.yml
ls -la /var/lib/prometheus/

Verify ownership:

prometheus:prometheus

---

## 4. Resource Problems

### Symptoms

- High memory usage.
- Slow queries.
- Disk-full conditions.
- OOM kills.

### Resolution

- Monitor memory.
- Monitor disk utilization.
- Review retention configuration.
- Optimize expensive queries.
- Reduce unnecessary metric cardinality.
- Scale storage when required.

---

## Useful Commands

promtool check config /etc/prometheus/prometheus.yml

systemctl status prometheus

journalctl -u prometheus -f

curl http://localhost:9090/-/healthy

curl http://localhost:9090/-/ready

curl http://localhost:9090/api/v1/targets
```

---

# 🤖 5.2 Automated Diagnostic Script

Create:

```bash
nano prometheus-diagnostics.sh
```

Add:

```bash
#!/bin/bash

LOG_FILE="/tmp/prometheus-diagnostics-$(date +%Y%m%d-%H%M%S).log"

echo "Prometheus Comprehensive Diagnostics" | tee "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
echo "Hostname: $(hostname)" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

run_check() {
    echo "--- $1 ---" | tee -a "$LOG_FILE"
    eval "$2" 2>&1 | tee -a "$LOG_FILE"
    echo | tee -a "$LOG_FILE"
}

run_check "System Information" "uname -a"
run_check "Memory Usage" "free -h"
run_check "Disk Usage" "df -h"
run_check "CPU Information" "lscpu | head -10"

run_check "Prometheus Service Status" \
    "systemctl status prometheus --no-pager"

run_check "Prometheus Process" \
    "ps aux | grep '[p]rometheus'"

run_check "Network Listening Ports" \
    "ss -ltnp | grep -E ':(9090|9100)'"

run_check "Configuration Validation" \
    "promtool check config /etc/prometheus/prometheus.yml"

run_check "Configuration File Permissions" \
    "ls -la /etc/prometheus/prometheus.yml"

run_check "Data Directory Permissions" \
    "ls -la /var/lib/prometheus/"

run_check "Prometheus Health Check" \
    "curl -s http://localhost:9090/-/healthy"

run_check "Prometheus Ready Check" \
    "curl -s http://localhost:9090/-/ready"

run_check "Node Exporter Check" \
    "curl -s http://localhost:9100/metrics | head -5"

run_check "Recent Prometheus Logs" \
    "journalctl -u prometheus --since '10 minutes ago' --no-pager"

echo "Diagnostics complete."
echo "Full log saved to: $LOG_FILE" | tee -a "$LOG_FILE"
```

Make executable:

```bash
chmod +x prometheus-diagnostics.sh
```

Run:

```bash
./prometheus-diagnostics.sh
```

The generated diagnostic report will be stored under:

```text
/tmp/prometheus-diagnostics-YYYYMMDD-HHMMSS.log
```

---

# 🩺 Common Problems and Solutions

| Problem            | Symptoms                  | Diagnostic Command         | Typical Solution       |
| ------------------ | ------------------------- | -------------------------- | ---------------------- |
| YAML error         | Prometheus won't start    | `promtool check config`    | Fix YAML syntax        |
| Target DOWN        | Metrics unavailable       | `curl target:port/metrics` | Check service/network  |
| Port conflict      | Service fails to bind     | `ss -ltnp`                 | Free/change port       |
| Permission denied  | File/data access errors   | `ls -la`                   | Correct ownership      |
| DNS failure        | Target unreachable        | `getent hosts hostname`    | Fix DNS/hostname       |
| Wrong metrics path | HTTP 404                  | `curl target/metrics`      | Correct `metrics_path` |
| Connection refused | Target unavailable        | `curl`                     | Start target service   |
| Disk full          | TSDB failures             | `df -h`                    | Free/expand storage    |
| High memory        | OOM/slow queries          | `free -h`                  | Optimize/scale         |
| Invalid rule       | Rule loading errors       | `promtool check rules`     | Correct PromQL         |
| Failed reload      | Old configuration remains | `journalctl`               | Fix config and reload  |
| Service crash      | systemd restart loop      | `systemctl status`         | Inspect logs/config    |

---

# 🔄 Troubleshooting Workflow

Use this sequence when diagnosing Prometheus:

```text
┌───────────────────────────┐
│ 1. Is Prometheus running? │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 2. Check systemd status   │
│    systemctl status       │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 3. Check configuration    │
│    promtool check config  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 4. Check Prometheus logs  │
│    journalctl             │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 5. Check target status    │
│    /api/v1/targets        │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 6. Test target manually   │
│    curl /metrics          │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 7. Fix configuration      │
│    and validate           │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 8. Reload Prometheus      │
│    /-/reload              │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 9. Verify targets/metrics │
└───────────────────────────┘
```

---

# 🔐 Production Best Practices

### 1. ✅ Always Validate Before Reloading

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Never reload an unvalidated production configuration.

### 2. 🔒 Protect Configuration Files

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
sudo chmod 644 /etc/prometheus/prometheus.yml
```

Use stricter permissions when configuration contents require it.

### 3. 📜 Monitor Prometheus Logs

```bash
journalctl -u prometheus
```

Look for:

* Configuration errors.
* Storage errors.
* Scrape failures.
* Rule evaluation errors.
* Resource problems.

### 4. 🎯 Monitor Target Health

Regularly inspect:

```bash
curl http://localhost:9090/api/v1/targets
```

Targets should normally remain in an `up` state.

### 5. 💾 Monitor Disk Usage

```bash
df -h /var/lib/prometheus
```

A full TSDB filesystem can cause serious monitoring failures.

### 6. 🧠 Control Query Complexity

Avoid unnecessarily expensive PromQL queries, especially across high-cardinality metrics.

### 7. 🏷️ Control Metric Cardinality

Avoid unbounded labels such as:

```text
request_id
session_id
user_id
```

These can generate excessive time series.

### 8. 🔄 Use Configuration Reload Carefully

Validate first:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Then:

```bash
curl -X POST http://localhost:9090/-/reload
```

Finally verify:

```bash
curl http://localhost:9090/api/v1/targets
```

---

# ✅ Validation Checklist

* [ ] Prometheus installed successfully.
* [ ] `prometheus --version` works.
* [ ] `promtool --version` works.
* [ ] Node Exporter is running.
* [ ] Node Exporter metrics are accessible.
* [ ] Prometheus configuration is valid.
* [ ] Broken configuration was tested.
* [ ] Rules were validated with `promtool`.
* [ ] Prometheus systemd service is running.
* [ ] Prometheus health endpoint responds.
* [ ] Prometheus readiness endpoint responds.
* [ ] Target API is accessible.
* [ ] Broken targets were identified.
* [ ] Configuration problems were corrected.
* [ ] Prometheus configuration was successfully reloaded.
* [ ] Debug logging was tested.
* [ ] Health-check script works.
* [ ] Diagnostic script generates a report.
* [ ] Troubleshooting documentation was created.
* [ ] Common failure scenarios were tested.

---

# 🧪 Final Verification Commands

Run the following commands before completing the lab:

```bash
echo "=== Prometheus Version ==="
prometheus --version

echo "=== Promtool Version ==="
promtool --version

echo "=== Configuration Validation ==="
promtool check config /etc/prometheus/prometheus.yml

echo "=== Prometheus Service ==="
systemctl is-active prometheus

echo "=== Node Exporter Service ==="
systemctl is-active node_exporter

echo "=== Prometheus Health ==="
curl -s http://localhost:9090/-/healthy

echo
echo "=== Prometheus Ready ==="
curl -s http://localhost:9090/-/ready

echo
echo "=== Node Exporter ==="
curl -s http://localhost:9100/metrics | head

echo
echo "=== Prometheus Targets ==="
curl -s http://localhost:9090/api/v1/targets
```

---

# 🏁 Conclusion

This lab provided a practical, production-oriented approach to troubleshooting Prometheus.

You learned how to:

* 🔍 Validate Prometheus configurations using **promtool**.
* 🧩 Identify YAML and configuration problems.
* 🎯 Diagnose failed scrape targets.
* 🌐 Test metrics endpoints with `curl`.
* 📜 Investigate Prometheus logs using `journalctl`.
* 🐞 Run Prometheus with debug logging.
* 🔄 Reload configuration without a full restart.
* 🩺 Verify Prometheus health and readiness.
* 🤖 Automate troubleshooting with Bash scripts.
* 📊 Collect diagnostic information into timestamped reports.
* 📝 Build reusable troubleshooting documentation.

The most important troubleshooting principle is to work systematically:

> **Validate → Check Service → Inspect Logs → Test Connectivity → Inspect Targets → Fix → Reload → Verify**

These techniques provide a strong foundation for maintaining reliable Prometheus monitoring infrastructure in production environments.

---

## 🌟 Skills Demonstrated

```text
Prometheus Administration
        │
        ├── promtool
        ├── YAML Configuration
        ├── Target Troubleshooting
        ├── Scrape Debugging
        ├── PromQL Testing
        ├── systemd
        ├── journalctl
        ├── HTTP/API Diagnostics
        ├── Bash Automation
        └── Production Troubleshooting
```

---

## 👨‍💻 Lab Outcome

**Successfully completing this lab demonstrates practical experience in Prometheus administration, monitoring troubleshooting, Linux service management, configuration validation, log analysis, network diagnostics, and automated observability operations.**

⭐ **If this lab is part of your GitHub portfolio, consider adding screenshots of `promtool check config`, Prometheus Targets, service status, diagnostic output, and the final healthy monitoring state.**
