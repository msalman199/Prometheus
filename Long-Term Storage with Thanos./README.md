# 🚀 Long-Term Storage with Thanos

![Thanos](https://img.shields.io/badge/Thanos-Long--Term%20Storage-blue?style=for-the-badge\&logo=prometheus)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange?style=for-the-badge\&logo=prometheus)
![MinIO](https://img.shields.io/badge/MinIO-Object%20Storage-red?style=for-the-badge\&logo=minio)
![Linux](https://img.shields.io/badge/Linux-Administration-black?style=for-the-badge\&logo=linux)
![Docker](https://img.shields.io/badge/Docker-Containerization-blue?style=for-the-badge\&logo=docker)

> 📊 **A hands-on monitoring lab demonstrating how to extend Prometheus with Thanos for long-term metrics storage, high availability, historical querying, object storage, compaction, and unified observability.**

---

## 🎯 Learning Objectives

By completing this lab, you will learn how to:

* 📚 Understand Thanos architecture and long-term metrics storage
* ⚙️ Install and configure Thanos on Linux
* 🔗 Integrate Thanos Sidecar with Prometheus
* 💾 Configure MinIO as S3-compatible object storage
* 🔍 Use Thanos Query for unified metric queries
* 🗄️ Configure Thanos Store Gateway for historical metrics
* 🧹 Configure Thanos Compactor for optimization
* 🧪 Generate and query historical monitoring data
* ✅ Verify the complete Thanos monitoring stack

The objectives and architecture follow the supplied lab content.

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      Prometheus      │
                    │     :9090            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Thanos Sidecar     │
                    │   :10901 / :10902    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       MinIO          │
                    │   S3 Object Storage   │
                    │       :9000           │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
     ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
     │ Thanos Store  │ │Thanos Compactor│ │ Thanos Query │
     │    :10906     │ │    :10907      │ │    :10904    │
     └───────────────┘ └───────────────┘ └───────┬───────┘
                                                 │
                                                 ▼
                                      ┌────────────────────┐
                                      │ Unified Metrics    │
                                      │ Historical + Live  │
                                      └────────────────────┘
```

---

## 🧰 Technology Stack

| Technology              | Purpose                             |
| ----------------------- | ----------------------------------- |
| 🐧 Linux                | Lab operating system                |
| 📊 Prometheus           | Metrics collection and monitoring   |
| ⚡ Thanos                | Long-term Prometheus storage and HA |
| 🗄️ MinIO               | S3-compatible object storage        |
| 🐳 Docker               | Container runtime/dependency        |
| 📈 Node Exporter        | Host-level metrics                  |
| 🔎 Thanos Query         | Unified metrics querying            |
| 🏪 Thanos Store Gateway | Historical object-storage access    |
| 🧹 Thanos Compactor     | Data compaction and downsampling    |
| 🔧 systemd              | Service management                  |
| 🐚 Bash                 | Automation and verification         |

The supplied lab uses a Linux environment and installs the required dependencies, including Docker and Docker Compose.

---

# 🧪 Lab Environment

The lab uses an **Al Nafi Linux cloud machine**. The provided environment starts without the required monitoring tools, so the components are installed during the exercises.

---

# 1️⃣ System Preparation

## 📦 Update the System

```bash
sudo apt update && sudo apt upgrade -y
```

## 🛠️ Install Dependencies

```bash
sudo apt install -y wget curl unzip docker.io docker-compose
```

## 🐳 Enable Docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

## 👤 Add Current User to Docker Group

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 📁 Create Lab Directories

```bash
mkdir -p ~/thanos-lab/{prometheus,thanos,storage}
cd ~/thanos-lab
```

These preparation steps are based directly on the supplied lab instructions.

---

# 2️⃣ Install Prometheus

Prometheus provides the primary metrics collection and local TSDB functionality.

```bash
cd ~/thanos-lab

wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz

tar -xzf prometheus-2.47.0.linux-amd64.tar.gz

mv prometheus-2.47.0.linux-amd64 prometheus-install

sudo cp prometheus-install/prometheus /usr/local/bin/
sudo cp prometheus-install/promtool /usr/local/bin/
```

Create the Prometheus service account and directories:

```bash
sudo useradd --no-create-home --shell /bin/false prometheus

sudo mkdir -p /etc/prometheus /var/lib/prometheus

sudo chown prometheus:prometheus \
  /etc/prometheus \
  /var/lib/prometheus
```

---

# 3️⃣ Configure Prometheus for Thanos

Create the configuration:

```bash
sudo tee /etc/prometheus/prometheus.yml > /dev/null <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'thanos-lab'
    replica: 'prometheus-1'

rule_files:

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'thanos-sidecar'
    static_configs:
      - targets: ['localhost:10902']

  - job_name: 'thanos-query'
    static_configs:
      - targets: ['localhost:10904']
EOF
```

Set ownership:

```bash
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

The lab specifically configures external labels such as `cluster` and `replica` for Thanos integration.

---

# 4️⃣ Install Node Exporter

Node Exporter generates host-level metrics that can be collected by Prometheus.

```bash
cd ~/thanos-lab

wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz

tar -xzf node_exporter-1.6.1.linux-amd64.tar.gz

sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
```

Create the systemd service:

```bash
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
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

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

---

# 5️⃣ Install Thanos

Download and install Thanos:

```bash
cd ~/thanos-lab

wget https://github.com/thanos-io/thanos/releases/download/v0.32.4/thanos-0.32.4.linux-amd64.tar.gz

tar -xzf thanos-0.32.4.linux-amd64.tar.gz

sudo cp thanos-0.32.4.linux-amd64/thanos /usr/local/bin/
```

Verify:

```bash
thanos --version
```

---

# 6️⃣ 🗄️ Configure MinIO Object Storage

Thanos uses object storage for long-term metric retention. This lab uses MinIO as a local S3-compatible backend.

Download MinIO:

```bash
cd ~/thanos-lab

wget https://dl.min.io/server/minio/release/linux-amd64/minio

chmod +x minio

sudo mv minio /usr/local/bin/
```

Create storage:

```bash
mkdir -p ~/thanos-lab/storage/minio-data
mkdir -p ~/.minio
```

Start MinIO:

```bash
cd ~/thanos-lab/storage

nohup minio server minio-data \
  --address :9000 \
  --console-address :9001 \
  > minio.log 2>&1 &
```

Verify:

```bash
sleep 10

curl -I http://localhost:9000/minio/health/live
```

---

# 7️⃣ 🪣 Create the Thanos Bucket

Install the MinIO client:

```bash
cd ~/thanos-lab

wget https://dl.min.io/client/mc/release/linux-amd64/mc

chmod +x mc

sudo mv mc /usr/local/bin/
```

Configure the MinIO alias:

```bash
mc alias set local http://localhost:9000 minioadmin minioadmin
```

Create the bucket:

```bash
mc mb local/thanos-bucket
```

Verify:

```bash
mc ls local/
```

---

# 8️⃣ 🔐 Configure Thanos Object Storage

Create the configuration directory:

```bash
mkdir -p ~/thanos-lab/thanos/config
```

Create the bucket configuration:

```bash
tee ~/thanos-lab/thanos/config/bucket.yml > /dev/null <<EOF
type: S3
config:
  bucket: "thanos-bucket"
  endpoint: "localhost:9000"
  access_key: "minioadmin"
  secret_key: "minioadmin"
  insecure: true
  signature_version2: false
  http_config:
    idle_conn_timeout: 90s
    response_header_timeout: 2m
    insecure_skip_verify: true
EOF
```

> 🔐 **Production Note:** The credentials shown above are lab credentials from the supplied material. Production deployments should use secure credentials management and should not commit secrets to Git.

---

# 9️⃣ 🚀 Configure Prometheus Service

Create the systemd service:

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
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle \
    --storage.tsdb.min-block-duration=2h \
    --storage.tsdb.max-block-duration=2h \
    --storage.tsdb.retention.time=6h

[Install]
WantedBy=multi-user.target
EOF
```

Start Prometheus:

```bash
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus
```

Check status:

```bash
sudo systemctl status prometheus
```

---

# 🔟 🔗 Configure Thanos Sidecar

The Sidecar runs alongside Prometheus and uploads Prometheus blocks to object storage.

```bash
sudo tee /etc/systemd/system/thanos-sidecar.service > /dev/null <<EOF
[Unit]
Description=Thanos Sidecar
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/thanos sidecar \
    --tsdb.path=/var/lib/prometheus \
    --prometheus.url=http://localhost:9090 \
    --grpc-address=0.0.0.0:10901 \
    --http-address=0.0.0.0:10902 \
    --objstore.config-file=/home/$USER/thanos-lab/thanos/config/bucket.yml

[Install]
WantedBy=multi-user.target
EOF
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl start thanos-sidecar
sudo systemctl enable thanos-sidecar
```

Verify:

```bash
sudo systemctl status thanos-sidecar
```

---

# 1️⃣1️⃣ 🔎 Configure Thanos Query

Thanos Query provides a unified interface for querying metrics from Thanos stores.

```bash
sudo tee /etc/systemd/system/thanos-query.service > /dev/null <<EOF
[Unit]
Description=Thanos Query
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/thanos query \
    --http-address=0.0.0.0:10904 \
    --grpc-address=0.0.0.0:10903 \
    --store=localhost:10901 \
    --store=localhost:10905

[Install]
WantedBy=multi-user.target
EOF
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl start thanos-query
sudo systemctl enable thanos-query
```

Verify:

```bash
sudo systemctl status thanos-query
```

---

# 1️⃣2️⃣ 🏪 Configure Thanos Store Gateway

Store Gateway provides access to historical metrics stored in object storage.

```bash
sudo mkdir -p /var/lib/thanos/store
sudo chown prometheus:prometheus /var/lib/thanos/store
```

Create the service:

```bash
sudo tee /etc/systemd/system/thanos-store.service > /dev/null <<EOF
[Unit]
Description=Thanos Store Gateway
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/thanos store \
    --data-dir=/var/lib/thanos/store \
    --objstore.config-file=/home/$USER/thanos-lab/thanos/config/bucket.yml \
    --http-address=0.0.0.0:10906 \
    --grpc-address=0.0.0.0:10905

[Install]
WantedBy=multi-user.target
EOF
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl start thanos-store
sudo systemctl enable thanos-store
```

---

# 1️⃣3️⃣ 🧹 Configure Thanos Compactor

The Compactor optimizes data stored in the object storage.

```bash
sudo mkdir -p /var/lib/thanos/compactor

sudo chown prometheus:prometheus \
  /var/lib/thanos/compactor
```

Create the service:

```bash
sudo tee /etc/systemd/system/thanos-compactor.service > /dev/null <<EOF
[Unit]
Description=Thanos Compactor
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/thanos compact \
    --data-dir=/var/lib/thanos/compactor \
    --objstore.config-file=/home/$USER/thanos-lab/thanos/config/bucket.yml \
    --http-address=0.0.0.0:10907 \
    --wait

[Install]
WantedBy=multi-user.target
EOF
```

Start:

```bash
sudo systemctl daemon-reload
sudo systemctl start thanos-compactor
sudo systemctl enable thanos-compactor
```

Verify:

```bash
sudo systemctl status thanos-compactor
```

---

# 1️⃣4️⃣ ✅ Verify All Services

Check the monitoring stack:

```bash
sudo systemctl status prometheus --no-pager -l
sudo systemctl status node_exporter --no-pager -l
sudo systemctl status thanos-sidecar --no-pager -l
sudo systemctl status thanos-query --no-pager -l
sudo systemctl status thanos-store --no-pager -l
sudo systemctl status thanos-compactor --no-pager -l
```

Check listening ports:

```bash
netstat -tlnp | grep -E \
"(9090|9100|10901|10902|10903|10904|10905|10906|10907|9000)"
```

---

# 1️⃣5️⃣ 🔍 Test Thanos Query

Test the Store API:

```bash
curl -s \
"http://localhost:10904/api/v1/stores" \
| python3 -m json.tool
```

Test a metric:

```bash
curl -s \
"http://localhost:10904/api/v1/query?query=up" \
| python3 -m json.tool
```

Test the web interface:

```bash
curl -I http://localhost:10904/
```

---

# 1️⃣6️⃣ 📈 Generate Historical Metrics

Create a simple load generator:

```bash
tee ~/thanos-lab/generate_load.sh > /dev/null <<'EOF'
#!/bin/bash

echo "Generating load for metrics collection..."

for i in {1..100}; do
    dd if=/dev/zero of=/dev/null bs=1M count=100 &
    sleep 1
    kill $! 2>/dev/null

    echo "Test data $i" > /tmp/test_file_$i
    rm -f /tmp/test_file_$i

    echo "Generated load iteration $i"
    sleep 2
done

echo "Load generation complete"
EOF
```

Make executable:

```bash
chmod +x ~/thanos-lab/generate_load.sh
```

Run:

```bash
nohup ~/thanos-lab/generate_load.sh \
  > ~/thanos-lab/load_generation.log 2>&1 &
```

---

# 1️⃣7️⃣ ☁️ Verify Object Storage

Allow time for metrics blocks to be uploaded:

```bash
sleep 300
```

Check the bucket:

```bash
mc ls local/thanos-bucket/ --recursive
```

Check Sidecar logs:

```bash
sudo journalctl \
  -u thanos-sidecar \
  --no-pager -l \
  --since "10 minutes ago"
```

---

# 1️⃣8️⃣ 🕐 Query Historical Metrics

Query current metrics:

```bash
curl -s \
"http://localhost:10904/api/v1/query?query=node_cpu_seconds_total"
```

Query a time range:

```bash
END_TIME=$(date +%s)
START_TIME=$((END_TIME - 3600))

curl -s \
"http://localhost:10904/api/v1/query_range?query=node_cpu_seconds_total&start=${START_TIME}&end=${END_TIME}&step=60"
```

The supplied lab validates both current and historical queries through the Thanos Query API.

---

# 1️⃣9️⃣ 🧪 Automated Verification

Create:

```bash
tee ~/thanos-lab/verify_setup.sh > /dev/null <<'EOF'
#!/bin/bash

echo "=== Thanos Setup Verification ==="
echo ""

echo "1. Service Status:"
services=(
  "prometheus"
  "node_exporter"
  "thanos-sidecar"
  "thanos-query"
  "thanos-store"
  "thanos-compactor"
)

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "   ✓ $service is running"
    else
        echo "   ✗ $service is not running"
    fi
done

echo ""
echo "2. Port Connectivity:"

ports=(
  "9090:Prometheus"
  "9100:Node Exporter"
  "10902:Thanos Sidecar"
  "10904:Thanos Query"
  "10906:Thanos Store"
  "10907:Thanos Compactor"
  "9000:MinIO"
)

for port_desc in "${ports[@]}"; do
    port=$(echo $port_desc | cut -d: -f1)
    desc=$(echo $port_desc | cut -d: -f2)

    if nc -z localhost $port 2>/dev/null; then
        echo "   ✓ $desc (port $port) is accessible"
    else
        echo "   ✗ $desc (port $port) is not accessible"
    fi
done

echo ""
echo "3. Object Storage:"

bucket_contents=$(mc ls local/thanos-bucket/ 2>/dev/null | wc -l)

if [ $bucket_contents -gt 0 ]; then
    echo "   ✓ Object storage contains $bucket_contents items"
else
    echo "   ⚠ Object storage is empty"
fi

echo ""
echo "4. Thanos Query Stores:"

stores_response=$(curl -s \
  "http://localhost:10904/api/v1/stores" 2>/dev/null)

if echo "$stores_response" | grep -q "sidecar"; then
    echo "   ✓ Thanos Query can see sidecar store"
else
    echo "   ✗ Thanos Query cannot see sidecar store"
fi

echo ""
echo "5. Sample Query Test:"

query_response=$(curl -s \
  "http://localhost:10904/api/v1/query?query=up" 2>/dev/null)

if echo "$query_response" | grep -q '"status":"success"'; then
    echo "   ✓ Sample query executed successfully"
else
    echo "   ✗ Sample query failed"
fi

echo ""
echo "=== Verification Complete ==="
EOF
```

Run:

```bash
chmod +x ~/thanos-lab/verify_setup.sh
~/thanos-lab/verify_setup.sh
```

---

# 🌐 Web Interfaces

| Component         |    Port | URL                      |
| ----------------- | ------: | ------------------------ |
| 📊 Prometheus     |  `9090` | `http://localhost:9090`  |
| 🔎 Thanos Query   | `10904` | `http://localhost:10904` |
| 🔗 Thanos Sidecar | `10902` | `http://localhost:10902` |
| 🏪 Store Gateway  | `10906` | `http://localhost:10906` |
| 🧹 Compactor      | `10907` | `http://localhost:10907` |
| 🗄️ MinIO Console |  `9001` | `http://localhost:9001`  |

These access points are listed in the supplied lab material.

---

# 🛠️ Troubleshooting

## ❌ Services Not Starting

Check logs:

```bash
sudo journalctl -u prometheus -f
sudo journalctl -u thanos-sidecar -f
sudo journalctl -u thanos-query -f
```

## ❌ MinIO Connection Problems

```bash
curl -I http://localhost:9000/minio/health/live

cat ~/thanos-lab/thanos/config/bucket.yml

mc ls local/thanos-bucket/
```

## ❌ No Data in Object Storage

Check Prometheus data:

```bash
sudo ls -la /var/lib/prometheus/
```

Check Sidecar upload activity:

```bash
sudo journalctl \
  -u thanos-sidecar \
  --since "1 hour ago" \
  | grep -i upload
```

Check Prometheus blocks:

```bash
sudo ls -la /var/lib/prometheus/01*
```

## ❌ Query Problems

Test Prometheus directly:

```bash
curl \
"http://localhost:9090/api/v1/query?query=up"
```

Test Thanos:

```bash
curl \
"http://localhost:10904/api/v1/query?query=up"
```

Check stores:

```bash
curl \
"http://localhost:10904/api/v1/stores"
```

---

# ⚙️ Advanced Configuration

## 🗃️ Retention Policies

The supplied lab demonstrates a retention configuration:

```yaml
retention:
  raw: 30d
  5m: 90d
  1h: 1y
```

---

## 🚨 Alerting Rules

The lab also demonstrates Prometheus alerting rules for:

* 🔴 High Thanos Query HTTP error rate
* 🟡 High Thanos Store gRPC error rate

Rules can be stored under:

```text
/etc/prometheus/rules/
```

and loaded through the Prometheus configuration.

---

# 📊 Performance Monitoring

A monitoring script is included in the lab to inspect:

* 🧠 Memory usage
* 💽 Disk usage
* 🌐 Network connections
* 🗄️ Object-storage objects
* ⚠️ Recent errors

Run:

```bash
chmod +x ~/thanos-lab/monitor_thanos.sh
~/thanos-lab/monitor_thanos.sh
```

---

# 🔌 Important Ports

```text
Prometheus       → 9090
Node Exporter    → 9100

Thanos Sidecar   → 10901 / 10902
Thanos Query     → 10903 / 10904
Thanos Store     → 10905 / 10906
Thanos Compactor → 10907

MinIO            → 9000
MinIO Console    → 9001
```

---

# 🧠 Key Concepts Learned

### 📊 Prometheus

Collects and stores monitoring metrics locally.

### 🔗 Thanos Sidecar

Connects Prometheus with the Thanos ecosystem and uploads TSDB blocks to object storage.

### 🔎 Thanos Query

Provides a unified query layer across multiple metric sources.

### 🏪 Store Gateway

Reads historical metrics from object storage.

### 🧹 Compactor

Optimizes stored data through compaction and downsampling.

### 🗄️ MinIO

Provides S3-compatible object storage for the lab.

---

# 🏆 Skills Demonstrated

```text
Linux Administration
        │
        ├── systemd Services
        ├── Linux Users & Permissions
        ├── Networking & Ports
        └── Bash Automation
                │
                ▼
        Prometheus Monitoring
                │
                ▼
          Thanos Integration
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    Sidecar   Query    Store
        │       │        │
        └───────┼────────┘
                ▼
             MinIO
                │
                ▼
          Long-Term Data
```

---

# 🎯 Lab Outcomes

By completing this project, you have implemented:

* ✅ Thanos Sidecar
* ✅ Thanos Query
* ✅ Thanos Store Gateway
* ✅ Thanos Compactor
* ✅ Prometheus integration
* ✅ Node Exporter metrics
* ✅ MinIO S3-compatible storage
* ✅ Long-term metric retention
* ✅ Historical metric querying
* ✅ Service and port verification
* ✅ Monitoring and troubleshooting scripts

The supplied lab summarizes these outcomes as long-term storage, high availability, cost efficiency, scalability, and unified querying.

---

# 🌍 Real-World Use Cases

Thanos is useful when organizations need:

* 🏢 Enterprise monitoring
* ☁️ Multi-cluster observability
* 📈 Long-term capacity planning
* 🔍 Historical troubleshooting
* 📋 Compliance-related metric retention
* 🌐 Centralized monitoring
* 📊 Large-scale Prometheus deployments

The source material specifically positions the architecture for long-term retention, compliance, capacity planning, trend analysis, and large-scale cloud-native monitoring.

---

# 🏁 Conclusion

This lab demonstrates a complete **Prometheus + Thanos + MinIO long-term monitoring architecture**.

The final environment provides a foundation for:

```text
Real-Time Metrics
       +
Historical Metrics
       +
Object Storage
       +
Unified Querying
       +
Data Compaction
       +
High Availability
       =
Enterprise Observability
```

🚀 **Hands-on experience gained:** Linux administration, Prometheus monitoring, Thanos architecture, S3-compatible storage, systemd service management, Bash automation, historical metrics querying, troubleshooting, and observability engineering.

---

## ⭐ Project Highlights

```text
╔══════════════════════════════════════════════════════╗
║              🚀 THANOS MONITORING LAB 🚀             ║
╠══════════════════════════════════════════════════════╣
║ 📊 Prometheus        → Metrics Collection            ║
║ 🔗 Thanos Sidecar    → Metrics Upload                ║
║ 🔎 Thanos Query      → Unified Querying              ║
║ 🏪 Store Gateway     → Historical Data               ║
║ 🧹 Compactor         → Data Optimization             ║
║ 🗄️ MinIO             → Long-Term Storage             ║
║ 🐧 Linux             → Infrastructure                ║
║ 🐚 Bash              → Automation & Verification     ║
╚══════════════════════════════════════════════════════╝
```

---

**📌 Repository Topic:** `Long-Term Storage with Thanos`
**🛠️ Focus:** Monitoring • Observability • Prometheus • Thanos • Linux • S3 Object Storage
**🎓 Training Environment:** Al Nafi Cloud Lab
