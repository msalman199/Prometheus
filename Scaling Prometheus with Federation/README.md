# 🚀 Scaling Prometheus with Federation

> **Production-style Prometheus Federation Lab**
> Build a two-tier monitoring architecture with independent cluster-level Prometheus instances and a global federation instance.

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus\&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-Metrics-FF6F00?logo=prometheus\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?logo=ubuntu\&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws\&logoColor=white)
![Python](https://img.shields.io/badge/Python-Exporter-3776AB?logo=python\&logoColor=white)
![systemd](https://img.shields.io/badge/systemd-Service%20Management-1E1E1E?logo=linux\&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-Querying-E6522C?logo=prometheus\&logoColor=white)

---

## 📌 Overview

This hands-on lab demonstrates how to build and operate a **hierarchical Prometheus federation topology**.

The architecture contains:

```text
                    ┌───────────────────────────┐
                    │     Global Prometheus      │
                    │       Federation          │
                    │        Port: 9092         │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
             /federate                     /federate
                    │                           │
        ┌───────────▼──────────┐    ┌──────────▼───────────┐
        │   Cluster A          │    │   Cluster B          │
        │   Prometheus         │    │   Prometheus         │
        │   Port: 9090         │    │   Port: 9091         │
        └───────────┬──────────┘    └──────────┬───────────┘
                    │                           │
             ┌──────▼──────┐             ┌──────▼──────┐
             │ Node Export │             │ Node Export │
             │ Port 9100   │             │ Port 9101   │
             └─────────────┘             └─────────────┘
```

The global Prometheus selectively collects metrics from the two cluster-level Prometheus servers instead of scraping application targets directly.

---

# 🎯 Objectives

By completing this lab, you will learn how to:

* 🏗️ Design a hierarchical Prometheus federation topology
* 🌐 Federate metrics from multiple Prometheus instances
* 🏷️ Preserve cluster and region labels using `external_labels`
* 🔄 Use `honor_labels: true` across federation boundaries
* 📊 Create cross-cluster PromQL recording rules
* 🚨 Configure federation health alerts
* 🐍 Build a Python-based synthetic metrics exporter
* 📈 Validate cross-cluster application metrics
* 🔢 Control Prometheus time-series cardinality
* 🔍 Troubleshoot federation, labels, scrape lag, and metric selection

---

# 🧰 Prerequisites

Before starting, make sure you have:

* 🐧 Linux administration knowledge
* ⚙️ Basic systemd experience
* 📝 YAML knowledge
* 🌐 Familiarity with HTTP APIs and `curl`
* 📊 Basic PromQL knowledge
* ☁️ Access to an AWS EC2 Ubuntu instance

The original lab specifies an AWS EC2 Ubuntu instance provided by Al Nafi.

---

# 🏗️ Lab Environment

All components run on a single Ubuntu EC2 host using different ports.

| Component                       |   Port |
| ------------------------------- | -----: |
| 🟢 Prometheus Cluster A         | `9090` |
| 🔵 Prometheus Cluster B         | `9091` |
| 🌍 Global Federation Prometheus | `9092` |
| 📊 Node Exporter A              | `9100` |
| 📊 Node Exporter B              | `9101` |
| 🟠 Application Exporter A       | `8080` |
| 🟣 Application Exporter B       | `8081` |

The federation design uses three independent Prometheus processes and two Node Exporter processes on the same host.

---

# 🧱 Technology Stack

| Technology                   | Purpose                                |
| ---------------------------- | -------------------------------------- |
| 🔥 **Prometheus**            | Metrics collection and monitoring      |
| 📊 **Node Exporter**         | Linux system metrics                   |
| 🔄 **Prometheus Federation** | Cross-instance metric aggregation      |
| 🧠 **PromQL**                | Metric querying and aggregation        |
| 🚨 **Alerting Rules**        | Federation health monitoring           |
| 📋 **Recording Rules**       | Pre-computed monitoring metrics        |
| 🐍 **Python**                | Synthetic application metrics exporter |
| ⚙️ **systemd**               | Service lifecycle management           |
| 🐧 **Ubuntu Linux**          | Lab operating system                   |
| ☁️ **AWS EC2**               | Lab infrastructure                     |
| 🐚 **Bash**                  | Automation and validation              |
| 🌐 **HTTP API**              | Prometheus API and federation          |

---

# 📁 Directory Structure

The lab creates the following structure:

```text
/usr/local/bin/
├── prometheus
├── promtool
└── node_exporter

/etc/prometheus/
├── cluster-a/
│   └── prometheus.yml
├── cluster-b/
│   └── prometheus.yml
└── federation/
    ├── prometheus.yml
    └── rules.yml

/var/lib/prometheus/
├── cluster-a/
├── cluster-b/
└── federation/
```

All Prometheus configuration and data directories should be owned by the `prometheus` user.

---

# 🚀 Task 1 — Provision the Monitoring Stack

## 🔹 Step 1.1 — Install Prometheus and Node Exporter

Create the dedicated monitoring user:

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

Create the required directories:

```bash
for d in /etc/prometheus/cluster-a /etc/prometheus/cluster-b /etc/prometheus/federation \
         /var/lib/prometheus/cluster-a /var/lib/prometheus/cluster-b /var/lib/prometheus/federation; do
    sudo mkdir -p "$d"
done
```

Set the versions:

```bash
PROM_VERSION="2.52.0"
NE_VERSION="1.8.1"
ARCH="linux-amd64"
```

Download Prometheus:

```bash
cd /tmp

wget -fsSL \
"https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.${ARCH}.tar.gz" \
-O prometheus.tar.gz

tar xf prometheus.tar.gz
```

Install Prometheus and `promtool`:

```bash
sudo cp "prometheus-${PROM_VERSION}.${ARCH}/prometheus" /usr/local/bin/
sudo cp "prometheus-${PROM_VERSION}.${ARCH}/promtool" /usr/local/bin/

sudo cp -r "prometheus-${PROM_VERSION}.${ARCH}/consoles" /etc/prometheus/
sudo cp -r "prometheus-${PROM_VERSION}.${ARCH}/console_libraries" /etc/prometheus/
```

Download Node Exporter:

```bash
wget -fsSL \
"https://github.com/prometheus/node_exporter/releases/download/v${NE_VERSION}/node_exporter-${NE_VERSION}.${ARCH}.tar.gz" \
-O node_exporter.tar.gz

tar xf node_exporter.tar.gz
```

Install it:

```bash
sudo cp \
"node_exporter-${NE_VERSION}.${ARCH}/node_exporter" \
/usr/local/bin/
```

Set ownership:

```bash
sudo chown prometheus:prometheus \
/usr/local/bin/prometheus \
/usr/local/bin/promtool \
/usr/local/bin/node_exporter

sudo chown -R prometheus:prometheus \
/etc/prometheus \
/var/lib/prometheus
```

### ✅ Verification

```bash
prometheus --version
promtool --version
node_exporter --version
```

### ⚠️ Troubleshooting

If GitHub cannot be reached:

```bash
curl -fsSL https://github.com
```

Check:

* 🌐 Internet connectivity
* 🔎 DNS resolution
* ☁️ EC2 outbound security-group rules

The source lab specifically identifies DNS/outbound connectivity as a common installation issue.

---

# 🔹 Step 1.2 — Configure Prometheus Instances

## 🟢 Cluster A

Create:

```bash
sudo tee /etc/prometheus/cluster-a/prometheus.yml > /dev/null
```

Configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "cluster-a"
    region: "us-east-1"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node"
    static_configs:
      - targets: ["localhost:9100"]
```

---

## 🔵 Cluster B

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "cluster-b"
    region: "us-west-2"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9091"]

  - job_name: "node"
    static_configs:
      - targets: ["localhost:9101"]
```

---

## 🌍 Global Federation

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

  external_labels:
    monitor: "global-federation"

rule_files:
  - "rules.yml"

scrape_configs:

  - job_name: "federate-cluster-a"
    honor_labels: true
    metrics_path: "/federate"

    params:
      "match[]":
        - '{__name__=~"up|node_cpu_seconds_total|node_memory_MemAvailable_bytes|node_filesystem_avail_bytes|prometheus_tsdb_head_series"}'

    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "federate-cluster-b"
    honor_labels: true
    metrics_path: "/federate"

    params:
      "match[]":
        - '{__name__=~"up|node_cpu_seconds_total|node_memory_MemAvailable_bytes|node_filesystem_avail_bytes|prometheus_tsdb_head_series"}'

    static_configs:
      - targets: ["localhost:9091"]
```

The federation configuration deliberately uses narrow `match[]` selectors to limit the amount of data transferred into the global Prometheus instance.

---

# 🔍 Validate Configuration

Run:

```bash
promtool check config \
/etc/prometheus/cluster-a/prometheus.yml

promtool check config \
/etc/prometheus/cluster-b/prometheus.yml

promtool check config \
/etc/prometheus/federation/prometheus.yml
```

Expected:

```text
SUCCESS
```

### 💡 Why `promtool`?

`promtool` catches configuration and YAML errors **before** they cause a Prometheus service failure.

---

# ⚙️ Configure systemd Services

The lab creates five services:

```text
node-exporter-a.service
node-exporter-b.service

prometheus-a.service
prometheus-b.service

prometheus-federation.service
```

Example Node Exporter service:

```ini
[Unit]
Description=Node Exporter - Cluster A
After=network-online.target
Wants=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
Restart=on-failure
ExecStart=/usr/local/bin/node_exporter --web.listen-address=:9100

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable and start all services:

```bash
for svc in node-exporter-a node-exporter-b prometheus-a prometheus-b prometheus-federation; do
    sudo systemctl enable --now "$svc"
done
```

---

# 🩺 Verify Services

```bash
systemctl status \
node-exporter-a \
node-exporter-b \
prometheus-a \
prometheus-b \
prometheus-federation
```

Check listening ports:

```bash
ss -tlnp
```

Expected ports:

```text
9090
9091
9092
9100
9101
```

The lab expects all five services to report `active (running)` and all five monitoring ports to be listening.

---

# 🔄 Task 2 — Implement Federation

## 🔹 Step 2.1 — Test `/federate`

Cluster A:

```bash
curl -fsSL \
"http://localhost:9090/federate?match%5B%5D=%7B__name__%3D~%22up%22%7D" \
| grep -E "^up"
```

Expected labels:

```text
cluster="cluster-a"
region="us-east-1"
```

Cluster B:

```bash
curl -fsSL \
"http://localhost:9091/federate?match%5B%5D=%7B__name__%3D~%22up%22%7D" \
| grep -E "^up"
```

Expected:

```text
cluster="cluster-b"
region="us-west-2"
```

---

# 🌍 Validate Global Prometheus

Query:

```bash
curl -fsSL \
"http://localhost:9092/api/v1/query?query=up"
```

Or use the provided Python validation:

```bash
curl -fsSL \
"http://localhost:9092/api/v1/query?query=up" \
| python3 -c "
import sys, json

payload = json.load(sys.stdin)

for r in payload['data']['result']:
    print(
        r['metric'].get('cluster','MISSING'),
        r['metric'].get('instance'),
        r['value'][1]
    )
"
```

### ✅ Expected

You should see both:

```text
cluster-a
cluster-b
```

with healthy targets reporting:

```text
1
```

This validates that `honor_labels: true` preserves the original cluster labels.

---

# 📊 Step 2.2 — Create Recording Rules

Create:

```bash
sudo tee /etc/prometheus/federation/rules.yml > /dev/null
```

Use:

```yaml
groups:

  - name: cluster_aggregates
    interval: 30s

    rules:

      - record: "cluster:node_cpu_utilisation:avg1m"
        expr: |
          1 - avg by (cluster) (
            rate(node_cpu_seconds_total{mode="idle"}[1m])
          )

      - record: "cluster:node_memory_available_bytes:avg"
        expr: |
          avg by (cluster) (
            node_memory_MemAvailable_bytes
          )

      - record: "global:node_cpu_utilisation:avg1m"
        expr: |
          avg(cluster:node_cpu_utilisation:avg1m)

  - name: federation_health

    rules:

      - alert: FederationTargetDown
        expr: up{job=~"federate-.*"} == 0
        for: 2m

        labels:
          severity: "critical"

        annotations:
          summary: "Federation target {{ $labels.instance }} is unreachable"
          description: "Job {{ $labels.job }} has been unable to scrape {{ $labels.instance }} for more than 2 minutes."
```

The lab requires three recording rules and one `FederationTargetDown` alert.

---

# 🔎 Validate Rules

```bash
promtool check rules \
/etc/prometheus/federation/rules.yml
```

Expected:

```text
SUCCESS
```

Reload Prometheus without restarting:

```bash
curl -fsSL \
-X POST \
http://localhost:9092/-/reload
```

Wait for rule evaluation:

```bash
sleep 35
```

Check loaded rules:

```bash
curl -fsSL \
"http://localhost:9092/api/v1/rules" \
| python3 -c "
import sys, json

payload = json.load(sys.stdin)

for g in payload['data']['groups']:
    print('Group:', g['name'])

    for r in g['rules']:
        print(
            '  ',
            r['type'],
            r.get('name') or r.get('alert')
        )
"
```

### ✅ Expected

```text
cluster_aggregates
federation_health

cluster:node_cpu_utilisation:avg1m
cluster:node_memory_available_bytes:avg
global:node_cpu_utilisation:avg1m
FederationTargetDown
```

---

# 🐍 Task 3 — Synthetic Application Metrics

The lab introduces a Python exporter to simulate application traffic across two clusters.

Two exporter instances are required:

```text
Cluster A → :8080
Cluster B → :8081
```

The exporter exposes:

```text
app_http_requests_total
app_request_duration_seconds
app_active_sessions
```

The required metrics and histogram buckets are defined by the lab specification.

---

# 📈 Application Metrics

## HTTP Request Counter

```text
app_http_requests_total
```

Labels:

```text
method
status_code
endpoint
```

---

## Request Duration Histogram

```text
app_request_duration_seconds
```

Buckets:

```text
0.05
0.1
0.25
0.5
1.0
2.5
```

Label:

```text
endpoint
```

---

## Active Sessions Gauge

```text
app_active_sessions
```

The simulated session count should fluctuate within:

```text
50 – 500
```

---

# 🧪 Exporter Interface

The exporter should implement:

```python
class TrafficSimulator:

    def __init__(self, seed_rng: int) -> None:
        ...

    def tick(self) -> None:
        ...

    def get_registry(self):
        ...
```

The WSGI application should:

```text
/metrics → return Prometheus metrics
other paths → HTTP 404
```

It should call `tick()` on every metrics request.

---

# 🔌 Configure Application Scraping

Cluster A:

```yaml
- job_name: "app"
  static_configs:
    - targets: ["localhost:8080"]
```

Cluster B:

```yaml
- job_name: "app"
  static_configs:
    - targets: ["localhost:8081"]
```

Extend federation selectors with:

```text
app_http_requests_total
app_request_duration_seconds
```

Reload Prometheus instances after changing the configuration.

---

# 🧪 Validate Application Metrics

Cluster A:

```bash
curl -fsSL \
http://localhost:8080/metrics \
| grep app_http_requests_total
```

Cluster B:

```bash
curl -fsSL \
http://localhost:8081/metrics \
| grep app_http_requests_total
```

### ✅ Expected

Both exporters should return non-zero request counters.

---

# 📊 Task 3.2 — Validate Cross-Cluster Aggregation

## ✅ Condition 1 — Request Rate

Run:

```bash
curl -fsSL \
"http://localhost:9092/api/v1/query?query=sum+by+(cluster)+(rate(app_http_requests_total%5B2m%5D))"
```

Expected:

```text
cluster-a
cluster-b
```

Both should have non-zero request rates.

---

# ⏱️ Condition 2 — 95th Percentile Latency

Use:

```promql
histogram_quantile(
  0.95,
  sum by (cluster, le) (
    rate(app_request_duration_seconds_bucket[2m])
  )
)
```

The returned latency should remain within the configured histogram range.

The lab specifically requires the p95 query to be validated through the Prometheus API rather than relying only on the web interface.

---

# 🏷️ Condition 3 — Label Preservation

Query:

```bash
curl -fsSL \
"http://localhost:9092/api/v1/query?query=app_http_requests_total"
```

Validate that every returned series contains:

```text
cluster="cluster-a"
```

or:

```text
cluster="cluster-b"
```

This confirms the interaction between:

```yaml
honor_labels: true
```

and:

```yaml
external_labels:
```

---

# 🔢 Condition 4 — Cardinality Budget

Query:

```bash
curl -fsSL \
"http://localhost:9092/api/v1/query?query=prometheus_tsdb_head_series"
```

The global Prometheus instance must remain below:

```text
2000
```

### 🟢 PASS

```text
Head series: <2000
```

### 🔴 FAIL

```text
Head series: >=2000
```

If cardinality exceeds the limit, narrow the federation `match[]` selectors.

The lab identifies narrow federation selectors as the primary operational control for limiting global time-series growth.

---

# 🔍 Troubleshooting Guide

## ❌ Prometheus Service Fails

Check:

```bash
sudo journalctl \
-u prometheus-a \
-n 30 \
--no-pager
```

Validate:

```bash
promtool check config \
/etc/prometheus/cluster-a/prometheus.yml
```

---

## ❌ YAML Parsing Error

Inspect hidden characters:

```bash
cat -A \
/etc/prometheus/federation/prometheus.yml
```

Check:

* Indentation
* Quotes
* Colons
* List formatting

---

## ❌ Federation Target DOWN

Check:

```bash
curl -fsSL \
http://localhost:9090/federate
```

and:

```bash
curl -fsSL \
http://localhost:9091/federate
```

Then inspect:

```bash
systemctl status prometheus-a
systemctl status prometheus-b
```

---

## ❌ Application Metrics Missing

Check exporter:

```bash
curl -fsSL \
http://localhost:8080/metrics
```

Then verify the cluster Prometheus target configuration.

Finally check:

```bash
curl -fsSL \
http://localhost:9092/api/v1/query?query=app_http_requests_total
```

---

## ❌ High Cardinality

Inspect:

```bash
prometheus_tsdb_head_series
```

Then reduce unnecessary metrics in:

```yaml
match[]:
```

For federation, avoid transferring high-cardinality metrics unless they are actually needed globally.

---

# 🧠 Key Concepts Learned

### 🔹 Prometheus Federation

Federation allows one Prometheus server to selectively collect metrics from another Prometheus server.

```text
Prometheus A ──┐
               ├──> Global Prometheus
Prometheus B ──┘
```

### 🔹 `external_labels`

Adds source-identifying labels:

```yaml
external_labels:
  cluster: "cluster-a"
  region: "us-east-1"
```

### 🔹 `honor_labels`

Preserves labels coming from the federated Prometheus instance instead of allowing the scraping job to overwrite them.

### 🔹 `match[]`

Controls which metrics are transferred:

```yaml
match[]:
  - '{__name__=~"up|node_cpu_seconds_total"}'
```

### 🔹 Recording Rules

Pre-compute expensive PromQL expressions:

```text
cluster:node_cpu_utilisation:avg1m
```

### 🔹 Cardinality

The number of active time series must be carefully controlled as federation scales.

---

# 🏆 Expected Outcomes

After completing the lab:

* ✅ Three Prometheus instances are running
* ✅ Two Node Exporters are running
* ✅ Cluster A is available on `9090`
* ✅ Cluster B is available on `9091`
* ✅ Global federation is available on `9092`
* ✅ Federation `/federate` endpoints work
* ✅ Cluster labels are preserved
* ✅ Cross-cluster recording rules are active
* ✅ Federation health alert is loaded
* ✅ Application metrics flow through the federation topology
* ✅ Request rates can be aggregated by cluster
* ✅ p95 latency can be calculated
* ✅ Global cardinality remains below the defined threshold

These outcomes correspond to the lab's expected global monitoring and recording-rule behavior.

---

# 📋 Final Validation Checklist

* [ ] Prometheus installed
* [ ] `promtool` installed
* [ ] Node Exporter installed
* [ ] `prometheus` system user created
* [ ] Configuration directories created
* [ ] Cluster A Prometheus running
* [ ] Cluster B Prometheus running
* [ ] Global Federation Prometheus running
* [ ] Node Exporter A running
* [ ] Node Exporter B running
* [ ] `/federate` endpoint validated
* [ ] `cluster-a` label preserved
* [ ] `cluster-b` label preserved
* [ ] Recording rules loaded
* [ ] `FederationTargetDown` alert loaded
* [ ] Application exporter A running
* [ ] Application exporter B running
* [ ] Application metrics visible
* [ ] Cross-cluster request rate validated
* [ ] 95th percentile latency validated
* [ ] Cluster label preservation validated
* [ ] Global TSDB series count below `2000`

---

# 🏁 Conclusion

This lab demonstrates how **Prometheus Federation** can create a scalable, hierarchical monitoring architecture.

Cluster-level Prometheus instances remain responsible for their own scraping, while the global Prometheus instance selectively pulls the metrics required for centralized visibility.

The combination of:

```text
external_labels
        +
honor_labels
        +
match[]
        +
recording rules
        +
cardinality controls
```

provides a practical foundation for multi-cluster observability.

The key operational lesson is to **federate only the metrics that are required globally**. Keeping `match[]` selectors narrow helps control cardinality and prevents unnecessary growth as additional clusters are introduced.

---

## ⭐ Skills Demonstrated

`Prometheus` `PromQL` `Federation` `Node Exporter` `Linux` `Ubuntu` `AWS EC2` `systemd` `Python` `Bash` `Monitoring` `Observability` `Recording Rules` `Alerting` `Metrics` `Cardinality Management` `HTTP APIs`

---

## 👨‍💻 Author

**Hafiz Muhammad Salman**

**Cloud DevOps Engineer | Linux Administrator**

⭐ Hands-on Cloud • DevOps • Linux • Monitoring • Security Labs

---

### 🔗 Technology Documentation

* [Prometheus Documentation](https://prometheus.io/docs/)
* [Prometheus Federation](https://prometheus.io/docs/prometheus/latest/federation/)
* [PromQL Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
* [Node Exporter](https://prometheus.io/docs/guides/node-exporter/)
