#!/usr/bin/env python3

import time
import random
import threading
from flask import Flask, request
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Counter Metrics - Values that only increase
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
error_count = Counter('http_errors_total', 'Total HTTP errors', ['status_code'])

# Gauge Metrics - Values that can go up and down
active_connections = Gauge('active_connections', 'Number of active connections')
cpu_usage = Gauge('cpu_usage_percent', 'Current CPU usage percentage')
memory_usage = Gauge('memory_usage_bytes', 'Current memory usage in bytes')

# Histogram Metrics - Observations in buckets
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', 
                           buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
response_size = Histogram('http_response_size_bytes', 'HTTP response size in bytes',
                         buckets=[100, 500, 1000, 5000, 10000, 50000])

# Summary Metrics - Observations with quantiles
request_latency = Summary('http_request_latency_seconds', 'HTTP request latency')
processing_time = Summary('data_processing_seconds', 'Time spent processing data')

# Simulate system metrics
def update_system_metrics():
    while True:
        # Simulate CPU usage (0-100%)
        cpu_usage.set(random.uniform(10, 90))
        
        # Simulate memory usage (in bytes)
        memory_usage.set(random.randint(1000000, 8000000))
        
        # Simulate active connections (0-50)
        active_connections.set(random.randint(0, 50))
        
        time.sleep(2)

# Start background thread for system metrics
metrics_thread = threading.Thread(target=update_system_metrics, daemon=True)
metrics_thread.start()

@app.route('/')
def home():
    # Increment request counter
    request_count.labels(method='GET', endpoint='/').inc()
    
    # Simulate request duration
    duration = random.uniform(0.1, 2.0)
    time.sleep(duration)
    
    # Record metrics
    request_duration.observe(duration)
    request_latency.observe(duration)
    
    response_data = "Welcome to Prometheus Metrics Demo!"
    response_size.observe(len(response_data))
    
    return response_data

@app.route('/api/data')
def api_data():
    request_count.labels(method='GET', endpoint='/api/data').inc()
    
    # Simulate processing time
    process_time = random.uniform(0.5, 3.0)
    processing_time.observe(process_time)
    
    # Simulate request duration
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
    error_count.labels(status_code='500').inc()
    
    duration = random.uniform(0.1, 0.5)
    request_duration.observe(duration)
    request_latency.observe(duration)
    
    return "Internal Server Error", 500

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    print("Starting sample application with Prometheus metrics...")
    print("Metrics available at: http://localhost:8000/metrics")
    app.run(host='0.0.0.0', port=8000, debug=False)
