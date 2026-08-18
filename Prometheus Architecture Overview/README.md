# 🚀 Prometheus Architecture Overview

<p align="center">
  <img src="https://raw.githubusercontent.com/prometheus/prometheus/main/documentation/images/prometheus-logo.svg" width="180">
</p>

<h2 align="center">📊 Prometheus Monitoring & Alerting Stack</h2>

<p align="center">
  <b>Hands-On Linux Monitoring Lab</b>
</p>

<p align="center">

![Prometheus](https://img.shields.io/badge/Prometheus-2.47.0-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-1.6.1-5BB8E8?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Process Exporter](https://img.shields.io/badge/Process%20Exporter-0.7.10-333333?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-0.26.0-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?style=for-the-badge\&logo=ubuntu\&logoColor=white)
![Systemd](https://img.shields.io/badge/systemd-Service%20Management-333333?style=for-the-badge\&logo=linux\&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-Configuration-CB171E?style=for-the-badge\&logo=yaml\&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-Query%20Language-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?style=for-the-badge\&logo=gnubash\&logoColor=white)

</p>

---

## 🌟 Project Overview

This repository contains a hands-on implementation of a **complete Prometheus monitoring and alerting stack** on a Linux machine.

The lab demonstrates how the major Prometheus components work together:

```text
                    ┌───────────────────────┐
                    │       Linux Host      │
                    │                       │
                    │  ┌─────────────────┐  │
                    │  │  Node Exporter  │  │
                    │  │     :9100       │  │
                    │  └────────┬────────┘  │
                    │           │           │
                    │  ┌─────────────────┐  │
                    │  │ Process Exporter│  │
                    │  │     :9256       │  │
                    │  └────────┬────────┘  │
                    │           │           │
                    │           ▼           │
                    │  ┌─────────────────┐  │
                    │  │   Prometheus    │  │
                    │  │     :9090       │  │
                    │  └────────┬────────┘  │
                    │           │           │
                    └───────────┼───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    Alertmanager     │
                     │       :9093         │
                     └──────────┬──────────┘
                                │
                                ▼
                         🚨 Notifications
```

---

# 🎯 Lab Objectives

By completing this lab, you will learn how to:

* 🏗️ Understand Prometheus architecture
* ⚙️ Install Prometheus from scratch
* 📊 Configure Prometheus scraping
* 🖥️ Install Node Exporter
* 🔄 Install Process Exporter
* 🚨 Configure Alertmanager
* 📝 Create Prometheus alert rules
* 🧠 Write PromQL queries
* 🌐 Explore the Prometheus Web UI
* 🔗 Understand communication between Prometheus components
* 🔍 Troubleshoot monitoring services

The original lab specifically identifies these objectives, including exporters, Alertmanager, PromQL, and the Prometheus UI.

---

# 🧰 Technology Stack

| Technology              | Purpose                                       |
| ----------------------- | --------------------------------------------- |
| 📊 **Prometheus**       | Metrics collection and time-series monitoring |
| 🖥️ **Node Exporter**   | Hardware and operating-system metrics         |
| 🔄 **Process Exporter** | Running-process metrics                       |
| 🚨 **Alertmanager**     | Alert handling and routing                    |
| 🧠 **PromQL**           | Query and analyze metrics                     |
| ⚙️ **systemd**          | Service management                            |
| 📝 **YAML**             | Configuration files                           |
| 🐧 **Linux**            | Monitoring host                               |
| 💻 **Bash**             | Automation and testing                        |

---

# 🏗️ Prometheus Architecture

The monitoring stack follows this flow:

```text
                ┌─────────────────────┐
                │     Linux Host      │
                └──────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      ┌─────────────┐             ┌──────────────┐
      │Node Exporter│             │Process       │
      │   :9100     │             │Exporter      │
      └──────┬──────┘             │   :9256      │
             │                     └──────┬───────┘
             │                            │
             └────────────┬───────────────┘
                          ▼
                  ┌──────────────┐
                  │  Prometheus  │
                  │    :9090     │
                  └──────┬───────┘
                         │
                  Alert Evaluation
                         │
                         ▼
                  ┌──────────────┐
                  │ Alertmanager │
                  │    :9093     │
                  └──────┬───────┘
                         │
                         ▼
                    🚨 Alerts
```

---

# 📋 Prerequisites

Before starting this lab, you should have:

* 🐧 Basic Linux command-line knowledge
* 📝 Familiarity with `nano` or `vim`
* 🌐 Basic networking knowledge
* 🔌 Understanding of ports and HTTP
* 📄 Basic YAML knowledge
* 📊 Basic monitoring and metrics knowledge

The lab is designed around a Linux-based cloud machine with required components installed manually.

---

# 🚀 Task 1 — Set Up Prometheus Server

## 🔹 Step 1.1 — Prepare the Linux System

Update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

Install required tools:

```bash
sudo apt install wget curl tar -y
```

### ✅ Checkpoint

```text
╔══════════════════════════════════╗
║        SYSTEM PREPARATION        ║
╠══════════════════════════════════╣
║ ✔ System updated                ║
║ ✔ wget installed                ║
║ ✔ curl installed                ║
║ ✔ tar installed                 ║
╚══════════════════════════════════╝
```

---

## 🔹 Step 1.2 — Create Prometheus User

Create a dedicated service account:

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

Create required directories:

```bash
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

🔐 **Security Principle**

Prometheus runs under a dedicated non-login user instead of the root account.

---

## 🔹 Step 1.3 — Download Prometheus

Move to `/tmp`:

```bash
cd /tmp
```

Download Prometheus:

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf prometheus-2.47.0.linux-amd64.tar.gz
```

Enter the directory:

```bash
cd prometheus-2.47.0.linux-amd64
```

---

## 🔹 Step 1.4 — Install Prometheus Binaries

Copy binaries:

```bash
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
```

Set ownership:

```bash
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

Copy console files:

```bash
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus
```

Set ownership:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

---

# ⚙️ Task 1.5 — Configure Prometheus

Create the configuration file:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'process-exporter'
    static_configs:
      - targets: ['localhost:9256']
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

### 🔍 Configuration Flow

```text
prometheus.yml
      │
      ├── Scrape Prometheus
      │       └── :9090
      │
      ├── Scrape Node Exporter
      │       └── :9100
      │
      ├── Scrape Process Exporter
      │       └── :9256
      │
      └── Send alerts
              └── Alertmanager :9093
```

The uploaded lab uses a 15-second scrape/evaluation interval and configures these three scrape targets plus Alertmanager on port 9093.

---

# ⚙️ Task 1.6 — Create Prometheus systemd Service

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
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
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

Check status:

```bash
sudo systemctl status prometheus
```

Verify metrics:

```bash
curl http://localhost:9090/metrics
```

---

# 🖥️ Task 2 — Install Node Exporter

Node Exporter collects Linux hardware and operating-system metrics.

## 🔹 Step 2.1 — Download Node Exporter

```bash
cd /tmp
```

```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
```

Enter directory:

```bash
cd node_exporter-1.6.1.linux-amd64
```

Copy binary:

```bash
sudo cp node_exporter /usr/local/bin/
```

---

## 🔹 Step 2.2 — Create Node Exporter User

```bash
sudo useradd --no-create-home --shell /bin/false node_exporter
```

Set ownership:

```bash
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

---

## 🔹 Step 2.3 — Create Node Exporter Service

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
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

Start and enable:

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
curl http://localhost:9100/metrics | head -20
```

---

# 🔄 Task 2.4 — Install Process Exporter

Process Exporter monitors running processes.

Download:

```bash
cd /tmp
```

```bash
wget https://github.com/ncabatoff/process-exporter/releases/download/v0.7.10/process-exporter-0.7.10.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf process-exporter-0.7.10.linux-amd64.tar.gz
```

Enter directory:

```bash
cd process-exporter-0.7.10.linux-amd64
```

Copy binary:

```bash
sudo cp process-exporter /usr/local/bin/
```

---

## 🔹 Create Process Exporter User

```bash
sudo useradd --no-create-home --shell /bin/false process_exporter
```

Set permissions:

```bash
sudo chown process_exporter:process_exporter /usr/local/bin/process-exporter
```

---

## 🔹 Configure Process Exporter

Create configuration directory:

```bash
sudo mkdir /etc/process-exporter
```

Create configuration:

```bash
sudo nano /etc/process-exporter/config.yml
```

Add:

```yaml
process_names:
  - name: "{{.Comm}}"
    cmdline:
    - '.+'
```

Set ownership:

```bash
sudo chown -R process_exporter:process_exporter /etc/process-exporter
```

---

## 🔹 Create Process Exporter Service

```bash
sudo nano /etc/systemd/system/process_exporter.service
```

Add:

```ini
[Unit]
Description=Process Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=process_exporter
Group=process_exporter
Type=simple
ExecStart=/usr/local/bin/process-exporter --config.path /etc/process-exporter/config.yml

[Install]
WantedBy=multi-user.target
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable process_exporter
sudo systemctl start process_exporter
```

Check:

```bash
sudo systemctl status process_exporter
```

Verify:

```bash
curl http://localhost:9256/metrics | grep process
```

---

# 🚨 Task 2.5 — Install Alertmanager

Alertmanager handles alerts generated by Prometheus.

## 🔹 Download Alertmanager

```bash
cd /tmp
```

```bash
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf alertmanager-0.26.0.linux-amd64.tar.gz
```

Enter directory:

```bash
cd alertmanager-0.26.0.linux-amd64
```

---

## 🔹 Create Alertmanager User and Directories

```bash
sudo useradd --no-create-home --shell /bin/false alertmanager
```

```bash
sudo mkdir /etc/alertmanager
sudo mkdir /var/lib/alertmanager
```

Copy binaries:

```bash
sudo cp alertmanager /usr/local/bin/
sudo cp amtool /usr/local/bin/
```

Set permissions:

```bash
sudo chown alertmanager:alertmanager /usr/local/bin/alertmanager
sudo chown alertmanager:alertmanager /usr/local/bin/amtool
sudo chown alertmanager:alertmanager /etc/alertmanager
sudo chown alertmanager:alertmanager /var/lib/alertmanager
```

---

# ⚙️ Configure Alertmanager

Create:

```bash
sudo nano /etc/alertmanager/alertmanager.yml
```

Add:

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alertmanager@example.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'
```

Set ownership:

```bash
sudo chown alertmanager:alertmanager /etc/alertmanager/alertmanager.yml
```

---

# ⚙️ Create Alertmanager systemd Service

```bash
sudo nano /etc/systemd/system/alertmanager.service
```

Add:

```ini
[Unit]
Description=Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple

ExecStart=/usr/local/bin/alertmanager \
    --config.file /etc/alertmanager/alertmanager.yml \
    --storage.path /var/lib/alertmanager/ \
    --web.listen-address=0.0.0.0:9093

[Install]
WantedBy=multi-user.target
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alertmanager
sudo systemctl start alertmanager
```

Check:

```bash
sudo systemctl status alertmanager
```

---

# 🚨 Task 2.6 — Create Prometheus Alert Rules

Create:

```bash
sudo nano /etc/prometheus/alert_rules.yml
```

Add:

```yaml
groups:
- name: basic_alerts
  rules:

  - alert: InstanceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Instance {{ $labels.instance }} down"
      description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 1 minute."

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is above 80% for more than 2 minutes on {{ $labels.instance }}"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is above 85% for more than 2 minutes on {{ $labels.instance }}"
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/alert_rules.yml
```

Restart Prometheus:

```bash
sudo systemctl restart prometheus
```

The lab defines alerts for an unavailable instance, CPU usage above 80%, and memory usage above 85%.

---

# 🌐 Task 3 — Explore Prometheus UI

## 🔹 Step 3.1 — Test Prometheus

```bash
curl -I http://localhost:9090
```

Check the machine IP:

```bash
ip addr show | grep inet
```

The Prometheus interface can be accessed through:

```text
http://YOUR_IP:9090
```

---

# 🧠 Step 3.2 — PromQL Queries

## 📊 Query 1 — Check Target Status

```promql
up
```

---

## 🖥️ Query 2 — CPU Usage

```promql
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

---

## 🧮 Query 3 — Memory Usage

```promql
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

---

## 💾 Query 4 — Disk Availability

```promql
node_filesystem_avail_bytes{fstype!="tmpfs"}
```

---

## 🌐 Query 5 — Network Traffic

```promql
rate(node_network_receive_bytes_total[5m])
```

These queries are included in the original lab for checking target health and analyzing CPU, memory, disk, and network metrics.

---

# 📋 Step 3.3 — Explore Prometheus Status

Navigate through:

```text
Prometheus UI
     │
     ├── Status
     │    ├── Targets
     │    ├── Configuration
     │    ├── Rules
     │    └── Service Discovery
     │
     └── Alerts
```

### 🔹 Status → Targets

View:

* Target health
* Scrape status
* Endpoint information

### 🔹 Status → Configuration

View the active Prometheus configuration.

### 🔹 Status → Rules

View loaded alerting and recording rules.

### 🔹 Status → Service Discovery

View discovered monitoring targets.

### 🔹 Alerts

View active alerts.

---

# 🔥 Step 3.4 — Test Alert Functionality

Create a CPU stress script:

```bash
nano cpu_stress.sh
```

Add:

```bash
#!/bin/bash

echo "Starting CPU stress test..."

for i in {1..4}; do
    yes > /dev/null &
done

echo "CPU stress test started."
echo "Run 'killall yes' to stop."
```

Make executable:

```bash
chmod +x cpu_stress.sh
```

Run:

```bash
./cpu_stress.sh
```

Wait approximately 2–3 minutes and check the Prometheus **Alerts** tab.

Stop the test:

```bash
killall yes
```

⚠️ **Lab Safety Note:** Run the stress test only in the lab environment and stop it after testing.

---

# 🔗 Task 4 — Verify Component Interaction

## 🔹 Check Target Health

```bash
curl -s http://localhost:9090/api/v1/targets \
| grep -o '"health":"[^"]*"' \
| sort \
| uniq -c
```

---

## 🔹 Check Alertmanager Connectivity

```bash
curl -s http://localhost:9090/api/v1/alertmanagers
```

---

## 🔹 Verify Metrics Collection

```bash
curl -s http://localhost:9090/api/v1/query?query=up \
| grep -o '"value":\[[^]]*\]'
```

---

# 🔍 Monitoring Component Relationship

```text
┌────────────────────┐
│   Node Exporter    │
│  System Metrics    │
└─────────┬──────────┘
          │
          │
┌─────────▼──────────┐
│ Process Exporter   │
│ Process Metrics    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│    Prometheus      │
│                    │
│ Scrape             │
│ Store              │
│ Query              │
│ Evaluate Rules     │
└─────────┬──────────┘
          │
          │ Alerts
          ▼
┌────────────────────┐
│   Alertmanager     │
│                    │
│ Group              │
│ Route              │
│ Notify             │
└────────────────────┘
```

---

# 🛠️ Troubleshooting

## ❌ Issue 1 — Service Fails to Start

Check status:

```bash
sudo systemctl status prometheus
```

Check logs:

```bash
sudo journalctl -u prometheus -f
```

Check ownership and permissions.

---

## ❌ Issue 2 — Target Shows DOWN

Check the relevant service:

```bash
sudo systemctl status node_exporter
```

Check port:

```bash
sudo netstat -tlnp
```

Test metrics endpoint:

```bash
curl http://localhost:9100/metrics
```

Check firewall:

```bash
sudo ufw status
```

---

## ❌ Issue 3 — Configuration Error

Validate Prometheus configuration:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Validate alert rules:

```bash
promtool check rules /etc/prometheus/alert_rules.yml
```

Check:

* YAML indentation
* File paths
* File ownership
* Configuration syntax

---

## ❌ Issue 4 — Alerts Not Firing

Validate rules:

```bash
promtool check rules /etc/prometheus/alert_rules.yml
```

Check Prometheus logs:

```bash
sudo journalctl -u prometheus -f
```

Verify that alert conditions are actually being met.

---

## ❌ Issue 5 — High Resource Usage

Monitor Prometheus itself.

Consider:

* Adjusting scrape intervals
* Checking retention settings
* Monitoring Prometheus resource usage

---

# 🧪 Verification Commands

## 🔹 Check All Services

```bash
sudo systemctl status prometheus node_exporter process_exporter alertmanager
```

---

## 🔹 Check Monitoring Ports

```bash
sudo netstat -tlnp | grep -E ':(9090|9100|9256|9093)'
```

### 📌 Expected Ports

```text
9090  → Prometheus
9100  → Node Exporter
9256  → Process Exporter
9093  → Alertmanager
```

---

## 🔹 Test Metric Collection

```bash
curl -s http://localhost:9090/api/v1/query?query=up | jq .
```

---

## 🔹 Check Target Health

```bash
curl -s http://localhost:9090/api/v1/targets \
| jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

---

# ✅ Completion Checklist

* [ ] 🟢 Prometheus installed
* [ ] 🟢 Prometheus systemd service configured
* [ ] 🟢 Prometheus running on port `9090`
* [ ] 🟢 Node Exporter installed
* [ ] 🟢 Node Exporter running on port `9100`
* [ ] 🟢 Process Exporter installed
* [ ] 🟢 Process Exporter running on port `9256`
* [ ] 🟢 Alertmanager installed
* [ ] 🟢 Alertmanager running on port `9093`
* [ ] 🟢 Alert rules created
* [ ] 🟢 Prometheus connected to Alertmanager
* [ ] 🟢 PromQL queries tested
* [ ] 🟢 Prometheus UI explored
* [ ] 🟢 Targets showing healthy status
* [ ] 🟢 Alert functionality tested

---

# 🏆 What I Learned

### 📊 Prometheus

* Server installation
* Configuration
* Scraping
* Time-series monitoring
* Target management

### 🖥️ Exporters

* Node Exporter
* Process Exporter
* System metrics
* Process metrics

### 🚨 Alerting

* Alert rules
* Alert conditions
* Alertmanager
* Alert routing
* Alert testing

### 🧠 PromQL

* Target health
* CPU usage
* Memory usage
* Disk metrics
* Network metrics

### ⚙️ Linux Administration

* systemd
* Service users
* File permissions
* Service management
* Log troubleshooting

---

# 🎯 Final Architecture

```text
                           ┌──────────────────────┐
                           │      Linux Host      │
                           │                      │
                           │  Node Exporter :9100 │
                           │  Process Exp.  :9256 │
                           └───────────┬──────────┘
                                       │
                                       │ Metrics
                                       ▼
                              ┌─────────────────┐
                              │   Prometheus    │
                              │     :9090       │
                              └────────┬────────┘
                                       │
                            PromQL / Alert Rules
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  Alertmanager   │
                              │     :9093       │
                              └────────┬────────┘
                                       │
                                       ▼
                                  🚨 Alerts
```

---

# 🎓 Conclusion

🎉 **Congratulations!**

You have successfully built a complete Prometheus monitoring stack on a Linux machine.

The completed environment contains:

```text
┌───────────────────────────────────────────┐
│       PROMETHEUS MONITORING STACK         │
├───────────────────────────────────────────┤
│                                           │
│ 📊 Prometheus       → :9090              │
│ 🖥️ Node Exporter    → :9100              │
│ 🔄 Process Exporter → :9256              │
│ 🚨 Alertmanager     → :9093              │
│ 🧠 PromQL           → Enabled             │
│ ⚙️ systemd          → Service Management  │
│                                           │
└───────────────────────────────────────────┘
```

The lab demonstrates how the **Prometheus server**, specialized **exporters**, **Alertmanager**, and **PromQL** work together to create a complete monitoring solution.

---

# 🚀 Future Improvements

The completed architecture provides a foundation for more advanced monitoring capabilities, including:

* 📈 Grafana visualization
* 🔎 Service discovery
* 🌐 Prometheus federation
* ☸️ Kubernetes monitoring
* 🐳 Container monitoring
* ☁️ Cloud infrastructure monitoring
* 🚨 Advanced alerting
* 📊 Custom application metrics

The original lab specifically identifies service discovery, federation, and Grafana integration as natural next steps.

---

<p align="center">

## ⭐ Monitor • Analyze • Alert • Improve

### 🚀 Prometheus | Exporters | Alertmanager | PromQL

</p>

<p align="center">

<b>📊 Building Reliable Monitoring Infrastructure with Open-Source Observability</b>

</p>
