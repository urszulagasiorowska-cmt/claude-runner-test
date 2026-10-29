#!/usr/bin/env python3
"""Shows the status of the notification service on twins-test and one publisher's sources.

Read-only: only GET requests. Standard library only.

    python3 twins_status.py           # print a table
    python3 twins_status.py --serve   # serve GET /status as JSON on localhost:8081
"""
import json
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE_URL = "https://notification.cm-tech.dev/internal"
PUBLISHER_ID = "84d864d8-2041-701f-684a-5daf0531cb2d"
HEALTH_URL = f"{BASE_URL}/actuator/health/readiness"
SOURCES_URL = f"{BASE_URL}/v1/publishers/{PUBLISHER_ID}/source-notification-settings"
TIMEOUT = 10
HOST, PORT = "localhost", 8081


def get_json(url):
    req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def collect_status():
    health = get_json(HEALTH_URL)
    sources = get_json(SOURCES_URL)
    return {
        "notification": health.get("status"),
        "publisher": PUBLISHER_ID,
        "sources": [{"id": s["id"], "isEnabled": s["isEnabled"]} for s in sources],
    }


def format_table(status):
    rows = [("notification", status["notification"])]
    rows += [(s["id"], "wł." if s["isEnabled"] else "wył.") for s in status["sources"]]
    width = max(len(name) for name, _ in rows)
    lines = [f"{'cel':<{width}} | status", f"{'-' * width}-+-------"]
    lines += [f"{name:<{width}} | {value}" for name, value in rows]
    lines.append(f"(źródła publishera {status['publisher']})")
    return "\n".join(lines)


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self._send(404, {"error": "not found"})
            return
        try:
            self._send(200, collect_status())
        except Exception as exc:
            self._send(502, {"error": f"{type(exc).__name__}: {exc}"})

    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main(argv):
    if "--serve" in argv:
        print(f"Serving GET /status on http://{HOST}:{PORT}", flush=True)
        HTTPServer((HOST, PORT), StatusHandler).serve_forever()
    else:
        print(format_table(collect_status()))


if __name__ == "__main__":
    main(sys.argv[1:])
