# W1 scaffold — evidence (MC 11274.1.7 / card 11292)

Date: 2026-10-25. Seat: code (11292). Repo: /home/claudecode/Games/gatewardens (main).

## Commit

    7b0fea70649e942eadc71791a0f51d4f98feb8f4  code (11292) <code@agent-town.local>
    W1 scaffold: Godot 4.7 project w/o autoloads, full-template web shell +
    GW bridge, Web export preset, GW own static-only server, hygiene gate +
    scaffold tests  —  18 files changed, 871 insertions(+)

git status after commit: only `?? .audits/` (evidence dir, not committed by design).

## pytest (DoD command)

    $ cd /home/claudecode/Games/gatewardens && python3 -m pytest tests/ -q
    ........                                                        [100%]
    8 passed in 0.41s
    exit=0

Tests: test_scaffold.py 8 green — no [autoload]; main-scene/script wiring; cfg
(head_include="" + custom_html_shell="res://web_shell.html" + thread_support=false
+ export_path ../static/index.html); web_shell.html contains ALL 8 $GODOT_* tokens
+ `new Engine(` + `<canvas id="canvas">` + __gwSnapshot/GW_STATE/gwHost.on_key and
ZERO VS-branded names; server smoke on ephemeral port GET / → 200 text/html
placeholder; /../server/server.py → 404 body {"error":"NOT_FOUND"}; hygiene gate
green on the scaffold AND planted-red proof (godot/scripts/_hygiene_probe_tmp.gd
with bare randf() -> exit!=0, file:line hit, cleaned up, green again).

## hygiene gate

    $ python3 tools/check_hygiene.py
    check_hygiene: 0 hit(s)
    exit=0

## Export sanity (bonus — RUN, not skipped)

    $ godot --headless --import godot/            -> exit 0 (class cache, F14 form)
    $ godot --headless --path godot/ --export-release Web   -> exit 0 (preset export_path)
    static/index.html: 6321 bytes (>1000), 1x "new Engine", 1x <canvas id="canvas">,
    2x window.gwHost + 1x window.GW_STATE (GW bridge carried), 0 unsubstituted
    $GODOT_* tokens, <title>Gatewardens</title> — LIVE page proven at W1.
    Companion files (index.js/.wasm/.pck/.png/audio worklets) removed, placeholder
    restored (247 B); pytest re-run green after restore; one commit unchanged.

## Inputs honoured

- godot/web_shell.html base = web_release.zip godot.html from
  ~/.local/share/godot/export_templates/4.7.2.stable (cmp-identical to the gate's
  working skeleton .tmp/shell_test/shell_full.html — the dead 125-byte head-JS
  shape (out_noph/index.html) is impossible: whole-template + F2-3 asserts in place).
- Server mechanics from VS static_app/server (realpath jail, NUL guard, ext
  allowlist incl. .map for debug wasm.map and .js covering audio.*.js/square.*.js);
  `from api import` REPLACED by GW's own send_error_json (F3/C10).
- BN1 honoured: check_hygiene blanks comments + string literals before the I1
  tripwire and the bare-rand scan (comment words can never trip it); prose .md
  not scanned.

## Ambiguity readings stated

- I8 scope for check_hygiene = the three scope DIRECTORIES (godot/ server/
  static/) + README.md, scanned RAW; docs/ARCHITECTURE.md excluded — it names the
  VS tokens itself as the invariant text and I8 exempts quote-necessary docs.
- I2 literal whitelist not in W1 (governed scene scripts exist W3+); lands in
  check_hygiene.py then — no second gate.
- Static-only server: methods other than GET answer the C10 NOT_FOUND shape.
- test_scaffold keeps the strictest [autoload] reading (any substring) — the
  project.godot comment was reworded instead of loosening the test.

VERIFY_EXIT=0
