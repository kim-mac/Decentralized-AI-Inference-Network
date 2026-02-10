from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

METRICS_FILE = "metrics.json"
PORT = 8000


def load_metrics():
    if not os.path.exists(METRICS_FILE):
        return {
            "tasks_completed": 0,
            "consensus_history": [],
            "reputation": {},
            "active_peers": []
        }

    with open(METRICS_FILE, "r") as f:
        return json.load(f)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            data = load_metrics()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")

            # 🔥 REQUIRED for React dashboard
            self.send_header("Access-Control-Allow-Origin", "*")

            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()


def run():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Metrics server running → http://localhost:{PORT}/metrics")
    server.serve_forever()


if __name__ == "__main__":
    run()
