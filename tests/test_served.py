"""W12 served contract (MC 11274.1.21 / card 11331) — engine-free stdlib tier.

Boots the SHIPPED server/server.py on an ephemeral GW_PORT and asserts the
C10 served shapes + the F2-3 engine bootstrap on the SERVED body (the W2
dead-shell trap lesson: a placeholder or un-substituted shell can never
pass again): served `/` is 200 text/html; the body contains `new Engine`
+ `<canvas` + the GW bridge trio (gwHost/__gwSnapshot/GW_STATE — present
side; the 0-hit VS side lives in test_bridge_contract); NO raw
$GODOT_URL/$GODOT_CONFIG token survives (substitution proof, stronger: no
$GODOT_ token at all); every asset the index really references — parsed
from the served body, never hardcoded names — returns 200 with
Content-Length > 0, .wasm/.pck with their C10 types; an unknown/escaping/
NUL path gets the shipped JSON 404 {"error":"NOT_FOUND"} shape.

static/ is build-side (.gitignore'd since W12): with no export present the
whole module SKIPS with an explicit reason (CI honesty); the W12 DoD run
has `bash tools/export_web.sh` executed first, so it runs green-not-skipped.
"""

import http.client
import json
import os
import re
import socket
import subprocess
import sys
import time

import pytest

from conftest import repo_path

INDEX = repo_path("static", "index.html")
SERVER = repo_path("server", "server.py")

if not os.path.isfile(INDEX):
    pytest.skip(
        "static/index.html missing — the web export is build-side and "
        "never committed; run `bash tools/export_web.sh` first "
        "(W12 DoD runs it present)", allow_module_level=True)

GW_NAMES = ("gwHost", "__gwSnapshot", "GW_STATE")

# Filename-shaped tokens inside the served index: src/href attrs plus the
# GODOT_CONFIG fileSizes map (index.pck/index.wasm). Parsed from the body,
# so an export renaming its files can never false-green this test.
ASSET_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.(?:js|wasm|pck|png|ico|map)")


def _free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture(scope="module")
def port():
    """Live server/server.py on an ephemeral GW_PORT; killed in teardown
    (waited for — a served test never leaves an orphan process behind)."""
    chosen = _free_port()
    proc = subprocess.Popen(
        [sys.executable, SERVER],
        env={**os.environ, "GW_PORT": str(chosen)},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            pytest.fail("server/server.py exited (%s) before binding port %d"
                        % (proc.returncode, chosen))
        try:
            with socket.create_connection(("127.0.0.1", chosen), 0.25):
                break
        except OSError:
            time.sleep(0.05)
    else:
        proc.kill()
        proc.wait(timeout=10)
        pytest.fail("server/server.py never accepted on port %d" % chosen)
    try:
        yield chosen
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)


def get(chosen, path):
    conn = http.client.HTTPConnection("127.0.0.1", chosen, timeout=10)
    try:
        conn.request("GET", path)
        resp = conn.getresponse()
        return resp.status, dict(resp.getheaders()), resp.read()
    finally:
        conn.close()


def served_index(chosen):
    status, headers, body = get(chosen, "/")
    assert status == 200, "GET / must serve 200 (C10)"
    assert headers["Content-Type"].startswith("text/html"), \
        "GET / must serve text/html (C10)"
    return body.decode("utf-8")


def test_root_serves_200_text_html_with_body(port):
    body = served_index(port)
    assert len(body) > 0, "GET / served an empty body"


def test_served_body_is_the_real_engine_bootstrap(port):
    body = served_index(port)
    assert "new Engine" in body, \
        "served body lacks `new Engine` — dead shell/placeholder (F2-3)"
    assert "<canvas" in body, \
        "served body lacks <canvas — dead shell/placeholder (F2-3)"
    for name in GW_NAMES:
        assert name in body, "GW bridge name %r missing in served body" % name


def test_no_raw_godot_tokens_survive_substitution(port):
    body = served_index(port)
    assert "$GODOT_URL" not in body, \
        "raw $GODOT_URL in served body — exporter substitution did not run"
    assert "$GODOT_CONFIG" not in body, \
        "raw $GODOT_CONFIG in served body — substitution did not run"
    assert "$GODOT_" not in body, \
        "raw $GODOT_* template token left in the export"


def test_every_referenced_asset_serves_200_nonempty(port):
    body = served_index(port)
    assets = sorted(set(ASSET_RE.findall(body)))
    assert assets, "parsed no asset references from index — blind test"
    c10_types = {".wasm": "application/wasm",
                 ".pck": "application/octet-stream"}
    for asset in assets:
        status, headers, blob = get(port, "/" + asset)
        assert status == 200, "referenced asset %s -> %d" % (asset, status)
        assert int(headers["Content-Length"]) > 0, \
            "asset %s served empty (Content-Length 0)" % asset
        assert len(blob) > 0, "asset %s body empty despite header" % asset
        extension = os.path.splitext(asset)[1]
        if extension in c10_types:
            assert headers["Content-Type"] == c10_types[extension], \
                "asset %s wrong content type (C10)" % asset


def test_unknown_paths_get_the_shipped_json_404_shape(port):
    for path in ("/no-such-thing.nope", "/../server/server.py",
                 "/%00nul.bin", "/index.secret"):
        status, headers, body = get(port, path)
        assert status == 404, "%s -> %d, want 404" % (path, status)
        assert headers["Content-Type"] == "application/json", \
            "%s: 404 must answer JSON (C10)" % path
        assert json.loads(body) == {"error": "NOT_FOUND"}, \
            "%s: 404 body must be the C10 NOT_FOUND shape" % path
