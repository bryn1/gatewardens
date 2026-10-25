"""Gatewardens server entrypoint: the web export's static files, one port.

GW's OWN static-only server (docs/ARCHITECTURE.md C10/F3): no api.py, no
db.py — every GET routes straight to static_app. Run:
    python3 server/server.py
Env: GW_PORT (default 8124). Binds 127.0.0.1. Methods other than GET get
the same C10 NOT_FOUND JSON shape (a static-only server has no verbs).
"""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import static_app

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(REPO_ROOT, "static")
HOST = "127.0.0.1"
DEFAULT_PORT = 8124


class GameHandler(BaseHTTPRequestHandler):
    server_version = "Gatewardens/1.0"

    def do_GET(self):
        static_app.serve(self, STATIC_DIR)

    def _static_only(self):
        static_app.send_error_json(self, 404, {"error": "NOT_FOUND"})

    do_POST = _static_only
    do_PUT = _static_only
    do_DELETE = _static_only
    do_PATCH = _static_only


def main():
    port = int(os.environ.get("GW_PORT", str(DEFAULT_PORT)))
    httpd = ThreadingHTTPServer((HOST, port), GameHandler)
    print("Gatewardens server on http://%s:%d (static: %s)"
          % (HOST, port, STATIC_DIR), flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
