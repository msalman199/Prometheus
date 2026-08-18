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
            
            # Here you would integrate with SMS service
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
