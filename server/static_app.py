"""Static file serving for the Gatewardens web client, docroot static/.

GW's own dispatcher (mechanics extended from the VS static server with its
api import REPLACED by send_error_json below — F3/C10): every path is
resolved with realpath and required to stay inside the docroot via
commonpath; anything escaping, NUL-bearing, missing, or outside the
extension allowlist is 404 {"error":"NOT_FOUND"} — never 403.
"""

import json
import os
from urllib.parse import unquote, urlsplit

# Godot web-export shapes covered: index.html/.js/.wasm/.pck, debug maps
# (index.wasm.map -> .map), audio worklet JS (index.audio.worklet.js and
# index.audio.position.worklet.js -> .js) and the export icons (.png/.ico).
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".map": "application/json",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".wasm": "application/wasm",
    ".pck": "application/octet-stream",
}


def send_error_json(handler, code, obj):
    """Reply with status `code` and JSON body `obj` (C10 error shape)."""
    body = json.dumps(obj).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _resolve(docroot, raw_path):
    """Absolute path inside realpath(docroot), or None if it escapes.

    A decoded NUL byte is rejected here: realpath would raise ValueError
    and kill the handler thread, so it resolves to None and gets the same
    404 NOT_FOUND as any other unknown path.
    """
    request_path = unquote(urlsplit(raw_path).path)
    if "\x00" in request_path:
        return None
    if request_path == "/":
        request_path = "/index.html"
    real_root = os.path.realpath(docroot)
    candidate = os.path.realpath(
        os.path.join(real_root, request_path.lstrip("/")))
    if os.path.commonpath([candidate, real_root]) != real_root:
        return None
    return candidate


def serve(handler, docroot):
    """Serve handler.path statically; always sends exactly one response."""
    path = _resolve(docroot, handler.path)
    if path is None or not os.path.isfile(path):
        send_error_json(handler, 404, {"error": "NOT_FOUND"})
        return
    extension = os.path.splitext(path)[1].lower()
    content_type = CONTENT_TYPES.get(extension)
    if content_type is None:
        send_error_json(handler, 404, {"error": "NOT_FOUND"})
        return
    try:
        with open(path, "rb") as handle:
            body = handle.read()
    except OSError:
        send_error_json(handler, 404, {"error": "NOT_FOUND"})
        return
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
