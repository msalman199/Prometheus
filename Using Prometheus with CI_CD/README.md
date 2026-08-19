# 🚀 Using Prometheus with CI/CD

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?style=for-the-badge\&logo=jenkins\&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-Alerting-E6522C?style=for-the-badge\&logo=prometheus\&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node_Exporter-System_Metrics-4C9A2A?style=for-the-badge)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?style=for-the-badge\&logo=ubuntu\&logoColor=white)
![Python](https://img.shields.io/badge/Python-Custom_Metrics-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version_Control-F05032?style=for-the-badge\&logo=git\&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-Configuration-CB171E?style=for-the-badge\&logo=yaml\&logoColor=white)

> 🧪 **Al Nafi Cloud Lab**
> A hands-on DevOps monitoring lab integrating **Prometheus, Jenkins, Node Exporter, Alertmanager, Python, and CI/CD pipelines**.

---

## 📌 Lab Overview

This lab demonstrates how to integrate **Prometheus monitoring with Jenkins CI/CD** to create an observable and alert-driven software delivery environment.

The implementation collects Jenkins build and pipeline metrics, monitors Linux system resources, creates custom deployment metrics, evaluates CI/CD health through PromQL queries, and sends alerts through Alertmanager.

The final architecture provides visibility into:

* 🏗️ Jenkins builds
* ❌ Build failures
* ⏱️ Build duration
* 📋 Jenkins queue backlog
* ⚙️ Executor utilization
* 🚀 Deployment success rates
* 🖥️ Linux system metrics
* 🔔 CI/CD alerts
* 📡 Custom application metrics

---

# 🎯 Lab Objectives

By completing this lab, you will learn how to:

* ✅ Install and configure Prometheus on Linux
* ✅ Install and configure Jenkins
* ✅ Integrate Jenkins with Prometheus
* ✅ Install Node Exporter
* ✅ Configure Alertmanager
* ✅ Create Jenkins-specific Prometheus alert rules
* ✅ Monitor Jenkins build metrics
* ✅ Create custom deployment metrics
* ✅ Build a Python webhook receiver
* ✅ Test CI/CD alerting workflows
* ✅ Create and monitor Jenkins Pipeline jobs
* ✅ Troubleshoot Prometheus-Jenkins integration problems
* ✅ Query CI/CD metrics using PromQL

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │       Jenkins       │
                         │       CI / CD       │
                         │      :8080          │
                         └──────────┬──────────┘
                                    │
                                    │ /prometheus
                                    ▼
┌─────────────────┐       ┌─────────────────────┐
│  Node Exporter  │──────▶│     Prometheus      │
│      :9100      │       │       :9090         │
└─────────────────┘       └──────────┬──────────┘
                                    │
                           Alert Rules
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Alertmanager     │
                         │       :9093         │
                         └──────────┬──────────┘
                                    │
                                    │ Webhook
                                    ▼
                         ┌─────────────────────┐
                         │ Python Webhook      │
                         │ Receiver :5001      │
                         └─────────────────────┘

                         Custom Metrics
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Python Metrics      │
                    │ Server :8081        │
                    └─────────────────────┘
```

---

# 🧰 Technologies Used

| Technology       | Purpose                                   |
| ---------------- | ----------------------------------------- |
| 🟠 Prometheus    | Metrics collection and monitoring         |
| 🔴 Jenkins       | CI/CD automation                          |
| 🟠 Alertmanager  | Alert routing and notification            |
| 🟢 Node Exporter | Linux system metrics                      |
| 🐍 Python        | Custom metrics and webhook services       |
| 🐧 Linux         | Lab operating system                      |
| 📄 YAML          | Prometheus and Alertmanager configuration |
| 🔎 PromQL        | Metrics querying                          |
| 🔧 systemd       | Service management                        |
| 🌐 HTTP          | Metrics and webhook communication         |

---

# 📋 Prerequisites

Before beginning the lab, you should have:

* Basic Linux command-line knowledge
* Understanding of CI/CD concepts
* Familiarity with Jenkins
* Basic YAML knowledge
* Understanding of HTTP and REST APIs
* Basic monitoring concepts
* Basic Prometheus knowledge

---

# ☁️ Lab Environment

The lab is performed on an **Al Nafi Linux cloud machine**.

The machine starts with minimal software, so the required components are installed manually.

Required services:

```text
Prometheus       : 9090
Jenkins          : 8080
Alertmanager     : 9093
Node Exporter    : 9100
Webhook Server   : 5001
Custom Metrics   : 8081
```

---

# 🔹 Task 1 — Environment Setup

## 1.1 Update Linux

```bash
sudo apt update && sudo apt upgrade -y
```

Install required packages:

```bash
sudo apt install -y wget curl git openjdk-11-jdk python3 python3-pip unzip
```

Verify Java:

```bash
java -version
```

Expected result:

```text
openjdk version "11..."
```

---

# 🔹 Task 2 — Install Prometheus

## 2.1 Create Prometheus User

```bash
sudo useradd --no-create-home --shell /bin/false prometheus

sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

---

## 2.2 Download Prometheus

```bash
cd /tmp

wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf prometheus-2.45.0.linux-amd64.tar.gz
```

Install Prometheus binaries:

```bash
sudo cp prometheus-2.45.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.45.0.linux-amd64/promtool /usr/local/bin/
```

Set ownership:

```bash
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

Copy console files:

```bash
sudo cp -r prometheus-2.45.0.linux-amd64/consoles /etc/prometheus
sudo cp -r prometheus-2.45.0.linux-amd64/console_libraries /etc/prometheus

sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

Verify:

```bash
prometheus --version
promtool --version
```

---

# 🔹 Task 3 — Configure Prometheus

Create the configuration:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Example configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "jenkins_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'jenkins'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/prometheus'
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

Validate:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

---

# 🔹 Task 4 — Create Prometheus systemd Service

Create:

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Configuration:

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

Start Prometheus:

```bash
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
```

Check status:

```bash
sudo systemctl status prometheus
```

Open:

```text
http://localhost:9090
```

---

# 🔹 Task 5 — Install Jenkins

## 5.1 Add Jenkins Repository

```bash
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
```

```bash
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
```

Install:

```bash
sudo apt update
sudo apt install -y jenkins
```

Start Jenkins:

```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
```

Verify:

```bash
sudo systemctl status jenkins
```

---

# 🔹 Task 6 — Configure Jenkins

Get the initial administrator password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Open:

```text
http://localhost:8080
```

Complete the Jenkins setup wizard and install the suggested plugins.

---

# 🔹 Task 7 — Install Jenkins Prometheus Plugin

Navigate to:

```text
Manage Jenkins
      ↓
Manage Plugins
      ↓
Available
      ↓
Prometheus metrics
```

Install the **Prometheus metrics plugin**.

Restart Jenkins:

```bash
sudo systemctl restart jenkins
```

---

# 🔹 Task 8 — Configure Jenkins Metrics

Navigate to:

```text
Manage Jenkins
      ↓
Configure System
      ↓
Prometheus
```

Configure:

```text
Path: /prometheus
Default namespace: jenkins
Collecting metrics period: 120 seconds
```

Save the configuration.

Test the endpoint:

```bash
curl http://localhost:8080/prometheus
```

You should receive Prometheus-formatted Jenkins metrics.

---

# 🔹 Task 9 — Install Node Exporter

Download:

```bash
cd /tmp

wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf node_exporter-1.6.0.linux-amd64.tar.gz
```

Install:

```bash
sudo cp node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/node_exporter
```

---

# 🔹 Task 10 — Configure Node Exporter Service

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
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

Verify:

```bash
sudo systemctl status node_exporter
```

Test:

```bash
curl http://localhost:9100/metrics
```

---

# 🔹 Task 11 — Install Alertmanager

Download:

```bash
cd /tmp

wget https://github.com/prometheus/alertmanager/releases/download/v0.25.0/alertmanager-0.25.0.linux-amd64.tar.gz
```

Extract:

```bash
tar xvf alertmanager-0.25.0.linux-amd64.tar.gz
```

Install:

```bash
sudo cp alertmanager-0.25.0.linux-amd64/alertmanager /usr/local/bin/
sudo cp alertmanager-0.25.0.linux-amd64/amtool /usr/local/bin/
```

Create configuration directory:

```bash
sudo mkdir /etc/alertmanager
sudo mkdir /var/lib/alertmanager

sudo chown prometheus:prometheus /etc/alertmanager
sudo chown prometheus:prometheus /var/lib/alertmanager
```

---

# 🔹 Task 12 — Configure Alertmanager

Create:

```bash
sudo nano /etc/alertmanager/alertmanager.yml
```

Configuration:

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alertmanager@example.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:

- name: 'web.hook'
  webhook_configs:
  - url: 'http://localhost:5001/webhook'
    send_resolved: true
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/alertmanager/alertmanager.yml
```

---

# 🔹 Task 13 — Create Alertmanager Service

Create:

```bash
sudo nano /etc/systemd/system/alertmanager.service
```

Add:

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
    --config.file=/etc/alertmanager/alertmanager.yml \
    --storage.path=/var/lib/alertmanager/

[Install]
WantedBy=multi-user.target
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alertmanager
sudo systemctl start alertmanager
```

Verify:

```bash
sudo systemctl status alertmanager
```

Open:

```text
http://localhost:9093
```

---

# 🔹 Task 14 — Create Jenkins Alert Rules

Create:

```bash
sudo nano /etc/prometheus/jenkins_rules.yml
```

Example rules:

```yaml
groups:

- name: jenkins_alerts

  rules:

  - alert: JenkinsDown
    expr: up{job="jenkins"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Jenkins is down"
      description: "Jenkins has been down for more than 1 minute."

  - alert: JenkinsBuildFailure
    expr: increase(jenkins_builds_failed_total[5m]) > 0
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Jenkins build failed"
      description: "A Jenkins build has failed in the last 5 minutes."

  - alert: JenkinsHighBuildDuration
    expr: jenkins_builds_duration_milliseconds_summary{quantile="0.5"} > 300000
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Jenkins build taking too long"
      description: "Jenkins build duration is above 5 minutes."

  - alert: JenkinsQueueBacklog
    expr: jenkins_queue_size_value > 5
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Jenkins queue backlog"
      description: "Jenkins has more than 5 jobs in queue."

  - alert: JenkinsExecutorUtilization
    expr: (jenkins_executor_in_use_value / jenkins_executor_count_value) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High Jenkins executor utilization"
      description: "Jenkins executor utilization is above 80%."
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/jenkins_rules.yml
```

---

# 🔹 Task 15 — Validate Prometheus Rules

Check configuration:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Check rules:

```bash
promtool check rules /etc/prometheus/jenkins_rules.yml
```

Reload:

```bash
sudo systemctl reload prometheus
```

---

# 🔹 Task 16 — Create Jenkins Test Jobs

## 🧪 Sample Build Job

Create a Jenkins Freestyle project:

```text
sample-build-job
```

Build trigger:

```text
H/2 * * * *
```

Build script:

```bash
#!/bin/bash

echo "Starting deployment simulation..."

sleep 10

echo "Running tests..."

sleep 5

if [ $((RANDOM % 4)) -eq 0 ]; then
    echo "Build failed!"
    exit 1
else
    echo "Build successful!"
    exit 0
fi
```

Run the job multiple times.

---

# 🔹 Task 17 — Create Long-Running Jenkins Job

Create:

```text
long-running-job
```

Execute:

```bash
#!/bin/bash

echo "Starting long-running process..."

sleep 360

echo "Process completed"
```

This job is designed to help test build-duration monitoring.

---

# 🔹 Task 18 — Create Webhook Receiver

Create:

```bash
nano webhook_receiver.py
```

The webhook receiver should:

* Accept POST requests
* Parse Alertmanager JSON
* Display alert status
* Display alert name
* Display summary
* Display description

Run:

```bash
chmod +x webhook_receiver.py
```

Start:

```bash
python3 webhook_receiver.py &
```

Verify:

```bash
curl http://localhost:5001
```

---

# 🔹 Task 19 — Verify Prometheus Targets

Open:

```text
http://localhost:9090/targets
```

Expected targets:

| Target        | Endpoint                    | Expected |
| ------------- | --------------------------- | -------- |
| Prometheus    | `localhost:9090`            | 🟢 UP    |
| Jenkins       | `localhost:8080/prometheus` | 🟢 UP    |
| Node Exporter | `localhost:9100`            | 🟢 UP    |

---

# 🔎 Task 20 — Query Jenkins Metrics

Open the Prometheus expression browser.

### Jenkins availability

```promql
up{job="jenkins"}
```

### Jenkins builds

```promql
jenkins_builds_total
```

### Build duration

```promql
jenkins_builds_duration_milliseconds_summary
```

### Jenkins queue

```promql
jenkins_queue_size_value
```

---

# 🚨 Task 21 — Test JenkinsDown Alert

Stop Jenkins:

```bash
sudo systemctl stop jenkins
```

Wait approximately 1–2 minutes.

Check:

```text
Prometheus
   ↓
Alerts
   ↓
JenkinsDown
```

The alert should transition to:

```text
FIRING
```

Check Alertmanager:

```text
http://localhost:9093
```

Restart Jenkins:

```bash
sudo systemctl start jenkins
```

---

# ❌ Task 22 — Test Build Failure Alert

Modify the sample Jenkins job:

```bash
exit 1
```

Run the job several times.

Monitor:

```promql
increase(jenkins_builds_failed_total[5m])
```

The `JenkinsBuildFailure` alert should become active when the corresponding metric is exposed by the installed Jenkins metrics plugin.

---

# ⏱️ Task 23 — Test Build Duration Alert

Start:

```text
long-running-job
```

Monitor:

```promql
jenkins_builds_duration_milliseconds_summary
```

Observe the configured duration alert.

---

# 🐍 Task 24 — Create Custom Deployment Metrics

Create:

```bash
nano custom_metrics.py
```

The Python service exposes:

```text
/metrics
```

on:

```text
localhost:8081
```

Example metrics:

```text
deployment_success_rate
deployment_failure_rate
deployment_response_time
deployments_total
```

Start:

```bash
python3 custom_metrics.py &
```

Verify:

```bash
curl http://localhost:8081/metrics
```

---

# 🔹 Task 25 — Add Custom Metrics to Prometheus

Edit:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add:

```yaml
  - job_name: 'custom-deployment-metrics'
    static_configs:
      - targets: ['localhost:8081']
    scrape_interval: 10s
```

Validate:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Reload:

```bash
sudo systemctl reload prometheus
```

Verify target:

```text
http://localhost:9090/targets
```

---

# 🚨 Task 26 — Deployment Alert Rules

Add:

```yaml
  - alert: LowDeploymentSuccessRate
    expr: deployment_success_rate < 90
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Low deployment success rate"
      description: "Deployment success rate is below 90% for 2 minutes."

  - alert: HighDeploymentResponseTime
    expr: deployment_response_time > 1.5
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "High deployment response time"
      description: "Deployment response time is above 1.5 seconds."
```

Reload:

```bash
sudo systemctl reload prometheus
```

---

# 🔄 Task 27 — Create Jenkins CI/CD Pipeline

Create a Jenkins Pipeline:

```text
cicd-pipeline
```

Pipeline stages:

```text
Checkout
    ↓
Build
    ↓
Test
    ↓
Deploy
```

Example Jenkinsfile:

```groovy
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                sleep 2
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'
                sleep 5
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sleep 3

                script {
                    if (Math.random() < 0.2) {
                        error('Tests failed!')
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying to production...'
                sleep 4
                echo 'Deployment completed successfully!'
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed'
        }

        success {
            echo 'Pipeline succeeded'
        }

        failure {
            echo 'Pipeline failed'
        }
    }
}
```

Run the pipeline several times to generate different CI/CD states.

---

# 📊 Task 28 — Monitor CI/CD Performance

### Total builds by job

```promql
sum by (job_name) (jenkins_builds_total)
```

### Build success rate

```promql
(jenkins_builds_success_total / jenkins_builds_total) * 100
```

### Average build duration

```promql
avg(jenkins_builds_duration_milliseconds_summary{quantile="0.5"}) / 1000
```

### Builds per hour

```promql
rate(jenkins_builds_total[1h]) * 3600
```

---

# 🔧 Troubleshooting

## ❗ Problem 1 — Jenkins Target is DOWN

Check Jenkins:

```bash
sudo systemctl status jenkins
```

Test the metrics endpoint:

```bash
curl http://localhost:8080/prometheus
```

Check Jenkins logs:

```bash
sudo journalctl -u jenkins -f
```

Verify that the Prometheus metrics plugin is installed.

---

## ❗ Problem 2 — Prometheus Configuration Error

Run:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Check Prometheus logs:

```bash
sudo journalctl -u prometheus -f
```

Restart if necessary:

```bash
sudo systemctl restart prometheus
```

---

## ❗ Problem 3 — Alert Rules Not Loading

Run:

```bash
promtool check rules /etc/prometheus/jenkins_rules.yml
```

Then:

```bash
sudo systemctl reload prometheus
```

Check:

```text
http://localhost:9090/rules
```

---

## ❗ Problem 4 — Webhook Not Receiving Alerts

Check the Python process:

```bash
ps aux | grep webhook_receiver
```

Check port:

```bash
ss -lntp | grep 5001
```

Restart Alertmanager:

```bash
sudo systemctl restart alertmanager
```

Check Alertmanager logs:

```bash
sudo journalctl -u alertmanager -f
```

---

## ❗ Problem 5 — High Memory Usage

Check memory:

```bash
free -h
```

Monitor processes:

```bash
htop
```

Reduce Prometheus retention by adding:

```text
--storage.tsdb.retention.time=7d
```

to the Prometheus service.

You can also increase scrape intervals to reduce metric ingestion.

---

# ✅ Final Verification

## Check All Services

```bash
sudo systemctl status prometheus
sudo systemctl status jenkins
sudo systemctl status alertmanager
sudo systemctl status node_exporter
```

All required services should show:

```text
Active: active (running)
```

---

## Check Prometheus Targets

Open:

```text
http://localhost:9090/targets
```

Verify:

```text
Prometheus       → UP
Jenkins          → UP
Node Exporter    → UP
Custom Metrics   → UP
```

---

## Check Important Metrics

Run:

```promql
up
```

```promql
jenkins_builds_total
```

```promql
node_cpu_seconds_total
```

```promql
deployment_success_rate
```

---

# 🧪 Complete Alert Flow

The final monitoring flow should work like this:

```text
Jenkins Build
     │
     ▼
Jenkins Metrics
     │
     ▼
Prometheus
     │
     ▼
Alert Rules
     │
     ▼
Alertmanager
     │
     ▼
Webhook Receiver
     │
     ▼
Alert Notification
```

Test:

```bash
sudo systemctl stop jenkins
```

Wait for the configured alert interval.

Then verify:

```text
Prometheus → Alerts → JenkinsDown → FIRING
```

Check Alertmanager:

```text
http://localhost:9093
```

Finally:

```bash
sudo systemctl start jenkins
```

The alert should eventually become resolved.

---

# 🏆 Skills Demonstrated

By completing this project, you demonstrated practical experience with:

* 🐧 Linux system administration
* 📊 Prometheus monitoring
* 🔴 Jenkins CI/CD
* 🚨 Alertmanager
* 📡 Prometheus exporters
* 🐍 Python HTTP services
* 🔎 PromQL
* ⚙️ systemd service management
* 📝 YAML configuration
* 🚀 CI/CD observability
* 📈 Deployment monitoring
* 🔔 Alert engineering
* 🛠️ Monitoring troubleshooting

---

# 🎓 Key Learning Outcomes

### 1. CI/CD Observability

You learned how to monitor the health and performance of a Jenkins-based CI/CD environment.

### 2. Metrics Collection

Prometheus collects metrics from Jenkins, Node Exporter, and custom Python endpoints.

### 3. Alert Engineering

Prometheus rules detect:

* Jenkins outages
* Build failures
* Long-running builds
* Queue backlogs
* Executor saturation
* Low deployment success rates
* High deployment response times

### 4. Alert Routing

Alertmanager provides centralized alert management and forwards notifications to a webhook receiver.

### 5. Custom Monitoring

The Python metrics server demonstrates how DevOps teams can expose application-specific metrics that are not available through standard exporters.

---

# 🚀 Production Extension Ideas

This lab can be extended into a more production-oriented monitoring platform by adding:

* 📊 Grafana dashboards
* 🔐 TLS authentication
* 🔒 Prometheus authentication
* ☁️ AWS/Azure infrastructure monitoring
* 📦 Kubernetes monitoring
* 🐳 Docker container metrics
* 💬 Slack notifications
* 📧 Email notifications
* 🔔 PagerDuty integration
* 📈 SLO/SLA monitoring
* 📋 Recording rules
* 🔄 Automated deployment metrics
* 🛡️ Security monitoring
* 📦 Long-term metrics storage using Thanos

---

# 📁 Suggested Repository Structure

```text
prometheus-jenkins-cicd/
│
├── README.md
│
├── prometheus/
│   ├── prometheus.yml
│   └── jenkins_rules.yml
│
├── alertmanager/
│   └── alertmanager.yml
│
├── jenkins/
│   └── Jenkinsfile
│
├── scripts/
│   ├── webhook_receiver.py
│   └── custom_metrics.py
│
└── systemd/
    ├── prometheus.service
    ├── alertmanager.service
    └── node_exporter.service
```

---

# 🌟 Conclusion

This lab successfully demonstrates a complete **Prometheus + Jenkins CI/CD monitoring and alerting environment**.

You installed and configured Prometheus, Jenkins, Node Exporter, and Alertmanager; integrated Jenkins metrics with Prometheus; created CI/CD-specific alert rules; developed custom deployment metrics; implemented a Python webhook receiver; and tested real-world build and deployment scenarios.

The resulting architecture provides **real-time visibility into CI/CD health, build performance, deployment reliability, and infrastructure resources**.

This project is an excellent foundation for production-grade **DevOps Observability**, where monitoring is integrated directly into the software delivery lifecycle.

> 🚀 **Monitor → Detect → Alert → Respond → Improve**

---

## 👨‍💻 Author

**Hafiz Muhammad Salman**

**Cloud DevOps Engineer | Linux Administrator**

### ⭐ If this project helped you

Consider giving the repository a ⭐ and sharing your feedback.

**Built with:** Prometheus • Jenkins • Alertmanager • Node Exporter • Python • Linux • CI/CD
