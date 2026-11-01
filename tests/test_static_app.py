"""W-T1 in-process static_app tests (MC 11878; closes P3 F-3 + F-3a + F-4).

server/static_app.py was reachable from the suite only through a SUBPROCESS
server (test_served), which mutmut cannot associate — the module scored
0/121 by association alone (P3-wave.log F-3). This file imports it
IN-PROCESS — `from server import static_app`, the exact path-derived
association key P3 §2 declared — so the next mutation sweep associates the
mutants with these legs. Ephemeral bind (port 0), test-owned tmp docroot:
zero collision with the subprocess-tier served tests, and the repo `static/`
export is never read here.

Leg map (finding -> leg, V15-PLAN-c2 §3 W-T1):
  F-3   every leg below (the in-process import itself)
  F-3a  test_oserror_branch_chmod000_gets_c10_404 — serve()'s
        `except OSError` branch (isfile true + open() fails): the 11
        surviving send_error_json mutants (serve_46..56) die here on the
        pinned status + exact C10 body.
        ROOT-SENSITIVITY (declared, plan §2-2b): mode-000 + open()-must-
        fail is true only for an unprivileged uid. The in-probe guard
        below fails LOUD (never silently green) if open() succeeds; the
        suite runs as `claudecode` on VM350 (whoami row in WT1-wave.log).
  F-4   test_f4_uppercase_x_name_served_byte_intact — mutant_21 is
        lstrip("/") -> lstrip("XX/XX"), a strip SET {X, /}: a post-slash
        name starting UPPERCASE X ("/XHR.js" -> "HR.js") goes RED under
        it; the lowercase companion stays green by design (that is the
        mutant's P3-wave.log:102 truth) and pins the ordinary case.
  DECLARED reading (plan sketch says "405 wrong method"): the SHIPPED
  contract is C10 — server.py:6-7 + :27-34 answer every non-GET verb with
  the 404 NOT_FOUND JSON, "a static-only server has no verbs". The verbs
  leg pins the shipped shape (== 404, never 405); server code is
  UNTOUCHED by this card, so the test follows the code, not the sketch.
  The verb WIRING mirrors server.py:27-34 on the associated module object
  (calling it through a second top-level `static_app` import would dodge
  the mutmut trampoline — P3 §2 association rule).
"""

import http.client
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from conftest import repo_path

sys.path.insert(0, repo_path())
from server import static_app  # noqa: E402  (P3 §2 association key)

# Byte-exact C10 error shape (P3 mutants 53-56 flip key/value case ONLY —
# a json.loads == dict compare would catch those too, but the served
# BYTE contract is what clients parse, so it is pinned as bytes).
C10_BODY = b'{"error": "NOT_FOUND"}'

INDEX_BODY = b"<!DOCTYPE html><html>wt1-index</html>\n"
JS_BODY = "const gw = 1; // w-t1 gr\u00e5 body\n".encode("utf-8")
XHR_UPPER_BODY = b"// uppercase-X post-slash name (mutant_21 killer)\n"
XHR_LOWER_BODY = b"// lowercase companion (survives mutant_21 by design)\n"
OUTSIDE_BODY = b"// outside the docroot; must never be served\n"
LOCKED_BODY = b"// must never be served even when isfile-true\n"


class _Handler(BaseHTTPRequestHandler):
    """GET routes through the real static_app.serve; verbs mirror the
    shipped _static_only wiring of server.py:27-34 (C10 static-only)."""

    docroot = None

    def do_GET(self):
        static_app.serve(self, self.docroot)

    def _static_only(self):
        static_app.send_error_json(self, 404, {"error": "NOT_FOUND"})

    do_POST = _static_only
    do_PUT = _static_only
    do_DELETE = _static_only
    do_PATCH = _static_only

    def log_message(self, fmt, *args):  # keep pytest output clean
        pass


def get(chosen, method="GET", path="/"):
    conn = http.client.HTTPConnection("127.0.0.1", chosen, timeout=10)
    try:
        conn.request(method, path)
        resp = conn.getresponse()
        return resp.status, dict(resp.getheaders()), resp.read()
    finally:
        conn.close()


def assert_c10_404(status, headers, body, what):
    assert status == 404, "%s -> %d, want 404 (C10 never 403/405)" % (
        what, status)
    assert headers["Content-Type"] == "application/json", \
        "%s: error must answer JSON (C10)" % what
    assert body == C10_BODY, \
        "%s: body %r != exact C10 %r" % (what, body, C10_BODY)


@pytest.fixture(scope="module")
def docroot(tmp_path_factory):
    """Test-owned docroot + one outside file; a symlink back INTO the
    docroot gives the escape leg a MUST-BE-REFUSED entry whose target is
    proven readable (non-vacuity control)."""
    outside = tmp_path_factory.mktemp("wt1-outside")
    secret = outside / "secret.js"
    secret.write_bytes(OUTSIDE_BODY)
    root = tmp_path_factory.mktemp("wt1-docroot")
    (root / "index.html").write_bytes(INDEX_BODY)
    (root / "hello.js").write_bytes(JS_BODY)
    (root / "XHR.js").write_bytes(XHR_UPPER_BODY)
    (root / "xhr.js").write_bytes(XHR_LOWER_BODY)
    os.symlink(str(secret), str(root / "escape.js"))
    return root, os.path.relpath(str(outside), str(root))


