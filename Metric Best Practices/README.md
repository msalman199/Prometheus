# 📊 Metric Best Practices

> **Production-Grade Prometheus Metrics, Cardinality Management, Recording Rules & Alerting**

---

## 🎯 Objectives

By completing this lab, you will learn how to:

* 🐍 Instrument a Python Flask web service with production-grade Prometheus metrics.
* 📏 Apply consistent metric naming conventions and unit suffixes.
* 🏷️ Design bounded label sets and avoid high-cardinality dimensions.
* 🚨 Implement Prometheus recording and alerting rules.
* ⚡ Pre-aggregate expensive PromQL queries using recording rules.
* 📈 Build a Grafana dashboard for monitoring application performance.
* 🔍 Compare compliant and non-compliant metric implementations.
* 🧪 Measure time-series cardinality, query behavior, and alert correctness.
* 🛠️ Diagnose and remediate deliberately broken metrics.

---

## 🏗️ Lab Architecture

```text
                         ┌───────────────────────┐
                         │     Traffic Generator │
                         └───────────┬───────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       │                           │
                       ▼                           ▼
             ┌─────────────────┐         ┌─────────────────┐
             │ Non-Compliant   │         │ Compliant Flask │
             │ Flask App       │         │ Flask App       │
             │ Port 5000       │         │ Port 5001       │
             └────────┬────────┘         └────────┬────────┘
                      │                           │
                      │       /metrics            │
                      └────────────┬──────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │     Prometheus      │
                         │      Port 9090      │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                  ┌──────────────┐      ┌──────────────┐
                  │ Recording &  │      │    Grafana   │
                  │ Alert Rules  │      │    Port 3000 │
                  └──────────────┘      └──────────────┘
```

---

## 🧰 Technology Stack

| Technology           | Purpose                           |
| -------------------- | --------------------------------- |
| 🐧 Ubuntu            | Lab operating system              |
| ☁️ AWS EC2           | Lab infrastructure                |
| 🔥 Prometheus        | Metrics collection and alerting   |
| 📊 Grafana OSS       | Metrics visualization             |
| 🖥️ Node Exporter    | Host-level metrics                |
| 🐍 Python            | Application implementation        |
| 🌶️ Flask            | Web application framework         |
| 📡 prometheus_client | Python Prometheus instrumentation |
| 🧠 psutil            | System resource metrics           |
| 🔎 PromQL            | Metrics querying                  |
| 🛠️ promtool         | Configuration and rule validation |
| ⚙️ systemd           | Service management                |
| 🧪 curl              | API and endpoint testing          |
| 📦 jq                | JSON processing                   |

---

# 🚀 Task 1 — Environment Setup

## 1.1 Install System Dependencies

Update the Ubuntu system and install the required tools:

```bash
sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install -y \
  curl \
  wget \
  git \
  vim \
  jq \
  python3 \
  python3-pip \
  net-tools
```

### ✅ Verify

```bash
python3 --version
pip3 --version
curl --version
jq --version
```

---

# 🔥 1.2 Install Prometheus

Download Prometheus:

```bash
cd /tmp

wget -fsSL \
https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

tar xzf prometheus-2.45.0.linux-amd64.tar.gz
```

Create the dedicated Prometheus user:

```bash
sudo useradd \
  --no-create-home \
  --shell /bin/false \
  prometheus
```

Create directories:

```bash
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus
```

Install Prometheus binaries:

```bash
sudo cp prometheus-2.45.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.45.0.linux-amd64/promtool /usr/local/bin/

sudo cp -r prometheus-2.45.0.linux-amd64/consoles /etc/prometheus/
sudo cp -r prometheus-2.45.0.linux-amd64/console_libraries /etc/prometheus/
```

Set ownership:

```bash
sudo chown -R prometheus:prometheus \
  /etc/prometheus \
  /var/lib/prometheus

sudo chown prometheus:prometheus \
  /usr/local/bin/prometheus \
  /usr/local/bin/promtool
```

Verify:

```bash
prometheus --version
promtool --version
```

---

## 🛠️ Prometheus Download Troubleshooting

If you encounter:

```text
tar: Error is not recoverable
```

check the downloaded file:

