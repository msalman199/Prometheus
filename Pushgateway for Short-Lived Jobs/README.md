# 🚀 Prometheus Pushgateway for Short-Lived Jobs

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus\&logoColor=white)
![Pushgateway](https://img.shields.io/badge/Pushgateway-Metrics-E6522C?logo=prometheus\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?logo=ubuntu\&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?logo=gnubash\&logoColor=white)
![cURL](https://img.shields.io/badge/cURL-HTTP_API-073551?logo=curl\&logoColor=white)
![systemd](https://img.shields.io/badge/systemd-Service_Management-000000?logo=linux\&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-Querying-E6522C?logo=prometheus\&logoColor=white)
![Python](https://img.shields.io/badge/Python-Validation-3776AB?logo=python\&logoColor=white)
![Monitoring](https://img.shields.io/badge/Observability-Monitoring-blue)
![License](https://img.shields.io/badge/License-Lab-green)

> 📊 A hands-on monitoring lab demonstrating how **Prometheus Pushgateway** can collect metrics from short-lived, batch, scheduled, and ephemeral jobs.

---

## 📌 Table of Contents

* [🎯 Objectives](#-objectives)
* [📚 Prerequisites](#-prerequisites)
* [🛠️ Technologies Used](#️-technologies-used)
* [🏗️ Architecture](#️-architecture)
* [🌐 How Pushgateway Works](#-how-pushgateway-works)
* [🧪 Lab Environment](#-lab-environment)
* [⚙️ Task 1 - Install and Configure Pushgateway and Prometheus](#️-task-1---install-and-configure-pushgateway-and-prometheus)
* [📦 Task 2 - Create Short-Lived Jobs](#-task-2---create-short-lived-jobs)
* [🚨 Task 3 - Alerting and Health Checks](#-task-3---alerting-and-health-checks)
* [💾 Persistence Validation](#-persistence-validation)
* [🧹 Cleanup](#-cleanup)
* [✅ Expected Outcomes](#-expected-outcomes)
* [🔍 Troubleshooting](#-troubleshooting)
* [📈 Key Learning Points](#-key-learning-points)
* [🏁 Conclusion](#-conclusion)

---

# 🎯 Objectives

By completing this lab, you will learn how to:

* 🔹 Understand Prometheus Pushgateway and its use cases
* 🔹 Install Pushgateway on a Linux system
* 🔹 Configure Pushgateway as a `systemd` service
* 🔹 Install and configure Prometheus
* 🔹 Configure Prometheus to scrape Pushgateway
* 🔹 Create short-lived Bash jobs
* 🔹 Push metrics using the Prometheus text exposition format
* 🔹 Query pushed metrics using PromQL
* 🔹 Create Prometheus alerting rules
* 🔹 Monitor batch-job failures and error rates
* 🔹 Detect stale batch jobs
* 🔹 Validate Pushgateway metric persistence
* 🔹 Manage the complete metric lifecycle: **Push → Scrape → Query → Alert → Delete**

---

# 📚 Prerequisites

Before starting, you should have:

* 🐧 Basic Linux command-line knowledge
* 📊 Basic understanding of Prometheus
* 🔧 Basic Bash scripting knowledge
* 🌐 Understanding of HTTP requests and REST APIs
* 🔎 Familiarity with PromQL
* ⏱️ Understanding of cron/batch jobs

Recommended tools:

```bash
sudo apt update
sudo apt install -y wget curl tar bc python3
```

Verify:

```bash
wget --version
curl --version
tar --version
bc --version
python3 --version
```

---

# 🛠️ Technologies Used

| Technology                 | Purpose                                |
| -------------------------- | -------------------------------------- |
| 🔥 Prometheus              | Metrics collection and monitoring      |
| 🚀 Pushgateway             | Receives metrics from short-lived jobs |
| 🐧 Linux                   | Lab operating system                   |
| 🐚 Bash                    | Batch-job automation                   |
| 🌐 cURL                    | HTTP metric submission and API testing |
| ⚙️ systemd                 | Service management                     |
| 🐍 Python                  | JSON/API response validation           |
| 📐 PromQL                  | Querying Prometheus metrics            |
| ⏱️ Cron-style Jobs         | Scheduled workload simulation          |
| 💾 Pushgateway Persistence | Metric persistence across restarts     |

---

# 🏗️ Architecture

```text
                    ┌──────────────────────────┐
                    │      Short-Lived Jobs    │
                    │                          │
                    │  ┌────────────────────┐  │
                    │  │ Simple Batch Job   │  │
                    │  ├────────────────────┤  │
                    │  │ Advanced Batch Job │  │
                    │  ├────────────────────┤  │
                    │  │ Maintenance Job    │  │
                    │  └────────────────────┘  │
                    └────────────┬─────────────┘
                                 │
                                 │ HTTP POST
                                 │ /metrics/job/...
                                 ▼
                    ┌──────────────────────────┐
                    │     Pushgateway :9091   │
                    │                          │
                    │   Metric Storage         │
                    │   Persistence Database   │
                    └────────────┬─────────────┘
                                 │
                                 │ Prometheus Scrape
                                 │ Every 15 seconds
                                 ▼
                    ┌──────────────────────────┐
                    │     Prometheus :9090     │
                    │                          │
                    │ • Time-Series Database   │
                    │ • PromQL                 │
                    │ • Alert Rules            │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Monitoring/API      │
                    │                          │
                    │ Queries • Rules • Alerts │
                    └──────────────────────────┘
```

---

# 🌐 How Pushgateway Works

Normally, Prometheus uses a **pull model**:

```text
Prometheus ──────► Application
             scrape
```

This works well for long-running applications.

Short-lived jobs may finish before Prometheus gets a chance to scrape them.

Pushgateway provides an intermediary:

```text
Batch Job
    │
    │ Push metrics
    ▼
Pushgateway
    │
    │ Prometheus scrape
    ▼
Prometheus
```

### Typical Use Cases

* 🧹 Scheduled cleanup jobs
* 💾 Backup scripts
* 📦 ETL processes
* 🔄 Data-processing jobs
* 🛠️ Maintenance scripts
* ⏰ Cron jobs
* 🧪 One-time automation tasks

> ⚠️ Pushgateway should not normally be used as a replacement for Prometheus scraping long-running applications. It is primarily useful when a job's lifetime is too short for normal scraping.

---

# 🧪 Lab Environment

This lab can be performed on an **Al Nafi Linux cloud machine**.

The environment starts with a basic Linux system, and the required monitoring components are installed manually.

Default ports:

| Service        |   Port |
| -------------- | -----: |
| 🔥 Prometheus  | `9090` |
| 🚀 Pushgateway | `9091` |

---

# ⚙️ Task 1 — Install and Configure Pushgateway and Prometheus

## 🔹 Step 1.1 — Download Pushgateway

Create the working directory:

```bash
mkdir -p ~/pushgateway
cd ~/pushgateway
```

Download Pushgateway:

```bash
wget https://github.com/prometheus/pushgateway/releases/download/v1.6.2/pushgateway-1.6.2.linux-amd64.tar.gz
```

Extract:

```bash
tar xzf pushgateway-1.6.2.linux-amd64.tar.gz
```

Move it:

```bash
sudo mv pushgateway-1.6.2.linux-amd64 /opt/pushgateway
```

Create a symbolic link:

```bash
sudo ln -sf /opt/pushgateway/pushgateway /usr/local/bin/pushgateway
```

---

## 👤 Step 1.2 — Create Pushgateway User

```bash
sudo useradd --no-create-home --shell /bin/false pushgateway || true
```

Set ownership:

```bash
sudo chown -R pushgateway:pushgateway /opt/pushgateway
```

---

## ⚙️ Step 1.3 — Create Pushgateway systemd Service

```bash
sudo tee /etc/systemd/system/pushgateway.service > /dev/null <<EOF
[Unit]
Description=Prometheus Pushgateway
Wants=network-online.target
After=network-online.target

[Service]
User=pushgateway
Group=pushgateway
Type=simple
ExecStart=/usr/local/bin/pushgateway \
    --web.listen-address=0.0.0.0:9091 \
    --web.telemetry-path=/metrics \
    --persistence.file=/opt/pushgateway/pushgateway.db \
    --persistence.interval=5m \
    --log.level=info

SyslogIdentifier=pushgateway
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable Pushgateway:

```bash
sudo systemctl enable pushgateway
```

Start it:

```bash
sudo systemctl start pushgateway
```

Check status:

```bash
sudo systemctl status pushgateway --no-pager
```

---

## 🔎 Step 1.4 — Verify Pushgateway

```bash
curl http://localhost:9091/metrics | head -n 20
```

Health check:

```bash
curl http://localhost:9091/-/healthy
```

Expected:

```text
OK
```

---

# 🔥 Step 1.5 — Install Prometheus

Create the working directory:

```bash
mkdir -p ~/prometheus
cd ~/prometheus
```

Download:

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
```

Extract:

```bash
tar xzf prometheus-2.45.0.linux-amd64.tar.gz
```

Move:

```bash
sudo mv prometheus-2.45.0.linux-amd64 /opt/prometheus
```

Create symbolic links:

```bash
sudo ln -sf /opt/prometheus/prometheus /usr/local/bin/prometheus
sudo ln -sf /opt/prometheus/promtool /usr/local/bin/promtool
```

Create required directories:

```bash
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus
sudo mkdir -p /etc/prometheus/rules
```

Create Prometheus user:

```bash
sudo useradd --no-create-home --shell /bin/false prometheus || true
```

Set ownership:

```bash
sudo chown prometheus:prometheus /var/lib/prometheus
sudo chown -R prometheus:prometheus /opt/prometheus
```

---

# 📝 Step 1.6 — Configure Prometheus

Create configuration:

```bash
sudo tee /etc/prometheus/prometheus.yml > /dev/null <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['localhost:9091']
EOF
```

---

# ⚙️ Step 1.7 — Create Prometheus systemd Service

```bash
sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
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
    --web.console.templates=/opt/prometheus/consoles \
    --web.console.libraries=/opt/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

SyslogIdentifier=prometheus
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

Set ownership:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus
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
sudo systemctl status prometheus --no-pager
```

---

# ✅ Step 1.8 — Validate Both Services

Prometheus:

```bash
curl -s http://localhost:9090/-/healthy
```

Pushgateway:

```bash
curl -s http://localhost:9091/-/healthy
```

Check Prometheus targets:

```bash
curl -s http://localhost:9090/api/v1/targets
```

Look for:

```text
"job": "pushgateway"
```

and:

```text
"health": "up"
```

### 🎯 Deliverable

```text
Prometheus       → Healthy
Pushgateway      → Healthy
Pushgateway      → UP in Prometheus targets
```

---

# 📦 Task 2 — Create Short-Lived Jobs

## 📁 Step 2.1 — Create Batch Job Directory

```bash
mkdir -p ~/batch-jobs
cd ~/batch-jobs
```

---

# 🟢 Step 2.2 — Simple Batch Job

Create:

```bash
tee batch_job_simple.sh > /dev/null <<'EOF'
#!/bin/bash
set -euo pipefail

JOB_NAME="data_processing_job"
INSTANCE="batch-server-01"
PUSHGATEWAY_URL="http://localhost:9091"

echo "Starting batch job: $JOB_NAME"

START_TIME=$(date +%s)

echo "Processing data..."
sleep 3

RECORDS_PROCESSED=1250
ERRORS_ENCOUNTERED=3

END_TIME=$(date +%s)
JOB_DURATION=$((END_TIME - START_TIME))

echo "Job completed."
echo "Processed: $RECORDS_PROCESSED records"
echo "Errors: $ERRORS_ENCOUNTERED"

cat <<METRICS | curl --silent --data-binary @- \
${PUSHGATEWAY_URL}/metrics/job/${JOB_NAME}/instance/${INSTANCE}

# HELP batch_job_records_processed_total Total number of records processed
# TYPE batch_job_records_processed_total counter
batch_job_records_processed_total $RECORDS_PROCESSED

# HELP batch_job_errors_total Total number of errors encountered
# TYPE batch_job_errors_total counter
batch_job_errors_total $ERRORS_ENCOUNTERED

# HELP batch_job_duration_seconds Time taken to complete the job
# TYPE batch_job_duration_seconds gauge
batch_job_duration_seconds $JOB_DURATION

# HELP batch_job_last_success_unixtime Last time the job completed successfully
# TYPE batch_job_last_success_unixtime gauge
batch_job_last_success_unixtime $END_TIME

METRICS

echo "Metrics pushed to Pushgateway successfully."
EOF
```

Make executable:

```bash
chmod +x batch_job_simple.sh
```

---

# 🔵 Step 2.3 — Advanced Batch Job

Create:

```bash
tee batch_job_advanced.sh > /dev/null <<'EOF'
#!/bin/bash

JOB_NAME="advanced_data_processor"
INSTANCE=$(hostname)
PUSHGATEWAY_URL="http://localhost:9091"
LOG_FILE="/tmp/${JOB_NAME}.log"

push_metrics() {
    local job_status=$1
    local records_processed=$2
    local errors_count=$3
    local duration=$4
    local timestamp=$5

    cat <<METRICS | curl --silent --data-binary @- \
${PUSHGATEWAY_URL}/metrics/job/${JOB_NAME}/instance/${INSTANCE}

# HELP batch_job_records_processed_total Total records processed
# TYPE batch_job_records_processed_total counter
batch_job_records_processed_total $records_processed

# HELP batch_job_errors_total Total errors encountered
# TYPE batch_job_errors_total counter
batch_job_errors_total $errors_count

# HELP batch_job_duration_seconds Duration of job execution
# TYPE batch_job_duration_seconds gauge
batch_job_duration_seconds $duration

# HELP batch_job_status Job completion status
# TYPE batch_job_status gauge
batch_job_status $job_status

# HELP batch_job_last_run_timestamp Unix timestamp of last execution
# TYPE batch_job_last_run_timestamp gauge
batch_job_last_run_timestamp $timestamp

METRICS
}

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

main() {
    local start_time
    start_time=$(date +%s)

    local records_processed=0
    local errors_count=0
    local job_status=1

    log_message "Starting advanced batch job: $JOB_NAME"

    for i in $(seq 1 50); do
        sleep 0.05

        if [ $((RANDOM % 20)) -eq 0 ]; then
            errors_count=$((errors_count + 1))
            log_message "Error processing record $i"
        else
            records_processed=$((records_processed + 1))
        fi
    done

    local end_time
    end_time=$(date +%s)

    local duration=$((end_time - start_time))

    if [ "$errors_count" -gt 10 ]; then
        job_status=0
        log_message "Job failed: too many errors ($errors_count)"
    else
        log_message "Job completed successfully"
    fi

    push_metrics \
        "$job_status" \
        "$records_processed" \
        "$errors_count" \
        "$duration" \
        "$end_time"

    log_message "Metrics pushed to Pushgateway"
}

main
EOF
```

Make executable:

```bash
chmod +x batch_job_advanced.sh
```

---

# 🟣 Step 2.4 — Scheduled Maintenance Job

Create:

```bash
tee scheduled_job.sh > /dev/null <<'EOF'
#!/bin/bash

JOB_NAME="system_maintenance"
INSTANCE=$(hostname)
PUSHGATEWAY_URL="http://localhost:9091"

echo "Running scheduled maintenance job..."

TASKS=(
    "cleanup_temp_files"
    "rotate_logs"
    "update_cache"
    "backup_config"
    "check_disk_space"
)

TOTAL_TASKS=${#TASKS[@]}
COMPLETED_TASKS=0
FAILED_TASKS=0
START_TIME=$(date +%s)

for task in "${TASKS[@]}"; do
    echo "Executing task: $task"

    sleep 1

    if [ $((RANDOM % 10)) -lt 9 ]; then
        echo "Task $task completed successfully"
        COMPLETED_TASKS=$((COMPLETED_TASKS + 1))
    else
        echo "Task $task failed"
        FAILED_TASKS=$((FAILED_TASKS + 1))
    fi
done

END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))

SUCCESS_RATE=$(echo \
"scale=2; $COMPLETED_TASKS * 100 / $TOTAL_TASKS" | bc -l)

cat <<METRICS | curl --silent --data-binary @- \
${PUSHGATEWAY_URL}/metrics/job/${JOB_NAME}/instance/${INSTANCE}

# HELP maintenance_tasks_total Total maintenance tasks
# TYPE maintenance_tasks_total gauge
maintenance_tasks_total $TOTAL_TASKS

# HELP maintenance_tasks_completed_total Completed maintenance tasks
# TYPE maintenance_tasks_completed_total counter
maintenance_tasks_completed_total $COMPLETED_TASKS

# HELP maintenance_tasks_failed_total Failed maintenance tasks
# TYPE maintenance_tasks_failed_total counter
maintenance_tasks_failed_total $FAILED_TASKS

# HELP maintenance_success_rate_percent Maintenance success rate
# TYPE maintenance_success_rate_percent gauge
maintenance_success_rate_percent $SUCCESS_RATE

# HELP maintenance_duration_seconds Maintenance duration
# TYPE maintenance_duration_seconds gauge
maintenance_duration_seconds $DURATION

# HELP maintenance_last_run_timestamp Last execution timestamp
# TYPE maintenance_last_run_timestamp gauge
maintenance_last_run_timestamp $END_TIME

METRICS

echo "Scheduled maintenance completed."
echo "Metrics pushed to Pushgateway."
EOF
```

Make executable:

```bash
chmod +x scheduled_job.sh
```

---

# ▶️ Step 2.5 — Execute All Jobs

```bash
cd ~/batch-jobs

./batch_job_simple.sh
./batch_job_advanced.sh
./scheduled_job.sh
```

---

# 🔎 Step 2.6 — Verify Metrics in Pushgateway

```bash
curl -s http://localhost:9091/metrics | \
grep -E "batch_job|maintenance"
```

Expected metrics include:

```text
batch_job_records_processed_total
batch_job_errors_total
batch_job_duration_seconds
batch_job_status
maintenance_tasks_completed_total
maintenance_tasks_failed_total
maintenance_success_rate_percent
```

---

# 📊 Step 2.7 — Verify Metrics in Prometheus

Wait at least one scrape interval:

```text
15 seconds
```

Query:

```bash
curl -s \
"http://localhost:9090/api/v1/query?query=batch_job_records_processed_total" \
| python3 -m json.tool
```

Query maintenance metrics:

```bash
curl -s \
"http://localhost:9090/api/v1/query?query=maintenance_tasks_completed_total" \
| python3 -m json.tool
```

### 🎯 Deliverable

The API response should contain:

```json
"result": [
    ...
]
```

and the metrics should include the expected:

```text
job
instance
```

labels.

---

# 🚨 Task 3 — Alerting and Health Checks

## 📝 Step 3.1 — Create Prometheus Alert Rules

Create:

```bash
sudo tee /etc/prometheus/rules/batch_jobs.yml > /dev/null <<'EOF'
groups:
  - name: batch_jobs

    rules:

      - alert: BatchJobFailed
        expr: batch_job_status == 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Batch job {{ $labels.job }} failed"
          description: "Batch job {{ $labels.job }} on instance {{ $labels.instance }} has failed"

      - alert: BatchJobHighErrorRate
        expr: batch_job_errors_total / batch_job_records_processed_total > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in batch job {{ $labels.job }}"
          description: "Batch job {{ $labels.job }} has an error rate above 10 percent"

      - alert: BatchJobNotRunRecently
        expr: time() - batch_job_last_success_unixtime > 86400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Batch job {{ $labels.job }} hasn't run recently"
          description: "Batch job {{ $labels.job }} last successful run was more than 24 hours ago"

      - alert: MaintenanceTasksFailed
        expr: maintenance_tasks_failed_total > 0
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "Maintenance tasks failed"
          description: "{{ $value }} maintenance tasks failed on {{ $labels.instance }}"
EOF
```

Set ownership:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus
```

---

# 🔍 Step 3.2 — Validate Alert Rules

```bash
promtool check rules /etc/prometheus/rules/batch_jobs.yml
```

Expected:

```text
SUCCESS
```

Reload Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

Verify:

```bash
curl -s \
http://localhost:9090/api/v1/rules \
| python3 -m json.tool
```

Look for:

```text
batch_jobs
```

---

# ❤️ Step 3.3 — Create Health Check Script

Create:

```bash
cd ~/batch-jobs

tee health_check.sh > /dev/null <<'EOF'
#!/bin/bash

PUSHGATEWAY_URL="http://localhost:9091"
PROMETHEUS_URL="http://localhost:9090"

echo "============================================"
echo " Pushgateway & Prometheus Health Check"
echo "============================================"

if curl -s "${PUSHGATEWAY_URL}/-/healthy" > /dev/null; then
    echo "1. Pushgateway: OK"
else
    echo "1. Pushgateway: FAILED"
fi

if curl -s "${PROMETHEUS_URL}/-/healthy" > /dev/null; then
    echo "2. Prometheus: OK"
else
    echo "2. Prometheus: FAILED"
fi

SCRAPE_RESULT=$(
    curl -s \
    "${PROMETHEUS_URL}/api/v1/query?query=up{job=\"pushgateway\"}" |
    python3 -c "
import sys, json
data=json.load(sys.stdin)
result=data['data']['result']
print(result[0]['value'][1] if result else '0')
" 2>/dev/null
)

if [ "$SCRAPE_RESULT" = "1" ]; then
    echo "3. Prometheus is scraping Pushgateway: OK"
else
    echo "3. Prometheus is scraping Pushgateway: FAILED"
fi

RULES_RESULT=$(
    curl -s "${PROMETHEUS_URL}/api/v1/rules" |
    python3 -c "
import sys, json
data=json.load(sys.stdin)
print(len(data['data']['groups']))
" 2>/dev/null
)

echo "4. Loaded rule groups: ${RULES_RESULT:-0}"

ALERTS_RESULT=$(
    curl -s "${PROMETHEUS_URL}/api/v1/alerts" |
    python3 -c "
import sys, json
data=json.load(sys.stdin)
alerts=[
    x for x in data['data']['alerts']
    if x['state']=='firing'
]
print(len(alerts))
" 2>/dev/null
)

echo "5. Firing alerts: ${ALERTS_RESULT:-0}"

echo "============================================"
echo " Health check completed."
echo "============================================"
EOF
```

Make executable:

```bash
chmod +x health_check.sh
```

Run:

```bash
./health_check.sh
```

Expected:

```text
1. Pushgateway: OK
2. Prometheus: OK
3. Prometheus is scraping Pushgateway: OK
4. Loaded rule groups: 1
5. Firing alerts: 0
```

---

# 💾 Persistence Validation

Push a temporary metric:

```bash
curl --data-binary @- \
http://localhost:9091/metrics/job/test_persistence/instance/test <<EOF

# HELP test_metric A test metric for persistence validation
# TYPE test_metric gauge
test_metric 42

EOF
```

Verify:

```bash
echo "Before restart:"
curl -s http://localhost:9091/metrics | grep test_metric
```

Expected:

```text
test_metric{instance="test",job="test_persistence"} 42
```

---

## 🔄 Restart Pushgateway

```bash
sudo systemctl restart pushgateway
```

Wait:

```bash
sleep 5
```

Check again:

```bash
echo "After restart:"
curl -s http://localhost:9091/metrics | grep test_metric
```

Expected:

```text
test_metric{instance="test",job="test_persistence"} 42
```

This confirms that the configured persistence file preserves pushed metrics across a Pushgateway process restart.

---

# 🗑️ Delete Test Metric

```bash
curl -X DELETE \
http://localhost:9091/metrics/job/test_persistence/instance/test
```

Verify:

```bash
curl -s http://localhost:9091/metrics | \
grep test_metric || echo "No test_metric found (expected)"
```

---

# 🧹 Cleanup

Pushgateway retains pushed metrics until they are explicitly removed.

Delete the lab metrics:

```bash
curl -X DELETE \
http://localhost:9091/metrics/job/data_processing_job/instance/batch-server-01
```

```bash
curl -X DELETE \
http://localhost:9091/metrics/job/advanced_data_processor
```

```bash
curl -X DELETE \
http://localhost:9091/metrics/job/system_maintenance
```

Verify:

```bash
curl -s http://localhost:9091/metrics | \
grep -E "batch_job|maintenance" || \
echo "All batch and maintenance metrics removed"
```

Expected:

```text
All batch and maintenance metrics removed
```

---

# 🔎 Verify Prometheus Cleanup

Wait for the next scrape interval and run:

```bash
curl -s \
"http://localhost:9090/api/v1/query?query=batch_job_records_processed_total" \
| python3 -m json.tool
```

Expected:

```json
"result": []
```

This confirms that the stale metrics were removed from Pushgateway and are no longer being scraped into new Prometheus samples.

---

# 📊 Monitoring Flow

The completed workflow is:

```text
┌──────────────────┐
│ Short-Lived Job  │
└────────┬─────────┘
         │
         │ Push Metrics
         ▼
┌──────────────────┐
│   Pushgateway    │
│     :9091        │
└────────┬─────────┘
         │
         │ Scrape
         ▼
┌──────────────────┐
│    Prometheus    │
│     :9090        │
└────────┬─────────┘
         │
         ├──────────────► PromQL Queries
         │
         ├──────────────► Alert Rules
         │
         └──────────────► Monitoring
```

---

# 🚨 Alerting Model

| Alert                    | Condition                 | Severity    |
| ------------------------ | ------------------------- | ----------- |
| `BatchJobFailed`         | Job status is `0`         | 🔴 Critical |
| `BatchJobHighErrorRate`  | Error rate > 10%          | 🟡 Warning  |
| `BatchJobNotRunRecently` | No successful run for 24h | 🟡 Warning  |
| `MaintenanceTasksFailed` | One or more tasks failed  | 🟡 Warning  |

---

# 🔐 Operational Considerations

## 1️⃣ Avoid Unbounded Labels

Avoid dynamic labels such as:

```text
request_id
timestamp
random_id
```

These can create excessive time-series cardinality.

Prefer stable labels:

```text
job
instance
environment
```

---

## 2️⃣ Clean Up Stale Metrics

Pushgateway does not automatically know whether a batch job is still active.

Therefore:

```text
Push
 ↓
Scrape
 ↓
Job finishes
 ↓
Metric remains
```

Metrics should be deleted when they are no longer meaningful.

---

## 3️⃣ Use Persistence Carefully

Persistence allows metrics to survive Pushgateway restarts:

```text
Pushgateway
     │
     ▼
pushgateway.db
```

This improves resilience but also makes stale-metric management important.

---

# 🛠️ Troubleshooting

## ❌ Pushgateway is not running

Check:

```bash
sudo systemctl status pushgateway
```

View logs:

```bash
sudo journalctl -u pushgateway -n 50 --no-pager
```

Restart:

```bash
sudo systemctl restart pushgateway
```

---

## ❌ Prometheus cannot scrape Pushgateway

Check:

```bash
curl http://localhost:9091/metrics
```

Check Prometheus target:

```bash
curl -s \
http://localhost:9090/api/v1/targets \
| python3 -m json.tool
```

Check configuration:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Restart:

```bash
sudo systemctl restart prometheus
```

---

## ❌ Metrics are not appearing

First check Pushgateway:

```bash
curl -s http://localhost:9091/metrics | grep batch_job
```

If they exist, check Prometheus:

```bash
curl -s \
"http://localhost:9090/api/v1/query?query=batch_job_status" \
| python3 -m json.tool
```

Also confirm the scrape target:

```bash
curl -s \
"http://localhost:9090/api/v1/query?query=up{job=\"pushgateway\"}"
```

Expected:

```text
1
```

---

## ❌ Alert rules are not loading

Validate:

```bash
promtool check rules \
/etc/prometheus/rules/batch_jobs.yml
```

Then reload:

```bash
curl -X POST http://localhost:9090/-/reload
```

Verify:

```bash
curl -s \
http://localhost:9090/api/v1/rules \
| python3 -m json.tool
```

---

# 📋 Validation Checklist

* [ ] 🐧 Linux environment prepared
* [ ] 📦 Required packages installed
* [ ] 🚀 Pushgateway installed
* [ ] ⚙️ Pushgateway systemd service created
* [ ] ❤️ Pushgateway health verified
* [ ] 🔥 Prometheus installed
* [ ] 📝 Prometheus configured
* [ ] 🔗 Pushgateway scrape target configured
* [ ] 🟢 Pushgateway target reports `UP`
* [ ] 📦 Simple batch job created
* [ ] 🔵 Advanced batch job created
* [ ] 🟣 Maintenance job created
* [ ] 📤 Metrics pushed successfully
* [ ] 🔎 Metrics visible in Pushgateway
* [ ] 📊 Metrics visible in Prometheus
* [ ] 🚨 Alert rules loaded
* [ ] ❤️ Health-check script working
* [ ] 💾 Persistence tested
* [ ] 🗑️ Test metrics deleted
* [ ] 🧹 Stale batch metrics removed

---

# 📈 Key Learning Points

### 🔹 Pushgateway

Provides an intermediary for metrics generated by short-lived jobs.

### 🔹 Prometheus

Uses its normal pull-based scraping model to collect metrics from Pushgateway.

### 🔹 Metric Types

This lab demonstrates:

* Counters
* Gauges
* Status metrics
* Timestamps
* Duration metrics

### 🔹 PromQL

Prometheus queries allow operators to:

* Inspect job status
* Calculate error rates
* Detect stale executions
* Monitor maintenance failures

### 🔹 Persistence

Pushgateway can persist pushed metrics across process restarts.

### 🔹 Metric Lifecycle

A healthy operational model is:

```text
CREATE
  ↓
PUSH
  ↓
SCRAPE
  ↓
QUERY
  ↓
ALERT
  ↓
DELETE
```

---

# 🎯 Expected Outcomes

After completing this lab, you should have:

```text
✅ Prometheus running on :9090
✅ Pushgateway running on :9091
✅ Pushgateway configured as a Prometheus target
✅ Three short-lived jobs
✅ Metrics successfully pushed
✅ Metrics successfully scraped
✅ PromQL queries returning results
✅ Alert rules configured
✅ Health-check automation
✅ Persistence successfully tested
✅ Stale metrics successfully cleaned
```

---

# 🏆 Skills Demonstrated

```text
🐧 Linux Administration
⚙️ systemd Service Management
🔥 Prometheus
🚀 Pushgateway
📊 Metrics Monitoring
📐 PromQL
🐚 Bash Automation
🌐 REST/HTTP APIs
🚨 Alerting
💾 Metrics Persistence
🧹 Monitoring Lifecycle Management
🔍 Observability
```

---

# 🏁 Conclusion

This hands-on lab demonstrates how **Prometheus Pushgateway** can be used to monitor short-lived and batch workloads that cannot reliably expose metrics long enough for normal Prometheus scraping.

You installed both **Prometheus and Pushgateway as systemd services**, configured Prometheus to scrape Pushgateway, and created three realistic Bash-based workloads representing data processing, advanced batch processing, and scheduled maintenance.

The lab then validated the complete monitoring pipeline:

```text
Short-Lived Job
      ↓
Pushgateway
      ↓
Prometheus
      ↓
PromQL
      ↓
Alerting
      ↓
Operational Cleanup
```

You also validated Pushgateway persistence across restarts and learned why stale metrics must be explicitly removed.

🎉 **Lab Completed — Prometheus Pushgateway for Short-Lived Jobs!**

---

## 👨‍💻 Author

**Hafiz Muhammad Salman**

☁️ Cloud DevOps Engineer
🐧 Linux Administrator
📊 Monitoring & Observability Enthusiast

---

## ⭐ If You Found This Useful

If this lab helped you understand Prometheus Pushgateway, consider giving the repository a ⭐ and sharing it with other DevOps and monitoring enthusiasts.

**Keep Learning • Keep Automating • Keep Monitoring 🚀**
