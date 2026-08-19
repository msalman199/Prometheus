# 🚀 Prometheus 

![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus\&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-Alerting-E6522C?logo=prometheus\&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Visualization-F46800?logo=grafana\&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node_Exporter-Metrics-E6522C?logo=prometheus\&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Monitoring-326CE5?logo=kubernetes\&logoColor=white)
![Thanos](https://img.shields.io/badge/Thanos-Long_Term_Storage-6B46C1)
![Linux](https://img.shields.io/badge/Linux-Administration-FCC624?logo=linux\&logoColor=black)
![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?logo=amazonaws\&logoColor=white)
![PromQL](https://img.shields.io/badge/PromQL-Querying-4285F4)

---

## 📌 Repository Purpose

This repository is a **hands-on Prometheus monitoring and observability laboratory** created as part of the **Al-Razzaq Programme**.

The primary purpose of this repository is to provide a practical, structured environment for learning how to **design, deploy, configure, secure, troubleshoot, scale, and operate Prometheus-based monitoring systems** in real-world Linux, cloud, Kubernetes, and DevOps environments.

Rather than focusing only on Prometheus theory, this repository emphasizes **practical implementation through progressive labs and real operational scenarios**.

Prometheus is designed to collect time-series metrics from configured targets, query those metrics using PromQL, evaluate rules, and generate alerts.

---

# 🎯 What This Repository Is Designed For

The repository is designed to develop practical skills in:

```text
                    ┌─────────────────────────┐
                    │       Applications       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │        Exporters         │
                    │ Node Exporter / Others   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Prometheus         │
                    │                          │
                    │  Metrics Collection      │
                    │  Time-Series Storage     │
                    │  PromQL                  │
                    │  Recording Rules         │
                    │  Alerting Rules          │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
             ┌─────────────┐          ┌──────────────┐
             │   Grafana   │          │ Alertmanager │
             │ Dashboards  │          │   Alerting   │
             └─────────────┘          └───────┬──────┘
                                              │
                                              ▼
                                      Notifications
```

The goal is to understand the **complete observability lifecycle**:

> **Collect → Store → Query → Visualize → Alert → Troubleshoot → Scale → Secure**

---

# 🧠 Learning Objectives

This repository helps develop the ability to:

* 📊 Collect infrastructure and application metrics.
* 🔎 Write and optimize PromQL queries.
* 📈 Build monitoring dashboards with Grafana.
* 🚨 Create effective alerting rules.
* 🛣️ Configure Alertmanager routing.
* 🛑 Reduce alert fatigue using inhibition strategies.
* ⚙️ Create recording rules for expensive PromQL expressions.
* 🔍 Monitor Kubernetes clusters.
* 📦 Monitor applications using exporters.
* 🔄 Implement service discovery.
* 📤 Monitor short-lived jobs with Pushgateway.
* 🌐 Scale Prometheus using federation.
* 🗄️ Implement long-term storage with Thanos.
* 🔐 Apply security practices to monitoring infrastructure.
* 🛠️ Troubleshoot Prometheus configuration and scraping problems.
* 🔗 Integrate Prometheus with CI/CD pipelines.
* 📋 Apply metric naming and cardinality best practices.

---

# 📚 Repository Learning Path

The repository is organized into progressive practical labs.

### 01 — Introduction to Prometheus

Learn the fundamentals of:

* Prometheus architecture
* Time-series metrics
* Targets
* Scraping
* Labels
* Prometheus configuration
* Basic monitoring workflows

---

### 02 — Prometheus Architecture Overview

Understand:

* Prometheus components
* Pull-based monitoring
* Time-series database concepts
* Exporters
* Alerting architecture
* Service discovery
* Federation

---

### 03 — Metric Types in Prometheus

Explore:

* Counters
* Gauges
* Histograms
* Summaries
* Metric labels
* Time-series characteristics

---

### 04 — Writing PromQL Queries

Develop practical skills with:

* Selectors
* Aggregations
* Functions
* Operators
* Rate calculations
* CPU analysis
* Memory analysis
* Network analysis
* Advanced PromQL

---

### 05 — Using Exporters with Prometheus

Learn how exporters expose application and infrastructure metrics for Prometheus collection.

Examples include:

* Node Exporter
* System metrics
* Custom exporters
* Exporter-based monitoring architecture

---

### 06 — Service Discovery and Configuration

Understand how Prometheus discovers monitoring targets and how configuration can be structured for dynamic environments.

Prometheus supports both static configuration and service discovery mechanisms.

---

### 07 — Setting Up Alerts in Prometheus

Learn how to:

* Create alerting rules
* Configure thresholds
* Add labels
* Add annotations
* Define `for` durations
* Connect Prometheus to Alertmanager

---

### 08 — Advanced Alerting Strategies

Implement advanced alerting concepts including:

* Multi-condition alerts
* CPU alerts
* Memory alerts
* Composite alerts
* Predictive alerts
* Alertmanager routing
* Severity-based notifications
* Inhibition rules
* Webhook notifications

---

### 09 — Creating and Using Recording Rules

Learn how recording rules can pre-compute frequently used or expensive PromQL expressions.

This helps improve query performance and makes dashboards and alerts easier to maintain.

---

### 10 — Analyzing Performance Metrics

Analyze:

* CPU utilization
* Memory usage
* Disk performance
* Network traffic
* System bottlenecks
* Performance trends

---

### 11 — Grafana Integration with Prometheus

Connect Prometheus to Grafana and build dashboards for:

* Infrastructure monitoring
* Resource utilization
* Application metrics
* Alert visualization
* Performance analysis

---

### 12 — Monitoring Kubernetes with Prometheus

Apply Prometheus monitoring to Kubernetes environments.

Topics include:

* Cluster monitoring
* Node metrics
* Pod metrics
* Kubernetes resources
* Service monitoring
* Prometheus Operator concepts
* Grafana visualization

---

### 13 — Pushgateway for Short-Lived Jobs

Learn how to monitor batch and short-lived workloads that cannot be scraped continuously.

The lab demonstrates:

```text
Short-Lived Job
      ↓
Pushgateway
      ↓
Prometheus
      ↓
Metrics
```

---

### 14 — Configuring Retention Policies

Understand Prometheus storage management and configure appropriate retention strategies for monitoring environments.

---

### 15 — Scaling Prometheus with Federation

Explore Prometheus federation for environments where monitoring needs to scale across multiple Prometheus servers.

Example architecture:

```text
             ┌─────────────────┐
             │ Global Prometheus│
             └────────┬────────┘
                      │
            ┌─────────┼─────────┐
            ▼         ▼         ▼
       Prometheus A  Prometheus B  Prometheus C
            │         │         │
          Nodes      Apps      Kubernetes
```

---

### 16 — Long-Term Storage with Thanos

Explore long-term Prometheus storage and scalable querying using Thanos.

The goal is to understand how Prometheus deployments can be extended beyond local time-series retention.

---

### 17 — Securing Prometheus

Apply security concepts such as:

* Access control
* Network restrictions
* Secure configuration
* Service-account permissions
* Endpoint protection
* Monitoring security

---

### 18 — Troubleshooting Prometheus

Practice diagnosing:

* Configuration errors
* Scrape failures
* Target failures
* Service problems
* Rule errors
* Connectivity problems
* Prometheus logs

Prometheus provides configuration validation and supports configuration reloads when lifecycle management is enabled.

---

### 19 — Using Prometheus with CI/CD

Integrate monitoring into DevOps pipelines to track:

* Deployment metrics
* Pipeline performance
* Deployment success/failure
* Application health
* CI/CD events

---

### 20 — Metric Best Practices

Learn production-oriented metric design principles including:

* Naming conventions
* Units
* Labels
* Cardinality control
* Recording rules
* Alerting design
* Query efficiency

---

# 🛠️ Technology Stack

| Technology           | Purpose                                                    |
| -------------------- | ---------------------------------------------------------- |
| 🟠 **Prometheus**    | Metrics collection, storage, querying and alert evaluation |
| 🟠 **Alertmanager**  | Alert routing, grouping and inhibition                     |
| 🟠 **Node Exporter** | Linux system metrics                                       |
| 🟠 **Grafana**       | Metrics visualization and dashboards                       |
| 🟣 **Thanos**        | Prometheus scalability and long-term storage               |
| 🔵 **Kubernetes**    | Container orchestration monitoring                         |
| 🐧 **Linux**         | Infrastructure and system administration                   |
| ☁️ **AWS**           | Cloud infrastructure                                       |
| 📜 **PromQL**        | Metrics querying and analysis                              |
| 🐍 **Python**        | Custom monitoring and webhook integrations                 |
| 🔧 **Pushgateway**   | Short-lived job metrics                                    |
| ⚙️ **CI/CD**         | DevOps monitoring integration                              |

---

# 🔬 Practical Approach

Every lab is intended to follow a practical engineering workflow:

```text
1. Understand
      ↓
2. Install
      ↓
3. Configure
      ↓
4. Deploy
      ↓
5. Test
      ↓
6. Monitor
      ↓
7. Troubleshoot
      ↓
8. Optimize
      ↓
9. Secure
      ↓
10. Scale
```

This approach mirrors the lifecycle of monitoring infrastructure used in production environments.

---

# 📁 Repository Structure

The repository contains dedicated directories for the individual labs:

```text
Prometheus/
│
├── Advanced Alerting Strategies/
├── Analyzing Performance Metrics/
├── Configuring Retention Policies/
├── Creating and Using Recording Rules/
├── Grafana Integration with Prometheus/
├── Introduction to Prometheus/
├── Long-Term Storage with Thanos/
├── Metric Best Practices/
├── Metric Types in Prometheus/
├── Monitoring Kubernetes with Prometheus/
├── Prometheus Architecture Overview/
├── Pushgateway for Short-Lived Jobs/
├── Scaling Prometheus with Federation/
├── Securing Prometheus/
├── Service Discovery and Configuration/
├── Setting Up Alerts in Prometheus/
├── Troubleshooting Prometheus/
├── Using Exporters with Prometheus/
├── Using Prometheus with CI_CD/
├── Writing PromQL Queries/
│
├── alertmanager
├── alertmanager.yml
├── amtool
├── cpu_stress.sh
├── webhook_receiver.py
│
├── LICENSE
├── NOTICE
└── README.md
```

The repository currently contains these practical lab areas and supporting monitoring files.

---

# 🎓 Skills Demonstrated

Completing the repository demonstrates practical exposure to:

```text
Prometheus
   │
   ├── Metrics Collection
   ├── PromQL
   ├── Alerting
   ├── Recording Rules
   ├── Exporters
   ├── Service Discovery
   ├── Federation
   ├── Retention
   ├── Security
   └── Troubleshooting
          │
          ▼
     Observability
          │
     ┌────┴────┐
     ▼         ▼
  Grafana   Alertmanager
     │         │
     ▼         ▼
Dashboards  Notifications
               │
               ▼
            Thanos
               │
               ▼
       Long-Term Storage
```

---

# 🌟 Why This Repository Matters

Monitoring is a fundamental part of modern **DevOps, Cloud, SRE, and Kubernetes engineering**.

A production system is not complete simply because the application is deployed. Engineers also need to know:

* Is the application healthy?
* Is CPU utilization increasing?
* Is memory being exhausted?
* Is disk space running out?
* Are services responding?
* Are deployments successful?
* Are Kubernetes workloads healthy?
* Are alerts reaching the correct teams?
* Can historical metrics be retained?
* Can monitoring scale with infrastructure growth?

This repository provides practical exercises for answering those questions using the Prometheus ecosystem.

---

# 🚀 Real-World Architecture

The concepts in this repository can be extended into a production observability platform:

```text
                         Cloud / Data Center
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
       Linux Servers        Kubernetes             Apps
          │                     │                     │
          ▼                     ▼                     ▼
    Node Exporter          Kube Metrics          App Metrics
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                ▼
                         ┌──────────────┐
                         │  Prometheus  │
                         └──────┬───────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
             PromQL         Grafana       Alertmanager
                 │                             │
                 │                             ▼
                 │                       Notifications
                 │
                 ▼
              Thanos
                 │
                 ▼
        Long-Term Storage
```

---

# 🧪 Repository Status

**Status:** 🚧 Practical Learning & Lab Repository

**Program:** Al-Razzaq Programme

**Focus:** Prometheus, Monitoring, Observability, Alerting, SRE and DevOps

**Repository:** [msalman199/Prometheus](https://github.com/msalman199/Prometheus?utm_source=chatgpt.com)

---

# 📖 Official Prometheus Resources

Prometheus officially describes itself as a systems and service monitoring system with a multidimensional time-series data model, PromQL, an HTTP pull model, service discovery, and alerting capabilities.

* [Prometheus Documentation](https://prometheus.io/docs/?utm_source=chatgpt.com)
* [Prometheus Getting Started](https://prometheus.io/docs/prometheus/latest/getting_started/?utm_source=chatgpt.com)
* [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/?utm_source=chatgpt.com)
* [Prometheus Installation](https://prometheus.io/docs/prometheus/latest/installation/?utm_source=chatgpt.com)

---

# ⭐ Final Purpose

> **The purpose of this repository is to build practical, production-oriented expertise in Prometheus and the wider observability ecosystem through hands-on labs covering monitoring, PromQL, alerting, visualization, exporters, Kubernetes, security, troubleshooting, scalability, federation, long-term storage, and CI/CD integration.**

This repository is intended to serve as both a **learning portfolio and a practical reference** for implementing Prometheus-based monitoring in Linux, Cloud, Kubernetes, and DevOps environments.

---

## 🚀 Learn → Build → Monitor → Alert → Troubleshoot → Secure → Scale

**Prometheus | Grafana | Alertmanager | Node Exporter | Thanos | Kubernetes | PromQL | DevOps | SRE**
