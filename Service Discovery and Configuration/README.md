<div align="center">

# 🔍 Service Discovery and Configuration

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![kind](https://img.shields.io/badge/kind-4285F4?style=for-the-badge&logo=kubernetes&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-CB171E?style=for-the-badge&logo=yaml&logoColor=white)

**A hands-on lab exploring static and dynamic service discovery in Prometheus — from file-based static targets to fully automated Kubernetes-native discovery.**

</div>

---

## 📑 Table of Contents

- [🎯 Lab Objectives](#-lab-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🧩 Key Concepts](#-key-concepts)
- [📌 Task 1: Configure Static Service Discovery in Prometheus](#-task-1-configure-static-service-discovery-in-prometheus)
- [☸️ Task 2: Monitor a Dynamic Kubernetes Environment](#️-task-2-monitor-a-dynamic-kubernetes-environment)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [✅ Lab Validation and Testing](#-lab-validation-and-testing)
- [🧹 Cleanup](#-cleanup)
- [🏁 Conclusion](#-conclusion)

---

## 🎯 Lab Objectives

By the end of this lab, you will be able to:

| # | Objective |
|---|-----------|
| 1 | Understand the concepts of static and dynamic service discovery in Prometheus |
| 2 | Configure Prometheus for static service discovery using file-based targets |
| 3 | Implement dynamic service discovery using Kubernetes integration |
| 4 | Set up a local Kubernetes cluster for monitoring purposes |
| 5 | Configure Prometheus to automatically discover and monitor services in Kubernetes |
| 6 | Analyze service discovery metrics and validate monitoring configurations |
| 7 | Troubleshoot common service discovery issues |

## 📋 Prerequisites

Before starting this lab, you should have:

- ✅ Basic understanding of Linux command line operations
- ✅ Familiarity with YAML configuration files
- ✅ Basic knowledge of containerization concepts
- ✅ Understanding of monitoring fundamentals
- ✅ Previous experience with Prometheus basics (recommended)

## 🖥️ Lab Environment

> **☁️ Al Nafi Cloud Machine**
> Al Nafi provides Linux-based cloud machines for this lab. Simply click **Start Lab** to access your dedicated environment. The provided Linux machine is bare metal with no pre-installed tools — you will install all required components during the lab exercises.

## 🧩 Key Concepts

| Concept | Description |
|---------|-------------|
| **Static Service Discovery** | Monitoring targets are manually defined and remain fixed — either directly in `prometheus.yml` or via `file_sd_configs` — suited to stable, slowly-changing environments |
| **Dynamic Service Discovery** | Prometheus automatically detects targets as they're created, scaled, or destroyed — essential for containerized/cloud-native environments |
| **`file_sd_configs`** | A file-based discovery mechanism that watches a directory for target-list files and reloads them on a defined `refresh_interval` |
| **`kubernetes_sd_configs`** | Native Prometheus integration that queries the Kubernetes API for discoverable roles: `node`, `pod`, `service`, `endpoints`, `ingress` |
| **Relabeling** | The `relabel_configs` mechanism rewrites, filters, or maps discovered target labels (e.g., `__meta_kubernetes_*` meta-labels) before scraping |
| **`prometheus.io/scrape` annotations** | Kubernetes pod/service annotations (`scrape`, `port`, `path`) that opt a workload into automatic discovery without editing Prometheus config |
| **RBAC for Prometheus** | A `ServiceAccount` + `ClusterRole` + `ClusterRoleBinding` granting Prometheus read (`get`/`list`/`watch`) access to nodes, pods, services, and endpoints via the Kubernetes API |
| **kind (Kubernetes in Docker)** | A tool for running local, disposable Kubernetes clusters inside Docker containers — ideal for lab and CI environments |

---

## 📌 Task 1: Configure Static Service Discovery in Prometheus

### 🧰 Subtask 1.1: Install Required Tools

First, install Docker, Prometheus, and other essential tools on your Linux machine.

**Step 1: Update the system and install Docker**

```bash
# 🔄 Update package repository
sudo apt update && sudo apt upgrade -y

# 📦 Install required packages
sudo apt install -y curl wget apt-transport-https ca-certificates gnupg lsb-release

# 🔑 Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 📥 Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 🐳 Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 👤 Add current user to docker group
sudo usermod -aG docker $USER

# ▶️ Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

**Step 2: Install kubectl and kind for Kubernetes**

```bash
# ⎈ Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 🐋 Install kind (Kubernetes in Docker)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# ✅ Verify installations
docker --version
kubectl version --client
kind version
```

**Step 3: Log out and log back in to apply Docker group changes**

```bash
# 🔁 Log out and log back in, or use newgrp
newgrp docker
```

### ⚙️ Subtask 1.2: Set Up Prometheus with Static Service Discovery

**Step 1: Create directory structure for Prometheus**

```bash
# 📁 Create working directory
mkdir -p ~/prometheus-lab
cd ~/prometheus-lab

# 📁 Create subdirectories
mkdir -p config data targets
```

**Step 2: Create static targets configuration**

```yaml
# 🎯 Create static targets file
cat > targets/static-targets.yml << 'EOF'
- targets:
  - 'localhost:9090'
  - 'localhost:9100'
  - 'localhost:8080'
  labels:
    job: 'static-services'
    environment: 'development'
    team: 'platform'

- targets:
  - 'localhost:3000'
  - 'localhost:8000'
  labels:
    job: 'web-services'
    environment: 'development'
    team: 'frontend'
EOF
```

**Step 3: Create Prometheus configuration with static service discovery**

```yaml
# ⚙️ Create Prometheus configuration
cat > config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  # Static configuration for Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # File-based service discovery
  - job_name: 'file-based-discovery'
    file_sd_configs:
      - files:
          - '/etc/prometheus/targets/*.yml'
        refresh_interval: 30s
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [job]
        target_label: service_type

  # Static targets for demonstration
  - job_name: 'static-demo'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          service: 'prometheus'
          tier: 'monitoring'
EOF
```

**Step 4: Start Prometheus with static configuration**

```bash
# 🚀 Run Prometheus in Docker with static configuration
docker run -d \
  --name prometheus-static \
  -p 9090:9090 \
  -v $(pwd)/config/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/targets:/etc/prometheus/targets \
  -v $(pwd)/data:/prometheus \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.console.templates=/etc/prometheus/consoles \
  --web.enable-lifecycle
```

**Step 5: Verify static service discovery**

```bash
# ✅ Check if Prometheus is running
docker ps | grep prometheus-static

# 📄 Check Prometheus logs
docker logs prometheus-static

# 🌐 Test Prometheus web interface (you can access it via browser at http://localhost:9090)
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool
```

### 🖧 Subtask 1.3: Create Mock Services for Static Discovery

**Step 1: Create simple HTTP services to monitor**

```python
# 🛠️ Create a simple Python HTTP server script
cat > mock-service.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import sys
from urllib.parse import urlparse, parse_qs

class MetricsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            port = sys.argv[1] if len(sys.argv) > 1 else "8000"
            metrics = f'''# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{{method="GET",service="mock-service-{port}"}} 42

# HELP service_uptime_seconds Service uptime in seconds
# TYPE service_uptime_seconds gauge
service_uptime_seconds{{service="mock-service-{port}"}} 3600

# HELP memory_usage_bytes Memory usage in bytes
# TYPE memory_usage_bytes gauge
memory_usage_bytes{{service="mock-service-{port}"}} 1048576
'''
            self.wfile.write(metrics.encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with socketserver.TCPServer(("", port), MetricsHandler) as httpd:
        print(f"Mock service running on port {port}")
        httpd.serve_forever()
EOF

chmod +x mock-service.py
```

**Step 2: Start mock services**

```bash
# ▶️ Start mock services on different ports
python3 mock-service.py 8080 &
python3 mock-service.py 3000 &
python3 mock-service.py 8000 &

# ✅ Verify services are running
curl http://localhost:8080/metrics
curl http://localhost:3000/metrics
curl http://localhost:8000/metrics
```

**Step 3: Update static targets and reload Prometheus**

```bash
# 🔄 Update the static targets file with actual running services
cat > targets/static-targets.yml << 'EOF'
- targets:
  - 'localhost:8080'
  - 'localhost:3000'
  - 'localhost:8000'
  labels:
    job: 'mock-services'
    environment: 'development'
    discovery_type: 'static'
EOF

# 🔃 Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload
```

---

## ☸️ Task 2: Monitor a Dynamic Kubernetes Environment

### 🏗️ Subtask 2.1: Set Up Local Kubernetes Cluster

**Step 1: Create Kubernetes cluster using kind**

```yaml
# ⎈ Create kind cluster configuration
cat > kind-config.yml << 'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: prometheus-lab
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF

# 🚀 Create the cluster
kind create cluster --config=kind-config.yml

# ✅ Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Step 2: Deploy sample applications to Kubernetes**

```yaml
# 📦 Create namespace for demo applications
kubectl create namespace demo-apps

# 🚀 Create a sample web application deployment
cat > sample-app.yml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-web-app
  namespace: demo-apps
  labels:
    app: sample-web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sample-web-app
  template:
    metadata:
      labels:
        app: sample-web-app
        version: v1.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: web-app
        image: nginx:alpine
        ports:
        - containerPort: 80
        - containerPort: 8080
          name: metrics
---
apiVersion: v1
kind: Service
metadata:
  name: sample-web-app-service
  namespace: demo-apps
  labels:
    app: sample-web-app
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
spec:
  selector:
    app: sample-web-app
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: metrics
    port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: demo-apps
  labels:
    app: api-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
        version: v2.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/api/metrics"
    spec:
      containers:
      - name: api
        image: httpd:alpine
        ports:
        - containerPort: 80
        - containerPort: 9090
          name: metrics
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: demo-apps
  labels:
    app: api-service
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/api/metrics"
spec:
  selector:
    app: api-service
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP
EOF

# 🚀 Deploy the applications
kubectl apply -f sample-app.yml

# ✅ Verify deployments
kubectl get pods -n demo-apps
kubectl get services -n demo-apps
```

### 🔐 Subtask 2.2: Configure Prometheus for Kubernetes Service Discovery

**Step 1: Create Kubernetes service account and RBAC for Prometheus**

```yaml
# 📦 Create Prometheus namespace
kubectl create namespace monitoring

# 🔐 Create service account and RBAC
cat > prometheus-rbac.yml << 'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups:
  - extensions
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
EOF

kubectl apply -f prometheus-rbac.yml
```

**Step 2: Create Prometheus configuration with Kubernetes service discovery**

```yaml
# ⚙️ Create ConfigMap with Prometheus configuration for Kubernetes
cat > prometheus-k8s-config.yml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
    # Prometheus itself
    - job_name: 'prometheus'
      static_configs:
      - targets: ['localhost:9090']

    # Kubernetes API server
    - job_name: 'kubernetes-apiservers'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

    # Kubernetes nodes
    - job_name: 'kubernetes-nodes'
      kubernetes_sd_configs:
      - role: node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics

    # Kubernetes pods
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

    # Kubernetes services
    - job_name: 'kubernetes-services'
      kubernetes_sd_configs:
      - role: service
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name

    # Kubernetes service endpoints
    - job_name: 'kubernetes-service-endpoints'
      kubernetes_sd_configs:
      - role: endpoints
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name
      - source_labels: [__meta_kubernetes_pod_node_name]
        action: replace
        target_label: kubernetes_node
EOF

kubectl apply -f prometheus-k8s-config.yml
```

**Step 3: Deploy Prometheus to Kubernetes**

```yaml
# 🚀 Create Prometheus deployment
cat > prometheus-deployment.yml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus/'
          - '--web.console.libraries=/etc/prometheus/console_libraries'
          - '--web.console.templates=/etc/prometheus/consoles'
          - '--storage.tsdb.retention.time=200h'
          - '--web.enable-lifecycle'
        ports:
        - containerPort: 9090
        resources:
          requests:
            cpu: 200m
            memory: 1000Mi
          limits:
            cpu: 1000m
            memory: 2000Mi
        volumeMounts:
        - name: prometheus-config-volume
          mountPath: /etc/prometheus/
        - name: prometheus-storage-volume
          mountPath: /prometheus/
      volumes:
      - name: prometheus-config-volume
        configMap:
          defaultMode: 420
          name: prometheus-config
      - name: prometheus-storage-volume
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
  namespace: monitoring
  annotations:
    prometheus.io/scrape: 'true'
    prometheus.io/port: '9090'
spec:
  selector:
    app: prometheus
  type: NodePort
  ports:
  - port: 9090
    targetPort: 9090
    nodePort: 30090
EOF

kubectl apply -f prometheus-deployment.yml
```

**Step 4: Verify Kubernetes service discovery**

```bash
# ✅ Check if Prometheus is running in Kubernetes
kubectl get pods -n monitoring
kubectl get services -n monitoring

# 📄 Check Prometheus logs
kubectl logs -n monitoring deployment/prometheus

# 🔌 Port forward to access Prometheus UI
kubectl port-forward -n monitoring service/prometheus-service 9091:9090 &

# 🧪 Test service discovery endpoints
curl -s http://localhost:9091/api/v1/targets | python3 -m json.tool
```

### 🔄 Subtask 2.3: Validate Dynamic Service Discovery

**Step 1: Scale applications and observe discovery**

```bash
# 📈 Scale up the sample web application
kubectl scale deployment sample-web-app --replicas=5 -n demo-apps

# 📈 Scale up the API service
kubectl scale deployment api-service --replicas=4 -n demo-apps

# ✅ Check the scaled deployments
kubectl get pods -n demo-apps

# ⏳ Wait a moment for Prometheus to discover new targets
sleep 30

# 🔍 Check discovered targets
curl -s http://localhost:9091/api/v1/targets | python3 -m json.tool | grep -A 5 -B 5 "demo-apps"
```

**Step 2: Add new services dynamically**

```yaml
# ➕ Create a new service with Prometheus annotations
cat > dynamic-service.yml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynamic-service
  namespace: demo-apps
  labels:
    app: dynamic-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dynamic-service
  template:
    metadata:
      labels:
        app: dynamic-service
        tier: backend
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/health/metrics"
    spec:
      containers:
      - name: dynamic-app
        image: nginx:alpine
        ports:
        - containerPort: 80
        - containerPort: 8080
          name: metrics
---
apiVersion: v1
kind: Service
metadata:
  name: dynamic-service
  namespace: demo-apps
  labels:
    app: dynamic-service
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/health/metrics"
spec:
  selector:
    app: dynamic-service
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: metrics
    port: 8080
    targetPort: 8080
  type: ClusterIP
EOF

# 🚀 Deploy the new service
kubectl apply -f dynamic-service.yml

# ✅ Verify deployment
kubectl get pods -n demo-apps -l app=dynamic-service
kubectl get services -n demo-apps -l app=dynamic-service
```

**Step 3: Monitor service discovery changes**

```bash
# 📊 Create a script to monitor target changes
cat > monitor-targets.sh << 'EOF'
#!/bin/bash

echo "Monitoring Prometheus targets for changes..."
echo "Press Ctrl+C to stop"

while true; do
    echo "=== $(date) ==="
    echo "Total targets discovered:"
    curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
active_targets = data['data']['activeTargets']
print(f'Active targets: {len(active_targets)}')
for target in active_targets:
    labels = target.get('labels', {})
    job = labels.get('job', 'unknown')
    instance = labels.get('instance', 'unknown')
    namespace = labels.get('kubernetes_namespace', 'N/A')
    print(f'  - Job: {job}, Instance: {instance}, Namespace: {namespace}')
"
    echo ""
    sleep 30
done
EOF

chmod +x monitor-targets.sh

# ▶️ Run the monitoring script in background
./monitor-targets.sh &
MONITOR_PID=$!

# ⏳ Let it run for a few minutes, then stop
sleep 120
kill $MONITOR_PID
```

---

## 🛠️ Troubleshooting

<details>
<summary><strong>Issue 1: Prometheus Cannot Discover Kubernetes Services</strong></summary>

**Problem:** Services with annotations are not being discovered.

**Solution:**

```bash
# Check if the service has correct annotations
kubectl get service -n demo-apps sample-web-app-service -o yaml | grep -A 5 annotations

# Verify RBAC permissions
kubectl auth can-i get services --as=system:serviceaccount:monitoring:prometheus

# Check Prometheus configuration
kubectl get configmap prometheus-config -n monitoring -o yaml
```

</details>

<details>
<summary><strong>Issue 2: Targets Showing as Down</strong></summary>

**Problem:** Discovered targets appear as "DOWN" in Prometheus.

**Solution:**

```bash
# Check if the metrics endpoint is accessible
kubectl exec -n demo-apps deployment/sample-web-app -- wget -qO- localhost:8080/metrics

# Verify port configuration in annotations
kubectl get pods -n demo-apps -o yaml | grep -A 3 -B 3 prometheus.io

# Check network policies
kubectl get networkpolicies --all-namespaces
```

</details>

<details>
<summary><strong>Issue 3: File-based Service Discovery Not Working</strong></summary>

**Problem:** Static targets file changes are not reflected.

**Solution:**

```bash
# Check file permissions
ls -la targets/

# Verify Prometheus can read the file
docker exec prometheus-static cat /etc/prometheus/targets/static-targets.yml

# Force configuration reload
curl -X POST http://localhost:9090/-/reload
```

</details>

---

## ✅ Lab Validation and Testing

**Validation Step 1: Verify Static Service Discovery**

```bash
# Test static service discovery
echo "Testing static service discovery..."

# Check if static targets are loaded
curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
static_targets = [t for t in data['data']['activeTargets'] if 'static' in t.get('labels', {}).get('job', '')]
print(f'Static targets found: {len(static_targets)}')
for target in static_targets:
    print(f'  - {target[\"labels\"][\"instance\"]} ({target[\"health\"]})')
"
```

**Validation Step 2: Verify Dynamic Service Discovery**

```bash
# Test Kubernetes service discovery
echo "Testing Kubernetes service discovery..."

# Check if Kubernetes targets are discovered
curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
k8s_targets = [t for t in data['data']['activeTargets'] if 'kubernetes' in t.get('labels', {}).get('job', '')]
print(f'Kubernetes targets found: {len(k8s_targets)}')
for target in k8s_targets:
    job = target.get('labels', {}).get('job', 'unknown')
    namespace = target.get('labels', {}).get('kubernetes_namespace', 'N/A')
    print(f'  - Job: {job}, Namespace: {namespace}')
"
```

**Validation Step 3: Test Service Discovery Responsiveness**

```bash
# Create a test to verify discovery responsiveness
cat > test-discovery-responsiveness.sh << 'EOF'
#!/bin/bash

echo "Testing service discovery responsiveness..."

# Get initial target count
INITIAL_COUNT=$(curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(len(data['data']['activeTargets']))
")

echo "Initial target count: $INITIAL_COUNT"

# Create a new service
kubectl create deployment test-discovery --image=nginx:alpine -n demo-apps
kubectl expose deployment test-discovery --port=80 --target-port=80 -n demo-apps
kubectl annotate service test-discovery prometheus.io/scrape=true -n demo-apps
kubectl annotate service test-discovery prometheus.io/port=80 -n demo-apps

echo "Created new service, waiting for discovery..."

# Wait and check for new targets
for i in {1..10}; do
    sleep 15
    NEW_COUNT=$(curl -s http://localhost:9091/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(len(data['data']['activeTargets']))
")
    echo "Attempt $i: Target count is now $NEW_COUNT"
    
    if [ "$NEW_COUNT" -gt "$INITIAL_COUNT" ]; then
        echo "SUCCESS: New service discovered!"
        break
    fi
done

# Cleanup
kubectl delete deployment test-discovery -n demo-apps
kubectl delete service test-discovery -n demo-apps
EOF

chmod +x test-discovery-responsiveness.sh
./test-discovery-responsiveness.sh
```

---

## 🧹 Cleanup

```bash
# 🛑 Stop background processes
pkill -f "python3 mock-service.py"
pkill -f "kubectl port-forward"

# 🐳 Stop Docker containers
docker stop prometheus-static
docker rm prometheus-static

# ☸️ Delete Kubernetes resources
kubectl delete namespace demo-apps
kubectl delete namespace monitoring

# 🗑️ Delete kind cluster
kind delete cluster --name prometheus-lab

# 🧹 Clean up files
cd ~
rm -rf prometheus-lab
```

---

## 🏁 Conclusion

In this lab, you have successfully:

### 🎯 Key Accomplishments

- ✅ Implemented static service discovery using file-based configuration in Prometheus, learning how to manually define and manage monitoring targets
- ✅ Configured dynamic service discovery with Kubernetes integration, enabling automatic discovery of services and pods
- ✅ Set up a complete monitoring environment using open-source tools including Prometheus, Kubernetes (kind), and Docker
- ✅ Validated service discovery functionality by scaling applications and observing automatic target updates
- ✅ Learned troubleshooting techniques for common service discovery issues

### 🌍 Real-World Applications

- **Static service discovery** is suitable for stable environments where services don't change frequently, providing simple configuration and predictable behavior.
- **Dynamic service discovery** is essential for containerized and cloud-native environments where services are created, scaled, and destroyed automatically.
- **Kubernetes service discovery** uses annotations and labels to automatically configure monitoring, reducing manual configuration overhead.
- **Proper RBAC configuration** is crucial for Prometheus to access the Kubernetes API and discover services.
- **Service discovery responsiveness** depends on configuration parameters like refresh intervals and can be tuned based on requirements.

This knowledge is fundamental for implementing monitoring solutions in modern infrastructure, where services are dynamic and require automated discovery mechanisms. Understanding both static and dynamic approaches allows you to choose the right strategy based on your environment's characteristics and requirements.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al%20Nafi-Cybersecurity%20Training-blueviolet?style=for-the-badge)

</div>
