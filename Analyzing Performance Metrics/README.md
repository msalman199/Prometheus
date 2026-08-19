# 📊 Analyzing Performance Metrics with Prometheus & Grafana

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Visualization-F46800?style=for-the-badge\&logo=grafana\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-System%20Administration-FCC624?style=for-the-badge\&logo=linux\&logoColor=black)
![PromQL](https://img.shields.io/badge/PromQL-Query%20Language-E6522C?style=for-the-badge)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-Metrics-6C8EBF?style=for-the-badge)

> 🚀 **Hands-on Monitoring Lab:** Build a complete Prometheus and Grafana monitoring environment, analyze CPU, memory, disk, and network performance, create dashboards, configure alerts, and identify system bottlenecks.

---

## 🎯 Lab Objectives

By completing this lab, students will learn how to:

* 🔧 Install and configure **Prometheus**
* 📡 Install and configure **Node Exporter**
* 📊 Install and configure **Grafana**
* 🔎 Write advanced **PromQL** queries
* 🖥️ Monitor CPU, memory, disk, and network performance
* 📈 Build comprehensive Grafana dashboards
* 🚨 Configure performance alerting rules
* 🧪 Generate controlled system load for testing
* 📉 Establish performance baselines
* 🔍 Identify system bottlenecks and abnormal behavior
* 🔗 Understand relationships between system performance metrics

---

## 🧰 Prerequisites

Before starting, students should have:

* Basic Linux command-line knowledge
* Understanding of CPU, memory, disk, and network monitoring
* Basic HTTP and web-browser knowledge
* Understanding of YAML configuration
* Basic networking concepts
* Familiarity with `systemctl`, `curl`, and package management

---

## 🖥️ Lab Environment

The lab is designed for an **Al Nafi Linux cloud machine**.

| Component        | Purpose                         |   Port |
| ---------------- | ------------------------------- | -----: |
| 🐧 Linux         | Monitoring host                 |      — |
| 🔥 Prometheus    | Metrics collection and querying | `9090` |
| 📡 Node Exporter | System metrics                  | `9100` |
| 📊 Grafana       | Visualization and dashboards    | `3000` |

---

# 🏗️ Task 1 — Set Up the Monitoring Environment

## 1.1 🔥 Install Prometheus

### Step 1 — Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2 — Create a Prometheus user

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

### Step 3 — Create Prometheus directories

```bash
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

### Step 4 — Download Prometheus

```bash
cd /tmp

wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

tar xvf prometheus-2.45.0.linux-amd64.tar.gz

cd prometheus-2.45.0.linux-amd64
```

### Step 5 — Install Prometheus binaries

```bash
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/

sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

### Step 6 — Copy Prometheus console files

```bash
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus

sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

### 🔍 Verify installation

```bash
prometheus --version
promtool --version
```

---

# ⚙️ 1.2 Configure Prometheus

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

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

Validate the configuration:

```bash
sudo promtool check config /etc/prometheus/prometheus.yml
```

Expected result:

```text
SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax
```

---

# 📡 1.3 Install Node Exporter

Node Exporter exposes Linux system metrics to Prometheus.

### Download Node Exporter

```bash
cd /tmp

wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz

tar xvf node_exporter-1.6.0.linux-amd64.tar.gz

cd node_exporter-1.6.0.linux-amd64
```

Copy the binary:

```bash
sudo cp node_exporter /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/node_exporter
```

Verify:

```bash
node_exporter --version
```

---

# ⚙️ 1.4 Create Systemd Services

## Prometheus Service

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
    --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
```

## Node Exporter Service

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

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Start services:

```bash
sudo systemctl start prometheus
sudo systemctl start node_exporter
```

Enable services:

```bash
sudo systemctl enable prometheus
sudo systemctl enable node_exporter
```

Check status:

```bash
sudo systemctl status prometheus
sudo systemctl status node_exporter
```

### ✅ Verify endpoints

```bash
curl http://localhost:9090/-/healthy
```

```bash
curl http://localhost:9100/metrics
```

---

# 📊 Task 2 — Install and Configure Grafana

## 2.1 Install Grafana

Install required packages:

```bash
sudo apt-get install -y software-properties-common
```

Add the Grafana repository:

```bash
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

echo "deb https://packages.grafana.com/oss/deb stable main" | \
sudo tee -a /etc/apt/sources.list.d/grafana.list
```

Update packages:

```bash
sudo apt-get update
```

Install Grafana:

```bash
sudo apt-get install grafana
```

Start Grafana:

```bash
sudo systemctl start grafana-server
```

Enable it:

```bash
sudo systemctl enable grafana-server
```

Check status:

```bash
sudo systemctl status grafana-server
```

---

# 🌐 2.2 Access Grafana

Open:

```text
http://localhost:3000
```

Default credentials:

```text
Username: admin
Password: admin
```

⚠️ **Security:** Change the default password immediately.

---

# 🔗 2.3 Add Prometheus Data Source

In Grafana:

**Configuration → Data Sources → Add data source → Prometheus**

Configure:

```text
Name: Prometheus
URL: http://localhost:9090
Access: Server
```

Click:

**Save & Test**

Expected result:

```text
Data source is working
```

---

# 🔎 Task 3 — PromQL Performance Analysis

Open:

```text
http://localhost:9090
```

Navigate to the Prometheus query interface.

---

## 🧠 3.1 Basic System Metrics

### CPU Usage

```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Memory Usage

```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### Disk Usage

```promql
100 - (
  (
    node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"}
    /
    node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"}
  ) * 100
)
```

---

# 🧮 3.2 Advanced CPU Analysis

### CPU Usage by Core

```promql
100 - (
  avg by (cpu) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
)
```

### CPU Usage by Mode

```promql
rate(node_cpu_seconds_total[5m]) * 100
```

### Load Average

```promql
node_load1
```

```promql
node_load5
```

```promql
node_load15
```

### Context Switches

```promql
rate(node_context_switches_total[5m])
```

---

# 🧠 3.3 Memory Analysis

### Memory Components

```promql
node_memory_MemTotal_bytes
```

```promql
node_memory_MemFree_bytes
```

```promql
node_memory_MemAvailable_bytes
```

```promql
node_memory_Buffers_bytes
```

```promql
node_memory_Cached_bytes
```

### Memory Percentage

```promql
(
  node_memory_MemTotal_bytes -
  node_memory_MemAvailable_bytes
)
/
node_memory_MemTotal_bytes * 100
```

### Swap Usage

```promql
(
  node_memory_SwapTotal_bytes -
  node_memory_SwapFree_bytes
)
/
node_memory_SwapTotal_bytes * 100
```

> 💡 If `SwapTotal` is zero, the swap percentage query can result in an invalid division. Check swap availability before interpreting this metric.

---

# 🌐 3.4 Network Analysis

### Receive Traffic

```promql
rate(node_network_receive_bytes_total{device!="lo"}[5m])
```

### Transmit Traffic

```promql
rate(node_network_transmit_bytes_total{device!="lo"}[5m])
```

### Receive Packets

```promql
rate(node_network_receive_packets_total{device!="lo"}[5m])
```

### Transmit Packets

```promql
rate(node_network_transmit_packets_total{device!="lo"}[5m])
```

### Receive Errors

```promql
rate(node_network_receive_errs_total{device!="lo"}[5m])
```

### Transmit Errors

```promql
rate(node_network_transmit_errs_total{device!="lo"}[5m])
```

### Dropped Packets

```promql
rate(node_network_receive_drop_total{device!="lo"}[5m])
```

```promql
rate(node_network_transmit_drop_total{device!="lo"}[5m])
```

---

# 📈 Task 4 — Create Grafana Dashboards

## 🖥️ 4.1 System Overview Dashboard

Create:

**Dashboard → Add new panel**

### Panel 1 — CPU Usage

```promql
100 - (
  avg by (instance) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
)
```

Configure:

```text
Title: CPU Usage (%)
Unit: Percent (0-100)
Minimum: 0
Maximum: 100
```

### Panel 2 — Memory Usage

```promql
(
  1 -
  (
    node_memory_MemAvailable_bytes /
    node_memory_MemTotal_bytes
  )
) * 100
```

Configure:

```text
Title: Memory Usage (%)
Unit: Percent (0-100)
```

### Panel 3 — Disk Usage

```promql
100 - (
  (
    node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"}
    /
    node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"}
  ) * 100
)
```

Configure:

```text
Title: Disk Usage (%)
Unit: Percent (0-100)
```

---

# 🧮 4.2 CPU Dashboard

Create a dedicated CPU dashboard.

Recommended panels:

| Panel            | Metric                  |
| ---------------- | ----------------------- |
| CPU by Core      | Per-core utilization    |
| CPU by Mode      | User/system/iowait/etc. |
| Load 1m          | Short-term load         |
| Load 5m          | Medium-term load        |
| Load 15m         | Long-term load          |
| Context Switches | Scheduler activity      |

### CPU by Core

```promql
100 - (
  avg by (cpu) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
)
```

### CPU Modes

```promql
rate(node_cpu_seconds_total[5m]) * 100
```

### System Load

```promql
node_load1
```

```promql
node_load5
```

```promql
node_load15
```

### Context Switches

```promql
rate(node_context_switches_total[5m])
```

---

# 🌐 4.3 Network Dashboard

Create a network-focused dashboard.

### Network Bytes/sec

```promql
rate(node_network_receive_bytes_total{device!="lo"}[5m])
```

```promql
rate(node_network_transmit_bytes_total{device!="lo"}[5m])
```

### Packets/sec

```promql
rate(node_network_receive_packets_total{device!="lo"}[5m])
```

```promql
rate(node_network_transmit_packets_total{device!="lo"}[5m])
```

### Network Errors

```promql
rate(node_network_receive_errs_total{device!="lo"}[5m])
```

```promql
rate(node_network_transmit_errs_total{device!="lo"}[5m])
```

---

# 🧪 4.4 Generate System Load

To observe meaningful metric changes, generate controlled workload.

## CPU Load

Install `stress-ng` if necessary:

```bash
sudo apt install stress-ng
```

Generate CPU load:

```bash
stress-ng --cpu 2 --timeout 300s
```

## Memory Load

```bash
stress-ng --vm 1 --vm-bytes 512M --timeout 300s
```

## Disk I/O

```bash
dd if=/dev/zero of=/tmp/testfile bs=1M count=1000
```

## Network Activity

Use a suitable large test file:

```bash
wget -O /tmp/testfile.iso https://releases.ubuntu.com/20.04/ubuntu-20.04.6-desktop-amd64.iso
```

⚠️ **Note:** Large downloads consume bandwidth and disk space. Remove test files afterward:

```bash
rm -f /tmp/testfile /tmp/testfile.iso
```

---

# 🚨 Task 5 — Advanced Query Analysis

## 5.1 Configure Alerting Rules

Create:

```bash
sudo nano /etc/prometheus/alert_rules.yml
```

Add:

```yaml
groups:
  - name: system_alerts
    rules:

      - alert: HighCPUUsage
        expr: |
          100 - (
            avg by (instance) (
              rate(node_cpu_seconds_total{mode="idle"}[5m])
            ) * 100
          ) > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 2 minutes"

      - alert: HighMemoryUsage
        expr: |
          (
            1 -
            (
              node_memory_MemAvailable_bytes /
              node_memory_MemTotal_bytes
            )
          ) * 100 > 85
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 2 minutes"

      - alert: DiskSpaceLow
        expr: |
          100 - (
            (
              node_filesystem_avail_bytes{
                mountpoint="/",
                fstype!="rootfs"
              }
              /
              node_filesystem_size_bytes{
                mountpoint="/",
                fstype!="rootfs"
              }
            ) * 100
          ) > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space is running low"
          description: "Disk usage is above 90% for more than 5 minutes"
```

Update Prometheus:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Configure:

```yaml
rule_files:
  - "alert_rules.yml"
```

Validate:

```bash
sudo promtool check rules /etc/prometheus/alert_rules.yml
```

Restart:

```bash
sudo systemctl restart prometheus
```

Verify:

```bash
sudo systemctl status prometheus
```

---

# 🧠 5.2 Multi-Metric Analysis

## System Health Score

A weighted score can combine CPU, memory, and disk observations:

```promql
(
  (
    100 -
    (
      100 -
      (
        avg by (instance) (
          rate(node_cpu_seconds_total{mode="idle"}[5m])
        ) * 100
      )
    )
  ) * 0.4
  +
  (
    (
      1 -
      (
        node_memory_MemAvailable_bytes /
        node_memory_MemTotal_bytes
      )
    ) * 100
  ) * 0.4
  +
  (
    100 -
    (
      (
        node_filesystem_avail_bytes{
          mountpoint="/",
          fstype!="rootfs"
        }
        /
        node_filesystem_size_bytes{
          mountpoint="/",
          fstype!="rootfs"
        }
      ) * 100
    )
  ) * 0.2
)
```

> 💡 This is a custom analytical score rather than a universal health standard. Define the scoring model according to your own SLOs and operational requirements.

## Network Utilization

```promql
(
  rate(node_network_receive_bytes_total{device!="lo"}[5m])
  +
  rate(node_network_transmit_bytes_total{device!="lo"}[5m])
) / 1024 / 1024
```

## I/O Wait

```promql
avg by (instance) (
  rate(node_cpu_seconds_total{mode="iowait"}[5m])
) * 100
```

---

# 🎛️ Task 6 — Dashboard Optimization

## 6.1 Create Dashboard Variables

Go to:

**Dashboard Settings → Variables → Add Variable**

Configure:

```text
Name: instance
Type: Query
Query: label_values(up, instance)
```

Then use:

```promql
100 - (
  avg by (instance) (
    rate(
      node_cpu_seconds_total{
        instance="$instance",
        mode="idle"
      }[5m]
    )
  ) * 100
)
```

This allows one dashboard to monitor multiple instances.

---

# ⏱️ 6.2 Configure Time Range

Recommended settings:

```text
Auto Refresh:
5s
10s
30s
1m
5m
15m
30m
1h
2h
1d

Default Time Range:
Last 5 minutes
```

Keep the time picker visible so operators can investigate historical behavior.

---

# 📊 6.3 Performance Baseline Analysis

## Average CPU — 24 Hours

```promql
avg_over_time(
  (
    100 -
    (
      avg by (instance) (
        rate(node_cpu_seconds_total{mode="idle"}[5m])
      ) * 100
    )
  )[24h:5m]
)
```

## Peak Memory — 24 Hours

```promql
max_over_time(
  (
    (
      1 -
      (
        node_memory_MemAvailable_bytes /
        node_memory_MemTotal_bytes
      )
    ) * 100
  )[24h:5m]
)
```

## Network Traffic Trend

```promql
avg_over_time(
  (
    rate(node_network_receive_bytes_total{device!="lo"}[5m])
    +
    rate(node_network_transmit_bytes_total{device!="lo"}[5m])
  )[24h:5m]
)
```

---

# 🛠️ Troubleshooting

## ❌ Issue 1 — Prometheus Does Not Start

Check configuration:

```bash
sudo promtool check config /etc/prometheus/prometheus.yml
```

Check logs:

```bash
sudo journalctl -u prometheus -f
```

Fix permissions:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus
```

Check service:

```bash
sudo systemctl status prometheus
```

---

## ❌ Issue 2 — Grafana Shows No Data

Check Prometheus:

```bash
curl http://localhost:9090/api/v1/query?query=up
```

Check Node Exporter:

```bash
curl http://localhost:9100/metrics
```

Check Prometheus targets:

```text
http://localhost:9090/targets
```

Verify Grafana data source:

```text
Grafana → Data Sources → Prometheus → Save & Test
```

---

## ❌ Issue 3 — High Resource Consumption

Review the scrape interval:

```yaml
global:
  scrape_interval: 15s
```

For larger environments, tune retention and storage according to the monitoring workload.

Example Prometheus flags:

```text
--storage.tsdb.retention.time=7d
--storage.tsdb.retention.size=1GB
```

> ⚠️ Retention settings are independent limits. Test storage behavior before applying aggressive limits in production.

---

# 🔍 Performance Analysis Guide

## 🖥️ CPU

| Range  | Interpretation                 |
| ------ | ------------------------------ |
| 0–70%  | 🟢 Generally healthy           |
| 70–85% | 🟡 Investigate sustained usage |
| >85%   | 🔴 Potential CPU pressure      |

### Important indicators

* High **iowait** → possible storage bottleneck
* High **system** time → increased kernel activity
* High **user** time → application workload
* High load with low CPU utilization → investigate I/O or other contention

---

# 🧠 Memory

Important metrics:

* `MemAvailable`
* `MemFree`
* `Buffers`
* `Cached`
* Swap utilization

### Indicators

* Consistent swap usage → possible memory pressure
* Rapid memory growth → possible memory leak
* Low available memory → increased performance risk
* High cache usage → not necessarily a problem because Linux uses memory for filesystem caching

---

# 🌐 Network

Monitor:

* Receive throughput
* Transmit throughput
* Packets/sec
* Receive errors
* Transmit errors
* Dropped packets

### Indicators

| Metric               | Possible Meaning                    |
| -------------------- | ----------------------------------- |
| Traffic spike        | Increased workload                  |
| High errors          | Interface/hardware/network issue    |
| High drops           | Congestion or resource pressure     |
| Asymmetric traffic   | Different inbound/outbound workload |
| Sustained saturation | Capacity concern                    |

---

# 🔗 Understanding Metric Relationships

Performance analysis becomes more useful when metrics are correlated.

### Example 1 — CPU + I/O Wait

```text
High CPU
   +
High iowait
   ↓
Investigate storage I/O
```

### Example 2 — Memory + Swap

```text
Low Available Memory
        +
Increasing Swap Usage
        ↓
Possible Memory Pressure
```

### Example 3 — Network + CPU

```text
High Network Traffic
        +
High CPU
        ↓
Investigate network processing/application workload
```

### Example 4 — Load + CPU

```text
High Load
   +
Low CPU
   ↓
Investigate I/O wait, blocked processes,
or other resource contention
```

---

# 🧪 Validation Checklist

* [ ] Prometheus installed
* [ ] Prometheus service running
* [ ] Node Exporter installed
* [ ] Node Exporter service running
* [ ] Prometheus configuration validated
* [ ] Prometheus target is `UP`
* [ ] Grafana installed
* [ ] Grafana service running
* [ ] Prometheus added as Grafana data source
* [ ] CPU dashboard created
* [ ] Memory dashboard created
* [ ] Disk dashboard created
* [ ] Network dashboard created
* [ ] PromQL queries tested
* [ ] Alert rules configured
* [ ] Dashboard variables configured
* [ ] Time-range controls configured
* [ ] System load generated
* [ ] Performance trends analyzed
* [ ] Bottlenecks identified

---

# 📁 Suggested Repository Structure

```text
analyzing-performance-metrics/
│
├── README.md
│
├── prometheus/
│   ├── prometheus.yml
│   └── alert_rules.yml
│
├── grafana/
│   └── dashboards/
│       ├── system-overview.json
│       ├── cpu-analysis.json
│       └── network-monitoring.json
│
├── scripts/
│   ├── generate-cpu-load.sh
│   ├── generate-memory-load.sh
│   └── cleanup.sh
│
└── screenshots/
    ├── prometheus-targets.png
    ├── grafana-overview.png
    ├── cpu-dashboard.png
    └── network-dashboard.png
```

---

# 🎓 Learning Outcomes

After completing this lab, students should be able to:

### 🔥 Prometheus

* Install Prometheus
* Configure scrape targets
* Validate Prometheus configuration
* Query time-series metrics
* Configure recording/alerting rules

### 📡 Node Exporter

* Export Linux system metrics
* Monitor CPU, memory, disk, and network
* Verify exporter endpoints

### 📊 Grafana

* Connect Grafana to Prometheus
* Build monitoring dashboards
* Configure dashboard variables
* Configure automatic refresh
* Visualize historical performance

### 🔎 PromQL

* Calculate CPU utilization
* Analyze memory consumption
* Monitor network traffic
* Calculate rates
* Analyze load averages
* Build multi-metric queries

### 🚨 Monitoring & Operations

* Establish performance baselines
* Detect abnormal behavior
* Configure alerts
* Correlate multiple metrics
* Identify infrastructure bottlenecks

---

# 🏁 Conclusion

This lab demonstrates how **Prometheus + Node Exporter + Grafana** can form a practical Linux performance-monitoring stack.

You installed and configured the monitoring components, collected system metrics, wrote PromQL queries, built Grafana dashboards, generated controlled workloads, configured alerting rules, and analyzed performance trends.

The most important lesson is that effective monitoring is not simply about collecting metrics. Engineers must **correlate metrics, establish baselines, recognize abnormal behavior, and investigate the underlying cause**.

The skills developed in this lab are directly applicable to:

* ☁️ Cloud Infrastructure
* 🔧 DevOps Engineering
* 🐧 Linux Administration
* 🚀 Site Reliability Engineering
* 📊 Observability Engineering
* 🛡️ Production Operations

---

## 💡 Key Takeaways

> 🔥 **Prometheus** collects and stores time-series metrics.

> 📡 **Node Exporter** exposes Linux system metrics.

> 📊 **Grafana** transforms metrics into actionable visualizations.

> 🔎 **PromQL** enables powerful performance analysis.

> 🚨 **Alerting** enables proactive detection of problems.

> 📈 **Baselines** help distinguish normal behavior from abnormal behavior.

> 🔗 **Metric correlation** helps engineers identify the actual source of performance problems.

> 🚀 Together, these technologies provide a strong foundation for **modern infrastructure monitoring and observability**.

---

## 🏆 Lab Complete

**Prometheus + Node Exporter + Grafana = Powerful Linux Performance Observability**

Keep monitoring. Keep analyzing. Keep improving. 🚀
