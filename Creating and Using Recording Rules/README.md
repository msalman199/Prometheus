# 🚀 Prometheus Recording Rules — Architecture & Performance Engineering

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange?style=for-the-badge\&logo=prometheus)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?style=for-the-badge\&logo=ubuntu)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge\&logo=amazonaws)
![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?style=for-the-badge\&logo=gnubash)
![PromQL](https://img.shields.io/badge/PromQL-Query%20Language-orange?style=for-the-badge)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-Metrics-blue?style=for-the-badge)
![Systemd](https://img.shields.io/badge/systemd-Service%20Management-1793D1?style=for-the-badge\&logo=linux)
![Monitoring](https://img.shields.io/badge/Observability-Monitoring-purple?style=for-the-badge)

> 🧠 **Architecture & Performance Engineering Lab**
>
> This hands-on lab demonstrates how Prometheus Recording Rules can move expensive PromQL computation from **query time** to **evaluation time**, creating a scalable and efficient monitoring architecture.

---

## 📌 Table of Contents

* [🎯 Objectives](#-objectives)
* [🏗️ Architecture](#️-architecture)
* [🛠️ Technology Stack](#️-technology-stack)
* [📋 Prerequisites](#-prerequisites)
* [☁️ Lab Environment](#️-lab-environment)
* [🔧 Task 1 — Install Observability Stack](#-task-1--install-and-verify-the-observability-stack)
* [📊 Task 2 — Recording Rule Hierarchy](#-task-2--design-and-deploy-a-multi-group-recording-rule-hierarchy)
* [⚡ Task 3 — Performance & Rule Health](#-task-3--measure-performance-and-validate-rule-health)
* [🧪 Verification](#-verification)
* [🚨 Troubleshooting](#-troubleshooting)
* [📈 Expected Results](#-expected-results)
* [🎓 Learning Outcomes](#-learning-outcomes)
* [🏁 Conclusion](#-conclusion)

---

# 🎯 Objectives

By completing this lab, you will learn how to:

* 🔹 Design a multi-group Prometheus recording rule hierarchy.
* 🔹 Eliminate redundant PromQL computation.
* 🔹 Build base and composite recording rule layers.
* 🔹 Use recording rules to improve query performance.
* 🔹 Measure raw PromQL versus precomputed query latency.
* 🔹 Monitor recording rule evaluation health.
* 🔹 Diagnose recording rule failures.
* 🔹 Use the Prometheus HTTP API for validation.
* 🔹 Use `promtool` for configuration and rule validation.
* 🔹 Understand dependencies between recording rule groups.
* 🔹 Apply production-oriented Prometheus performance engineering concepts.

---

# 🏗️ Architecture

The lab implements a two-layer recording-rule architecture:

```text
                     ┌─────────────────────────────┐
                     │       Node Exporter         │
                     │          :9100              │
                     └──────────────┬──────────────┘
                                    │
                                    │ Raw Metrics
                                    ▼
                     ┌─────────────────────────────┐
                     │         Prometheus          │
                     │           :9090              │
                     └──────────────┬──────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │     node_base       │
                         │      15 seconds     │
                         ├─────────────────────┤
                         │ CPU Utilization     │
                         │ Memory Utilization  │
                         │ Disk Utilization    │
                         │ Network Throughput  │
                         └──────────┬──────────┘
                                    │
                         Precomputed Metrics
                                    │
                         ┌──────────▼──────────┐
                         │   node_composite    │
                         │      30 seconds     │
                         ├─────────────────────┤
                         │ System Pressure     │
                         │ Network Mbps        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                       ┌────────────────────────┐
                       │ Dashboards / Alerts /   │
                       │ Applications / Queries  │
                       └────────────────────────┘
```

### 🔥 Core Concept

Instead of repeatedly executing:

```text
Raw Metrics
     ↓
rate()
     ↓
aggregation
     ↓
calculation
     ↓
dashboard query
```

Prometheus calculates the expression periodically:

```text
Raw Metrics
     ↓
Recording Rule
     ↓
Stored Time Series
     ↓
Fast Query
```

This shifts computational cost from **query time** to **rule evaluation time**.

---

# 🛠️ Technology Stack

| Technology             | Purpose                                |
| ---------------------- | -------------------------------------- |
| 🟠 Prometheus          | Metrics collection and recording rules |
| 🟢 Node Exporter       | Linux host metrics                     |
| 🐧 Ubuntu              | Lab operating system                   |
| ☁️ AWS EC2             | Lab infrastructure                     |
| 📜 Bash                | Automation and benchmarking            |
| 🔎 PromQL              | Metrics querying and calculations      |
| ⚙️ systemd             | Service management                     |
| 🧰 promtool            | Configuration and rule validation      |
| 🌐 Prometheus HTTP API | Metrics and rule verification          |
| 🐍 Python 3            | JSON parsing                           |
| 💾 Prometheus TSDB     | Time-series storage                    |

---

# 📋 Prerequisites

Before starting, make sure you have:

* Linux administration knowledge
* Basic systemd experience
* Understanding of Linux permissions
* Prometheus fundamentals
* PromQL knowledge
* Understanding of:

  * Time series
  * Labels
  * Cardinality
  * Scrape intervals
  * Range vectors
  * `rate()`
  * Aggregation operators

---

# ☁️ Lab Environment

The lab uses:

```text
AWS EC2
   │
   └── Ubuntu Linux
        │
        ├── Prometheus :9090
        │
        ├── Node Exporter :9100
        │
        ├── Prometheus TSDB
        │
        └── Recording Rules
```

Prometheus and Node Exporter run under a dedicated non-login account:

```text
prometheus
```

---

# 🔧 Task 1 — Install and Verify the Observability Stack

## 🔹 Step 1.1 — Create Prometheus System Account

Create a dedicated service account:

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

Create required directories:

```bash
sudo mkdir -p \
  /etc/prometheus \
  /var/lib/prometheus \
  /opt/prometheus \
  /opt/node_exporter
```

Set ownership:

```bash
sudo chown prometheus:prometheus \
  /etc/prometheus \
  /var/lib/prometheus \
  /opt/prometheus \
  /opt/node_exporter
```

### ✅ Verification

```bash
id prometheus
```

Expected:

```text
uid=... prometheus
```

---

## 🔹 Step 1.2 — Download Prometheus

Download the Prometheus release:

```bash
curl -fsSL \
https://github.com/prometheus/prometheus/releases/download/v2.52.0/prometheus-2.52.0.linux-amd64.tar.gz \
-o /tmp/prometheus.tar.gz
```

Extract:

```bash
tar -xzf /tmp/prometheus.tar.gz -C /tmp
```

Install binaries:

```bash
sudo cp /tmp/prometheus-2.52.0.linux-amd64/prometheus \
/opt/prometheus/prometheus

sudo cp /tmp/prometheus-2.52.0.linux-amd64/promtool \
/opt/prometheus/promtool
```

Copy console files:

```bash
sudo cp -r \
/tmp/prometheus-2.52.0.linux-amd64/consoles \
/opt/prometheus/

sudo cp -r \
/tmp/prometheus-2.52.0.linux-amd64/console_libraries \
/opt/prometheus/
```

Set ownership:

```bash
sudo chown -R prometheus:prometheus /opt/prometheus
```

### 🔍 Verify

```bash
/opt/prometheus/prometheus --version
```

```bash
/opt/prometheus/promtool --version
```

---

## 🔹 Step 1.3 — Install Node Exporter

Download Node Exporter:

```bash
curl -fsSL \
https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-amd64.tar.gz \
-o /tmp/node_exporter.tar.gz
```

Extract:

```bash
tar -xzf /tmp/node_exporter.tar.gz -C /tmp
```

Install:

```bash
sudo cp \
/tmp/node_exporter-1.8.1.linux-amd64/node_exporter \
/opt/node_exporter/node_exporter
```

Set ownership:

```bash
sudo chown prometheus:prometheus \
/opt/node_exporter/node_exporter
```

Verify:

```bash
/opt/node_exporter/node_exporter --version
```

---

# ⚙️ Step 1.4 — Configure Node Exporter systemd Service

Create the service:

```bash
sudo tee /etc/systemd/system/node_exporter.service <<'EOF'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/node_exporter/node_exporter

[Install]
WantedBy=multi-user.target
EOF
```

---

# ⚙️ Step 1.5 — Configure Prometheus systemd Service

Create:

```bash
sudo tee /etc/systemd/system/prometheus.service <<'EOF'
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus \
    --web.console.templates=/opt/prometheus/consoles \
    --web.console.libraries=/opt/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
EOF
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

> ⚠️ Prometheus configuration will be created in the next step.

---

# 🔹 Step 1.6 — Create Prometheus Configuration

Create:

```bash
sudo tee /etc/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/recording_rules.yml"

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: node
    static_configs:
      - targets: ["localhost:9100"]
EOF
```

Set ownership:

```bash
sudo chown prometheus:prometheus \
/etc/prometheus/prometheus.yml
```

Validate:

```bash
/opt/prometheus/promtool check config \
/etc/prometheus/prometheus.yml
```

Expected:

```text
SUCCESS: configuration file is valid
```

---

# 🚀 Step 1.7 — Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter prometheus
```

Check status:

```bash
sudo systemctl status node_exporter
```

```bash
sudo systemctl status prometheus
```

Both services should display:

```text
Active: active (running)
```

---

# 🔍 Step 1.8 — Verify Prometheus Targets

Run:

```bash
curl -fsSL \
http://localhost:9090/api/v1/targets \
| python3 -c \
"import sys,json; [print(t['labels']['job'], t['health']) for t in json.load(sys.stdin)['data']['activeTargets']]"
```

Expected:

```text
prometheus up
node up
```

You can also access:

```text
http://<EC2-IP>:9090/targets
```

Both targets must show:

```text
UP
```

---

# 📊 Task 2 — Design and Deploy a Multi-Group Recording Rule Hierarchy

## 🧠 Recording Rules

A Prometheus recording rule evaluates a PromQL expression periodically and stores the result as a new time series.

Example:

```text
node:cpu_utilization:rate5m
```

Naming convention:

```text
level:metric:operation
```

Example:

```text
node:memory_utilization:ratio
node:disk_utilization:ratio
node:network_throughput:rate5m_bytes
```

---

# 🔹 Step 2.1 — Base Metric Layer

Create:

```bash
sudo nano /etc/prometheus/recording_rules.yml
```

Use the following structure:

```yaml
groups:

  - name: node_base
    interval: 15s

    rules:

      - record: node:cpu_utilization:rate5m
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

      - record: node:memory_utilization:ratio
        expr: 1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)

      - record: node:disk_utilization:ratio
        expr: 1 - (
          node_filesystem_avail_bytes{mountpoint="/"}
          /
          node_filesystem_size_bytes{mountpoint="/"}
        )

      - record: node:network_throughput:rate5m_bytes
        expr: sum by (instance, device) (
          rate(node_network_receive_bytes_total{device!="lo"}[5m])
          +
          rate(node_network_transmit_bytes_total{device!="lo"}[5m])
        )
```

Set permissions:

```bash
sudo chown prometheus:prometheus \
/etc/prometheus/recording_rules.yml
```

---

# 🧪 Step 2.2 — Validate Recording Rules

Run:

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/recording_rules.yml
```

Expected:

```text
SUCCESS
```

---

# 🔄 Step 2.3 — Reload Prometheus

```bash
curl -fsSL \
-X POST \
http://localhost:9090/-/reload
```

Check:

```bash
sudo systemctl status prometheus
```

---

# 🔎 Step 2.4 — Verify Base Metrics

CPU:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:cpu_utilization:rate5m'
```

Memory:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:memory_utilization:ratio'
```

Disk:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:disk_utilization:ratio'
```

Network:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:network_throughput:rate5m_bytes'
```

Each query should return a non-empty:

```json
"result": [...]
```

---

# 🔹 Step 2.5 — Create Composite Layer

Append the following group to:

```text
/etc/prometheus/recording_rules.yml
```

```yaml
  - name: node_composite
    interval: 30s

    rules:

      - record: node:system_pressure:score
        expr: |
          (
            node:cpu_utilization:rate5m * 0.40
          )
          +
          (
            node:memory_utilization:ratio * 100 * 0.35
          )
          +
          (
            node:disk_utilization:ratio * 100 * 0.25
          )

      - record: node:network_throughput:rate5m_mbps
        expr: node:network_throughput:rate5m_bytes * 8 / 1000000
```

### 🧠 Dependency Model

```text
node_cpu_seconds_total
        │
        ▼
node:cpu_utilization:rate5m
        │
        │
node_memory_*
        │
        ▼
node:memory_utilization:ratio
        │
        │
node_filesystem_*
        │
        ▼
node:disk_utilization:ratio
        │
        └───────────────┐
                        ▼
             node:system_pressure:score
```

The composite layer uses **only recording-rule metrics**.

---

# 🔄 Step 2.6 — Validate and Reload

Validate:

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/recording_rules.yml
```

Reload:

```bash
curl -fsSL \
-X POST \
http://localhost:9090/-/reload
```

---

# 🔍 Step 2.7 — Verify Rule Groups

Run:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/rules' \
| python3 -c \
"import sys,json; d=json.load(sys.stdin); [print(g['name'], len(g['rules']), 'rules') for g in d['data']['groups']]"
```

Expected:

```text
node_base 4 rules
node_composite 2 rules
```

---

# 📈 Step 2.8 — Verify System Pressure

Query:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:system_pressure:score'
```

The result should contain a numeric value between:

```text
0 and 100
```

---

# ⚡ Task 3 — Measure Performance and Validate Rule Health

# 🔬 Step 3.1 — Benchmark Raw PromQL vs Recording Rules

Create the benchmark script:

```bash
sudo tee /opt/prometheus/bench.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

PROMETHEUS_URL="http://localhost:9090"

bench_query() {
    local description="$1"
    local query="$2"
    local iterations="$3"

    local total=0

    for ((i=1; i<=iterations; i++)); do
        start=$(date +%s%N)

        curl -fsS \
          --get \
          --data-urlencode "query=${query}" \
          "${PROMETHEUS_URL}/api/v1/query" \
          > /dev/null

        end=$(date +%s%N)

        elapsed=$((end - start))
        total=$((total + elapsed))
    done

    mean_ms=$(awk \
      "BEGIN {printf \"%.2f\", ($total / $iterations) / 1000000}")

    echo "${description}: ${mean_ms} ms"
}

bench_query \
"CPU Raw" \
'100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)' \
5

bench_query \
"CPU Recording Rule" \
'node:cpu_utilization:rate5m' \
5

bench_query \
"Memory Raw" \
'(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100' \
5

bench_query \
"Memory Recording Rule" \
'node:memory_utilization:ratio * 100' \
5

bench_query \
"System Pressure Raw" \
'((100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) * 0.40) + ((1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 * 0.35) + ((1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 * 0.25)' \
5

bench_query \
"System Pressure Recording Rule" \
'node:system_pressure:score' \
5
EOF
```

Make executable:

```bash
sudo chmod +x /opt/prometheus/bench.sh
```

Run:

```bash
/opt/prometheus/bench.sh \
| tee /tmp/bench_results.txt
```

---

# 📊 Expected Benchmark Structure

Example:

```text
CPU Raw: 4.20 ms
CPU Recording Rule: 2.10 ms

Memory Raw: 3.50 ms
Memory Recording Rule: 1.80 ms

System Pressure Raw: 5.40 ms
System Pressure Recording Rule: 1.90 ms
```

> ⚠️ Actual values depend on EC2 instance resources, Prometheus TSDB size, number of time series, and system load.

---

# 🩺 Step 3.2 — Recording Rule Health Monitoring

Create:

```bash
sudo tee /opt/prometheus/rule_health.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

PROMETHEUS_URL="http://localhost:9090"
FAILURES_FOUND=0

rule_health_check() {
    local metric_name="$1"

    echo
    echo "========================================"
    echo "Metric: ${metric_name}"
    echo "========================================"

    curl -fsS \
      --get \
      --data-urlencode "query=${metric_name}" \
      "${PROMETHEUS_URL}/api/v1/query" \
    | python3 -c '
import sys
import json

data = json.load(sys.stdin)

for result in data["data"]["result"]:
    metric = result["metric"]
    value = result["value"][1]

    group = (
        metric.get("rule_group")
        or metric.get("group")
        or metric.get("instance")
        or "unknown"
    )

    print(f"group={group} value={value}")
'
}

rule_health_check \
"prometheus_rule_evaluation_duration_seconds"

rule_health_check \
"prometheus_rule_evaluation_failures_total"

rule_health_check \
"prometheus_rule_group_last_duration_seconds"

FAILURE_COUNT=$(
    curl -fsS \
      --get \
      --data-urlencode \
      "query=sum(prometheus_rule_evaluation_failures_total)" \
      "${PROMETHEUS_URL}/api/v1/query" \
    | python3 -c '
import sys
import json

data = json.load(sys.stdin)
results = data["data"]["result"]

if not results:
    print("0")
else:
    print(results[0]["value"][1])
'
)

if python3 - "$FAILURE_COUNT" <<'PY'
import sys
value = float(sys.argv[1])
sys.exit(0 if value <= 0 else 1)
PY
then
    echo
    echo "✅ All rule groups healthy."
    exit 0
else
    echo "❌ RULE HEALTH DEGRADED" >&2
    exit 1
fi
EOF
```

Make executable:

```bash
sudo chmod +x /opt/prometheus/rule_health.sh
```

Run:

```bash
/opt/prometheus/rule_health.sh
```

Check exit status:

```bash
echo "Exit code: $?"
```

Healthy environment:

```text
Exit code: 0
```

If rule failures exist:

```text
Exit code: 1
```

---

# 🔎 Prometheus Internal Metrics

The health script focuses on:

### 1️⃣ Evaluation Duration

```text
prometheus_rule_evaluation_duration_seconds
```

Used to understand rule evaluation latency.

### 2️⃣ Evaluation Failures

```text
prometheus_rule_evaluation_failures_total
```

Used to detect failed rule evaluations.

### 3️⃣ Group Evaluation Duration

```text
prometheus_rule_group_last_duration_seconds
```

Used to determine how long the most recent rule-group evaluation took.

---

# 🧪 Verification

## ✅ Verify Prometheus

```bash
systemctl is-active prometheus
```

Expected:

```text
active
```

---

## ✅ Verify Node Exporter

```bash
systemctl is-active node_exporter
```

Expected:

```text
active
```

---

## ✅ Verify Configuration

```bash
/opt/prometheus/promtool check config \
/etc/prometheus/prometheus.yml
```

---

## ✅ Verify Recording Rules

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/recording_rules.yml
```

---

## ✅ Verify Targets

```bash
curl -fsSL \
http://localhost:9090/api/v1/targets
```

---

## ✅ Verify Rule Groups

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

---

## ✅ Verify CPU Recording Rule

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:cpu_utilization:rate5m'
```

---

## ✅ Verify Memory Recording Rule

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:memory_utilization:ratio'
```

---

## ✅ Verify Disk Recording Rule

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:disk_utilization:ratio'
```

---

## ✅ Verify Network Recording Rule

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:network_throughput:rate5m_bytes'
```

---

## ✅ Verify Composite Rule

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node:system_pressure:score'
```

---

# 🚨 Troubleshooting

## ❌ Prometheus Service Fails

Check:

```bash
sudo journalctl -u prometheus -n 50 --no-pager
```

Run Prometheus manually:

```bash
sudo -u prometheus \
/opt/prometheus/prometheus \
--config.file=/etc/prometheus/prometheus.yml
```

---

## ❌ `promtool check config` Fails

Run:

```bash
cat -A /etc/prometheus/prometheus.yml
```

Look for:

* Tabs
* Incorrect indentation
* Hidden characters
* Invalid YAML

YAML should use spaces rather than tabs.

---

## ❌ Prometheus Targets Are DOWN

Check Node Exporter:

```bash
sudo systemctl status node_exporter
```

Check port:

```bash
ss -lntp | grep 9100
```

Test:

```bash
curl http://localhost:9100/metrics
```

---

## ❌ Recording Rule Has No Data

First verify the source metrics:

```bash
curl -fsSL \
'http://localhost:9090/api/v1/query?query=node_cpu_seconds_total'
```

Then check recording rules:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

Look for:

```text
lastError
```

---

# 🧩 Understanding Parse-Time vs Runtime Errors

### Parse-Time Error

A parse-time error occurs when Prometheus cannot understand the configuration or PromQL syntax.

Example:

```text
promtool check rules
```

may return an error.

Fix the syntax before Prometheus can successfully load the rule.

---

### Runtime Evaluation Error

A runtime error occurs when the rule is syntactically valid but fails during evaluation.

The Rules API may show:

```text
lastError
```

Inspect:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

Runtime failures can also be investigated with:

```text
prometheus_rule_evaluation_failures_total
```

---

# 🔥 Troubleshooting: Composite Rule Has No Data

If:

```text
node:cpu_utilization:rate5m
```

has data but:

```text
node:system_pressure:score
```

does not, investigate the dependency chain.

```text
Raw Metrics
     │
     ▼
node_base
     │
     ├── CPU
     ├── Memory
     └── Disk
     │
     ▼
node_composite
     │
     ▼
System Pressure
```

Check rule groups:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

Look for:

```text
lastEvaluation
lastEvaluationDuration
lastError
```

Also inspect:

```text
prometheus_rule_group_last_duration_seconds
```

This can help determine whether a group is evaluating correctly and whether evaluation is taking longer than expected.

---

# 📈 Performance Engineering Concept

Without recording rules:

```text
Dashboard Query
      │
      ▼
PromQL Parser
      │
      ▼
Raw Time Series
      │
      ▼
rate()
      │
      ▼
Aggregation
      │
      ▼
Calculation
      │
      ▼
Result
```

With recording rules:

```text
Raw Metrics
     │
     ▼
Recording Rule
     │
     ▼
Precomputed Time Series
     │
     ▼
Dashboard Query
     │
     ▼
Fast Result
```

### 🚀 Key Advantage

Recording rules are particularly valuable when the same expensive PromQL expression is repeatedly used by:

* 📊 Grafana dashboards
* 🚨 Alerting rules
* 🔄 Dependent recording rules
* 👨‍💻 Engineers
* 🤖 Automation systems
* 📡 API consumers

---

# 📊 Expected Results

After completing the lab:

```text
Prometheus                 ✅ Running
Node Exporter              ✅ Running
Prometheus Targets         ✅ UP
Configuration              ✅ Valid
Recording Rules            ✅ Loaded
node_base                  ✅ 4 rules
node_composite             ✅ 2 rules
CPU Recording Rule         ✅ Working
Memory Recording Rule      ✅ Working
Disk Recording Rule        ✅ Working
Network Recording Rule     ✅ Working
System Pressure            ✅ Working
Benchmark                  ✅ Completed
Rule Health                ✅ Healthy
```

---

# 🎓 Learning Outcomes

After completing this lab, you should understand:

### 🧠 Prometheus Recording Rules

How Prometheus precomputes frequently used PromQL expressions.

### 🏗️ Rule Hierarchies

How one recording rule group can consume metrics generated by another group.

### ⚡ Performance Optimization

Why precomputed metrics can reduce query latency.

### 📊 PromQL Engineering

How to design efficient PromQL expressions.

### 🔍 Observability

How to monitor Prometheus itself using internal metrics.

### 🩺 Troubleshooting

How to distinguish configuration errors from runtime rule evaluation failures.

### 🛡️ Production Engineering

How recording rules can reduce repeated computational workloads in larger Prometheus deployments.

---

# 📁 Suggested Repository Structure

```text
prometheus-recording-rules/
│
├── README.md
│
├── prometheus/
│   ├── prometheus.yml
│   └── recording_rules.yml
│
├── systemd/
│   ├── prometheus.service
│   └── node_exporter.service
│
├── scripts/
│   ├── bench.sh
│   └── rule_health.sh
│
└── results/
    └── bench_results.txt
```

---

# 🏆 Production Best Practices

Use these practices when implementing recording rules in production:

* ✅ Use meaningful metric names.
* ✅ Follow the `level:metric:operation` naming convention.
* ✅ Avoid unnecessary high-cardinality labels.
* ✅ Keep rule expressions simple where possible.
* ✅ Separate base and composite rule groups.
* ✅ Validate rules with `promtool`.
* ✅ Monitor rule evaluation failures.
* ✅ Monitor evaluation duration.
* ✅ Benchmark expensive queries before and after optimization.
* ✅ Keep frequently reused expressions precomputed.
* ✅ Avoid duplicating expensive PromQL expressions across dashboards.
* ✅ Test rule dependencies before production deployment.

---

# 🏁 Conclusion

Prometheus Recording Rules are an important performance-engineering mechanism for production observability platforms.

Instead of repeatedly calculating expensive PromQL expressions during every query, Prometheus can evaluate them on a fixed schedule and store the results as time series.

The architecture implemented in this lab demonstrates:

```text
Raw Metrics
     │
     ▼
Base Recording Rules
     │
     ▼
Composite Recording Rules
     │
     ▼
Fast Queries
```

This hierarchical approach reduces repeated computation, simplifies downstream queries, and provides a scalable foundation for dashboards, alerts, and other monitoring workloads.

> 🚀 **Key takeaway:** Recording rules shift computational work from **query time → evaluation time**, making frequently used and computationally expensive PromQL expressions significantly easier to operate at scale.

---

## ⭐ Lab Completion Checklist

* [ ] Prometheus installed
* [ ] Node Exporter installed
* [ ] systemd services configured
* [ ] Prometheus configuration validated
* [ ] Node Exporter target is UP
* [ ] Prometheus target is UP
* [ ] Base recording rules created
* [ ] Composite recording rules created
* [ ] Recording rules validated with `promtool`
* [ ] Prometheus Rules API verified
* [ ] Raw queries benchmarked
* [ ] Recording-rule queries benchmarked
* [ ] Benchmark results captured
* [ ] Rule health script created
* [ ] Rule evaluation metrics checked
* [ ] Rule health confirmed
* [ ] Troubleshooting scenarios tested

---

## 👨‍💻 Author

**Hafiz Muhammad Salman**

**Cloud DevOps Engineer | Linux Administrator**

### 🔗 Professional Focus

```text
Linux Administration
Cloud Architecture
DevOps
AWS
Azure
Prometheus
Monitoring & Observability
Infrastructure Automation
Cyber Security
```

---

## 🌟 Final Lab Status

```text
╔══════════════════════════════════════════════╗
║        PROMETHEUS RECORDING RULES            ║
║                                              ║
║   Architecture      ✅ Completed             ║
║   Installation      ✅ Completed             ║
║   Recording Rules   ✅ Completed             ║
║   Performance       ✅ Tested                ║
║   Rule Health       ✅ Validated             ║
║   Troubleshooting   ✅ Covered               ║
║                                              ║
║       🚀 PRODUCTION-READY CONCEPTS 🚀        ║
╚══════════════════════════════════════════════╝
```
