<div align="center">

# 🚨 Setting Up Alerts in Prometheus

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node%20Exporter-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-CB171E?style=for-the-badge&logo=yaml&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

**A hands-on lab building a complete Prometheus alerting pipeline — from alert rule definitions through Alertmanager routing to email and webhook notification delivery.**

</div>

---

## 📑 Table of Contents

- [🎯 Lab Objectives](#-lab-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🧩 Key Concepts](#-key-concepts)
- [📏 Task 1: Define Basic Alerting Rules in Prometheus](#-task-1-define-basic-alerting-rules-in-prometheus)
- [📧 Task 2: Set Up Alertmanager and Test Email/SMS Notifications](#-task-2-set-up-alertmanager-and-test-emailsms-notifications)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [✅ Lab Verification Commands](#-lab-verification-commands)
- [🏁 Conclusion](#-conclusion)

---

## 🎯 Lab Objectives

By the end of this lab, you will be able to:

| # | Objective |
|---|-----------|
| 1 | Understand the fundamentals of Prometheus alerting architecture |
| 2 | Configure alert rules in Prometheus to monitor system metrics |
| 3 | Install and configure Alertmanager for notification management |
| 4 | Set up email notifications for triggered alerts |
| 5 | Test the complete alerting pipeline from rule definition to notification delivery |
| 6 | Troubleshoot common alerting configuration issues |

## 📋 Prerequisites

Before starting this lab, you should have:

- ✅ Basic understanding of Linux command line operations
- ✅ Familiarity with YAML configuration files
- ✅ Knowledge of Prometheus basics and PromQL queries
- ✅ Understanding of system monitoring concepts
- ✅ Access to an email account for testing notifications

## 🖥️ Lab Environment

> **☁️ Al Nafi Cloud Machine**
> Al Nafi provides Linux-based cloud machines for this lab. Simply click **Start Lab** to access your dedicated environment. The provided Linux machine is bare metal with no pre-installed tools — you will install all required components during the lab exercises.
>
> All tasks in this lab are performed on a **single Linux machine**. No additional virtual machines or remote hosts are required.

## 🧩 Key Concepts

| Concept | Description |
|---------|-------------|
| **Alert Rule** | A PromQL expression evaluated on a schedule; when it evaluates to a non-empty result for longer than the `for` duration, the alert fires |
| **`for` duration** | The minimum time an alert condition must persist before Prometheus moves it from `Pending` to `Firing` — prevents flapping on transient spikes |
| **Alertmanager** | A separate component that receives firing alerts from Prometheus and handles deduplication, grouping, routing, and notification delivery |
| **Routing Tree** | Alertmanager's `route` block, which determines which `receiver` handles an alert based on its labels |
| **Grouping (`group_by`)** | Bundles related alerts into a single notification instead of sending one message per alert |
| **Inhibition Rules** | Suppress lower-severity notifications when a related higher-severity alert is already firing (e.g., suppress `warning` when a matching `critical` fires) |
| **Receiver** | A named notification target in Alertmanager — email, webhook, Slack, PagerDuty, etc. |
| **Webhook Integration** | A generic HTTP callback (`webhook_configs`) that lets Alertmanager hand off alerts to custom or third-party systems, such as SMS gateways |

---

## 📏 Task 1: Define Basic Alerting Rules in Prometheus

### 📦 Subtask 1.1: Install Prometheus

First, install Prometheus on your Linux machine.

```bash
# 🔄 Update the system packages
sudo apt update && sudo apt upgrade -y

# 👤 Create a prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus

# 📁 Create directories for Prometheus
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus

# ⬇️ Download Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

# 📦 Extract the archive
tar xvf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

# 📋 Copy binaries to system directories
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool

# 📋 Copy configuration files
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

### ⚙️ Subtask 1.2: Create Basic Prometheus Configuration

Create the main Prometheus configuration file:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add the following configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"       # 📏 alert rule definitions loaded here

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093  # 📧 where Prometheus sends firing alerts

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

Set proper ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

### 🖥️ Subtask 1.3: Install Node Exporter for System Metrics

Install Node Exporter to collect system metrics:

```bash
# ⬇️ Download Node Exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz

# 📦 Extract and install
tar xvf node_exporter-1.6.0.linux-amd64.tar.gz
sudo cp node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/node_exporter

# 🛠️ Create systemd service for Node Exporter
sudo nano /etc/systemd/system/node_exporter.service
```

Add the following service configuration:

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

Enable and start Node Exporter:

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
sudo systemctl status node_exporter
```

### 📏 Subtask 1.4: Create Alert Rules

Create the alert rules file:

```bash
sudo nano /etc/prometheus/alert_rules.yml
```

Add the following alert rules:

```yaml
groups:
  - name: system_alerts
    rules:
      - alert: HighCPUUsage                                              # ⚠️ warning-level
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 2 minutes on instance {{ $labels.instance }}"

      - alert: HighMemoryUsage                                           # ⚠️ warning-level
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 2 minutes on instance {{ $labels.instance }}"

      - alert: DiskSpaceLow                                              # 🔴 critical
        expr: (1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100 > 90
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Disk space is running low"
          description: "Disk usage is above 90% on {{ $labels.device }} mounted at {{ $labels.mountpoint }}"

      - alert: ServiceDown                                               # 🔴 critical
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Service {{ $labels.job }} on instance {{ $labels.instance }} is down"
```

Set proper ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/alert_rules.yml
```

### 🛠️ Subtask 1.5: Create Prometheus Systemd Service

Create the Prometheus systemd service:

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Add the following configuration:

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

Enable and start Prometheus:

```bash
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus
```

### ✅ Subtask 1.6: Verify Alert Rules Configuration

Check if the alert rules are loaded correctly:

```bash
# ✅ Validate the configuration
/usr/local/bin/promtool check config /etc/prometheus/prometheus.yml

# ✅ Check alert rules syntax
/usr/local/bin/promtool check rules /etc/prometheus/alert_rules.yml
```

> 🌐 Access the Prometheus web interface by opening a web browser and navigating to `http://localhost:9090`. Go to **Status > Rules** to verify that your alert rules are loaded.

---

## 📧 Task 2: Set Up Alertmanager and Test Email/SMS Notifications

### 📦 Subtask 2.1: Install Alertmanager

Download and install Alertmanager:

```bash
# ⬇️ Download Alertmanager
cd /tmp
wget https://github.com/prometheus/alertmanager/releases/download/v0.25.0/alertmanager-0.25.0.linux-amd64.tar.gz

# 📦 Extract the archive
tar xvf alertmanager-0.25.0.linux-amd64.tar.gz
cd alertmanager-0.25.0.linux-amd64

# 📋 Copy binaries
sudo cp alertmanager /usr/local/bin/
sudo cp amtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/alertmanager
sudo chown prometheus:prometheus /usr/local/bin/amtool

# 📁 Create directories
sudo mkdir /etc/alertmanager
sudo mkdir /var/lib/alertmanager
sudo chown prometheus:prometheus /etc/alertmanager
sudo chown prometheus:prometheus /var/lib/alertmanager
```

### ✉️ Subtask 2.2: Configure Alertmanager for Email Notifications

Create the Alertmanager configuration file:

```bash
sudo nano /etc/alertmanager/alertmanager.yml
```

Add the following configuration (replace email settings with your actual SMTP details):

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'your-email@gmail.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']    # 📦 bundle alerts of the same name together
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'recipient@example.com'
        subject: 'Prometheus Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'   # 🔴 if a critical alert is firing...
    target_match:
      severity: 'warning'    # ⚠️ ...suppress matching warning alerts
    equal: ['alertname', 'dev', 'instance']
```

> 📝 **Note:** For Gmail, you need to use an **App Password** instead of your regular password. Enable 2-factor authentication and generate an App Password in your Google Account settings.

Set proper ownership:

```bash
sudo chown prometheus:prometheus /etc/alertmanager/alertmanager.yml
```

### 🛠️ Subtask 2.3: Create Alertmanager Systemd Service

Create the systemd service file:

```bash
sudo nano /etc/systemd/system/alertmanager.service
```

Add the following configuration:

```ini
[Unit]
Description=Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/alertmanager \
    --config.file /etc/alertmanager/alertmanager.yml \
    --storage.path /var/lib/alertmanager/ \
    --web.listen-address=0.0.0.0:9093

[Install]
WantedBy=multi-user.target
```

Enable and start Alertmanager:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alertmanager
sudo systemctl start alertmanager
sudo systemctl status alertmanager
```

### 📬 Subtask 2.4: Install Mailutils for Local Testing

Install mailutils to test email functionality locally:

```bash
sudo apt install mailutils -y

# ⚙️ Configure postfix (choose "Local only" when prompted)
sudo dpkg-reconfigure postfix
```

### 🔥 Subtask 2.5: Test Alert Configuration

Create a simple script to generate high CPU usage for testing:

```bash
nano cpu_stress.sh
```

Add the following content:

```bash
#!/bin/bash
echo "Starting CPU stress test..."
for i in {1..4}; do
    yes > /dev/null &      # 🔥 spin up CPU-bound background jobs
done
echo "CPU stress test started. Run 'killall yes' to stop."
```

Make it executable:

```bash
chmod +x cpu_stress.sh
```

### 🔍 Subtask 2.6: Verify Alerting Pipeline

1. **Check Prometheus targets:** Navigate to `http://localhost:9090/targets` to ensure all targets are up.
2. **View alert rules:** Go to `http://localhost:9090/rules` to see your configured rules.
3. **Monitor alerts:** Visit `http://localhost:9090/alerts` to see active alerts.
4. **Access Alertmanager:** Open `http://localhost:9093` to view the Alertmanager interface.
5. **Trigger an alert:** Run the CPU stress test:

```bash
./cpu_stress.sh
```

> ⏳ Wait for 2–3 minutes, then check the alerts page. You should see the `HighCPUUsage` alert firing.

6. **Stop the stress test:**

```bash
killall yes
```

### 📲 Subtask 2.7: Configure Alternative Notification Methods

For SMS notifications using a webhook service, modify the Alertmanager configuration:

```bash
sudo nano /etc/alertmanager/alertmanager.yml
```

Add a webhook receiver:

```yaml
receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'recipient@example.com'
        subject: 'Prometheus Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
          {{ end }}
    webhook_configs:
      - url: 'http://localhost:8080/webhook'   # 🪝 generic HTTP callback
        send_resolved: true
```

Create a simple webhook receiver for testing:

```bash
nano webhook_receiver.py
```

Add the following Python script:

```python
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            alert_data = json.loads(post_data.decode('utf-8'))
            logging.info(f"Received alert: {json.dumps(alert_data, indent=2)}")
            
            # 📲 Here you would integrate with SMS service
            for alert in alert_data.get('alerts', []):
                print(f"ALERT: {alert.get('annotations', {}).get('summary', 'Unknown alert')}")
                
        except json.JSONDecodeError:
            logging.error("Invalid JSON received")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), WebhookHandler)
    print("Webhook server running on http://localhost:8080")
    server.serve_forever()
```

Make it executable and run:

```bash
chmod +x webhook_receiver.py
python3 webhook_receiver.py &
```

### 🔁 Subtask 2.8: Test Complete Alerting Pipeline

1. **Restart Alertmanager** to load the new configuration:

```bash
sudo systemctl restart alertmanager
```

2. **Trigger alerts again:**

```bash
./cpu_stress.sh
```

3. Monitor the webhook receiver output to see incoming alerts.
4. Check email for alert notifications.
5. **Verify alert resolution** by stopping the stress test:

```bash
killall yes
```

> ⏳ Wait for the alert to resolve and check for resolution notifications.

---

## 🛠️ Troubleshooting

<details>
<summary><strong>Issue 1: Prometheus Not Starting</strong></summary>

Check the logs:

```bash
sudo journalctl -u prometheus -f
```

**Common solutions:**

- Verify configuration syntax with `promtool check config`
- Check file permissions
- Ensure ports are not in use

</details>

<details>
<summary><strong>Issue 2: Alerts Not Firing</strong></summary>

**Verify:**

- Alert rule syntax with `promtool check rules`
- Metrics are being collected (check `/metrics` endpoint)
- Alert evaluation interval in Prometheus config

</details>

<details>
<summary><strong>Issue 3: Email Notifications Not Working</strong></summary>

**Check:**

- SMTP credentials and server settings
- Firewall rules for SMTP ports
- Alertmanager logs: `sudo journalctl -u alertmanager -f`

</details>

<details>
<summary><strong>Issue 4: High Resource Usage</strong></summary>

Monitor system resources:

```bash
# Check CPU and memory usage
htop

# Check disk space
df -h

# Check service status
sudo systemctl status prometheus node_exporter alertmanager
```

</details>

---

## ✅ Lab Verification Commands

Use these commands to verify your setup:

```bash
# Check all services are running
sudo systemctl status prometheus node_exporter alertmanager

# Verify Prometheus configuration
curl http://localhost:9090/api/v1/status/config

# Check loaded rules
curl http://localhost:9090/api/v1/rules

# View current alerts
curl http://localhost:9090/api/v1/alerts

# Test Alertmanager API
curl http://localhost:9093/api/v1/status

# Check if metrics are being collected
curl http://localhost:9100/metrics | head -20
```

---

## 🏁 Conclusion

In this lab, you have successfully:

### 🎯 Key Accomplishments

- ✅ Installed and configured Prometheus with custom alert rules for monitoring system metrics
- ✅ Set up comprehensive alerting rules that monitor CPU usage, memory consumption, disk space, and service availability
- ✅ Deployed Alertmanager with email notification capabilities for alert management
- ✅ Created a complete alerting pipeline from metric collection to notification delivery
- ✅ Tested the entire system by generating alerts and verifying notification delivery
- ✅ Implemented webhook integration for alternative notification methods like SMS

### 🌍 Real-World Applications

This alerting setup provides a robust foundation for monitoring your infrastructure. The skills you've learned enable you to:

- Proactively monitor system health and performance
- Receive timely notifications when issues arise
- Scale monitoring across multiple services and systems
- Customize alert rules based on specific business requirements

Understanding Prometheus alerting is crucial for maintaining reliable systems in production environments. The combination of flexible rule definitions, powerful query language (PromQL), and versatile notification options makes Prometheus an excellent choice for modern monitoring and alerting solutions.

Remember to regularly review and update your alert rules based on system behavior and business needs. Consider implementing alert fatigue prevention strategies such as proper grouping, inhibition rules, and appropriate severity levels to ensure your alerting system remains effective and actionable.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al%20Nafi-Cybersecurity%20Training-blueviolet?style=for-the-badge)

</div>
