#!/usr/bin/env python3
"""Status of the notification service on twins-test (stdlib only, GET only).

  python3 twins_status.py            print a table
  python3 twins_status.py --serve    serve GET /status as JSON on localhost:8080
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE_URL = os.environ.get("NOTIFICATION_URL", "https://notification.cm-tech.dev")
DEFAULT_PUBLISHER_ID = "84d864d8-2041-701f-684a-5daf0531cb2d"
TIMEOUT = 10


def get_json(path):
    req = urllib.request.Request(BASE_URL + path, method="GET",
                                 headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def fetch_health():
    return get_json("/internal/actuator/health/readiness").get("status", "UNKNOWN")


def fetch_sources(publisher_id):
    path = f"/internal/v1/publishers/{publisher_id}/source-notification-settings"
    return [{"id": s["id"], "isEnabled": bool(s.get("isEnabled"))} for s in get_json(path)]


def collect(publisher_id):
    result = {"publisherId": publisher_id}
    try:
        result["notification"] = fetch_health()
    except (urllib.error.URLError, OSError, ValueError) as e:
        result["notification"] = "DOWN"
        result["healthError"] = str(e)
    try:
        result["sources"] = fetch_sources(publisher_id)
    except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError) as e:
        result["sources"] = []
        result["sourcesError"] = str(e)
    return result


def print_table(result):
    mark = lambda ok: "✅" if ok else "❌"
    print(f"{'Check':<40} | Status")
    print("-" * 40 + "-+-------")
    print(f"{'notification readiness':<40} | {mark(result['notification'] == 'UP')} {result['notification']}")
    if "healthError" in result:
        print(f"  error: {result['healthError']}")
    print()
    print(f"Sources of publisher {result['publisherId']}")
    print(f"{'Source id':<40} | isEnabled")
    print("-" * 40 + "-+----------")
    for s in result["sources"]:
        print(f"{s['id']:<40} | {mark(s['isEnabled'])}")
    if "sourcesError" in result:
        print(f"  error: {result['sourcesError']}")
    elif not result["sources"]:
        print("  (no sources)")


def serve(publisher_id, port):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/status":
                self.send_error(404)
                return
            body = json.dumps(collect(publisher_id), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving GET http://localhost:{port}/status", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--publisher-id",
                        default=os.environ.get("PUBLISHER_ID", DEFAULT_PUBLISHER_ID))
    parser.add_argument("--serve", action="store_true", help="serve GET /status as JSON")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    if args.serve:
        serve(args.publisher_id, args.port)
    else:
        result = collect(args.publisher_id)
        print_table(result)
        sys.exit(0 if result["notification"] == "UP" and "sourcesError" not in result else 1)


if __name__ == "__main__":
    main()
