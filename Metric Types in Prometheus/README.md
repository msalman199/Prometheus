<div align="center">

# 📊 Metric Types in Prometheus

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-DA4E31?style=for-the-badge&logo=prometheus&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

**A hands-on lab exploring Prometheus's four core metric types — Counter, Gauge, Histogram, and Summary — through a live Flask instrumentation target and PromQL analysis.**

</div>

---

## 📑 Table of Contents

- [🎯 Lab Objectives](#-lab-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🧩 Key Concepts](#-key-concepts)
- [🚀 Task 1: Environment Setup and Prometheus Installation](#-task-1-environment-setup-and-prometheus-installation)
- [🐍 Task 2: Create Sample Application with Different Metric Types](#-task-2-create-sample-application-with-different-metric-types)
- [▶️ Task 3: Start Services and Generate Traffic](#️-task-3-start-services-and-generate-traffic)
- [🔢 Task 4: Explore Counter Metrics](#-task-4-explore-counter-metrics)
- [📈 Task 5: Explore Gauge Metrics](#-task-5-explore-gauge-metrics)
- [📊 Task 6: Explore Histogram Metrics](#-task-6-explore-histogram-metrics)
- [🧮 Task 7: Explore Summary Metrics](#-task-7-explore-summary-metrics)
- [🔬 Task 8: Advanced Metric Analysis](#-task-8-advanced-metric-analysis)
- [⚖️ Task 9: Metric Type Comparison and Best Practices](#️-task-9-metric-type-comparison-and-best-practices)
- [✅ Task 10: Cleanup and Verification](#-task-10-cleanup-and-verification)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🏁 Conclusion](#-conclusion)

---

## 🎯 Lab Objectives

By the end of this lab, you will be able to:

| # | Objective |
|---|-----------|
| 1 | Understand the four core metric types in Prometheus: counter, gauge, histogram, and summary |
| 2 | Write effective Prometheus queries (PromQL) to demonstrate each metric type |
| 3 | Set up and configure a sample application that exposes different metric types |
| 4 | Collect and analyze metrics from a running application using Prometheus |
| 5 | Interpret the behavior and use cases for each metric type through hands-on practice |

## 📋 Prerequisites

Before starting this lab, you should have:

- ✅ Basic understanding of Linux command line operations
- ✅ Familiarity with text editors (nano, vim, or similar)
- ✅ Basic knowledge of HTTP concepts and web services
- ✅ Understanding of monitoring concepts and time-series data
- ✅ Completion of previous Prometheus labs or equivalent knowledge

## 🖥️ Lab Environment

> **☁️ Al Nafi Cloud Machine**
> Al Nafi provides Linux-based cloud machines for this lab. Simply click **Start Lab** to access your dedicated environment. The provided Linux machine is bare metal with no pre-installed tools — you will install all required software during the lab exercises.
>
> All tasks in this lab are performed on a **single Linux machine**. No additional virtual machines or remote hosts are required.

## 🧩 Key Concepts

| Concept | Description |
|---------|-------------|
| **Counter** | A cumulative metric that only ever increases (or resets to 0 on restart) — ideal for request counts, error counts, and events processed |
| **Gauge** | A metric that can arbitrarily go up and down — ideal for CPU/memory usage, active connections, and queue sizes |
| **Histogram** | Samples observations into configurable buckets, exposing `_bucket`, `_sum`, and `_count` series — enables server-side, aggregatable quantile calculation via `histogram_quantile()` |
| **Summary** | Calculates configurable quantiles client-side and exposes them directly — lower query overhead but cannot be aggregated across instances |
| **PromQL** | Prometheus's functional query language used to select and aggregate time-series data |
| **`rate()`** | Calculates the per-second average rate of increase of a counter over a time window |
| **`histogram_quantile()`** | Estimates a quantile (e.g., p95) from cumulative histogram bucket data |
| **Cardinality** | The number of unique time series produced by a metric and its label combinations |

---

## 🚀 Task 1: Environment Setup and Prometheus Installation

### 📦 Subtask 1.1: Update System and Install Dependencies

Update your system and install necessary dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y wget curl tar python3 python3-pip git
```

### ⬇️ Subtask 1.2: Download and Install Prometheus

Download the latest Prometheus release:

```bash
cd /opt
sudo wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz
sudo tar xvfz prometheus-2.47.0.linux-amd64.tar.gz
sudo mv prometheus-2.47.0.linux-amd64 prometheus
sudo chown -R $USER:$USER /opt/prometheus
```

Create a symbolic link for easy access:

```bash
sudo ln -s /opt/prometheus/prometheus /usr/local/bin/prometheus
sudo ln -s /opt/prometheus/promtool /usr/local/bin/promtool
```

### ⚙️ Subtask 1.3: Create Prometheus Configuration

Create a basic Prometheus configuration file:

```bash
mkdir -p ~/prometheus-lab
cd ~/prometheus-lab
```

Create the configuration file:

```yaml
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s      # 🔄 how often Prometheus scrapes targets
  evaluation_interval: 15s  # 🔄 how often alerting rules are evaluated

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']   # 📍 Prometheus scraping itself

  - job_name: 'sample-app'
    static_configs:
      - targets: ['localhost:8000']   # 📍 our Flask instrumentation target
    scrape_interval: 5s
EOF
```

---

## 🐍 Task 2: Create Sample Application with Different Metric Types

### 📦 Subtask 2.1: Install Python Dependencies

Install the Prometheus Python client library:

```bash
pip3 install prometheus_client flask
```

### 🛠️ Subtask 2.2: Create Sample Application

Create a comprehensive sample application that demonstrates all metric types:

```python
cat > sample_app.py << 'EOF'
#!/usr/bin/env python3

import time
import random
import threading
from flask import Flask, request
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# 🔢 Counter Metrics - Values that only increase
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
error_count = Counter('http_errors_total', 'Total HTTP errors', ['status_code'])

# 📈 Gauge Metrics - Values that can go up and down
active_connections = Gauge('active_connections', 'Number of active connections')
cpu_usage = Gauge('cpu_usage_percent', 'Current CPU usage percentage')
memory_usage = Gauge('memory_usage_bytes', 'Current memory usage in bytes')

# 📊 Histogram Metrics - Observations in buckets
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', 
                           buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
response_size = Histogram('http_response_size_bytes', 'HTTP response size in bytes',
                         buckets=[100, 500, 1000, 5000, 10000, 50000])

# 🧮 Summary Metrics - Observations with quantiles
request_latency = Summary('http_request_latency_seconds', 'HTTP request latency')
processing_time = Summary('data_processing_seconds', 'Time spent processing data')

# 🔁 Simulate system metrics
def update_system_metrics():
    while True:
        # 💻 Simulate CPU usage (0-100%)
        cpu_usage.set(random.uniform(10, 90))
        
        # 🧠 Simulate memory usage (in bytes)
        memory_usage.set(random.randint(1000000, 8000000))
        
        # 🔌 Simulate active connections (0-50)
        active_connections.set(random.randint(0, 50))
        
        time.sleep(2)

# ▶️ Start background thread for system metrics
metrics_thread = threading.Thread(target=update_system_metrics, daemon=True)
metrics_thread.start()

@app.route('/')
def home():
    # ➕ Increment request counter
    request_count.labels(method='GET', endpoint='/').inc()
    
    # ⏱️ Simulate request duration
    duration = random.uniform(0.1, 2.0)
    time.sleep(duration)
    
    # 📝 Record metrics
    request_duration.observe(duration)
    request_latency.observe(duration)
    
    response_data = "Welcome to Prometheus Metrics Demo!"
    response_size.observe(len(response_data))
    
    return response_data

@app.route('/api/data')
def api_data():
    request_count.labels(method='GET', endpoint='/api/data').inc()
    
    # ⚙️ Simulate processing time
    process_time = random.uniform(0.5, 3.0)
    processing_time.observe(process_time)
    
    # ⏱️ Simulate request duration
    duration = random.uniform(0.2, 1.5)
    request_duration.observe(duration)
    request_latency.observe(duration)
    
    time.sleep(duration)
    
    response_data = {"status": "success", "data": [1, 2, 3, 4, 5]}
    response_size.observe(len(str(response_data)))
    
    return response_data

@app.route('/api/error')
def api_error():
    request_count.labels(method='GET', endpoint='/api/error').inc()
    error_count.labels(status_code='500').inc()  # 🚨 error path
    
    duration = random.uniform(0.1, 0.5)
    request_duration.observe(duration)
    request_latency.observe(duration)
    
    return "Internal Server Error", 500

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}  # 📤 scrape endpoint

if __name__ == '__main__':
    print("Starting sample application with Prometheus metrics...")
    print("Metrics available at: http://localhost:8000/metrics")
    app.run(host='0.0.0.0', port=8000, debug=False)
EOF
```

### 🔐 Subtask 2.3: Make Application Executable

```bash
chmod +x sample_app.py
```

---

## ▶️ Task 3: Start Services and Generate Traffic

### 🚦 Subtask 3.1: Start Prometheus

Open a new terminal session and start Prometheus:

```bash
cd ~/prometheus-lab
prometheus --config.file=prometheus.yml --storage.tsdb.path=./data --web.console.templates=/opt/prometheus/consoles --web.console.libraries=/opt/prometheus/console_libraries
```

### 🖥️ Subtask 3.2: Start Sample Application

Open another terminal session and start the sample application:

```bash
cd ~/prometheus-lab
python3 sample_app.py
```

### 🚗 Subtask 3.3: Generate Traffic

Open a third terminal session to generate traffic:

```bash
# 🛠️ Create a traffic generation script
cat > generate_traffic.sh << 'EOF'
#!/bin/bash

echo "Generating traffic to sample application..."

while true; do
    # 🌐 Generate random requests
    curl -s http://localhost:8000/ > /dev/null
    sleep 1
    
    curl -s http://localhost:8000/api/data > /dev/null
    sleep 2
    
    # ⚠️ Occasionally hit error endpoint
    if [ $((RANDOM % 10)) -eq 0 ]; then
        curl -s http://localhost:8000/api/error > /dev/null
    fi
    
    sleep 1
done
EOF

chmod +x generate_traffic.sh
./generate_traffic.sh
```

> ⏳ Let the traffic generator run for about **2–3 minutes** to collect sufficient data.

---

## 🔢 Task 4: Explore Counter Metrics

### 🌐 Subtask 4.1: Access Prometheus Web Interface

Open your web browser and navigate to:

```
http://localhost:9090
```

### 🔍 Subtask 4.2: Query Counter Metrics

Execute the following queries in the Prometheus web interface:

**Basic Counter Query:**
```promql
http_requests_total
```

**Counter with Label Filtering:**
```promql
http_requests_total{endpoint="/"}
```

**Rate of Counter Increase:**
```promql
rate(http_requests_total[5m])
```

**Total Requests per Endpoint:**
```promql
sum by (endpoint) (http_requests_total)
```

**Error Rate Calculation:**
```promql
rate(http_errors_total[5m]) / rate(http_requests_total[5m])
```

### 🧠 Subtask 4.3: Analyze Counter Behavior

Observe that:

- ✅ Counters only increase (never decrease)
- ✅ The `rate()` function shows the per-second increase
- ✅ Counters reset to zero when the application restarts

---

## 📈 Task 5: Explore Gauge Metrics

### 🔍 Subtask 5.1: Query Gauge Metrics

Execute these gauge queries:

**Current CPU Usage:**
```promql
cpu_usage_percent
```

**Memory Usage Over Time:**
```promql
memory_usage_bytes
```

**Active Connections:**
```promql
active_connections
```

**Average CPU Usage:**
```promql
avg_over_time(cpu_usage_percent[10m])
```

**Maximum Memory Usage:**
```promql
max_over_time(memory_usage_bytes[10m])
```

### 🧠 Subtask 5.2: Analyze Gauge Behavior

Observe that:

- ✅ Gauges can increase and decrease
- ✅ Values represent current state
- ✅ Useful for resource utilization metrics

---

## 📊 Task 6: Explore Histogram Metrics

### 🔍 Subtask 6.1: Query Histogram Metrics

Execute these histogram queries:

**Request Duration Buckets:**
```promql
http_request_duration_seconds_bucket
```

**95th Percentile Response Time:**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**50th Percentile (Median) Response Time:**
```promql
histogram_quantile(0.5, rate(http_request_duration_seconds_bucket[5m]))
```

**Average Request Duration:**
```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

**Requests per Second:**
```promql
rate(http_request_duration_seconds_count[5m])
```

### 📦 Subtask 6.2: Analyze Response Size Histogram

**Response Size Distribution:**
```promql
http_response_size_bytes_bucket
```

**Large Response Rate (>1KB):**
```promql
rate(http_response_size_bytes_bucket{le="+Inf"}[5m]) - rate(http_response_size_bytes_bucket{le="1000"}[5m])
```

### 🧠 Subtask 6.3: Analyze Histogram Behavior

Observe that:

- ✅ Histograms create multiple time series (`_bucket`, `_sum`, `_count`)
- ✅ Buckets are cumulative (`le="1.0"` includes all values ≤ 1.0)
- ✅ Quantiles can be calculated from bucket data

---

## 🧮 Task 7: Explore Summary Metrics

### 🔍 Subtask 7.1: Query Summary Metrics

Execute these summary queries:

**Request Latency Quantiles:**
```promql
http_request_latency_seconds
```

**95th Percentile Latency:**
```promql
http_request_latency_seconds{quantile="0.95"}
```

**50th Percentile Latency:**
```promql
http_request_latency_seconds{quantile="0.5"}
```

**Average Processing Time:**
```promql
rate(data_processing_seconds_sum[5m]) / rate(data_processing_seconds_count[5m])
```

**Processing Rate:**
```promql
rate(data_processing_seconds_count[5m])
```

### ⚖️ Subtask 7.2: Compare Summary vs Histogram

Create a comparison query:

**Summary 95th Percentile:**
```promql
http_request_latency_seconds{quantile="0.95"}
```

**Histogram 95th Percentile:**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### 🧠 Subtask 7.3: Analyze Summary Behavior

Observe that:

- ✅ Summaries pre-calculate quantiles on the client side
- ✅ Summary quantiles cannot be aggregated across instances
- ✅ Summaries are more accurate for single-instance quantiles

---

## 🔬 Task 8: Advanced Metric Analysis

### 🧪 Subtask 8.1: Create Complex Queries

**Request Rate by Endpoint:**
```promql
sum by (endpoint) (rate(http_requests_total[5m]))
```

**Error Percentage:**
```promql
(sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m]))) * 100
```

**Resource Utilization Correlation:**
```promql
cpu_usage_percent and memory_usage_bytes
```

**SLA Compliance (requests under 1 second):**
```promql
(rate(http_request_duration_seconds_bucket{le="1.0"}[5m]) / rate(http_request_duration_seconds_count[5m])) * 100
```

### 🚨 Subtask 8.2: Create Alerting Rules

Create an alerting rules file:

```yaml
cat > alert_rules.yml << 'EOF'
groups:
  - name: sample_app_alerts
    rules:
      - alert: HighErrorRate
        expr: (rate(http_errors_total[5m]) / rate(http_requests_total[5m])) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"
      
      - alert: SlowRequests
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Slow request response time"
          description: "95th percentile latency is {{ $value }}s"
EOF
```

---

## ⚖️ Task 9: Metric Type Comparison and Best Practices

### 📋 Subtask 9.1: Create Comparison Dashboard

Create queries that demonstrate when to use each metric type:

| Metric Type | Use For |
|-------------|---------|
| 🔢 **Counters** | Request counts, error counts, bytes transferred, events processed |
| 📈 **Gauges** | CPU/memory usage, active connections, queue sizes, temperature readings |
| 📊 **Histograms** | Request durations, response sizes, batch processing times, when you need aggregatable quantiles |
| 🧮 **Summaries** | Client-side quantile calculations, when you don't need cross-instance aggregation, pre-calculated percentiles |

### ⚡ Subtask 9.2: Performance Analysis

Compare the performance characteristics:

**Check Metric Cardinality:**
```promql
{__name__=~"http_.*"}
```

**Count Time Series:**
```promql
count by (__name__) ({__name__=~".*"})
```

---

## ✅ Task 10: Cleanup and Verification

### 🔎 Subtask 10.1: Verify All Metric Types

Run a final verification of all metric types:

```bash
# ✅ Check if all metrics are being collected
curl -s http://localhost:8000/metrics | grep -E "(http_requests_total|cpu_usage_percent|http_request_duration_seconds|http_request_latency_seconds)"
```

### 📄 Subtask 10.2: Export Sample Queries

Create a reference file with all the queries used:

```bash
cat > metric_queries_reference.txt << 'EOF'
# Counter Queries
http_requests_total
rate(http_requests_total[5m])
sum by (endpoint) (http_requests_total)

# Gauge Queries
cpu_usage_percent
avg_over_time(cpu_usage_percent[10m])
max_over_time(memory_usage_bytes[10m])

# Histogram Queries
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Summary Queries
http_request_latency_seconds{quantile="0.95"}
rate(data_processing_seconds_count[5m])

# Complex Queries
(sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m]))) * 100
(rate(http_request_duration_seconds_bucket{le="1.0"}[5m]) / rate(http_request_duration_seconds_count[5m])) * 100
EOF
```

### 🛑 Subtask 10.3: Stop Services

Stop all running services:

```bash
# Stop traffic generation (Ctrl+C in the traffic terminal)
# Stop sample application (Ctrl+C in the app terminal)
# Stop Prometheus (Ctrl+C in the Prometheus terminal)
```

---

## 🛠️ Troubleshooting

<details>
<summary><strong>Prometheus not scraping metrics</strong></summary>

- Check if the sample application is running on port 8000
- Verify the `/metrics` endpoint is accessible: `curl http://localhost:8000/metrics`
- Check the Prometheus targets page: `http://localhost:9090/targets`

</details>

<details>
<summary><strong>No data in queries</strong></summary>

- Ensure the traffic generation script has been running
- Check the time range in the Prometheus web interface
- Verify metric names are spelled correctly

</details>

<details>
<summary><strong>Python dependencies not found</strong></summary>

- Install missing packages: `pip3 install prometheus_client flask`
- Check Python version: `python3 --version`

</details>

<details>
<summary><strong>Permission denied errors</strong></summary>

- Ensure proper file permissions: `chmod +x script_name.sh`
- Check directory ownership: `ls -la`

</details>

---

## 🏁 Conclusion

In this comprehensive lab, you have successfully:

### 🎯 Key Accomplishments

- ✅ Explored all four Prometheus metric types: counters, gauges, histograms, and summaries
- ✅ Created a functional sample application that demonstrates each metric type in realistic scenarios
- ✅ Written and executed PromQL queries to extract meaningful insights from each metric type
- ✅ Understood the behavioral differences between metric types and their appropriate use cases
- ✅ Implemented advanced monitoring concepts including rate calculations, quantile analysis, and alerting rules

### 🌍 Real-World Applications

- **Counter metrics** are essential for tracking cumulative values like request counts and errors — they only increase and are perfect for calculating rates of change.
- **Gauge metrics** represent point-in-time values that can fluctuate, making them ideal for resource utilization monitoring like CPU and memory usage.
- **Histogram metrics** provide detailed distribution analysis with pre-defined buckets, enabling accurate quantile calculations and aggregation across multiple instances.
- **Summary metrics** offer client-side quantile calculations with lower storage overhead but cannot be aggregated across instances.

This hands-on experience with Prometheus metric types provides the foundation for implementing effective monitoring strategies in production environments. Understanding when and how to use each metric type is crucial for building robust observability systems that provide actionable insights into application and infrastructure performance. The skills developed in this lab directly apply to real-world monitoring scenarios where choosing the appropriate metric type can significantly impact the effectiveness of your monitoring and alerting systems.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al%20Nafi-Cybersecurity%20Training-blueviolet?style=for-the-badge)

</div>
