# W12 evidence — real web export, reproducible + served contract (MC 11274.1.21 / card 11331)

Seat: code (11331) · Date: 2026-10-26 · Repo: /home/claudecode/Games/gatewardens (main)

## Deliverables (one commit, declared scope)

- `tools/export_web.sh` — NEW, the wrapper: headless `--export-release Web` via the SHIPPED
  preset (thread_support=false, custom_html_shell=res://web_shell.html, export_path
  ../static/index.html); GW_GODOT env override (conftest idiom); ~15 lines, no cleverness.
- `.gitignore` — `static/*` + `!static/.gitkeep`; placeholder `static/index.html` UNTRACKED
  (`git rm --cached`) — a tracked file would go dirty on every export; static/.gitkeep is the
  committed discoverability marker.
- `tests/test_served.py` — NEW, engine-free stdlib tier (5 tests), module-skip WITH explicit
  reason when static/index.html missing (CI honesty).
- DECLARED extras beyond the brief's list (both genuinely required for the DoD):
  1. `tools/check_hygiene.py` — ceiling scope fix: the gate's OWN header and the pinned
     ARCHITECTURE hygiene row say "ceiling .gd/.py <= 400 ... data/config files (every other
     extension) are exempt from ceilings entirely", but the code applied the ceiling to ALL
     scanned CODE_EXTS — the gitignored BUILD `static/index.js` (910 lines) tripped it, so
     "check_hygiene 0 hits with the export present" was unachievable without it. One-hunk fix
     aligning code to the documented+pinned rule; tripwire/I8 scopes untouched.
  2. `README.md` — one DECLARED line naming the build + serve commands (the untracked
     placeholder's "run the Web export" pointer dies with it; the command must stay
     discoverable).
- `server/` NOT touched: the shipped GET/404 surface already satisfies every served assert
  (HEAD is answered 501 by the shipped server — C10 pins GET shapes only, no route added).

## R-list (pinned rows quoted / conflicts stated)

- F2-3 (pinned table): "web_shell.html IS the full Godot 4.7 web template page ($GODOT_*
  tokens + canvas + `new Engine`) with GW JS inlined ... bridge/served tests assert the engine
  bootstrap" → served-body asserts in test_served.
- C10 (pinned): "GET `/` → 200 text/html; .wasm → application/wasm; .pck →
  application/octet-stream; unknown/escaping path → 404 {"error":"NOT_FOUND"}" → pinned in tests.
- I1/I8 scopes include static/ → tripwire + rename greps STILL scan static/ (untouched); only
  the ceiling class changed (see declared extra 1).
- ARCHITECTURE body says static/ "committed ('web export x2' rule)" (layout comment + §static/
  bullet). The PINNED F-TABLE carries no artifact-commitment row; the brief overrides with
  trail doctrine ("built binaries evidence-side") and the DoD verifies no static/ artifacts
  via git show --stat. READ: the body bullet goes stale against this brief — LEDGER/orchestrator
  owns that doc line (LEDGER.md and docs/ are outside my declared commit scope; LEDGER W12 row
  left to the closing seat per the same rule).
- Brief "usable twice from clean static/" + "pck byte-identity NOT required — name what you
  asserted" → asserted rows below.

## Reproducibility pass (export A/B from clean static/)

`bash tools/export_web.sh` run twice, each after `find static -mindepth 1 ! -name .gitkeep
-delete` (clean static/ = the tracked marker only). EXPORT_A_EXIT=0, EXPORT_B_EXIT=0 (~4.7s each).

File SET (names+sizes), PASS A (PASS B `diff` = identical, FILE_SET_IDENTICAL):

| file | bytes |
|---|---|
| index.apple-touch-icon.png | 11944 |
| index.audio.position.worklet.js | 2973 |
| index.audio.worklet.js | 7298 |
| index.html | 6323 |
| index.icon.png | 5700 |
| index.js | 279815 |
| index.pck | 215104 |
| index.png | 21443 |
| index.wasm | 39514754 |

