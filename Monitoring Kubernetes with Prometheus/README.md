<div align="center">

# ☸️ Monitoring Kubernetes with Prometheus

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Minikube](https://img.shields.io/badge/Minikube-FF6E42?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red?style=for-the-badge)

**Deploy a production-grade Prometheus monitoring stack on Minikube, with RBAC-scoped service discovery across nodes, cAdvisor, Node Exporter, and annotated pods.**

</div>

---

## 📖 Table of Contents

- [🎯 Objectives](#-objectives)
- [📋 Prerequisites](#-prerequisites)
- [🖥️ Lab Environment](#️-lab-environment)
- [🔑 Key Concepts](#-key-concepts)
- [🚀 Task 1: Install and Verify the Full Toolchain](#-task-1-install-and-verify-the-full-toolchain)
- [📊 Task 2: Deploy Prometheus and Instrument the Cluster](#-task-2-deploy-prometheus-and-instrument-the-cluster)
- [🎯 Expected Outcomes](#-expected-outcomes)
- [✅ Conclusion](#-conclusion)

---

## 🎯 Objectives

| # | Objective |
|---|-----------|
| 1 | Deploy a production-grade Prometheus monitoring stack on a single-node Kubernetes cluster running in Minikube |
| 2 | Configure Prometheus service discovery to automatically scrape metrics from Kubernetes nodes, pods, and the cAdvisor container runtime |
| 3 | Demonstrate cluster observability by querying live resource metrics through the Prometheus HTTP API |

## 📋 Prerequisites

| # | Requirement |
|---|-------------|
| 1 | Comfort with Linux command-line operations including file editing, process management, and reading command output |
| 2 | Conceptual understanding of Kubernetes primitives: pods, deployments, services, namespaces, ConfigMaps, and RBAC |
| 3 | Familiarity with YAML syntax sufficient to write resource manifests without a template |

## 🖥️ Lab Environment

> You will work on a dedicated **AWS EC2 Ubuntu instance** provided by Al Nafi. The instance has a base Ubuntu installation; you will install all required tools in Task 1.

## 🔑 Key Concepts

| Concept | Description |
|---------|-------------|
| **ServiceAccount** | An identity assigned to a pod that controls its Kubernetes API permissions |
| **ClusterRole / RBAC** | Cluster-scoped permission set granting read access to specific resources (nodes, pods, services, endpoints, `/metrics`) |
| **cAdvisor** | The container advisor daemon embedded in the kubelet, exposing per-container resource metrics |
| **DaemonSet** | A controller that runs exactly one pod per node — used here for Node Exporter |
| **Node Exporter** | Prometheus exporter that reads kernel-level host metrics via mounted `/proc`, `/sys`, and `/` |
| **`prometheus.io/scrape` annotation** | Pod-level annotation that drives Prometheus's annotation-based auto-discovery |
| **NodePort Service** | Exposes a cluster-internal port externally, enabling access via `minikube service` |
| **emptyDir Volume** | Ephemeral pod storage — used here for Prometheus's in-cluster TSDB |

---

## 🚀 Task 1: Install and Verify the Full Toolchain

### Requirement 1.1

Design and implement a repeatable installation sequence that produces a working Docker engine, the `kubectl` CLI, and Minikube on the bare Ubuntu instance. Every tool must be installed from its official distribution channel. After installation, start a Minikube cluster using the Docker driver with at least 2 CPUs and 4 GiB of memory allocated, then confirm the cluster control plane is reachable.

**1. System prerequisites** 📦

```bash
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y curl wget apt-transport-https ca-certificates gnupg lsb-release
```

**2. Docker engine** 📦

```bash
# Official guide if the URL below changes: https://docs.docker.com/engine/install/ubuntu/
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu %s stable\n' \
  "$(dpkg --print-architecture)" "$(lsb_release -cs)" \
  | sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker "$USER"
newgrp docker <<'DOCKERTEST'
docker run --rm hello-world
DOCKERTEST
```

> **Troubleshoot this step:**
> You see `E: Malformed entry 1 in list file /etc/apt/sources.list.d/docker.list` — the file contains a literal backslash or newline.
> Inspect with `cat /etc/apt/sources.list.d/docker.list`; it must be one unbroken line. Delete it with `sudo rm /etc/apt/sources.list.d/docker.list` and re-run the `printf | tee` command above.
> Official reference: https://docs.docker.com/engine/install/ubuntu/

**3. kubectl** 📦

```bash
# Official guide if the URL below changes: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
KUBECTL_VERSION="$(curl -fsSL https://dl.k8s.io/release/stable.txt)"
curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

> **Troubleshoot this step:**
> You see `curl: (22) The requested URL returned error: 404` — the stable version string fetch failed and produced a malformed path.
> Run `curl -fsSL https://dl.k8s.io/release/stable.txt` alone to confirm it returns a version string like `v1.30.2`; if the endpoint is unreachable, check your instance's outbound internet access with `curl -fsSL https://example.com`.
> Official reference: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

**4. Minikube** 📦

```bash
# Official guide if the URL below changes: https://minikube.sigs.k8s.io/docs/start/
curl -fsSL https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 -o minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
```

> **Troubleshoot this step:**
> You see `minikube: command not found` after installation — the binary was not placed on PATH.
> Confirm the install target with `ls -lh /usr/local/bin/minikube`; if missing, re-run the `sudo install` command and verify `/usr/local/bin` is in your PATH with `echo $PATH`.
> Official reference: https://minikube.sigs.k8s.io/docs/start/

**5. Start the cluster** ▶️

```bash
minikube start --driver=docker --cpus=2 --memory=4096
minikube status
kubectl cluster-info
kubectl get nodes
```

> **Troubleshoot this step:**
> You see `Exiting due to PROVIDER_DOCKER_NOT_RUNNING: Docker is not running` — the current shell session does not yet have the docker group applied.
> Run `newgrp docker` to apply the group in the current shell without logging out, then retry `minikube start`.
> Official reference: https://minikube.sigs.k8s.io/docs/drivers/docker/

**Acceptance criteria:**

- [ ] `kubectl get nodes` returns one node with status `Ready`.
- [ ] `minikube status` shows `host: Running`, `kubelet: Running`, and `apiserver: Running` on three separate lines.

### Requirement 1.2

Design and implement a verification procedure that confirms `kubectl` can communicate with the cluster API server and that the Docker daemon is accessible without `sudo`. The procedure must produce unambiguous pass/fail output for each check so that any misconfiguration is visible before proceeding. 🔍

```bash
# Confirm kubectl API access
kubectl get namespaces
kubectl get pods -A

# Confirm Docker access without sudo
docker ps
docker info | grep -i "server version"
```

**Acceptance criteria:**

- [ ] `kubectl get namespaces` lists at least the `default`, `kube-system`, and `kube-public` namespaces without an authentication error.
- [ ] `docker ps` runs without `permission denied` and `docker info` returns a `Server Version` line.

---

## 📊 Task 2: Deploy Prometheus and Instrument the Cluster

### Requirement 2.1

Design and implement a complete Prometheus deployment inside the Kubernetes cluster that satisfies all of the following constraints. You must produce every manifest from scratch.

**Constraints:**

- All Prometheus components must live in a namespace named `monitoring`.
- Prometheus must run under a dedicated Kubernetes ServiceAccount bound to a ClusterRole granting read access to nodes, pods, services, endpoints, and the `/metrics` non-resource URL.
- The Prometheus configuration (stored in a ConfigMap) must define at minimum four scrape jobs: `prometheus` (self-scrape), `kubernetes-nodes` (node kubelet metrics via the API server proxy), `kubernetes-cadvisor` (per-container resource metrics exposed by cAdvisor), and `kubernetes-pods` (annotation-driven pod scrape using `prometheus.io/scrape: "true"`).
- The Prometheus pod must mount the ConfigMap at `/etc/prometheus/` and use an `emptyDir` volume for TSDB storage at `/prometheus/`.
- The Prometheus Service must expose port `9090` as a `NodePort` so it is reachable from outside the cluster via `minikube service`.
- After applying all manifests, deploy a three-replica `nginx` workload in a namespace named `monitoring-demo` with CPU and memory resource requests and limits defined. Annotate the pods with `prometheus.io/scrape: "true"` and `prometheus.io/port: "80"` so Prometheus discovers them automatically.

```bash
# Verify your manifests are applied and the stack is healthy
kubectl get all -n monitoring
kubectl get all -n monitoring-demo
kubectl logs -n monitoring -l app=prometheus-server --tail=30
```

**Acceptance criteria:**

- [ ] `kubectl get pods -n monitoring` shows the Prometheus pod in `Running` state with `1/1` containers ready.
- [ ] `kubectl logs -n monitoring -l app=prometheus-server --tail=30` contains no `level=error` lines related to configuration loading or RBAC.

### Requirement 2.2

Design and implement a Node Exporter deployment as a Kubernetes DaemonSet in the `monitoring` namespace. The DaemonSet must mount `/proc`, `/sys`, and `/` from the host into the container so Node Exporter can read kernel-level metrics. Update the Prometheus ConfigMap to add a `node-exporter` scrape job that uses Kubernetes endpoint discovery filtered to the node-exporter service. After updating the ConfigMap, trigger a rolling restart of the Prometheus deployment and confirm the new configuration is loaded.

Then write and execute a single shell script named `cluster-report.sh` that uses `curl` against the Prometheus HTTP API (`/api/v1/query`) to print the following five values to stdout, each on a labelled line:

| # | Metric | PromQL Query |
|---|--------|--------------|
| 1 | Total number of cluster nodes | `count(kube_node_info)` |
| 2 | Total number of running pods across all namespaces | `count(kube_pod_status_phase{phase="Running"})` |
| 3 | Number of pods in the `monitoring-demo` namespace | `count(kube_pod_info{namespace="monitoring-demo"})` |
| 4 | Pod with the highest 5-minute CPU rate | `topk(1, rate(container_cpu_usage_seconds_total{pod!=""}[5m]))` |
| 5 | Pod with the highest current memory usage in MiB | `topk(1, container_memory_usage_bytes{pod!=""})` |

The script must start its own `kubectl port-forward` process, wait for it to be ready, run all five queries, then terminate the port-forward before exiting. The script must exit with code `0` on success and print a clear error message and exit with code `1` if any query returns a non-success status from the Prometheus API.

```bash
# After writing the script, run it
chmod +x cluster-report.sh
./cluster-report.sh
```

**Acceptance criteria:**

- [ ] `kubectl rollout status deployment/prometheus-deployment -n monitoring` completes with `successfully rolled out` after the ConfigMap update.
- [ ] `./cluster-report.sh` exits with code `0` and prints all five labelled metric values with no Python or shell errors; confirm with `echo "Exit code: $?"` immediately after running the script.

---

## 🎯 Expected Outcomes

- A fully operational Prometheus monitoring stack running inside Minikube that automatically discovers and scrapes metrics from Kubernetes nodes, cAdvisor, Node Exporter, and annotated pods without any static IP configuration.
- A reproducible shell script that demonstrates live cluster observability by querying five distinct Prometheus metrics and presenting them in human-readable form.

---

## ✅ Conclusion

This lab required you to reason about Kubernetes RBAC, service discovery, and metric collection simultaneously — the same concerns that appear in production observability platforms. The annotation-driven pod discovery pattern you implemented is the foundation of operator-managed stacks such as the kube-prometheus project. As a next step, consider deploying Alertmanager alongside Prometheus and routing a `PodCrashLooping` alert to a webhook receiver to complete the alerting pipeline.

---

<div align="center">

![Al Nafi](https://img.shields.io/badge/Al_Nafi-Cybersecurity_Training-blueviolet?style=for-the-badge)

</div>
