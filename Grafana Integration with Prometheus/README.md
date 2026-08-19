# 🚀 Monitoring Kubernetes with Prometheus and Grafana

![Kubernetes](https://img.shields.io/badge/Kubernetes-Container%20Orchestration-326CE5?style=for-the-badge\&logo=kubernetes)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge\&logo=prometheus)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=for-the-badge\&logo=grafana)
![Helm](https://img.shields.io/badge/Helm-Package%20Manager-0F1689?style=for-the-badge\&logo=helm)
![K3s](https://img.shields.io/badge/K3s-Lightweight%20Kubernetes-FFC61C?style=for-the-badge\&logo=k3s)
![Docker](https://img.shields.io/badge/Docker-Container%20Runtime-2496ED?style=for-the-badge\&logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge\&logo=amazonaws)
![Ubuntu](https://img.shields.io/badge/Ubuntu-Linux-E95420?style=for-the-badge\&logo=ubuntu)
![PromQL](https://img.shields.io/badge/PromQL-Metrics%20Queries-E6522C?style=for-the-badge)
![Alertmanager](https://img.shields.io/badge/Alertmanager-Alerting-FF6B35?style=for-the-badge)

> 📊 **Hands-on Kubernetes Observability Lab**
>
> Deploy a complete Prometheus and Grafana monitoring platform on a single-node Kubernetes cluster using Helm, collect Kubernetes/node/pod metrics, build dashboards through the Grafana API, and validate alerting under synthetic workload.

---

## 📌 Table of Contents

* [🎯 Objectives](#-objectives)
* [🏗️ Architecture](#️-architecture)
* [🛠️ Technology Stack](#️-technology-stack)
* [📋 Prerequisites](#-prerequisites)
* [☁️ Lab Environment](#️-lab-environment)
* [🔧 Task 1 — Install and Verify Toolchain](#-task-1--install-and-verify-the-full-toolchain)
* [📊 Task 2 — Deploy Monitoring Stack](#-task-2--deploy-the-prometheus-and-grafana-monitoring-stack)
* [📈 Task 3 — Build Grafana Dashboards](#-task-3--build-and-validate-grafana-dashboards)
* [🚨 Alert Validation](#-alert-validation)
* [🧪 End-to-End Verification](#-end-to-end-verification)
* [🚨 Troubleshooting](#-troubleshooting)
* [📁 Repository Structure](#-repository-structure)
* [🎓 Learning Outcomes](#-learning-outcomes)
* [🏁 Conclusion](#-conclusion)

---

# 🎯 Objectives

By completing this lab, you will learn how to:

* 🚀 Deploy a single-node Kubernetes cluster.
* 📦 Install and manage Kubernetes applications with Helm.
* 📊 Deploy the `kube-prometheus-stack`.
* 🔍 Monitor Kubernetes nodes, pods, namespaces, and workloads.
* 🧩 Configure Prometheus ServiceMonitors.
* 📜 Create custom `PrometheusRule` resources.
* 🚨 Build Kubernetes alerting rules.
* 📈 Create Grafana dashboards using the HTTP API.
* 🔄 Configure dashboard auto-refresh.
* 🧪 Generate synthetic CPU and memory workloads.
* ⚡ Validate real-time metric collection.
* 🔥 Verify Prometheus alert state transitions.
* 🧹 Clean up test workloads and validate recovery.

---

# 🏗️ Architecture

The completed lab creates the following observability architecture:

```text
                         ☁️ AWS EC2 Ubuntu
                                │
                                ▼
                       ┌──────────────────┐
                       │       K3s        │
                       │ Single Node K8s  │
                       └────────┬─────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        Kubernetes Pods     Node Metrics     Cluster State
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                  ┌────────────────────────┐
                  │      Prometheus        │
                  │       :9090            │
                  │                        │
                  │ • Metrics Collection   │
                  │ • PromQL               │
                  │ • Alert Evaluation     │
                  └───────────┬────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
           Node Exporter  Kube-State    ServiceMonitors
                            Metrics
                              │
                              ▼
                     ┌────────────────┐
                     │  Alertmanager  │
                     │                │
                     │ Alert Routing  │
                     └────────────────┘

                              │
                              ▼
                     ┌────────────────┐
                     │    Grafana     │
                     │   NodePort     │
                     │                │
                     │ Dashboards     │
                     │ Visualization  │
                     └────────────────┘
```

---

# 🛠️ Technology Stack

| Technology            | Purpose                                 |
| --------------------- | --------------------------------------- |
| ☸️ Kubernetes         | Container orchestration                 |
| 🟡 K3s                | Lightweight Kubernetes distribution     |
| 🐳 Docker             | Container runtime                       |
| ⛵ Helm                | Kubernetes package manager              |
| 🟠 Prometheus         | Metrics collection and alert evaluation |
| 🟢 Grafana            | Metrics visualization                   |
| 🚨 Alertmanager       | Alert management                        |
| 📊 Node Exporter      | Host/node metrics                       |
| 🔎 kube-state-metrics | Kubernetes object-state metrics         |
| 🔥 PromQL             | Prometheus query language               |
| ☁️ AWS EC2            | Lab infrastructure                      |
| 🐧 Ubuntu             | Operating system                        |
| 🌐 HTTP API           | Prometheus/Grafana automation           |
| 📜 YAML               | Kubernetes and Helm configuration       |

---

# 📋 Prerequisites

You should have basic knowledge of:

* Linux command line
* Linux file permissions
* Process management
* Kubernetes Pods
* Kubernetes Deployments
* Kubernetes Services
* Kubernetes Namespaces
* YAML configuration
* Basic PromQL

---

# ☁️ Lab Environment

The lab runs on:

```text
AWS EC2
   │
   └── Ubuntu Linux
        │
        └── K3s
             │
             └── Single Kubernetes Node
```

The monitoring stack will be deployed inside:

```text
monitoring
```

namespace.

---

# 🔧 Task 1 — Install and Verify the Full Toolchain

## 🔹 Step 1.1 — Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

Verify OS:

```bash
cat /etc/os-release
```

---

## 🔹 Step 1.2 — Install Docker

Install Docker from the official Docker distribution channel.

Verify:

```bash
docker --version
```

Check service:

```bash
sudo systemctl status docker
```

Expected:

```text
Active: active (running)
```

Enable Docker:

```bash
sudo systemctl enable docker
```

---

# ☸️ Step 1.3 — Install K3s

Install K3s:

```bash
curl -sfL https://get.k3s.io | sh -
```

Check service:

```bash
sudo systemctl status k3s
```

Expected:

```text
Active: active (running)
```

---

# 🔐 Step 1.4 — Configure kubectl Access

K3s creates the Kubernetes configuration at:

```text
/etc/rancher/k3s/k3s.yaml
```

Set permissions:

```bash
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
```

Verify:

```bash
kubectl get nodes
```

Expected:

```text
NAME       STATUS   ROLES                  AGE   VERSION
<node>     Ready    control-plane,master   ...   ...
```

🎯 **Acceptance Criterion:**

```text
STATUS = Ready
```

---

# 🔎 Step 1.5 — Verify Kubernetes System Pods

```bash
kubectl get pods -A
```

System namespaces should contain healthy workloads.

Check for problematic states:

```bash
kubectl get pods -A | grep -E \
'CrashLoopBackOff|Pending|Error|ImagePullBackOff'
```

The command should return no problematic pods.

---

# ⛵ Step 1.6 — Install Helm

Install Helm using the official installation method.

Verify:

```bash
helm version
```

Expected:

```text
version.BuildInfo{...}
```

---

# 📦 Step 1.7 — Add Helm Repositories

Add Prometheus Community:

```bash
helm repo add prometheus-community \
https://prometheus-community.github.io/helm-charts
```

Add Grafana:

```bash
helm repo add grafana \
https://grafana.github.io/helm-charts
```

Update repositories:

```bash
helm repo update
```

Verify:

```bash
helm repo list
```

Expected repositories:

```text
prometheus-community
grafana
```

---

# 🔎 Step 1.8 — Search for kube-prometheus-stack

```bash
helm search repo kube-prometheus-stack
```

Expected:

```text
prometheus-community/kube-prometheus-stack
```

This confirms that the Helm repository cache is working.

---

# 📊 Task 2 — Deploy the Prometheus and Grafana Monitoring Stack

## 🔹 Step 2.1 — Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

Verify:

```bash
kubectl get namespace monitoring
```

---

# 📝 Step 2.2 — Create Helm Values File

Create:

```bash
mkdir -p ~/k8s-monitoring
cd ~/k8s-monitoring
```

Create:

```bash
nano values.yaml
```

Example configuration:

```yaml
prometheus:
  prometheusSpec:
    retention: 15d

    serviceMonitorSelectorNilUsesHelmValues: false

grafana:
  enabled: true

  service:
    type: NodePort
    nodePort: 30300

alertmanager:
  enabled: true

nodeExporter:
  enabled: true

kubeStateMetrics:
  enabled: true
```

### 📌 Configuration Summary

```text
Prometheus Retention     → 15 days
Grafana Service Type     → NodePort
Grafana NodePort         → 30300
Alertmanager             → Enabled
Node Exporter            → Enabled
kube-state-metrics       → Enabled
```

> 💡 The NodePort `30300` is within Kubernetes' standard NodePort range of `30000-32767`.

---

# 🚀 Step 2.3 — Install kube-prometheus-stack

```bash
helm install monitoring \
prometheus-community/kube-prometheus-stack \
--namespace monitoring \
--values values.yaml
```

Check release:

```bash
helm list -n monitoring
```

Expected:

```text
NAME        NAMESPACE    STATUS
monitoring  monitoring   deployed
```

---

# ⏳ Step 2.4 — Wait for Monitoring Pods

```bash
kubectl get pods -n monitoring -w
```

Wait until all components become ready.

Check:

```bash
kubectl get pods -n monitoring
```

Expected components include:

```text
prometheus
grafana
alertmanager
node-exporter
kube-state-metrics
```

Every container should show:

```text
READY
N/N
```

---

# 🔎 Step 2.5 — Verify Services

```bash
kubectl get svc -n monitoring
```

Locate Grafana:

```bash
kubectl get svc -n monitoring | grep grafana
```

Expected:

```text
grafana    NodePort    ...    3000:30300/TCP
```

---

# 🌐 Step 2.6 — Verify Grafana Health

Run:

```bash
curl -fsSL \
http://localhost:30300/api/health
```

Expected response contains:

```json
{
  "database": "ok"
}
```

🎯 This confirms that Grafana is running and its internal database is initialized.

---

# 🔍 Step 2.7 — Access Prometheus

Find Prometheus service:

```bash
kubectl get svc -n monitoring | grep prometheus
```

Port-forward:

```bash
kubectl port-forward \
-n monitoring \
svc/monitoring-kube-prometheus-prometheus \
9090:9090
```

Prometheus is then available at:

```text
http://localhost:9090
```

Verify:

```bash
curl -fsSL http://localhost:9090/-/ready
```

---

# 🚨 Task 2 — Configure Prometheus Alert Rules

## 🔹 Step 2.8 — Create PrometheusRule

Create:

```bash
nano prometheus-rules.yaml
```

Example:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: kubernetes-custom-alerts
  namespace: monitoring
  labels:
    release: monitoring
spec:
  groups:

    - name: kubernetes.custom.rules

      rules:

        - alert: PodCrashLooping
          expr: |
            increase(kube_pod_container_status_restarts_total[5m]) > 0
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Pod is restarting repeatedly"
            description: "A Kubernetes pod has restarted during the last five minutes."

        - alert: NodeMemoryPressureHigh
          expr: |
            (
              1 -
              node_memory_MemAvailable_bytes /
              node_memory_MemTotal_bytes
            ) * 100 > 80
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Node memory utilization is high"
            description: "Node memory utilization has remained above 80 percent for five minutes."

        - alert: PodNotRunning
          expr: |
            kube_pod_status_phase{
              phase!~"Running|Succeeded"
            } > 0
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Pod is not running"
            description: "A pod has remained in a non-running state for more than five minutes."
```

Apply:

```bash
kubectl apply -f prometheus-rules.yaml
```

---

# 🔎 Step 2.9 — Verify PrometheusRule

```bash
kubectl get prometheusrules -n monitoring
```

Inspect:

```bash
kubectl describe prometheusrule \
kubernetes-custom-alerts \
-n monitoring
```

---

# 📡 Step 2.10 — Verify Rules Through Prometheus API

With Prometheus port-forward active:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

Filter alert names:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules \
| grep -E \
'PodCrashLooping|NodeMemoryPressureHigh|PodNotRunning'
```

The rules should appear under an alerting-rule group.

---

# 🔥 Task 2 — Generate Synthetic Workload

Create a stress deployment:

```bash
kubectl create deployment stress \
--image=progrium/stress \
-n monitoring
```

Scale to two replicas:

```bash
kubectl scale deployment stress \
--replicas=2 \
-n monitoring
```

Verify:

```bash
kubectl get pods -n monitoring -l app=stress
```

---

# 🧪 Step 2.11 — Verify Stress Metrics

Query Prometheus:

```bash
curl -fsSL --get \
--data-urlencode \
'query=rate(container_cpu_usage_seconds_total[2m])' \
http://localhost:9090/api/v1/query
```

The result should contain:

```text
"result": [...]
```

Look for:

```text
metric.pod
```

matching your stress workload pods.

---

# 📈 Task 3 — Build and Validate Grafana Dashboards

## 🔹 Step 3.1 — Verify Grafana Datasource

Retrieve Grafana credentials from the Kubernetes secret:

```bash
kubectl get secret \
monitoring-grafana \
-n monitoring \
-o jsonpath="{.data.admin-password}" \
| base64 -d
```

Save the password:

```bash
export GRAFANA_PASSWORD='<password>'
```

Query datasources:

```bash
curl -fsSL \
-u "admin:${GRAFANA_PASSWORD}" \
http://localhost:30300/api/datasources
```

Confirm that a Prometheus datasource exists.

---

# 📊 Step 3.2 — Recommended Dashboard 1

### Dashboard Name

```text
Kubernetes Cluster Overview
```

Recommended panels:

```text
┌─────────────────────────────────────────────┐
│       Kubernetes Cluster Overview            │
├─────────────────────┬───────────────────────┤
│ Cluster CPU %       │ Cluster Memory %      │
├─────────────────────┴───────────────────────┤
│                                             │
│        Pod Count by Namespace               │
│                                             │
└─────────────────────────────────────────────┘
```

### CPU Query

```promql
100 - (
  avg(
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
)
```

### Memory Query

```promql
(
  1 -
  sum(node_memory_MemAvailable_bytes)
  /
  sum(node_memory_MemTotal_bytes)
) * 100
```

### Pod Count Query

```promql
count by (namespace) (
  kube_pod_info
)
```

---

# 📊 Step 3.3 — Recommended Dashboard 2

### Dashboard Name

```text
Kubernetes Pod Resource Usage
```

Panels:

```text
┌─────────────────────────────────────────────┐
│        Kubernetes Pod Resource Usage        │
├─────────────────────────────────────────────┤
│                                             │
│         Per-Pod CPU Usage                   │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│         Per-Pod Memory Usage                │
│                                             │
└─────────────────────────────────────────────┘
```

### Per-Pod CPU

```promql
sum by (pod) (
  rate(container_cpu_usage_seconds_total[5m])
)
```

### Per-Pod Memory

```promql
sum by (pod) (
  container_memory_working_set_bytes
)
```

---

# 🔄 Step 3.4 — Dashboard Configuration

Both dashboards should use:

```text
Auto Refresh: 30s
Default Time Range: Last 1 hour
Datasource: Prometheus
```

Dashboard creation should be performed through the Grafana HTTP API.

---

# 🌐 Step 3.5 — Verify Grafana API

Check home:

```bash
curl -fsSL \
-u "admin:${GRAFANA_PASSWORD}" \
http://localhost:30300/api/dashboards/home
```

Check dashboards:

```bash
curl -fsSL \
-u "admin:${GRAFANA_PASSWORD}" \
http://localhost:30300/api/search?type=dash-db
```

Expected:

```text
Kubernetes Cluster Overview
Kubernetes Pod Resource Usage
```

---

# 🔎 Step 3.6 — Verify Grafana Datasource

```bash
curl -fsSL \
-u "admin:${GRAFANA_PASSWORD}" \
http://localhost:30300/api/datasources
```

Confirm the Prometheus datasource has a valid:

```text
name
uid
url
type
```

Dashboard JSON must reference the correct datasource UID.

---

# 🚨 Alert Validation

## 🔥 Step 4.1 — Generate CPU Load

Inspect the stress deployment:

```bash
kubectl get deployment stress -n monitoring
```

Check resource metrics:

```bash
kubectl top pods -n monitoring
```

If metrics-server is available, this provides a quick view of resource consumption.

---

# 📡 Step 4.2 — Monitor Prometheus Alerts

Query:

```bash
curl -fsSL \
http://localhost:9090/api/v1/alerts
```

Search for custom alerts:

```bash
curl -fsSL \
http://localhost:9090/api/v1/alerts \
| grep -E \
'PodCrashLooping|NodeMemoryPressureHigh|PodNotRunning'
```

An alert can transition through:

```text
inactive
   ↓
pending
   ↓
firing
```

---

# 📊 Step 4.3 — Verify CPU Utilization

Query:

```bash
curl -fsSL --get \
--data-urlencode \
'query=100-(avg(irate(node_cpu_seconds_total{mode="idle"}[2m]))*100)' \
http://localhost:9090/api/v1/query
```

During sustained load, the result should increase.

The lab target is:

```text
CPU > 60%
```

for at least three minutes.

---

# 🔥 Step 4.4 — Verify Alert State

```bash
curl -fsSL \
http://localhost:9090/api/v1/alerts
```

Look for:

```json
"state": "pending"
```

or:

```json
"state": "firing"
```

and verify:

```text
labels.alertname
```

matches one of the configured alert names.

---

# 🧹 Step 4.5 — Remove Stress Workload

Delete the deployment:

```bash
kubectl delete deployment stress -n monitoring
```

Verify:

```bash
kubectl get pods -n monitoring
```

Wait for the workload pods to disappear.

---

# 📉 Step 4.6 — Verify CPU Recovery

After approximately five minutes:

```bash
curl -fsSL --get \
--data-urlencode \
'query=100-(avg(irate(node_cpu_seconds_total{mode="idle"}[2m]))*100)' \
http://localhost:9090/api/v1/query
```

Target:

```text
CPU < 20%
```

Check alerts:

```bash
curl -fsSL \
http://localhost:9090/api/v1/alerts
```

Expected:

```text
alerts = []
```

or alerts should be:

```text
inactive
```

---

# 🧪 End-to-End Verification

The complete observability pipeline is:

```text
             🔥 Synthetic Workload
                      │
                      ▼
              Kubernetes Pods
                      │
                      ▼
               Metrics Generated
                      │
                      ▼
              Prometheus Scrape
                      │
                      ▼
                  PromQL
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
       Grafana Panels       Alert Rules
            │                   │
            ▼                   ▼
      Visualization          Alert State
```

---

# ✅ Final Validation Checklist

### Kubernetes

* [ ] K3s installed
* [ ] Kubernetes node is `Ready`
* [ ] System pods are healthy
* [ ] kubectl works without sudo
* [ ] Helm installed

### Helm

* [ ] Prometheus Community repository added
* [ ] Grafana repository added
* [ ] Helm repository cache updated
* [ ] `kube-prometheus-stack` found

### Prometheus

* [ ] Prometheus deployed
* [ ] Prometheus pod is Ready
* [ ] 15-day retention configured
* [ ] Kubernetes metrics available
* [ ] Node metrics available
* [ ] Pod metrics available

### Grafana

* [ ] Grafana deployed
* [ ] Grafana NodePort configured
* [ ] Grafana health API returns database `ok`
* [ ] Prometheus datasource configured
* [ ] Dashboard 1 imported
* [ ] Dashboard 2 imported
* [ ] 30-second refresh configured
* [ ] One-hour default time range configured

### Alerting

* [ ] PrometheusRule created
* [ ] Pod crash-loop alert created
* [ ] Node memory alert created
* [ ] Non-running pod alert created
* [ ] Severity labels configured
* [ ] Summary annotations configured
* [ ] Description annotations configured
* [ ] Alert rules visible through Prometheus API

### Load Testing

* [ ] Stress deployment created
* [ ] Two replicas running
* [ ] CPU/memory metrics visible
* [ ] CPU load exceeds target
* [ ] Alert enters pending/firing
* [ ] Grafana shows elevated utilization
* [ ] Stress deployment removed
* [ ] CPU returns below target
* [ ] Alerts recover

---

# 🚨 Troubleshooting

## ❌ kubectl Cannot Access K3s

Check:

```bash
sudo systemctl status k3s
```

Check kubeconfig:

```bash
ls -l /etc/rancher/k3s/k3s.yaml
```

Fix permissions:

```bash
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
```

Test:

```bash
kubectl get nodes
```

---

## ❌ Monitoring Pod Stuck in Pending

Inspect:

```bash
kubectl describe pod \
-n monitoring \
<pod-name>
```

Check node resources:

```bash
kubectl describe node \
| grep -A5 "Allocated resources"
```

On a small EC2 instance, the complete monitoring stack can consume significant memory.

Check:

```bash
kubectl top nodes
```

If metrics-server is available.

---

## ❌ PrometheusRule Not Appearing

Check:

```bash
kubectl get prometheusrules -n monitoring
```

Inspect labels:

```bash
kubectl get prometheusrule \
kubernetes-custom-alerts \
-n monitoring \
-o jsonpath='{.metadata.labels}'
```

Inspect Prometheus configuration:

```bash
kubectl get prometheus \
-n monitoring \
-o yaml
```

Look for:

```text
ruleSelector
```

The Prometheus Operator must select the labels attached to your `PrometheusRule`.

---

## ❌ Grafana Says "Datasource Not Found"

List datasources:

```bash
curl -fsSL \
-u "admin:${GRAFANA_PASSWORD}" \
http://localhost:30300/api/datasources
```

Check:

```text
name
uid
type
url
```

Make sure the dashboard JSON references the correct datasource UID.

---

## ❌ Grafana Shows "No Data"

First test Prometheus directly:

```bash
curl -fsSL --get \
--data-urlencode \
'query=up' \
http://localhost:9090/api/v1/query
```

Then test the actual panel query.

For CPU:

```bash
curl -fsSL --get \
--data-urlencode \
'query=sum by (pod) (rate(container_cpu_usage_seconds_total[5m]))' \
http://localhost:9090/api/v1/query
```

If Prometheus has data but Grafana does not, investigate the Grafana datasource configuration.

---

## ❌ Alert Does Not Fire

Check rules:

```bash
curl -fsSL \
http://localhost:9090/api/v1/rules
```

Check alerts:

```bash
curl -fsSL \
http://localhost:9090/api/v1/alerts
```

Check Prometheus logs:

```bash
kubectl logs \
-n monitoring \
-l app.kubernetes.io/name=prometheus
```

---

# 📁 Suggested Repository Structure

```text
kubernetes-prometheus-grafana/
│
├── README.md
│
├── helm/
│   └── values.yaml
│
├── prometheus/
│   └── prometheus-rules.yaml
│
├── grafana/
│   ├── dashboard-cluster.json
│   ├── dashboard-pods.json
│   └── datasource.json
│
├── workloads/
│   └── stress-deployment.yaml
│
└── scripts/
    ├── verify-prometheus.sh
    ├── verify-grafana.sh
    └── load-test.sh
```

---

# 🎓 Learning Outcomes

After completing this project, you should understand:

### ☸️ Kubernetes Monitoring

How to monitor:

* Nodes
* Pods
* Namespaces
* Deployments
* Container resources

### 📊 Prometheus

How to:

* Scrape Kubernetes metrics
* Query metrics with PromQL
* Configure recording/alerting rules
* Use the Prometheus HTTP API

### 📈 Grafana

How to:

* Configure Prometheus datasources
* Create dashboards through an API
* Build resource utilization panels
* Configure dashboard refresh intervals

### 🚨 Alerting

How to:

* Create `PrometheusRule` resources
* Configure severity labels
* Create human-readable annotations
* Validate alert states

### 🧪 Observability Testing

How to:

```text
Generate Load
     ↓
Generate Metrics
     ↓
Prometheus Scrape
     ↓
PromQL Evaluation
     ↓
Alert State
     ↓
Grafana Visualization
     ↓
Workload Recovery
```

---

# 🔥 Production Monitoring Concepts

This lab introduces several concepts used in real Kubernetes environments:

```text
                    Kubernetes
                        │
             ┌──────────┴──────────┐
             │                     │
          Metrics                Events
             │                     │
             ▼                     ▼
        Prometheus             Kubernetes
             │                  API/State
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                     Grafana
                        │
              ┌─────────┴─────────┐
              │                   │
         Visualization         Alerting
              │                   │
              ▼                   ▼
          Engineers          Alertmanager
```

---

# 🏆 Best Practices

* ✅ Keep monitoring resources in a dedicated namespace.
* ✅ Manage Helm configuration through version-controlled values files.
* ✅ Avoid unnecessary `--set` overrides for production configuration.
* ✅ Use meaningful alert names.
* ✅ Add `severity` labels to alerts.
* ✅ Always provide useful alert summaries and descriptions.
* ✅ Monitor both infrastructure and Kubernetes object state.
* ✅ Test alerts using controlled synthetic workloads.
* ✅ Verify metrics directly in Prometheus before troubleshooting Grafana.
* ✅ Use APIs for repeatable dashboard provisioning.
* ✅ Monitor Prometheus resource consumption.
* ✅ Configure appropriate metric retention.
* ✅ Keep dashboards focused on actionable information.

---

# 🏁 Conclusion

This lab builds a complete Kubernetes observability platform from a bare Ubuntu EC2 instance.

The final environment provides:

```text
☁️ AWS EC2
   │
   ▼
☸️ K3s Kubernetes
   │
   ▼
⛵ Helm
   │
   ▼
📊 kube-prometheus-stack
   │
   ├── 🔥 Prometheus
   ├── 📈 Grafana
   ├── 🚨 Alertmanager
   ├── 🖥️ Node Exporter
   └── 🔎 kube-state-metrics
```

The project demonstrates the complete monitoring lifecycle:

```text
Workload
   ↓
Metrics Generation
   ↓
Prometheus Scraping
   ↓
PromQL
   ↓
Grafana Visualization
   ↓
PrometheusRule
   ↓
Alert State
   ↓
Alert Recovery
```

> 🚀 **Key takeaway:** Effective Kubernetes observability is not simply installing Prometheus and Grafana. It requires reliable metric collection, meaningful PromQL queries, actionable alerts, useful dashboards, automated validation, and continuous testing of the complete monitoring pipeline.

---

# 🌟 Lab Completion Status

```text
╔══════════════════════════════════════════════════════╗
║       KUBERNETES OBSERVABILITY LAB                  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  ☸️  Kubernetes / K3s             ✅ Completed       ║
║  ⛵  Helm                          ✅ Completed       ║
║  📊  Prometheus                   ✅ Completed       ║
║  📈  Grafana                      ✅ Completed       ║
║  🚨  Alertmanager                 ✅ Completed       ║
║  🖥️  Node Exporter                ✅ Completed       ║
║  🔎  kube-state-metrics            ✅ Completed       ║
║  🚨  Custom Alert Rules            ✅ Completed       ║
║  📊  Grafana Dashboards            ✅ Completed       ║
║  🧪  Synthetic Load Testing        ✅ Completed       ║
║  🔥  Alert State Validation        ✅ Completed       ║
║  🧹  Recovery Validation           ✅ Completed       ║
║                                                      ║
║          🚀 KUBERNETES OBSERVABILITY 🚀             ║
╚══════════════════════════════════════════════════════╝
```

---

## 👨‍💻 Author

**Hafiz Muhammad Salman**

**Cloud DevOps Engineer | Linux Administrator**

### 🔗 Technology Focus

```text
Linux Administration
Cloud Computing
AWS
Azure
Kubernetes
Docker
Helm
Prometheus
Grafana
DevOps
Monitoring & Observability
Infrastructure Automation
Cyber Security
```
