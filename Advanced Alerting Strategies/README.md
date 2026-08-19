# 🚨 Advanced Alerting Strategies

> **Production-Grade Prometheus & Alertmanager Monitoring Lab**

![Prometheus](https://img.shields.io/badge/Prometheus-v2.47.0-E6522C?logo=prometheus\&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-v0.26.0-E6522C?logo=prometheus\&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node_Exporter-v1.6.1-E6522C?logo=prometheus\&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-Linux-E95420?logo=ubuntu\&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws\&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python\&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-Alerting-4285F4)
![Systemd](https://img.shields.io/badge/systemd-Services-1F2937)

---

## 📌 Lab Overview

This lab demonstrates how to build an **advanced, production-style alerting pipeline** from scratch on an Ubuntu server.

The complete monitoring architecture consists of:

```text
                    ┌─────────────────────┐
                    │     Linux Host      │
                    │      Ubuntu         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Node Exporter    │
                    │      :9100          │
                    └──────────┬──────────┘
                               │ Metrics
                               ▼
                    ┌─────────────────────┐
                    │     Prometheus      │
                    │      :9090          │
                    │                     │
                    │ PromQL + Rules      │
                    └──────────┬──────────┘
                               │ Alerts
                               ▼
                    ┌─────────────────────┐
                    │    Alertmanager     │
                    │      :9093          │
                    │                     │
                    │ Routing + Inhibition│
                    └──────────┬──────────┘
                               │ Webhooks
                               ▼
                    ┌─────────────────────┐
                    │ Python Webhook      │
                    │      :5001          │
                    └─────────────────────┘
```

The lab covers:

* Prometheus installation and configuration
* Node Exporter installation
* Alertmanager installation
* systemd service management
* PromQL alert rules
* Multi-condition alerts
* Predictive disk alerts
* Alert severity classification
* Alertmanager routing
* Alert inhibition
* Python webhook notifications
* Controlled system load generation
* Alert lifecycle validation
* End-to-end alert testing

---

# 🎯 Objectives

By completing this lab, you will be able to:

* 🚀 Deploy Prometheus, Alertmanager, and Node Exporter on Ubuntu.
* 🔐 Run monitoring components using dedicated non-login service accounts.
* ⚙️ Configure all components as systemd services.
* 📊 Collect CPU, memory, filesystem, and system metrics.
* 🧠 Write advanced PromQL alert expressions.
* 🔥 Create CPU warning and critical alerts.
* 🧩 Build multi-condition composite alerts.
* 🔮 Create predictive alerts using `predict_linear`.
* 🧪 Generate controlled CPU and memory load with `stress-ng`.
* 🛣️ Design Alertmanager routing trees.
* 🚦 Route alerts according to severity and alert type.
* 🛑 Reduce alert noise with inhibition rules.
* 🐍 Build a Python webhook receiver.
* 🔄 Validate the complete alert lifecycle from Prometheus to Alertmanager.
* 🛠️ Troubleshoot common monitoring-stack failures.

---

# 🧰 Technology Stack

| Technology       |             Version | Purpose                                 |
| ---------------- | ------------------: | --------------------------------------- |
| 🟠 Prometheus    |              2.47.0 | Metrics collection and alert evaluation |
| 🟠 Alertmanager  |              0.26.0 | Alert routing, grouping, and inhibition |
| 🟠 Node Exporter |               1.6.1 | Linux system metrics                    |
| 🐧 Ubuntu        |          Base image | Lab operating system                    |
| ☁️ AWS EC2       | Al Nafi Environment | Lab infrastructure                      |
| 🐍 Python        |                 3.x | Webhook receiver                        |
| 🔥 stress-ng     |      System package | Controlled resource generation          |
| ⚙️ systemd       |              Native | Service management                      |
| 📜 PromQL        |              Native | Metric querying and alert expressions   |
| 🔧 promtool      |              2.47.0 | Configuration and rule validation       |
| 🛠️ amtool       |              0.26.0 | Alertmanager configuration validation   |

---

# 📋 Prerequisites

Before starting, you should have:

* Basic Linux command-line knowledge
* Experience navigating Linux filesystems
* Familiarity with `sudo`
* Basic systemd knowledge
* Basic YAML knowledge
* Understanding of CPU utilization
* Understanding of memory utilization
* Understanding of filesystem usage
* Basic Prometheus concepts
* Basic knowledge of HTTP and JSON

---

# ☁️ Lab Environment

The lab uses a dedicated **AWS EC2 Ubuntu instance provided by Al Nafi**.

All monitoring components are installed directly on the instance.

### Required Ports

|   Port | Component      | Purpose              |
| -----: | -------------- | -------------------- |
| `9090` | Prometheus     | Prometheus web/API   |
| `9100` | Node Exporter  | Linux metrics        |
| `9093` | Alertmanager   | Alertmanager web/API |
| `5001` | Python Webhook | Alert notifications  |

---

# 🏗️ Task 1 — Install and Verify Monitoring Stack

## 1.1 Update the System

🟢 **Technology: Ubuntu / APT**

```bash
sudo apt-get update -y
sudo apt-get install -y wget curl tar python3 stress-ng net-tools
```

Verify:

```bash
wget --version
curl --version
python3 --version
stress-ng --version
```

---

## 1.2 Install Prometheus

🟠 **Technology: Prometheus**

Download Prometheus `v2.47.0`:

```bash
cd /tmp

wget -fsSL \
https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz \
-O prometheus.tar.gz
```

Extract:

```bash
tar xzf prometheus.tar.gz
```

Create the dedicated service account:

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
```

Create directories:

```bash
sudo mkdir -p /opt/prometheus
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus
```

Copy Prometheus components:

```bash
sudo cp prometheus-2.47.0.linux-amd64/prometheus /opt/prometheus/
sudo cp prometheus-2.47.0.linux-amd64/promtool /opt/prometheus/
sudo cp -r prometheus-2.47.0.linux-amd64/consoles /opt/prometheus/
sudo cp -r prometheus-2.47.0.linux-amd64/console_libraries /opt/prometheus/
```

Set ownership:

```bash
sudo chown -R prometheus:prometheus \
/opt/prometheus \
/etc/prometheus \
/var/lib/prometheus
```

Verify:

```bash
/opt/prometheus/prometheus --version
/opt/prometheus/promtool --version
```

---

## 1.3 Install Node Exporter

🟠 **Technology: Node Exporter**

```bash
cd /tmp

wget -fsSL \
https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz \
-O node_exporter.tar.gz
```

Extract:

```bash
tar xzf node_exporter.tar.gz
```

Copy binary:

```bash
sudo cp \
node_exporter-1.6.1.linux-amd64/node_exporter \
/opt/prometheus/
```

Verify:

```bash
/opt/prometheus/node_exporter --version
```

---

## 1.4 Install Alertmanager

🟠 **Technology: Alertmanager**

```bash
cd /tmp

wget -fsSL \
https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz \
-O alertmanager.tar.gz
```

Extract:

```bash
tar xzf alertmanager.tar.gz
```

Create the service account:

```bash
sudo useradd --no-create-home --shell /bin/false alertmanager
```

Create directories:

```bash
sudo mkdir -p /opt/alertmanager
sudo mkdir -p /etc/alertmanager
sudo mkdir -p /var/lib/alertmanager
```

Copy binaries:

```bash
sudo cp alertmanager-0.26.0.linux-amd64/alertmanager /opt/alertmanager/
sudo cp alertmanager-0.26.0.linux-amd64/amtool /opt/alertmanager/
```

Set ownership:

```bash
sudo chown -R alertmanager:alertmanager \
/opt/alertmanager \
/etc/alertmanager \
/var/lib/alertmanager
```

Verify:

```bash
/opt/alertmanager/alertmanager --version
/opt/alertmanager/amtool --version
```

---

# ⚙️ 1.5 Create Node Exporter systemd Service

🟢 **Technology: systemd**

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
ExecStart=/opt/prometheus/node_exporter

[Install]
WantedBy=multi-user.target
EOF
```

---

# ⚙️ 1.6 Create Prometheus systemd Service

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
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/opt/prometheus/consoles \
    --web.console.libraries=/opt/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
EOF
```

---

# ⚙️ 1.7 Create Alertmanager systemd Service

```bash
sudo tee /etc/systemd/system/alertmanager.service <<'EOF'
[Unit]
Description=Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple
ExecStart=/opt/alertmanager/alertmanager \
    --config.file=/etc/alertmanager/alertmanager.yml \
    --storage.path=/var/lib/alertmanager/ \
    --web.listen-address=0.0.0.0:9093

[Install]
WantedBy=multi-user.target
EOF
```

---

# 📝 1.8 Configure Prometheus

```bash
sudo tee /etc/prometheus/prometheus.yml <<'EOF'
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

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
EOF
```

Set permissions:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
sudo chmod 640 /etc/prometheus/prometheus.yml
```

---

# 📝 1.9 Create Initial Alert Rules

```bash
sudo tee /etc/prometheus/alert_rules.yml <<'EOF'
groups: []
EOF

sudo chown prometheus:prometheus /etc/prometheus/alert_rules.yml
sudo chmod 640 /etc/prometheus/alert_rules.yml
```

---

# 📝 1.10 Configure Alertmanager

```bash
sudo tee /etc/alertmanager/alertmanager.yml <<'EOF'
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'webhook-default'

receivers:
  - name: 'webhook-default'
    webhook_configs:
      - url: 'http://localhost:5001/alerts'
        send_resolved: true

inhibit_rules: []
EOF

sudo chown alertmanager:alertmanager /etc/alertmanager/alertmanager.yml
sudo chmod 640 /etc/alertmanager/alertmanager.yml
```

---

# ▶️ 1.11 Start the Monitoring Stack

```bash
sudo systemctl daemon-reload

sudo systemctl enable --now \
node_exporter \
prometheus \
alertmanager
```

Check status:

```bash
sudo systemctl status node_exporter --no-pager
sudo systemctl status prometheus --no-pager
sudo systemctl status alertmanager --no-pager
```

Quick verification:

```bash
sudo systemctl is-active node_exporter prometheus alertmanager
```

Expected:

```text
active
active
active
```

---

# 🔍 1.12 Validate Configuration

Prometheus:

```bash
/opt/prometheus/promtool check config \
/etc/prometheus/prometheus.yml
```

Expected:

```text
SUCCESS
```

Alertmanager:

```bash
/opt/alertmanager/amtool check-config \
/etc/alertmanager/alertmanager.yml
```

---

# 🌐 1.13 Verify HTTP APIs

Prometheus:

```bash
curl -fsSL \
http://localhost:9090/api/v1/status/buildinfo \
| python3 -m json.tool
```

Node Exporter:

```bash
curl -fsSL \
http://localhost:9100/metrics | head -5
```

Alertmanager:

```bash
curl -fsSL \
http://localhost:9093/api/v1/status \
| python3 -m json.tool
```

Check targets:

```bash
curl -fsSL \
http://localhost:9090/api/v1/targets \
| python3 -m json.tool
```

Both `prometheus` and `node` should report:

```text
"health": "up"
```

---

# 🛠️ Troubleshooting — Task 1

### Prometheus will not start

```bash
sudo journalctl -u prometheus -n 30 --no-pager
```

Validate configuration:

```bash
/opt/prometheus/promtool check config \
/etc/prometheus/prometheus.yml
```

Check binary:

```bash
ls -lh /opt/prometheus/prometheus
```

### Node Exporter unavailable

```bash
sudo systemctl status node_exporter
sudo journalctl -u node_exporter -n 30 --no-pager
```

Check port:

```bash
sudo ss -tlnp | grep 9100
```

### Alertmanager unavailable

```bash
sudo systemctl status alertmanager
sudo journalctl -u alertmanager -n 30 --no-pager
```

---

# 🚨 Task 2 — Implement Multi-Condition Alerting Rules

## 2.1 CPU Warning Alert

The first rule detects CPU utilization above `80%` for two minutes.

```promql
100 - (
  avg by(instance) (
    irate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
) > 80
```

Configuration:

```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 2m
  labels:
    severity: warning
    service: system
```

---

# 🔥 2.2 Critical CPU Alert

CPU above `95%` for one minute:

```yaml
- alert: CriticalCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 95
  for: 1m
  labels:
    severity: critical
    service: system
```

---

# 🧩 2.3 Composite CPU + Memory Alert

The composite alert requires **both conditions** to be true.

```yaml
- alert: SystemUnderStress
  expr: |
    (
      100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 70
    )
    and
    (
      (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 70
    )
  for: 3m
  labels:
    severity: warning
    service: system
    alert_type: composite
```

The `and` operator is important because the alert does not fire when only one resource exceeds its threshold.

---

# 🔮 2.4 Predictive Disk Alert

Prometheus `predict_linear()` can estimate future filesystem availability based on historical data.

```yaml
- alert: DiskSpaceRunningOut
  expr: predict_linear(node_filesystem_avail_bytes{fstype!="tmpfs"}[6h], 86400) < 0
  for: 10m
  labels:
    severity: warning
    service: storage
    alert_type: predictive
```

The `86400` value represents:

```text
24 hours × 60 minutes × 60 seconds = 86400 seconds
```

---

# 📝 2.5 Complete Alert Rules File

```bash
sudo tee /etc/prometheus/alert_rules.yml <<'EOF'
groups:
  - name: cpu_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 2m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | printf \"%.1f\" }}%, above the 80% threshold for over 2 minutes."

      - alert: CriticalCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 95
        for: 1m
        labels:
          severity: critical
          service: system
        annotations:
          summary: "Critical CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | printf \"%.1f\" }}%, above the 95% threshold for over 1 minute."

  - name: composite_alerts
    rules:
      - alert: SystemUnderStress
        expr: |
          (
            100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 70
          )
          and
          (
            (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 70
          )
        for: 3m
        labels:
          severity: warning
          service: system
          alert_type: composite
        annotations:
          summary: "System under stress on {{ $labels.instance }}"
          description: "Both CPU and memory usage have exceeded 70% simultaneously for more than 3 minutes on {{ $labels.instance }}."

  - name: predictive_alerts
    rules:
      - alert: DiskSpaceRunningOut
        expr: predict_linear(node_filesystem_avail_bytes{fstype!="tmpfs"}[6h], 86400) < 0
        for: 10m
        labels:
          severity: warning
          service: storage
          alert_type: predictive
        annotations:
          summary: "Disk space exhaustion predicted on {{ $labels.instance }}"
          description: "Filesystem {{ $labels.mountpoint }} on {{ $labels.instance }} is projected to run out of space within 24 hours based on the current 6-hour usage trend."
EOF
```

Set permissions:

```bash
sudo chown prometheus:prometheus /etc/prometheus/alert_rules.yml
sudo chmod 640 /etc/prometheus/alert_rules.yml
```

---

# 🔎 2.6 Validate Alert Rules

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/alert_rules.yml
```

Expected:

```text
SUCCESS
```

Reload Prometheus:

```bash
curl -fsSL -X POST \
http://localhost:9090/-/reload
```

Verify:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules \
| python3 -m json.tool
```

Search for rule names:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules \
| grep -E \
'HighCPUUsage|CriticalCPUUsage|SystemUnderStress|DiskSpaceRunningOut'
```

---

# 🔥 2.7 Generate Controlled System Load

🟢 **Technology: stress-ng**

Start CPU stress:

```bash
stress-ng --cpu 4 --timeout 360s &
STRESS_CPU_PID=$!
```

Start memory stress:

```bash
stress-ng --vm 2 --vm-bytes 75% --timeout 360s &
STRESS_MEM_PID=$!
```

Display process IDs:

```bash
echo "CPU PID=${STRESS_CPU_PID}"
echo "MEM PID=${STRESS_MEM_PID}"
```

If the Ubuntu version does not accept percentage notation:

```bash
stress-ng --vm 2 --vm-bytes 1G --timeout 360s &
```

---

# 📡 2.8 Monitor Alert State

Poll Prometheus every 30 seconds:

```bash
for i in $(seq 1 12); do
  echo "=== Poll ${i} at $(date '+%Y-%m-%d %H:%M:%S') ==="

  curl -fsSL \
  http://localhost:9090/api/v1/alerts |
  python3 -c "
import sys, json

data = json.load(sys.stdin)
alerts = data.get('data', {}).get('alerts', [])

if not alerts:
    print('  No active alerts')

for a in alerts:
    print(
        '  Alert:', a['labels'].get('alertname'),
        '| State:', a['state'],
        '| Severity:', a['labels'].get('severity', 'n/a'),
        '| ActiveAt:', a.get('activeAt', 'n/a')
    )
"

  sleep 30
done
```

Observe transitions such as:

```text
pending
firing
```

---

# 🚦 Task 3 — Alert Routing, Inhibition & Webhook

## 3.1 Build Python Webhook Receiver

🐍 **Technology: Python**

Create the webhook server:

```bash
cat > /tmp/webhook_server.py <<'PYEOF'
#!/usr/bin/env python3

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        try:
            payload = json.loads(body.decode('utf-8'))

            ts = datetime.now(timezone.utc).strftime(
                '%Y-%m-%dT%H:%M:%SZ'
            )

            print(f"\n{'=' * 60}")
            print(f"Webhook received at {ts}")
            print(f"endpoint={self.path}")

            for alert in payload.get('alerts', []):
                labels = alert.get('labels', {})
                annotations = alert.get('annotations', {})

                print(
                    f"  alertname : "
                    f"{labels.get('alertname', 'unknown')}"
                )

                print(
                    f"  status    : "
                    f"{alert.get('status', 'unknown')}"
                )

                print(
                    f"  severity  : "
                    f"{labels.get('severity', 'unknown')}"
                )

                print(
                    f"  instance  : "
                    f"{labels.get('instance', 'unknown')}"
                )

                print(
                    f"  summary   : "
                    f"{annotations.get('summary', 'none')}"
                )

                print("  ---")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        except Exception as exc:
            print(f"Parse error: {exc}")
            self.send_response(400)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


HTTPServer(
    ('0.0.0.0', 5001),
    WebhookHandler
).serve_forever()
PYEOF
```

Make executable:

```bash
chmod +x /tmp/webhook_server.py
```

---

# ▶️ 3.2 Start Webhook Server

```bash
python3 /tmp/webhook_server.py \
> /tmp/webhook_server.log 2>&1 &
```

Check process:

```bash
ps aux | grep webhook_server
```

Check port:

```bash
sudo ss -tlnp | grep 5001
```

---

# 🧪 3.3 Test Webhook

```bash
curl -fsSL \
-X POST \
http://localhost:5001/test \
-H 'Content-Type: application/json' \
-d '{
  "alerts": [
    {
      "labels": {
        "alertname": "TestAlert",
        "severity": "info",
        "instance": "localhost"
      },
      "annotations": {
        "summary": "Connectivity test"
      },
      "status": "firing"
    }
  ]
}'
```

Inspect the log:

```bash
cat /tmp/webhook_server.log
```

---

# 🛣️ 3.4 Configure Alertmanager Routing

The routing architecture is:

```text
                         Alertmanager
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
         CRITICAL          WARNING          PREDICTIVE
              │               │                │
              ▼               ▼                ▼
       critical-team    warning-team    capacity-planning
              │               │                │
              ▼               ▼                ▼
          /critical        /warning         /capacity
```

Create the configuration:

```bash
sudo tee /etc/alertmanager/alertmanager.yml <<'EOF'
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'

  routes:
    - match:
        alert_type: predictive
      receiver: 'capacity-planning'
      repeat_interval: 6h

    - match:
        severity: critical
      receiver: 'critical-team'
      group_wait: 5s
      repeat_interval: 5m

    - match:
        severity: warning
      receiver: 'warning-team'
      repeat_interval: 2h

receivers:

  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:5001/alerts'
        send_resolved: true

  - name: 'critical-team'
    webhook_configs:
      - url: 'http://localhost:5001/critical'
        send_resolved: true

  - name: 'warning-team'
    webhook_configs:
      - url: 'http://localhost:5001/warning'
        send_resolved: true

  - name: 'capacity-planning'
    webhook_configs:
      - url: 'http://localhost:5001/capacity'
        send_resolved: true

inhibit_rules:

  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal:
      - instance

  - source_match:
      alert_type: 'composite'
    target_match:
      alert_type: 'predictive'
    equal:
      - instance
EOF
```

Set permissions:

```bash
sudo chown alertmanager:alertmanager \
/etc/alertmanager/alertmanager.yml

sudo chmod 640 \
/etc/alertmanager/alertmanager.yml
```

---

# 🔍 3.5 Validate Alertmanager Configuration

```bash
/opt/alertmanager/amtool check-config \
/etc/alertmanager/alertmanager.yml
```

Expected:

```text
SUCCESS
```

Restart:

```bash
sudo systemctl restart alertmanager
```

Verify:

```bash
sudo systemctl status alertmanager --no-pager
```

---

# 🌳 3.6 Inspect Routing Tree

```bash
/opt/alertmanager/amtool config routes \
--alertmanager.url=http://localhost:9093
```

The output should contain:

```text
critical-team
warning-team
capacity-planning
```

---

# 🛑 3.7 Alert Inhibition Logic

### Critical → Warning

When a critical alert exists for the same instance:

```text
CRITICAL ALERT
      │
      └──► Suppresses WARNING alerts
```

Configured using:

```yaml
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal:
    - instance
```

### Composite → Predictive

When a composite alert fires:

```text
COMPOSITE ALERT
      │
      └──► Suppresses PREDICTIVE alerts
```

Configured using:

```yaml
- source_match:
    alert_type: 'composite'
  target_match:
    alert_type: 'predictive'
  equal:
    - instance
```

This helps prevent duplicate or redundant notifications.

---

# 🔥 3.8 Trigger a Test Alert

Temporarily reduce the CPU threshold:

```bash
sudo sed -i \
's/> 80/> 1/' \
/etc/prometheus/alert_rules.yml
```

Reload Prometheus:

```bash
curl -fsSL \
-X POST http://localhost:9090/-/reload
```

Wait for the alert:

```bash
sleep 90
```

Check alerts:

```bash
curl -fsSL \
http://localhost:9093/api/v1/alerts \
| python3 -m json.tool
```

Check webhook:

```bash
cat /tmp/webhook_server.log
```

You should see:

```text
Webhook received at ...
endpoint=/warning

alertname : HighCPUUsage
status    : firing
severity  : warning
instance  : localhost:9100
summary   : High CPU usage on ...
```

---

# ♻️ 3.9 Restore the Original Threshold

Restore the CPU threshold:

```bash
sudo sed -i \
's/> 1/> 80/' \
/etc/prometheus/alert_rules.yml
```

Reload:

```bash
curl -fsSL \
-X POST http://localhost:9090/-/reload
```

Verify:

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/alert_rules.yml
```

---

# 🧪 Validation Checklist

## Task 1 — Monitoring Stack

* [ ] Prometheus is installed.
* [ ] Node Exporter is installed.
* [ ] Alertmanager is installed.
* [ ] Dedicated service users exist.
* [ ] systemd services are enabled.
* [ ] All services are active.
* [ ] Prometheus API responds.
* [ ] Node Exporter exposes metrics.
* [ ] Alertmanager API responds.
* [ ] Prometheus sees both targets as `up`.
* [ ] Configuration permissions are `640` or stricter.

## Task 2 — Alerting Rules

* [ ] CPU warning alert exists.
* [ ] CPU critical alert exists.
* [ ] Composite CPU/memory alert exists.
* [ ] Predictive disk alert exists.
* [ ] `promtool check rules` succeeds.
* [ ] Rules are loaded into Prometheus.
* [ ] CPU stress can trigger alerts.
* [ ] Memory stress can trigger alerts.
* [ ] Composite alert reaches `firing`.
* [ ] Alert lifecycle is observed.

## Task 3 — Alertmanager

* [ ] Python webhook server is running.
* [ ] Port `5001` is listening.
* [ ] Critical receiver exists.
* [ ] Warning receiver exists.
* [ ] Capacity receiver exists.
* [ ] Critical route uses 5-second `group_wait`.
* [ ] Critical route uses 5-minute `repeat_interval`.
* [ ] Warning route uses 2-hour `repeat_interval`.
* [ ] Predictive route uses 6-hour `repeat_interval`.
* [ ] Critical alerts inhibit warning alerts.
* [ ] Composite alerts inhibit predictive alerts.
* [ ] Webhook receives firing alerts.
* [ ] End-to-end routing is confirmed.

---

# 🔧 Troubleshooting Guide

## Prometheus Port 9090 Not Responding

```bash
sudo systemctl status prometheus
```

Then:

```bash
sudo journalctl \
-u prometheus \
-n 50 \
--no-pager
```

Validate:

```bash
/opt/prometheus/promtool check config \
/etc/prometheus/prometheus.yml
```

---

## Node Exporter Port 9100 Not Responding

```bash
sudo systemctl status node_exporter
```

Check:

```bash
sudo ss -tlnp | grep 9100
```

Test:

```bash
curl http://localhost:9100/metrics
```

---

## Alertmanager Port 9093 Not Responding

```bash
sudo systemctl status alertmanager
```

Check logs:

```bash
sudo journalctl \
-u alertmanager \
-n 50 \
--no-pager
```

Validate:

```bash
/opt/alertmanager/amtool check-config \
/etc/alertmanager/alertmanager.yml
```

---

## Rules Are Not Loading

Run:

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/alert_rules.yml
```

Then:

```bash
curl -fsSL \
-X POST http://localhost:9090/-/reload
```

Check:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

---

## Webhook Is Not Receiving Alerts

Check process:

```bash
ps aux | grep webhook_server
```

Check port:

```bash
sudo ss -tlnp | grep 5001
```

Check log:

```bash
cat /tmp/webhook_server.log
```

Test manually:

```bash
curl -X POST \
http://localhost:5001/test \
-H 'Content-Type: application/json' \
-d '{"alerts":[]}'
```

---

# 🏆 Acceptance Criteria

## Task 1

The following command:

```bash
sudo systemctl is-active \
node_exporter \
prometheus \
alertmanager
```

must return:

```text
active
active
active
```

Prometheus must report both targets as `up`.

Configuration validation must succeed:

```bash
/opt/prometheus/promtool check config \
/etc/prometheus/prometheus.yml
```

Expected:

```text
SUCCESS
```

---

## Task 2

The following alerts must exist:

```text
HighCPUUsage
CriticalCPUUsage
SystemUnderStress
DiskSpaceRunningOut
```

Validate:

```bash
/opt/prometheus/promtool check rules \
/etc/prometheus/alert_rules.yml
```

During controlled load testing, at least one alert must reach:

```text
firing
```

The `SystemUnderStress` alert must fire when CPU and memory simultaneously exceed their configured thresholds for the required duration.

---

## Task 3

Alertmanager configuration must pass:

```bash
/opt/alertmanager/amtool check-config \
/etc/alertmanager/alertmanager.yml
```

The routing tree must contain:

```text
critical-team
warning-team
capacity-planning
```

The webhook log must demonstrate an end-to-end alert:

```text
Prometheus
    ↓
Alert Rule
    ↓
Pending
    ↓
Firing
    ↓
Alertmanager
    ↓
Routing
    ↓
Webhook
```

---

# 📊 Expected Outcomes

After completing the lab, you should have a fully operational monitoring and alerting pipeline:

```text
┌─────────────────────────────────────────────────────────────┐
│                    Ubuntu EC2 Instance                      │
│                                                             │
│  ┌───────────────┐                                          │
│  │ Node Exporter │ :9100                                    │
│  └───────┬───────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌───────────────┐                                          │
│  │  Prometheus   │ :9090                                    │
│  │               │                                          │
│  │ • Metrics     │                                          │
│  │ • PromQL      │                                          │
│  │ • Rules       │                                          │
│  └───────┬───────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────────────┐                                  │
│  │      Alertmanager      │ :9093                            │
│  │                        │                                  │
│  │ Routing                │                                  │
│  │ Grouping               │                                  │
│  │ Inhibition             │                                  │
│  └───────────┬────────────┘                                  │
│              │                                               │
│      ┌───────┼───────────┐                                   │
│      │       │           │                                   │
│      ▼       ▼           ▼                                   │
│  /critical /warning  /capacity                              │
│      │       │           │                                   │
│      └───────┼───────────┘                                   │
│              ▼                                               │
│      ┌────────────────┐                                      │
│      │ Python Webhook │ :5001                                │
│      └────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

---

# 🚀 Production Extension Ideas

Once the basic lab is complete, extend the architecture with:

### 📢 Persistent Notifications

Integrate Alertmanager with:

* Slack
* PagerDuty
* Microsoft Teams
* Email
* Opsgenie

### 📈 Grafana

Add Grafana dashboards for:

* CPU utilization
* Memory utilization
* Disk utilization
* Network traffic
* Alert status
* Node health

### 🧮 Recording Rules

Pre-compute expensive PromQL expressions:

```yaml
groups:
  - name: performance_recording_rules
    rules:
      - record: instance:cpu_usage:percent
        expr: 100 - (
          avg by(instance)(
            irate(node_cpu_seconds_total{mode="idle"}[5m])
          ) * 100
        )
```

### 🔐 Security Hardening

Consider:

* TLS for Prometheus endpoints
* Authentication
* Restricted firewall rules
* Dedicated service accounts
* Read-only filesystem permissions
* Secrets management
* Network segmentation

### 📦 High Availability

For production environments, consider:

```text
Prometheus HA
      │
      ├── Prometheus A
      │
      └── Prometheus B
             │
             ▼
          Thanos
             │
             ▼
       Long-Term Storage
```

---

# 📚 Official Documentation

* [Prometheus Documentation](https://prometheus.io/docs/)
* [Prometheus Installation](https://prometheus.io/docs/prometheus/latest/installation/)
* [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
* [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
* [Prometheus Management API](https://prometheus.io/docs/prometheus/latest/management_api/)
* [Node Exporter Guide](https://prometheus.io/docs/guides/node-exporter/)
* [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
* [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
* [stress-ng Documentation](https://github.com/ColinIanKing/stress-ng)
* [Python HTTP Server Documentation](https://docs.python.org/3/library/http.server.html)

---

# 🎓 Conclusion

This lab demonstrates how to design an **advanced alerting architecture using Prometheus and Alertmanager** rather than relying only on basic threshold alerts.

You implemented:

```text
System Metrics
      ↓
Node Exporter
      ↓
Prometheus
      ↓
PromQL Rules
      ↓
Pending → Firing
      ↓
Alertmanager
      ↓
Severity / Type Routing
      ↓
Inhibition
      ↓
Webhook Notification
```

The combination of **multi-condition PromQL expressions, predictive alerting, severity-based routing, and inhibition rules** provides a strong foundation for reducing alert fatigue and building reliable production observability systems.

> 💡 **Next Step:** Extend this lab by integrating Slack or PagerDuty notifications, adding Grafana dashboards, introducing recording rules, and deploying Prometheus/Alertmanager in a highly available architecture.

---

## 👨‍💻 Lab Skills Demonstrated

`Prometheus` · `Alertmanager` · `Node Exporter` · `PromQL` · `Linux Administration` · `Ubuntu` · `systemd` · `AWS EC2` · `Python` · `Webhooks` · `Monitoring` · `Observability` · `SRE` · `Incident Response` · `Alert Routing` · `Alert Inhibition`

---

### ⭐ Advanced Observability Lab

**Build it → Monitor it → Alert on it → Route it → Suppress the noise → Validate it**

🚀 **Prometheus + Alertmanager + Node Exporter = Production-Ready Alerting Foundation**
