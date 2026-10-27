# W17d evidence — the SERVED keyboard is dead (MC 11274.1.31 / card 11396)

Repo /home/claudecode/Games/gatewardens, branch main.
Commit: 940ecc68b317dfe834f395c233aa897190cb2c43 (author `code (11396)`).

## Root cause (quote, main.gd BEFORE this fix, lines 171–178)

```gdscript
func _install_js_relay() -> void:
	if _js_bridge == null:
		return
	_js_relay = _js_bridge.call("create_callback", _on_js_key)
	_js_bridge.call("eval", "window.gwHost = window.gwHost || {};", true)
	var host: Object = _js_bridge.call("get_object", "gwHost")   # <- DEAD API
	if host != null and _js_relay != null:
		host.set("on_key", _js_relay)
```

`get_object` is the Godot 3 JavaScriptBridge API. On 4.7.2 the call raises
"Nonexistent function"/proxy error, `host` is null, the guard skips, and
`window.gwHost.on_key` is NEVER assigned — exactly the measured served
state (`Object.keys(gwHost) == []`, all three synthetic event routes
inert). web_shell.html:107 relays behind an existence guard → silent
no-op.

## 4.7 semantics — VERIFIED against the SHIPPED engine (instrument citations)

Source of truth: the engine binaries the export pipeline itself ships —
/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64
(v4.7.2.stable.official.ed1daf0bf) and
~/.local/share/godot/export_templates/4.7.2.stable/web_release.zip /
web_debug.zip (godot.wasm). No docs site used; every claim below is
measured this session (probe project .tmp/w17d/probe, exported release,
served on :8123, driven via Playwright MCP):

1. `--dump-extension-api` (desktop binary): JavaScriptBridge methods =
   `eval(String,bool)`, `get_interface(String)->JavaScriptObject`,
   `create_callback(Callable)->JavaScriptObject`, is_js_buffer, … — no
   get_object.
2. ClassDB in the live WEB build (probe print):
   `PROBE has_get_object=false` — the dead call's name is not a method.
3. wasm strings (release + debug, exact-match): `create_callback` 1,
   `get_interface` 1, `JavaScriptObject` 1, `get_object` 0, `dispatch` 0.
   → the brief's `.dispatch` hypothesis is DISCONFIRMED on this engine;
   no such string exists in either shipped wasm.
4. get_interface returns a TRANSPARENT JS proxy: every METHOD call
   (`win.call`, `host.set`, `cb.get_class`) is routed to the underlying
   JS object and errors `obj[method] is not a function` (console
   transcripts .playwright-mcp/console-2026-10-26T21-36-07-889Z.log,
   console-2026-10-26T21-41-13-206Z.log). The install therefore rides
   the PROPERTY path (`host.on_key = cb` → native `_set` virtual), the
   untyped-var dynamic-assignment form.
5. Return shape: JS call `window.gwHost.on_key("X", true)` returns
   `null` SYNCHRONOUSLY — `ret_is_promise=false`. No promise exists in
   this engine, so a `.catch` guard has nothing to catch; shipping one
   would be dead code (declared reading of the DoD gate line: it names
   the brief's PRE-RESEARCH tokens `.dispatch(`/`.catch`, while the Fix
   section itself orders "inspect Godot 4.7 JavaScriptBridge semantics
   FIRST … ship the ONE correct install idiom". The gate asserts the
   measured-shipped contract instead; divergence declared, not silent).
6. Argument shape: the GDScript callable receives ONE Array
   `[code:String, down:bool]` — `PROBE3 cb_in code=Digit1 down=true
   t_code=4 t_down=1` — matching the existing `_on_js_key(args: Array)`
   and bridge.on_key contract.
7. E1 anchor is LOAD-BEARING: with the relay held only in a local, the
   proxy died at `_ready` return and every JS-side call became a silent
   no-op (probe v2: call succeeded, `cb_in` never printed). The
   `_js_relay` MEMBER keeps the handle alive — kept, unchanged.

## Install mechanism (shipped, main.gd web branch, diff of the commit)

