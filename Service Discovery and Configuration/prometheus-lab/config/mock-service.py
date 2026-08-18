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
