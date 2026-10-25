"""W1 scaffold contract (card 11292): no autoloads (C1), the web export
preset shape (F2-3/F9), the FULL engine-template web shell with the GW
bridge inlined, the C10 static server smoke, and the hygiene gate proven
GREEN on the tree and RED on a planted bad file — a gate that has never
gone red is not a gate (A9 rule).
"""

import http.client
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

import conftest
from conftest import REPO_ROOT, repo_path

GODOT_TOKENS = (
    "$GODOT_PROJECT_NAME", "$GODOT_SPLASH", "$GODOT_SPLASH_CLASSES",
    "$GODOT_SPLASH_COLOR", "$GODOT_HEAD_INCLUDE", "$GODOT_URL",
    "$GODOT_CONFIG", "$GODOT_THREADS_ENABLED",
)
VS_BRANDED = ("VS_STATE", "__vsSnapshot", "vsHost", "vsShowSubmit",
              "Hollow Dawn", "HollowDawn", "vampire")
HYGIENE = repo_path("tools", "check_hygiene.py")


def read(*parts):
    with open(repo_path(*parts), encoding="utf-8") as handle:
        return handle.read()


def test_project_godot_has_no_autoload_section():
    project = read("godot", "project.godot")
    assert "[autoload]" not in project
    assert 'run/main_scene="res://Main.tscn"' in project
    assert 'config/features=PackedStringArray("4.7"' in project


def test_main_scene_wires_the_root_script():
    scene = read("godot", "Main.tscn")
    assert "[node name=\"Main\" type=\"Node\"]" in scene
    assert "res://scripts/main.gd" in scene
    assert "extends Node" in read("godot", "scripts", "main.gd")


def test_web_preset_contract():
    cfg = read("godot", "export_presets.cfg")
    assert 'html/head_include=""' in cfg
    assert 'html/custom_html_shell="res://web_shell.html"' in cfg
    assert "variant/thread_support=false" in cfg
    assert 'export_path="../static/index.html"' in cfg


def test_web_shell_is_full_engine_template_with_gw_bridge():
    shell = read("godot", "web_shell.html")
    for token in GODOT_TOKENS:
        assert token in shell, token
    assert "new Engine(" in shell
    assert '<canvas id="canvas">' in shell
    assert "window.__gwSnapshot" in shell
    assert "window.GW_STATE" in shell
    assert "window.gwHost" in shell and ".on_key(" in shell
    low = shell.lower()
    for name in VS_BRANDED:
        assert name.lower() not in low, name


def _free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class _Server:
    def __init__(self):
        self.port = _free_port()
        env = dict(os.environ, GW_PORT=str(self.port))
        self.proc = subprocess.Popen(
            [sys.executable, repo_path("server", "server.py")],
            cwd=REPO_ROOT, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def request(self, method, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.putrequest(method, path)
        conn.endheaders()
        resp = conn.getresponse()
        body = resp.read()
        conn.close()
        return resp, body

    def wait_ready(self):
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                resp, _ = self.request("GET", "/")
                return resp
            except OSError:
                time.sleep(0.1)
        raise AssertionError("server never answered on port %d" % self.port)

    def stop(self):
        self.proc.terminate()
        self.proc.wait(timeout=10)


def test_server_serves_placeholder_on_ephemeral_port():
    server = _Server()
    try:
        resp = server.wait_ready()
        body = server.request("GET", "/")[1]
        assert resp.status == 200
        assert resp.getheader("Content-Type").startswith("text/html")
        assert b"Gatewardens" in body
    finally:
        server.stop()


def test_server_path_escape_is_404_json_not_found():
    server = _Server()
    try:
        server.wait_ready()
        resp, body = server.request("GET", "/../server/server.py")
        assert resp.status == 404
        assert json.loads(body.decode("utf-8")) == {"error": "NOT_FOUND"}
    finally:
        server.stop()


def _run_hygiene():
    return subprocess.run([sys.executable, HYGIENE], cwd=REPO_ROOT,
                          capture_output=True, text=True)


def test_hygiene_gate_is_green_on_the_scaffold():
    proc = _run_hygiene()
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_hygiene_gate_goes_red_on_planted_bare_randf():
    probe = repo_path("godot", "scripts", "_hygiene_probe_tmp.gd")
    with open(probe, "w", encoding="utf-8") as handle:
        handle.write("extends Node\n\n\nfunc _ready() -> void:\n"
                     "\tprint(randf())\n")
    try:
        proc = _run_hygiene()
        assert proc.returncode != 0, "gate must fail on bare randf()"
        assert "_hygiene_probe_tmp.gd" in proc.stdout
        assert "randf" in proc.stdout
    finally:
        os.remove(probe)
    green = _run_hygiene()
    assert green.returncode == 0, green.stdout + green.stderr
