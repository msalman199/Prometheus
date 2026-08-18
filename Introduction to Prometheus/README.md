# 🚀 Introduction to Prometheus

<p align="center">
  <img src="https://raw.githubusercontent.com/prometheus/prometheus/main/documentation/images/prometheus-logo.svg" width="180">
</p>

<h3 align="center">📊 Linux Monitoring with Prometheus & Node Exporter</h3>

<p align="center">
  <b>Hands-On Monitoring Lab</b> • <b>Metrics Collection</b> • <b>PromQL</b> • <b>Linux System Monitoring</b>
</p>

<p align="center">

![Prometheus](https://img.shields.io/badge/Prometheus-2.47.0-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-1.6.1-5BB8E8?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?style=for-the-badge\&logo=ubuntu\&logoColor=white)
![Systemd](https://img.shields.io/badge/Systemd-Service%20Management-333333?style=for-the-badge\&logo=linux\&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-Configuration-CB171E?style=for-the-badge\&logo=yaml\&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-Monitoring%20Queries-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?style=for-the-badge\&logo=gnubash\&logoColor=white)

</p>

---

## 🌟 About This Lab

This repository contains a hands-on implementation of **Prometheus monitoring on Linux**.

The lab demonstrates how to install Prometheus, configure metric scraping, deploy Node Exporter, manage both services with systemd, verify metric collection, and use basic **PromQL** queries.

Prometheus collects and stores time-series metrics from configured targets and provides a web interface and query API for monitoring and analysis.

---

## 🎯 Lab Objectives

By completing this lab, you will learn how to:

* 📊 Understand the architecture of Prometheus
* ⚙️ Install Prometheus on a Linux system
* 🔧 Configure Prometheus scraping targets
* 🖥️ Install and configure Node Exporter
* 📡 Collect Linux system metrics
* 💾 Verify time-series data storage
* 🌐 Access the Prometheus web interface
* 🔎 Use the Prometheus HTTP API
* 🧠 Learn basic PromQL queries
* 🚀 Configure Prometheus and Node Exporter as systemd services
* 🔐 Apply proper service-user ownership and permissions

---

# 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │      Linux Server       │
                    │                         │
                    │   ┌─────────────────┐   │
                    │   │ Node Exporter   │   │
                    │   │   Port: 9100    │   │
                    │   └────────┬────────┘   │
                    │            │             │
                    │            │ Metrics     │
                    │            ▼             │
                    │   ┌─────────────────┐   │
                    │   │   Prometheus    │   │
                    │   │   Port: 9090    │   │
                    │   └────────┬────────┘   │
                    │            │             │
                    │            ▼             │
                    │   ┌─────────────────┐   │
                    │   │ Time-Series DB  │   │
                    │   │ /var/lib/...    │   │
                    │   └─────────────────┘   │
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │ Prometheus Web UI│
                       │     / API        │
                       └──────────────────┘
```

---

# 🧩 Prometheus Components

| Component            | Purpose                                 |
| -------------------- | --------------------------------------- |
| 📊 Prometheus Server | Scrapes and stores time-series metrics  |
| 🖥️ Node Exporter    | Exposes Linux system metrics            |
| 📚 Client Libraries  | Instrument application code             |
| 🚪 Push Gateway      | Supports short-lived jobs               |
| 📦 Exporters         | Expose metrics from third-party systems |
| 🚨 Alertmanager      | Handles alerts and notifications        |

---

# 🛠️ Prerequisites

Before starting, make sure you have:

* 🐧 Linux machine
* 💻 Basic Linux command-line knowledge
* 🌐 Basic networking knowledge
* 🔌 Understanding of ports and HTTP
* 📝 Basic YAML knowledge
* 📊 Basic understanding of monitoring and metrics

---

# 🧪 Lab Environment

This lab is designed for a Linux-based cloud machine.

The environment starts with no required monitoring tools installed, so Prometheus and Node Exporter are installed manually during the exercise.

---

# 🚀 Task 1 — Install Prometheus

## 🔹 Step 1.1 — Update System Packages

Update the Linux package repository and installed packages.

```bash
sudo apt update && sudo apt upgrade -y
```

✅ **Expected Result:** System packages are updated successfully.

---

## 🔹 Step 1.2 — Create Prometheus User

Create a dedicated service account.

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

🎯 **Why?**

Running Prometheus under a dedicated non-login user improves service isolation and security.

---

## 🔹 Step 1.3 — Create Required Directories

Create directories for configuration and time-series data.

```bash
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

✅ **Checkpoint**

```text
✔ /etc/prometheus
✔ /var/lib/prometheus
✔ prometheus user
✔ Correct ownership
```

---

## 🔹 Step 1.4 — Download Prometheus

Move to `/tmp`:

```bash
cd /tmp
```

Download Prometheus:

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz
```

Extract the archive:

```bash
tar xvf prometheus-2.47.0.linux-amd64.tar.gz
```

Enter the extracted directory:

```bash
cd prometheus-2.47.0.linux-amd64
```

---

## 🔹 Step 1.5 — Install Prometheus Binaries

Copy the Prometheus binaries:

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

## 🔹 Step 1.6 — Verify Prometheus Installation

Check the installed version:

```bash
prometheus --version
```

Expected output should contain:

```text
prometheus, version 2.47.0
```

🎉 **Prometheus installation completed!**

---

# ⚙️ Task 2 — Configure Prometheus

## 🔹 Step 2.1 — Create Prometheus Configuration

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

### 🔍 Configuration Explained

```text
scrape_interval
      │
      └── Prometheus collects metrics every 15 seconds

evaluation_interval
      │
      └── Rules are evaluated every 15 seconds

prometheus target
      │
      └── localhost:9090

node_exporter target
      │
      └── localhost:9100
```

---

## 🔹 Step 2.2 — Set Configuration Ownership

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

---

# ⚙️ Step 2.3 — Create Prometheus systemd Service

Create the service:

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

💡 **Important Configuration**

```text
Prometheus
   │
   ├── Config → /etc/prometheus/prometheus.yml
   ├── Storage → /var/lib/prometheus/
   └── Web UI → Port 9090
```

---

# 🖥️ Task 2.4 — Install Node Exporter

Node Exporter exposes Linux system metrics for Prometheus.

Move to `/tmp`:

```bash
cd /tmp
```

Download Node Exporter:

```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
```

Copy the binary:

```bash
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
```

---

## 🔹 Create Node Exporter User

```bash
sudo useradd --no-create-home --shell /bin/false node_exporter
```

Set ownership:

```bash
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

---

# ⚙️ Step 2.5 — Create Node Exporter systemd Service

Create:

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

---

# ▶️ Task 3 — Start Monitoring Services

## 🔹 Step 3.1 — Reload systemd

```bash
sudo systemctl daemon-reload
```

Start Node Exporter:

```bash
sudo systemctl start node_exporter
```

Start Prometheus:

```bash
sudo systemctl start prometheus
```

---

## 🔹 Step 3.2 — Enable Services at Boot

```bash
sudo systemctl enable node_exporter
sudo systemctl enable prometheus
```

🎯 **Result**

```text
✔ Node Exporter starts automatically
✔ Prometheus starts automatically
✔ Monitoring survives system reboot
```

---

# 🔍 Step 3.3 — Check Service Status

Check Prometheus:

```bash
sudo systemctl status prometheus
```

Check Node Exporter:

```bash
sudo systemctl status node_exporter
```

Both services should report:

```text
Active: active (running)
```

---

# 🌐 Step 3.4 — Verify Ports

Prometheus:

```bash
sudo netstat -tlnp | grep :9090
```

Node Exporter:

```bash
sudo netstat -tlnp | grep :9100
```

### 📌 Port Map

| Service       |   Port | Purpose                    |
| ------------- | -----: | -------------------------- |
| Prometheus    | `9090` | Monitoring server / Web UI |
| Node Exporter | `9100` | Linux system metrics       |

---

# 📡 Step 3.5 — Test Node Exporter Metrics

Run:

```bash
curl http://localhost:9100/metrics | head -20
```

You should see Prometheus-formatted system metrics.

🎉 **Node Exporter is successfully exposing metrics!**

---

# 🔎 Step 3.6 — Test Prometheus Targets

Run:

```bash
curl http://localhost:9090/api/v1/targets
```

The response should contain the configured targets.

Expected targets:

```text
prometheus
node_exporter
```

---

# 🌍 Step 3.7 — Access Prometheus Web Interface

Install Lynx:

```bash
sudo apt install -y lynx
```

Open Prometheus:

```bash
lynx http://localhost:9090
```

Navigate to:

```text
Status
   │
   └── Targets
```

You should see:

```text
prometheus      UP
node_exporter   UP
```

🎯 **Target Status Goal:**

```text
🟢 UP
🟢 UP
```

---

# 🧠 Step 3.8 — Query Metrics with PromQL

## 📊 Check Target Availability

```bash
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up'
```

---

## 🖥️ Check CPU Usage

```bash
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
```

---

## 🧮 Check Available Memory

```bash
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=node_memory_MemAvailable_bytes'
```

---

# 💾 Step 3.9 — Verify Prometheus Data Storage

Check the Prometheus data directory:

```bash
sudo ls -la /var/lib/prometheus/
```

Prometheus should have created files and directories used for time-series data storage.

---

# ⚙️ Step 3.10 — Verify Loaded Configuration

Run:

```bash
curl http://localhost:9090/api/v1/status/config
```

This returns the configuration currently loaded by Prometheus.

---

# 🛠️ Troubleshooting

## ❌ Prometheus Service Fails

Check logs:

```bash
sudo journalctl -u prometheus -f
```

Validate the configuration:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Check ownership:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus/
```

---

## ❌ Node Exporter Target Shows DOWN

Check service:

```bash
sudo systemctl status node_exporter
```

Check port:

```bash
netstat -tlnp | grep 9100
```

Test metrics:

```bash
curl http://localhost:9100/metrics
```

Check firewall settings if required.

---

## ❌ Permission Denied

Fix Prometheus directory ownership:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus/
```

Check storage permissions:

```bash
ls -la /var/lib/prometheus/
```

---

## ❌ Configuration Error

Validate:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Also check YAML indentation.

⚠️ **Use spaces instead of tabs in YAML files.**

---

# ✅ Lab Verification Checklist

* [ ] 🟢 Prometheus installed successfully
* [ ] 🟢 Prometheus running on port `9090`
* [ ] 🟢 Node Exporter installed successfully
* [ ] 🟢 Node Exporter running on port `9100`
* [ ] 🟢 Both services enabled at boot
* [ ] 🟢 Prometheus configuration created
* [ ] 🟢 Configuration ownership configured correctly
* [ ] 🟢 Prometheus target shows `UP`
* [ ] 🟢 Node Exporter target shows `UP`
* [ ] 🟢 PromQL queries return data
* [ ] 🟢 Prometheus API responds successfully
* [ ] 🟢 Time-series data exists under `/var/lib/prometheus/`

---

# 📊 Final Monitoring Flow

```text
                 Linux System
                      │
                      ▼
              ┌───────────────┐
              │ Node Exporter │
              │    :9100      │
              └───────┬───────┘
                      │
                 System Metrics
                      │
                      ▼
              ┌───────────────┐
              │  Prometheus   │
              │    :9090      │
              └───────┬───────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Time-Series DB          PromQL/API
          │                       │
          └───────────┬───────────┘
                      ▼
              Monitoring & Analysis
```

---

# 🎓 What I Learned

Through this lab, I gained hands-on experience with:

### 📊 Prometheus

* Prometheus installation
* Server configuration
* Metric scraping
* Time-series storage
* Prometheus API
* Target monitoring

### 🖥️ Linux Monitoring

* Node Exporter
* CPU metrics
* Memory metrics
* Service monitoring
* Network ports

### ⚙️ Linux Administration

* Dedicated service users
* File ownership
* systemd services
* Service startup
* Boot persistence
* Journal logs

### 🧠 PromQL

* `up`
* CPU utilization queries
* Memory metrics
* Metric filtering
* Basic time-series analysis

---

# 🚀 Future Improvements

After completing this foundation, the monitoring stack can be extended with:

* 📈 Grafana dashboards
* 🚨 Alerting rules
* 📣 Alertmanager
* 📦 Additional exporters
* 🧩 Custom application metrics
* ☸️ Kubernetes monitoring
* 🐳 Container monitoring
* ☁️ Cloud infrastructure monitoring
* 🔐 Production monitoring and alerting

---

# 🏆 Conclusion

🎉 **Congratulations!**

You have successfully completed the **Introduction to Prometheus** lab.

The environment now contains:

```text
┌────────────────────────────────────┐
│       Prometheus Monitoring        │
├────────────────────────────────────┤
│                                    │
│  Prometheus Server      : 9090     │
│  Node Exporter          : 9100     │
│  Prometheus Storage     : /var/lib │
│  Configuration          : /etc     │
│  PromQL                 : Enabled  │
│  systemd                : Enabled  │
│                                    │
└────────────────────────────────────┘
```

This lab provides a strong foundation for building more advanced observability solutions using **Prometheus, Grafana, Alertmanager, exporters, containers, Kubernetes, and cloud infrastructure**.

---

# 💡 Why Prometheus Matters

Monitoring is an essential part of modern infrastructure and DevOps.

Prometheus provides a reliable way to:

```text
Collect
   ↓
Store
   ↓
Query
   ↓
Analyze
   ↓
Alert
   ↓
Improve Reliability
```

These skills form the foundation for implementing production-grade monitoring and observability.

---

# 🧰 Technology Stack

<p align="center">

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)

![Node Exporter](https://img.shields.io/badge/Node%20Exporter-System%20Metrics-5BB8E8?style=for-the-badge\&logo=prometheus\&logoColor=white)

![Linux](https://img.shields.io/badge/Linux-Administration-FCC624?style=for-the-badge\&logo=linux\&logoColor=black)

![Ubuntu](https://img.shields.io/badge/Ubuntu-OS-E95420?style=for-the-badge\&logo=ubuntu\&logoColor=white)

![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?style=for-the-badge\&logo=gnubash\&logoColor=white)

![YAML](https://img.shields.io/badge/YAML-Configuration-CB171E?style=for-the-badge\&logo=yaml\&logoColor=white)

![Systemd](https://img.shields.io/badge/systemd-Service%20Management-333333?style=for-the-badge\&logo=linux\&logoColor=white)

![PromQL](https://img.shields.io/badge/PromQL-Query%20Language-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)

</p>

---

# ⭐ Skills Demonstrated

```text
📊 Monitoring
⚙️ Linux Administration
🐧 Linux Service Management
🔧 Prometheus Configuration
🖥️ System Metrics
📡 Metrics Collection
🧠 PromQL
🌐 HTTP/API Testing
🔐 Linux Permissions
🚀 Infrastructure Monitoring
```

---

<p align="center">

### 🚀 Monitor Everything. Understand Everything. Improve Everything.

**Prometheus + Node Exporter = Powerful Linux Monitoring**

</p>

<p align="center">

⭐ If this lab helped you, consider giving the repository a star!

</p>