```bash
file /tmp/prometheus-2.45.0.linux-amd64.tar.gz
```

Expected:

```text
gzip compressed data
```

If it reports:

```text
HTML document
```

remove the corrupted file:

```bash
rm -f /tmp/prometheus-2.45.0.linux-amd64.tar.gz
```

Then download the official release asset again.

📚 Official documentation:
[Prometheus Installation Documentation](https://prometheus.io/docs/prometheus/latest/installation/?utm_source=chatgpt.com)

---

# 🖥️ 1.3 Install Node Exporter

Download Node Exporter:

```bash
cd /tmp

wget -fsSL \
https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz

tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
```

Install the binary:

```bash
sudo cp \
node_exporter-1.6.1.linux-amd64/node_exporter \
/usr/local/bin/

sudo chown prometheus:prometheus \
/usr/local/bin/node_exporter
```

Verify:

```bash
node_exporter --version
```

---

# 📊 1.4 Install Grafana OSS

Install dependencies:

```bash
sudo apt-get install -y \
  apt-transport-https \
  software-properties-common
```

Create the keyring:

```bash
sudo mkdir -p /etc/apt/keyrings
```

Import Grafana's signing key:

```bash
wget -fsSL https://apt.grafana.com/gpg.key | \
gpg --dearmor | \
sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
```

Create the repository:

```bash
sudo tee /etc/apt/sources.list.d/grafana.list <<'EOF'
deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main
EOF
```

Install Grafana:

```bash
sudo apt-get update
sudo apt-get install -y grafana
```

Verify:

```bash
grafana-server -v
```

📚 Official documentation:
[Grafana Debian Installation Guide](https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/?utm_source=chatgpt.com)

---

# ⚙️ Task 1.5 — Configure systemd Services

## Prometheus Service

```bash
sudo tee /etc/systemd/system/prometheus.service <<'EOF'
[Unit]
Description=Prometheus Monitoring System
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
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```

---

## Node Exporter Service

```bash
sudo tee /etc/systemd/system/node_exporter.service <<'EOF'
[Unit]
Description=Prometheus Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```

---

# 📝 1.6 Configure Prometheus

```bash
sudo tee /etc/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:

  - job_name: prometheus
    static_configs:
      - targets:
          - localhost:9090

  - job_name: node_exporter
    static_configs:
      - targets:
          - localhost:9100
EOF

sudo chown prometheus:prometheus \
/etc/prometheus/prometheus.yml
```

Validate:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

---

# ▶️ 1.7 Start the Monitoring Stack

```bash
sudo systemctl daemon-reload

sudo systemctl enable --now \
  prometheus \
  node_exporter \
  grafana-server
```

Check services:

```bash
sudo systemctl is-active \
  prometheus \
  node_exporter \
  grafana-server
```

Expected:

```text
active
active
active
```

Test Prometheus:

```bash
curl -fsSL http://localhost:9090/-/healthy
```

Test Node Exporter:

```bash
curl -fsSL http://localhost:9100/metrics | head -5
```

Test Grafana:

```bash
curl -fsSL http://localhost:3000/api/health
```

---

## 🛠️ Troubleshooting

If Prometheus returns:

```text
Connection refused
```

wait a few seconds and retry.

Check logs:

```bash
sudo journalctl -u prometheus -n 30
```

Validate configuration:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

---

# 🐍 Task 2 — Application Instrumentation

This task creates two Flask applications:

```text
┌──────────────────────────┐
│ Non-Compliant App        │
│ Port 5000                │
│                         │
│ ❌ High cardinality      │
│ ❌ Poor naming           │
│ ❌ Raw URL labels        │
└──────────────────────────┘

             VS

┌──────────────────────────┐
│ Compliant App            │
│ Port 5001                │
│                         │
│ ✅ Bounded labels        │
│ ✅ Correct units         │
│ ✅ Explicit histograms   │
└──────────────────────────┘
```

---

# 📦 2.1 Install Python Dependencies

```bash
pip3 install flask prometheus_client psutil
```

Verify:

```bash
python3 -c "import flask, prometheus_client, psutil; print('Dependencies OK')"
```

---

# ❌ 2.2 Non-Compliant Application

The non-compliant application intentionally demonstrates Prometheus anti-patterns.

### Problems Demonstrated

* ❌ Missing namespace.
* ❌ Missing unit suffix.
* ❌ High-cardinality `user_id`.
* ❌ High-cardinality `session_id`.
* ❌ High-cardinality `ip_address`.
* ❌ Raw URL paths used as labels.
* ❌ Ambiguous memory and disk metrics.

Required endpoints:

```text
/
 /api/users/<user_id>
 /metrics
```

The application runs on:

```text
http://localhost:5000
```

The application should create metrics equivalent to:

```text
requests
requests{method,endpoint,status,user_id,session_id,ip_address}
memory_usage
disk_usage
```

The intentionally problematic labels allow the number of unique time series to increase as traffic grows.

---

# ✅ 2.3 Compliant Application

The compliant application runs on:

```text
http://localhost:5001
```

It should enforce:

### Metric naming

```text
<namespace>_<subsystem>_<name>_<unit>
```

Examples:

```text
myapp_http_requests_total
myapp_http_request_duration_seconds
myapp_memory_usage_ratio
myapp_disk_usage_bytes
```

### Bounded Labels

Use only:

```text
method
handler
status_code
```

Avoid:

```text
user_id
session_id
ip_address
raw_url
request_id
```

### Histogram

Use explicit buckets such as:

```text
0.005
0.01
0.025
0.05
0.1
0.25
0.5
1
2.5
5
10
```

This allows latency distribution to be measured appropriately.

---

# 📐 Metric Design

A production-ready application should expose metrics similar to:

| Metric                                | Type      | Labels                       |
| ------------------------------------- | --------- | ---------------------------- |
| `myapp_build_info`                    | Info      | Metadata                     |
| `myapp_http_requests_total`           | Counter   | method, handler, status_code |
| `myapp_http_request_duration_seconds` | Histogram | method, handler              |
| `myapp_active_users`                  | Gauge     | None                         |
| `myapp_memory_usage_ratio`            | Gauge     | None                         |
| `myapp_disk_usage_bytes`              | Gauge     | None                         |
| `myapp_errors_total`                  | Counter   | error_type                   |

---

# 🚦 2.4 Application Behavior

The compliant application should:

* Record request count.
* Measure request duration.
* Track active users.
* Collect memory usage with `psutil`.
* Collect disk usage with `psutil`.
* Record errors using bounded `error_type` values.
* Reject user IDs outside `1–9999`.
* Use fixed handler names.
* Expose `/metrics`.
* Provide a health endpoint.

Example health endpoint:

```text
GET /api/health
```

Expected response:

```json
{
  "status": "healthy",
  "uptime_seconds": 123.45
}
```

---

# 🔄 Task 2.5 — Register Applications in Prometheus

Add both applications to:

```text
/etc/prometheus/prometheus.yml
```

Example:

```yaml
scrape_configs:

  - job_name: bad-app
    static_configs:
      - targets:
          - localhost:5000

  - job_name: good-app
    static_configs:
      - targets:
          - localhost:5001
```

Validate:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Reload Prometheus without restarting:

```bash
curl -fsSL \
-X POST \
http://localhost:9090/-/reload
```

---

# 🧪 Task 2.6 — Generate Traffic

The traffic generator should:

* Run for at least 60 seconds.
* Generate at least 200 different user IDs for port `5000`.
* Generate `/api/users/<id>` requests.
* Use IDs between `1–500`.
* Call `/api/health` on port `5001`.
* Generate concurrent requests.
* Display progress every 20 requests.

Example execution:

```bash
python3 traffic_generator.py
```

Monitor application metrics:

```bash
curl -fsSL http://localhost:5000/metrics
```

```bash
curl -fsSL http://localhost:5001/metrics
```

---

# 🔎 Task 2.7 — Cardinality Audit

Run:

```bash
echo "=== Non-compliant app: series count ==="

curl -fsSL \
'http://localhost:9090/api/v1/query?query=count({job="bad-app"})' |
jq '.data.result[0].value[1]'
```

Compliant application:

```bash
echo "=== Compliant app: all series count ==="

curl -fsSL \
'http://localhost:9090/api/v1/query?query=count({job="good-app"})' |
jq '.data.result[0].value[1]'
```

Request counter combinations:

```bash
echo "=== Compliant request counter combinations ==="

curl -fsSL \
'http://localhost:9090/api/v1/query?query=count(myapp_http_requests_total)' |
jq '.data.result[0].value[1]'
```

### 🎯 Expected Result

The non-compliant application should produce substantially more time series.

Target:

```text
Non-compliant series >= 5 × compliant series
```

This demonstrates the cost of uncontrolled label cardinality.

---

# 🚨 Task 3 — Recording & Alerting Rules

Create the rules directory:

```bash
sudo mkdir -p /etc/prometheus/rules

sudo chown -R prometheus:prometheus \
/etc/prometheus/rules
```

---

# ⚡ 3.1 Recording Rules

Create:

```text
/etc/prometheus/rules/recording_rules.yml
```

The recording rules should calculate:

### Request rate

```text
myapp:http_request_rate5m_by_handler
```

Purpose:

```text
Pre-compute the 5-minute request rate per handler.
```

### Error ratio

```text
myapp:http_error_ratio5m
```

Purpose:

```text
5xx responses / total responses
```

### Disk usage

```text
myapp:disk_usage_gib
```

Purpose:

```text
Convert disk usage from bytes to GiB.
```

---

# 🚨 3.2 Alerting Rules

Create:

```text
/etc/prometheus/rules/alerting_rules.yml
```

Required alerts:

| Alert             | Condition          | Duration | Severity |
| ----------------- | ------------------ | -------: | -------- |
| `HighErrorRate`   | Error ratio > 5%   |       2m | warning  |
| `HighMemoryUsage` | Memory ratio > 85% |       5m | critical |
| `ApplicationDown` | `up == 0`          |       1m | critical |

Each alert should include:

```yaml
annotations:
  summary: "..."
  description: "..."
```

The description should expose the current value using:

```text
{{ $value }}
```

or:

```text
{{ $value | humanizePercentage }}
```

---

# 🔍 3.3 Validate Rules

Validate Prometheus configuration:

```bash
promtool check config \
/etc/prometheus/prometheus.yml
```

Validate recording rules:

```bash
promtool check rules \
/etc/prometheus/rules/recording_rules.yml
```

Validate alerting rules:

```bash
promtool check rules \
/etc/prometheus/rules/alerting_rules.yml
```

Reload Prometheus:

```bash
curl -fsSL \
-X POST \
http://localhost:9090/-/reload
```

Check loaded rules:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules |
jq '[.data.groups[].rules[].name]'
```

Expected rule names:

```text
HighErrorRate
HighMemoryUsage
ApplicationDown
myapp:http_request_rate5m_by_handler
myapp:http_error_ratio5m
myapp:disk_usage_gib
```

---

# 📊 Task 3.4 — Configure Grafana

Grafana is available at:

```text
http://localhost:3000
```

Default credentials:

```text
Username: admin
Password: admin
```

Add Prometheus as a data source:

```bash
curl -fsSL \
-X POST \
http://admin:admin@localhost:3000/api/datasources \
-H 'Content-Type: application/json' \
-d '{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "isDefault": true
}'
```

---

# 🛠️ Grafana Troubleshooting

If you receive:

```json
{
  "message": "Data source with the same name already exists"
}
```

List existing data sources:

```bash
curl -fsSL \
http://admin:admin@localhost:3000/api/datasources |
jq '.[].name'
```

Retrieve data source information:

```bash
curl -fsSL \
http://admin:admin@localhost:3000/api/datasources |
jq .
```

Update an existing source instead of creating a duplicate.

📚 Official Grafana API documentation:
[Grafana Data Source HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/data_source/?utm_source=chatgpt.com)

---

# 📈 Task 3.5 — Grafana Dashboard

Create:

```text
~/metric-lab/dashboards/comparison.json
```

The dashboard should contain exactly **four panels** arranged in a **2×2 layout**.

---

## Panel 1 — Request Rate

**Type:**

```text
Time series
```

**PromQL:**

```promql
sum(myapp:http_request_rate5m_by_handler) by (handler)
```

Purpose:

```text
Display request rate while demonstrating bounded handler labels.
```

---

## Panel 2 — Error Ratio

**Type:**

```text
Stat
```

**PromQL:**

```promql
myapp:http_error_ratio5m
```

Purpose:

```text
Display the pre-computed error ratio.
```

---

## Panel 3 — Series Count Comparison

**Type:**

```text
Bar gauge
```

Queries:

```promql
count({job="bad-app"})
```

and:

```promql
count({job="good-app"})
```

Purpose:

```text
Visualize the cardinality difference.
```

---

## Panel 4 — P95 Request Latency

**Type:**

```text
Time series
```

PromQL:

```promql
histogram_quantile(
  0.95,
  sum(
    rate(
      myapp_http_request_duration_seconds_bucket[5m]
    )
  ) by (le, handler)
)
```

Purpose:

```text
Validate the histogram bucket design and application latency.
```

---

# 📥 Import Dashboard

Import the dashboard using the Grafana API:

```bash
curl -fsSL \
-X POST \
http://admin:admin@localhost:3000/api/dashboards/import \
-H 'Content-Type: application/json' \
-d "{\"dashboard\": $(cat ~/metric-lab/dashboards/comparison.json), \"overwrite\": true, \"folderId\": 0}"
```

---

# 🧪 Validation Checklist

## Prometheus

* [ ] Prometheus service is running.
* [ ] Prometheus runs as the `prometheus` user.
* [ ] `/var/lib/prometheus` is owned by `prometheus`.
* [ ] Prometheus is accessible on port `9090`.
* [ ] Node Exporter is accessible on port `9100`.
* [ ] Grafana is accessible on port `3000`.
* [ ] Both applications are being scraped.

## Non-Compliant Application

* [ ] Bare metric names are present.
* [ ] Unit-free metrics are present.
* [ ] High-cardinality labels are present.
* [ ] Raw URL paths are used as labels.
* [ ] Series count grows with traffic.

## Compliant Application

* [ ] Metrics have a namespace.
* [ ] Metrics use appropriate unit suffixes.
* [ ] HTTP labels are bounded.
* [ ] Raw URLs are not used as labels.
* [ ] Histogram uses explicit buckets.
* [ ] System metrics use `psutil`.
* [ ] Error types are bounded.
* [ ] User IDs outside `1–9999` return HTTP 400.

## Prometheus Rules

* [ ] Recording rules pass `promtool check rules`.
* [ ] Alerting rules pass `promtool check rules`.
* [ ] `HighErrorRate` exists.
* [ ] `HighMemoryUsage` exists.
* [ ] `ApplicationDown` exists.
* [ ] Rules report healthy status.

## Grafana

* [ ] Prometheus is configured as a data source.
* [ ] Dashboard imports successfully.
* [ ] Dashboard contains exactly four panels.
* [ ] Cardinality comparison is visible.
* [ ] Error ratio is displayed.
* [ ] Request rate is displayed.
* [ ] P95 latency is displayed.
* [ ] P95 query does not return `NaN`.

---

# 🔬 Troubleshooting & Investigation

## ❓ P95 Latency Shows `NaN`

If the P95 panel displays:

```text
NaN
```

or:

```text
0
```

investigate the histogram buckets.

Check raw bucket metrics:

```promql
myapp_http_request_duration_seconds_bucket
```

Then inspect rates:

```promql
rate(
  myapp_http_request_duration_seconds_bucket[5m]
)
```

Check bucket distribution:

```promql
sum(
  rate(
    myapp_http_request_duration_seconds_bucket[5m]
  )
) by (le)
```

If requests are falling outside the useful bucket range, the histogram boundaries may not represent the application's actual latency distribution.

---

# ❓ HighErrorRate Does Not Fire

First evaluate the recording rule directly:

```promql
myapp:http_error_ratio5m
```

Then inspect the underlying metric:

```promql
myapp_http_requests_total
```

Check 5xx responses:

```promql
sum(
  rate(
    myapp_http_requests_total{
      status_code=~"5.."
    }[5m]
  )
)
```

Compare against total requests:

```promql
sum(
  rate(
    myapp_http_requests_total[5m]
  )
)
```

A common cause is a label mismatch.

For example, the metric may use:

```text
status_code
```

while the recording rule incorrectly selects:

```text
status
```

The selector must match the actual metric label name.

---

# 📚 Key Prometheus Best Practices

## 1. Use Meaningful Names

Prefer:

```text
myapp_http_requests_total
```

instead of:

```text
requests
```

---

## 2. Include Units

Prefer:

```text
myapp_request_duration_seconds
myapp_disk_usage_bytes
myapp_memory_usage_ratio
```

instead of:

```text
request_duration
disk_usage
memory_usage
```

---

## 3. Avoid High Cardinality

❌ Avoid:

```text
user_id
session_id
request_id
ip_address
raw_url
```

These values can create thousands or millions of unique series.

Prefer:

```text
method
handler
status_code
```

---

## 4. Never Use Raw URLs as Labels

❌ Bad:

```text
endpoint="/api/users/4821"
```

❌ Bad:

```text
endpoint="/api/users/9123"
```

✅ Good:

```text
handler="get_user"
```

The route remains stable regardless of the user ID.

---

## 5. Use Counters Correctly

Counters should normally end with:

```text
_total
```

Example:

```text
myapp_http_requests_total
```

---

## 6. Use Histograms for Request Duration

Request duration should generally be represented using:

```text
_seconds
```

Example:

```text
myapp_http_request_duration_seconds
```

Explicit buckets should reflect real application behavior.

---

## 7. Use Recording Rules for Expensive Queries

Instead of repeatedly calculating:

```promql
sum(rate(...[5m])) by (...)
```

store the result as:

```text
myapp:http_request_rate5m_by_handler
```

This reduces repeated query computation for dashboards and alerts.

---

# 📊 Expected Results

After completing the lab, you should observe:

```text
                 Time-Series Cardinality