sha256 index.html — A `2d122612cdf216c2e1d9bdbef1bc137326edaf1fab69e179f660eb50865581b7` =
B (INDEX_SHA_IDENTICAL). Stronger measured fact ALSO held this build: per-file sha256 of ALL
nine files byte-identical A vs B (ALL_FILE_SHA_IDENTICAL) — the engine's .pck carried no
run-varying bytes; the CONTRACT nonetheless pins only file-set + index sha (engine-timestamped
.pck bytes would not fail the gate).

## Served contract (shipped server/server.py, ephemeral GW_PORT; GET-with-headers transcript —
HEAD answered 501 by the shipped server by design, C10 pins GET only)

| GET path | status | Content-Type | Content-Length |
|---|---|---|---|
| / | 200 | text/html; charset=utf-8 | 6323 |
| /index.js | 200 | text/javascript; charset=utf-8 | 279815 |
| /index.wasm | 200 | application/wasm | 39514754 |
| /index.pck | 200 | application/octet-stream | 215104 |
| /index.png | 200 | image/png | 21443 |
| /index.icon.png | 200 | image/png | 5700 |
| /index.apple-touch-icon.png | 200 | image/png | 11944 |
| /index.audio.worklet.js | 200 | text/javascript; charset=utf-8 | 7298 |
| /index.audio.position.worklet.js | 200 | text/javascript; charset=utf-8 | 2973 |
| /no-such-thing.nope | 404 | application/json | 22 |
| /../server/server.py | 404 | application/json | 22 |
| /%00nul.bin | 404 | application/json | 22 |

404 bodies verbatim: `{"error": "NOT_FOUND"}` (both probes). Server started
`Gatewardens server on http://127.0.0.1:53483 ...`, killed with TERM,
SERVER_STOPPED_CLEANLY=143 (WTERMSIG=15, no orphan). Tests boot the same server in a fixture
with terminate+wait teardown.

## test_served.py legs + gate red-proof (a gate that never went red is not a gate)

5 tests: root 200 text/html non-empty · F2-3 served body has `new Engine` + `<canvas` +
gwHost/__gwSnapshot/GW_STATE · NO raw $GODOT_URL/$GODOT_CONFIG (any `$GODOT_`) survives
substitution · every asset PARSED from the served body (regex, never hardcoded names) 200 +
Content-Length>0 (+ C10 types for .wasm/.pck) · unknown/escaping/NUL paths → JSON 404 shape.

GREEN (DoD run, export present): full suite `python3 -m pytest tests/ -q` → `180 passed in
19.16s`, PYTEST_EXIT=0 (prior 175 + new 5; test_served GREEN-NOT-SKIPPED).

PLANTED-RED: static/index.html replaced with a dead-shell placeholder (no engine bootstrap) →
`3 failed, 2 passed` (test_served_body_is_the_real_engine_bootstrap,
test_no_raw_godot_tokens_survive_substitution, test_every_referenced_asset_serves_200_nonempty)
→ file restored, sha = 2d122612... (matches export A), re-run `5 passed`.

SKIP-LEG: static/index.html moved aside → `SKIPPED [1] tests/test_served.py:37:
static/index.html missing — the web export is build-side and never committed; run \`bash
tools/export_web.sh\` first (W12 DoD runs it present)` → restored, `5 passed`.

## Hygiene

`python3 tools/check_hygiene.py` WITH the built export in static/: `check_hygiene: 0 hit(s)`,
HYGIENE_EXIT=0 (pre-fix the same tree produced `static/index.js:1: [ceiling] 910 lines > 400`
— the red case for the declared gate fix). test_served.py 159 lines ≤600; check_hygiene.py 219
≤400; export_web.sh 15 lines.

## Readings

- E-facts tier: N/A (no `-s` engine run in this card; stdlib tier only).
- `index.audio.*.worklet.js` are referenced by the engine JS at runtime, not by the index HTML;
  they sit in the served transcript anyway (all 200).
- Export determinism measured stronger than required (all-file sha equal); contract pinned at
  file-set + index.html sha per brief.
- server/server.py 501-on-HEAD noted, not changed (no C10 HEAD row; adding do_HEAD beside the
  shipped GET-only surface = a second mechanism without a contract).

VERIFY_EXIT=0
