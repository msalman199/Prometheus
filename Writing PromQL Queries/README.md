<div align="center">

# 📝 Writing PromQL Queries

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-DA4E31?style=for-the-badge&logo=prometheus&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)
![systemd](https://img.shields.io/badge/systemd-3776AB?style=for-the-badge&logo=linux&logoColor=white)
![AWS EC2](https://img.shields.io/badge/AWS%20EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)

**A design-brief lab: stand up a production-representative Prometheus + Node Exporter stack, then design and build a validated PromQL query library covering selectors, rate functions, aggregation, and alerting thresholds.**

</div>

---

## 📑 Table of Contents

- [🎯 Objectives](#-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🧩 Key Concepts](#-key-concepts)
- [⚙️ Task 1: Environment Setup — Prometheus and Node Exporter](#️-task-1-environment-setup--prometheus-and-node-exporter)
- [🔎 Task 2: Instant Queries — Selectors, Filters, and Functions](#-task-2-instant-queries--selectors-filters-and-functions)
- [📚 Task 3: Aggregation, Grouping, and a Validated Query Library](#-task-3-aggregation-grouping-and-a-validated-query-library)
- [✅ Expected Outcomes](#-expected-outcomes)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🏁 Conclusion](#-conclusion)

---

## 🎯 Objectives

| # | Objective |
|---|-----------|
| 1 | Design and execute PromQL queries that extract, filter, and aggregate time-series metrics from a live Prometheus instance backed by Node Exporter |
| 2 | Apply rate functions, label matchers, and regex selectors to isolate meaningful signals from high-cardinality metric streams |
| 3 | Build a validated query library that covers CPU, memory, disk, and network dimensions and is suitable for alerting rule integration |

## 📋 Prerequisites

- ✅ Comfort navigating and editing files on an Ubuntu Linux system via the command line
- ✅ Familiarity with the concept of time-series data and key-value label pairs as identifiers
- ✅ Understanding of Linux system resource concepts: CPU modes, memory pages, filesystem mount points, and network interfaces

## 🖥️ Lab Environment

> **☁️ Al Nafi AWS EC2 Instance**
> You will work on a dedicated AWS EC2 Ubuntu instance provided by Al Nafi. The instance has a base Ubuntu installation — you will install all required tools in Task 1.

## 🧩 Key Concepts

| Concept | Description |
|---------|-------------|
| **Instant Query** | Returns a single value per time series evaluated at one point in time |
| **Range Query** | Returns a matrix of values for each time series across a time window |
| **Range Vector Selector** | A metric name followed by a bracketed duration (e.g., `[5m]`) — required input for functions like `rate()` and `increase()` |
| **`rate()`** | Computes the per-second average rate of increase of a counter over a duration, correctly handling counter resets |
| **`increase()`** | Computes the total increase of a counter over a duration (`rate` × window length) |
| **`predict_linear()`** | Extrapolates a linear trend from a range vector a specified number of seconds into the future — used for capacity forecasting |
| **Label Matchers** | `=` (equality), `!=` (inequality), `=~` (regex match), `!~` (regex non-match) — used to filter time series by label value |
| **Aggregation Operators** | `sum`, `avg`, `count`, `topk`, `bottomk`, etc., with optional `by (label)` (keep only named labels) or `without (label)` (drop only named labels) clauses |
| **Node Exporter** | A Prometheus exporter that exposes host-level OS and hardware metrics (CPU, memory, disk, network) at `/metrics` |

---

## ⚙️ Task 1: Environment Setup — Prometheus and Node Exporter

### 📌 Requirement 1.1: Deploy Prometheus and Node Exporter as systemd services

Your environment must satisfy all of the following constraints before you proceed to Task 2:

- Prometheus (v2.47.0 or later) runs as a non-root dedicated system user with no login shell, listening on port 9090
- Node Exporter (v1.6.1 or later) runs under the same user, listening on port 9100
- Both processes are managed by systemd and survive a `systemctl restart`
- Prometheus is configured to scrape both itself and Node Exporter on a 15-second interval
- All binary, configuration, and data directories have ownership set to the Prometheus system user

> Use the official release tarballs from the Prometheus GitHub releases page. The commands below show the download and extraction pattern; adapt version strings if the URLs have changed.

```bash
# Create the dedicated system user
sudo useradd --no-create-home --shell /bin/false prometheus
# Create required directories and set ownership
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus
# Download Prometheus
cd /tmp
wget -fsSL https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz \
  -O prometheus.tar.gz
```

> 📖 Official installation reference: https://prometheus.io/docs/prometheus/latest/installation/

```bash
# Extract and install binaries
tar xzf /tmp/prometheus.tar.gz -C /tmp
sudo cp /tmp/prometheus-2.47.0.linux-amd64/prometheus /usr/local/bin/
sudo cp /tmp/prometheus-2.47.0.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool
sudo cp -r /tmp/prometheus-2.47.0.linux-amd64/consoles /etc/prometheus/
sudo cp -r /tmp/prometheus-2.47.0.linux-amd64/console_libraries /etc/prometheus/
sudo chown -R prometheus:prometheus /etc/prometheus/consoles /etc/prometheus/console_libraries
```

```yaml
# Write the Prometheus configuration file
sudo tee /etc/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

```ini
# Write the Prometheus systemd unit
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

[Install]
WantedBy=multi-user.target
EOF
```

```bash
# Download Node Exporter
wget -fsSL https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz \
  -O /tmp/node_exporter.tar.gz
```

> 📖 Official installation reference: https://prometheus.io/docs/guides/node-exporter/

```bash
# Install Node Exporter binary
tar xzf /tmp/node_exporter.tar.gz -C /tmp
sudo cp /tmp/node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/node_exporter
```

```ini
# Write the Node Exporter systemd unit
sudo tee /etc/systemd/system/node_exporter.service <<'EOF'
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

```bash
# Enable and start both services
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
sudo systemctl enable --now prometheus
```

> **🛠️ Troubleshoot this step:**
> You may see `Failed to start prometheus.service: Unit not found` or `code=exited, status=1/FAILURE` in `journalctl -u prometheus`.
> Run `sudo journalctl -u prometheus -n 30 --no-pager` to read the exact startup error; the most common cause is a wrong path in `ExecStart` — verify each path exists with `ls -l /usr/local/bin/prometheus /etc/prometheus/prometheus.yml`.
> 📖 Official systemd integration guide: https://prometheus.io/docs/prometheus/latest/installation/#using-systemd

### 📌 Requirement 1.2: Verify metric collection is active

Wait approximately 90 seconds after starting both services, then confirm that Prometheus is actively scraping Node Exporter. Both targets must show state `up` before you continue.

```bash
# Confirm both services are active
sudo systemctl is-active prometheus node_exporter
```

```bash
# Confirm Prometheus HTTP API is reachable and returning metric names
curl -fsSL "http://localhost:9090/api/v1/label/__name__/values" | python3 -m json.tool | head -30
```

```bash
# Confirm both scrape targets are healthy (state must be "up" for both)
curl -fsSL "http://localhost:9090/api/v1/targets" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data['data']['activeTargets']:
    print(t['labels']['job'], '->', t['health'])
"
```

> ✅ **Expected output:** both `prometheus` and `node_exporter` print `-> up`.

> **🛠️ Troubleshoot this step:**
> You may see `curl: (7) Failed to connect to localhost port 9090` or the targets API returns `health: down`.
> Check whether Prometheus bound to the port with `ss -tlnp | grep 9090`; if the port is absent, the process crashed — inspect `sudo journalctl -u prometheus -n 50 --no-pager` for the root cause.
> 📖 Prometheus target troubleshooting: https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config

---

## 🔎 Task 2: Instant Queries — Selectors, Filters, and Functions

PromQL operates on two query types: **instant queries** return a single value per time series at one point in time; **range queries** return a matrix of values over a time window. Task 2 focuses on instant queries.

### 📌 Requirement 2.1: Build a reusable query executor and implement selector-level queries

Implement a Bash query executor that wraps the Prometheus HTTP API. The executor must satisfy this interface contract:

```bash
# Interface contract — implement these two functions in a file named pql.sh

# pql_instant QUERY
#   Sends an instant query to the Prometheus API.
#   Prints the raw JSON result to stdout.
#   Exits non-zero and prints the API error message to stderr if status != "success".
pql_instant() { : ; }

# pql_range QUERY START_EPOCH END_EPOCH STEP
#   Sends a range query to the Prometheus API.
#   Prints the raw JSON result to stdout.
#   Exits non-zero and prints the API error message to stderr if status != "success".
pql_range() { : ; }
```

Once the executor is implemented, use it to run the following selector queries. Each query must return at least one result; record the result count for each.

```bash
# Metric name selector — all time series for node CPU counters
# node_cpu_seconds_total is a counter: it only ever increases, recording cumulative CPU time per mode per core
source ./pql.sh
pql_instant "node_cpu_seconds_total"

# Equality label filter — idle CPU time on core 0 only
pql_instant 'node_cpu_seconds_total{cpu="0",mode="idle"}'

# Inequality filter — all CPU modes except idle
pql_instant 'node_cpu_seconds_total{mode!="idle"}'

# Regex inclusion filter — user and system modes only
pql_instant 'node_cpu_seconds_total{mode=~"user|system"}'

# Regex exclusion filter — filesystems that are not tmpfs, devtmpfs, or overlay
# node_filesystem_size_bytes reports the total capacity of each mounted filesystem
pql_instant 'node_filesystem_size_bytes{fstype!~"tmpfs|devtmpfs|overlay|squashfs"}'

# Negative regex on device name — network interfaces excluding loopback and virtual bridges
pql_instant 'node_network_receive_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}'
```

> ✅ **Confirmation:** each `pql_instant` call prints JSON with `"status": "success"` and a non-empty result array.

### 📌 Requirement 2.2: Apply rate, increase, and mathematical transformation functions

`rate(v[d])` computes the per-second average rate of increase of a counter over duration `d`, handling counter resets. It requires a range vector (a metric name followed by a bracketed duration such as `[5m]`). Use `rate` rather than raw counter values whenever you want a meaningful instantaneous speed.

```bash
# Per-second CPU utilisation rate per core per mode over the last 5 minutes
pql_instant "rate(node_cpu_seconds_total[5m])"

# Per-second network receive rate, physical interfaces only
pql_instant 'rate(node_network_receive_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}[5m])'

# Total bytes received in the last 5 minutes (increase = rate * window duration)
pql_instant 'increase(node_network_receive_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}[5m])'

# Memory usage as a percentage — arithmetic on two instant vectors
# node_memory_MemAvailable_bytes is the kernel's estimate of reclaimable memory
pql_instant "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"

# Root filesystem usage percentage
pql_instant '(1 - (node_filesystem_free_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100'

# CPU utilisation percentage — subtract idle fraction from 100
pql_instant '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'

# Predict available memory in 1 hour using linear regression over the last 30 minutes
# predict_linear(v[d], t) extrapolates the trend in v over d by t seconds into the future
pql_instant "predict_linear(node_memory_MemAvailable_bytes[30m], 3600)"
```

> ✅ **Confirmation:** the CPU utilisation query returns a scalar between 0 and 100; the `predict_linear` query returns a single float value.

---

## 📚 Task 3: Aggregation, Grouping, and a Validated Query Library

### 📌 Requirement 3.1: Implement aggregation operators with and without grouping dimensions

Aggregation operators collapse multiple time series into fewer series. The `by` clause names the label dimensions to preserve; all other labels are dropped. The `without` clause names labels to drop; all others are preserved.

```bash
# Sum all CPU time across every core and mode — collapses to a single scalar
pql_instant "sum(node_cpu_seconds_total)"

# Sum CPU rate grouped by mode — one output series per CPU mode
pql_instant "sum by (mode) (rate(node_cpu_seconds_total[5m]))"

# Sum CPU rate grouped by CPU core — one output series per core
pql_instant "sum by (cpu) (rate(node_cpu_seconds_total[5m]))"

# Average load normalised by CPU count
# count(count by (cpu) (...)) is the idiomatic way to count distinct label values
pql_instant "node_load1 / count(count by (cpu) (node_cpu_seconds_total))"

# Top 3 network interfaces by current receive rate
# topk(k, v) returns the k time series with the highest current values
pql_instant 'topk(3, rate(node_network_receive_bytes_total[5m]))'

# Bottom 3 filesystems by free space percentage — useful for capacity alerting
pql_instant "bottomk(3, (node_filesystem_free_bytes / node_filesystem_size_bytes) * 100)"

# Count of distinct CPU cores visible to the kernel
pql_instant "count(count by (cpu) (node_cpu_seconds_total))"
```

> ✅ **Confirmation:** `sum by (mode)` returns one series per CPU mode label value (typically: `idle`, `iowait`, `irq`, `nice`, `softirq`, `steal`, `system`, `user`); `topk(3, ...)` returns exactly three series.

### 📌 Requirement 3.2: Build and validate a production-grade query library

Implement a query library file named `query_library.sh` that satisfies the following interface contract. The library must source `pql.sh` and must not duplicate its implementation.

```bash
# Interface contract for query_library.sh

# run_category CATEGORY_NAME
#   Prints a section header to stdout.
run_category() { : ; }

# run_query DESCRIPTION PROMQL_EXPRESSION
#   Prints DESCRIPTION, executes pql_instant on PROMQL_EXPRESSION,
#   extracts the numeric value(s) from the JSON result,
#   and prints them in a human-readable format.
#   Exits non-zero if the query fails validation.
run_query() { : ; }

# validate_query PROMQL_EXPRESSION
#   Returns 0 if the Prometheus API accepts the expression as syntactically valid.
#   Returns 1 and prints the API error string to stderr otherwise.
validate_query() { : ; }
```

The library must cover all four resource dimensions listed below. Every query must pass `validate_query` before its result is printed. Implement the following query set inside `query_library.sh`:

```bash
# CPU dimension
CPU_UTIL='100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
CPU_BY_MODE='sum by (mode) (rate(node_cpu_seconds_total[5m])) * 100'
CPU_EXCL_IDLE_IOWAIT='sum by (cpu) (rate(node_cpu_seconds_total{mode!~"idle|iowait"}[5m]))'

# Memory dimension
MEM_USED_PCT='(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
MEM_AVAILABLE_GB='node_memory_MemAvailable_bytes / 1073741824'
MEM_TREND='predict_linear(node_memory_MemAvailable_bytes[30m], 3600)'

# Disk dimension
DISK_USED_PCT='(1 - (node_filesystem_free_bytes{fstype!~"tmpfs|devtmpfs|overlay|squashfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|devtmpfs|overlay|squashfs"})) * 100'
DISK_READ_RATE='sum(rate(node_disk_read_bytes_total[5m]))'
DISK_WRITE_RATE='sum(rate(node_disk_written_bytes_total[5m]))'
DISK_IO_UTIL='avg(rate(node_disk_io_time_seconds_total[5m])) * 100'

# Network dimension
NET_RX_RATE='sum(rate(node_network_receive_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}[5m]))'
NET_TX_RATE='sum(rate(node_network_transmit_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}[5m]))'
NET_ERR_RATE='sum(rate(node_network_receive_errs_total[5m])) + sum(rate(node_network_transmit_errs_total[5m]))'
NET_TOP3='topk(3, rate(node_network_receive_bytes_total[5m]))'

# Alerting threshold queries — these return an empty result set when the condition is not breached
ALERT_CPU_HIGH='100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80'
ALERT_MEM_HIGH='(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90'
ALERT_DISK_HIGH='(1 - (node_filesystem_free_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 85'
ALERT_TARGET_DOWN='up == 0'
```

Run the completed library and confirm all queries pass validation:

```bash
bash query_library.sh 2>&1 | tee query_library_output.txt
grep -c "PASS" query_library_output.txt
```

> ✅ **Confirmation:** the `grep` count equals the total number of queries defined in the library (16 in the set above); no line in the output contains `FAIL` or `error`.

---

## ✅ Expected Outcomes

- Every query in `query_library.sh` executes successfully against the live Prometheus instance, returns a non-empty result for resource metrics, and returns an empty result for alerting threshold queries when the system is not under stress.
- The `validate_query` function correctly distinguishes syntactically valid PromQL expressions from invalid ones, returning exit code `0` for valid expressions and exit code `1` with an API error message for expressions such as `rate(node_cpu_seconds_total)` (missing required range selector).

---

## 🛠️ Troubleshooting

Work through the following diagnostic questions yourself as part of validating your query library:

1. If several queries return empty result sets even though the services are running, what does the Prometheus target health page at `http://localhost:9090/targets` tell you about scrape duration and last scrape error, and how would you correlate that with the timestamps on the metrics returned by `node_cpu_seconds_total`?
2. If `rate(node_cpu_seconds_total[5m])` returns no data but `node_cpu_seconds_total` returns data, what property of the range selector duration relative to the scrape interval could explain the gap, and how would you adjust the duration or the scrape configuration to resolve it?

---

## 🏁 Conclusion

This lab established a production-representative Prometheus stack from a bare Ubuntu instance and progressed from raw metric selectors through rate functions, aggregation operators, and threshold expressions to a fully validated query library. The query patterns you implemented — particularly `rate` over counters, `sum by` grouping, and `predict_linear` for capacity forecasting — are the same constructs used in Grafana dashboards and Prometheus alerting rules in production environments. The `validate_query` contract you built is directly extensible into a CI pipeline that lints PromQL expressions before they are deployed to a live alerting system.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al%20Nafi-Cybersecurity%20Training-blueviolet?style=for-the-badge)

</div>