Non-Compliant App
████████████████████████████████████████████

Compliant App
██████
```

The exact values depend on the generated traffic, but the non-compliant implementation should produce **at least five times more series** than the compliant implementation under the required traffic workload.

The compliant application should remain below approximately:

```text
20 unique time series
```

regardless of how many different user IDs are requested.

---

# 🧠 Key Learning Outcomes

This lab demonstrates that **metric cardinality is an architectural decision**.

An application that creates labels from:

```text
user IDs
session IDs
IP addresses
request IDs
raw URLs
```

can rapidly increase the number of Prometheus time series.

By contrast, bounded labels such as:

```text
method
handler
status_code
```

provide useful observability without allowing uncontrolled series growth.

Recording rules further improve monitoring performance by pre-computing expensive aggregations, while alerting rules allow Prometheus to continuously evaluate SLO-related conditions.

---

# 🏁 Conclusion

The **Metric Best Practices** lab demonstrates how to design Prometheus instrumentation that is suitable for production environments.

The comparison between the two Flask applications highlights the difference between:

```text
❌ Uncontrolled Metrics
        ↓
High Cardinality
        ↓
Higher Memory Usage
        ↓
Expensive Queries
        ↓
Difficult Monitoring
```

and:

```text
✅ Well-Designed Metrics
        ↓
Bounded Cardinality
        ↓
Predictable Resource Usage
        ↓
Efficient PromQL
        ↓
Reliable Dashboards & Alerts
```

The key principle is simple:

> **Metrics should be designed for long-term operational scalability, not just short-term visibility.**

By applying consistent naming, correct units, bounded labels, appropriate histogram buckets, recording rules, and meaningful alerts, Prometheus can remain reliable as applications, teams, traffic, and retention requirements grow.

---

## 🌟 Skills Demonstrated

```text
🔥 Prometheus
📊 Grafana
🐍 Python / Flask
📈 PromQL
🚨 Alerting Rules
⚡ Recording Rules
🏷️ Metric Cardinality
📏 Metric Naming Standards
📡 Node Exporter
🧠 psutil
⚙️ systemd
🛠️ promtool
☁️ AWS EC2
🐧 Linux Administration
🔍 Observability
```

---

## 👨‍💻 Lab Focus

**Prometheus Metric Engineering • Observability • Monitoring Best Practices • Cardinality Optimization • SLO Alerting • Grafana Visualization**

---