@pytest.fixture(scope="module")
def port(docroot):
    """ThreadingHTTPServer on port 0 (OS-assigned ephemeral): the task's
    zero-collision rule, never a probed fixed port."""
    _Handler.docroot = str(docroot[0])
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd.server_address[1]
    finally:
        httpd.shutdown()
        thread.join(timeout=10)
        httpd.server_close()


# ---------- F-3: real module, real HTTP, byte-exact serving ----------

def test_root_maps_to_index_and_serves_bytes(port, docroot):
    status, headers, body = get(port, path="/")
    assert status == 200, "GET / -> %d, want 200" % status
    assert headers["Content-Type"].startswith("text/html"), \
        "GET / must serve text/html (C10)"
    assert body == INDEX_BODY, "GET / body not byte-intact"


def test_js_serves_200_byte_intact(port, docroot):
    status, headers, body = get(port, path="/hello.js")
    assert status == 200, "GET /hello.js -> %d, want 200" % status
    assert headers["Content-Type"] == "text/javascript; charset=utf-8", \
        "hello.js wrong content type (C10)"
    assert headers["Content-Length"] == str(len(JS_BODY)), \
        "hello.js Content-Length != payload size"
    assert body == JS_BODY, "hello.js body not byte-intact (transcode?)"


def test_missing_file_gets_exact_404_c10_body(port, docroot):
    status, headers, body = get(port, path="/no-such-thing.js")
    assert_c10_404(status, headers, body, "missing /no-such-thing.js")
    assert headers["Content-Length"] == str(len(C10_BODY)), \
        "404 Content-Length != body size"


def test_non_get_verbs_get_static_only_404(port, docroot):
    # DECLARED: shipped contract is C10 404 for verbs (server.py:6-7,
    # :27-34), NOT 405 — the plan sketch line, followed as written, would
    # pin a shape the product does not serve. == 404 asserts both
    # "is refused" and "is never 405" at once.
    for verb in ("POST", "PUT", "DELETE", "PATCH"):
        status, headers, body = get(port, method=verb, path="/hello.js")
        assert_c10_404(status, headers, body, "%s /hello.js" % verb)


# ---------- F-4: _resolve lstrip("/") boundary (mutant_21) ----------

def test_f4_uppercase_x_name_served_byte_intact(port, docroot):
    # mutant_21: lstrip("/") -> lstrip("XX/XX"), set {X, /}. This path
    # ("/XHR.js" -> "HR.js" under it -> isfile false -> 404) is the leg
    # P3-wave.log:102 says the lowercase case can never cover.
    status, headers, body = get(port, path="/XHR.js")
    assert status == 200, "/XHR.js -> %d, want 200 (mutant_21 kills it)" \
        % status
    assert body == XHR_UPPER_BODY, "/XHR.js body not byte-intact"


def test_f4_lowercase_companion_served_byte_intact(port, docroot):
    # Companion row (plan §2-2c): green under mutant_21 BY DESIGN
    # (lowercase x is not in the {X, /} strip set); pins the ordinary
    # case so the boundary leg above cannot drift into a weird general
    # "serve only uppercase" rule.
    status, headers, body = get(port, path="/xhr.js")
    assert status == 200, "/xhr.js -> %d, want 200" % status
    assert body == XHR_LOWER_BODY, "/xhr.js body not byte-intact"


# ---------- F-3a: serve() OSError branch (surviving mutants 46-56) ------

def test_oserror_branch_chmod000_gets_c10_404(port, docroot):
    locked = docroot[0] / "locked.js"
    locked.write_bytes(LOCKED_BODY)
    os.chmod(locked, 0o000)
    try:
        assert os.path.isfile(str(locked)), \
            "branch precondition: mode-000 file must still be isfile-true"
        # IN-PROBE GUARD (never silently green): if open() SUCCEEDS on a
        # 000 file the uid is privileged (root/DAC_OVERRIDE) and this leg
        # cannot reach the OSError branch — fail LOUD, naming the cause
        # (root-sensitivity declared, plan §2-2b + risk 7).
        try:
            with open(str(locked), "rb"):
                pytest.fail(
                    "IN-PROBE GUARD: open() of mode-000 file SUCCEEDED — "
                    "uid privileged (root? DAC_OVERRIDE?) — the F-3a "
                    "OSError branch cannot be exercised here")
        except OSError:
            pass  # the expected permission refusal: precondition holds
        status, headers, body = get(port, path="/locked.js")
        assert_c10_404(status, headers, body, "OSError branch /locked.js")
    finally:
        os.chmod(locked, 0o644)  # leave the tmp tree deletable/clean


# ---------- unknown-dir / escape / NUL refusal (plan §3 leg 6) ---------

def test_escape_nul_and_unknown_dir_refused(port, docroot):
    outside_rel = docroot[1]  # e.g. "../wt1-outside0" (sibling of docroot)
    target = outside_rel.replace(os.sep, "/")
    # Non-vacuity: the escape target exists and is readable OUTSIDE the
    # docroot — the 404 below is the resolver refusing, not file absence.
    real_target = os.path.join(str(docroot[0]), outside_rel, "secret.js")
    assert os.path.isfile(real_target), "escape target missing (blind leg)"
    with open(real_target, "rb") as handle:
        assert handle.read() == OUTSIDE_BODY, "escape target unreadable"
    for path in ("/%s/secret.js" % target,
                 "/%s/secret.js" % target.replace("/", "%2F"),
                 "/escape.js",
                 "/%00nul.js",
                 "/no/such/dir/deep.js",
                 "/index.secret"):
        status, headers, body = get(port, path=path)
        assert_c10_404(status, headers, body, "refusal %s" % path)