```gdscript
_js_relay = _js_bridge.call("create_callback", _on_js_key)
_js_bridge.call("eval", "window.gwHost = window.gwHost || {};", true)
var host = _js_bridge.call("get_interface", "gwHost")   # was get_object
if host != null and _js_relay != null:
	host.on_key = _js_relay                              # was host.set(...)
```

Order kept: the `gwHost || {}` eval merge runs BEFORE get_interface
(probe: get_interface binds an EXISTING global). Shell untouched —
measured fact 5 shows its guard-less fire-and-forget call is safe
(sync, null, engine swallows script errors internally; 11 calls, zero
unhandled rejections). Desktop path untouched (has_feature("web") guard
kept; boot leg stderr still empty).

## Live proof of the shipped idiom (probe v3 = EXACT fix code + shipped shell)

`cp godot/web_shell.html` into the probe project, export release, boot
in Chromium (Playwright MCP):

```
PROBE3 install_done host=true
real keys  : PROBE3 cb_in code=Digit1 down=true  t_code=4 t_down=1
             PROBE3 cb_in code=Digit1 down=false ...  (keyup)
             PROBE3 cb_in code=F1 down=true / down=false
synthetic  : 6x cb_in code=F2 (KeyboardEvent dispatched to window,
             document AND canvas — all three orchestrator routes fire)
             cb_in code=ProbeRet (direct call)
ret_type = "null", ret_is_promise=false
```

11 callbacks, zero errors. Console log:
/home/claudecode/Games/.playwright-mcp/console-2026-10-26T21-45-13-235Z.log
This is ENGINE+shell proof of the install line — NOT the product re-
journey (hero swap/abilities/stations in the REAL export), which is the
orchestrator's tier.

## Mouse-path declaration

Mouse input is unchanged and rides the native Godot canvas input:
main.gd `_unhandled_input` (lines 135–149) forwards
InputEventMouseButton → `bridge.mouse_code(button_index)` →
`bridge.on_key("MouseLeft"/"MouseRight"/"MouseMiddle", pressed)`.
Godot's web runtime delivers real mouse events on the canvas as
InputEvents natively (panel clicks WORKED in the journey — the brief's
own finding), so no JS mouse relay is installed and none is needed.

## Gates (this session, exit codes captured)

- Full suite: `python3 -m pytest tests/ -q` → `206 passed in 39.61s`,
  GREEN_EXIT=0 (204 prior + 2 new legs in tests/test_bridge_contract.py).
- `python3 tools/check_hygiene.py` → `check_hygiene: 0 hit(s)`,
  HYGIENE_EXIT=0. main.gd 192 lines ≤ 250.
- New legs: `test_web_branch_installs_gwhost_on_key` (create_callback +
  get_interface + web-guard tokens + the assignment as an exact CODE
  line) and `test_web_branch_no_godot3_get_object_call` (the retired
  CALL stays grep-zero; header prose is blanked context, not a call).
- Planted red 1 (install line → `pass  # PLANTED-11396`):
  `FAILED … test_web_branch_installs_gwhost_on_key — install assignment
  missing as CODE`, RED1_EXIT=1.
  First run of this plant stayed GREEN and exposed a gate defect (the
  token substring was satisfied by the header comment); the leg was
  rewritten to an exact stripped-CODE-line match and the plant then
  went red. The gate is trusted only after this second run.
- Planted red 2 (restore `call("get_object", "gwHost")`):
  `FAILED … installs_gwhost_on_key` + `FAILED …
  no_godot3_get_object_call`, `2 failed, 5 passed`, RED2_EXIT=1.
- Restore → `7 passed` bridge contract file, full-suite green above.

## Runtime proof PENDING (orchestrator re-journey)

Static + engine-level browser proof is landed and mine; the product
re-export + served-build keyboard journey (Digit1–4 abilities, F1–F3
hero swap, hub stations) is PENDING the orchestrator's browser
re-journey over a re-export of this commit.

git sha: 940ecc68b317dfe834f395c233aa897190cb2c43

VERIFY_EXIT=0
