# W13 evidence — A9-journey fixes F-1/F-2/F-3 + OPEN-Q starter meta
MC 11274.1.22 / card 11332 — frontend (11332) — 2026-10-26
PROBE: stat -c %s /home/claudecode/Games/gatewardens/.audits/20261025-1033-dd2-decomposition/w13-hub-fresh.png => ^[1-9][0-9]{3,}$
COMMIT: 865b6683798632903045cdd4afe482f1cd96069b (author frontend (11332))
Built served artifacts (evidence-side, never committed): index.html sha256 a7cd4abbf65675afd37febc6…, index.pck sha256 0b33e5cd46a019a0594d6413…

## Fixes

F-1 (P1 hub overlap) — hub.gd layout is CONTAINERS end to end: hub root →
VBox "Layout" (PRESET_FULL_RECT) → rows: VBox "Stations" (title / Meta
status / HBox Bar) + VBox "PanelSlot" carrying all five station panels
(one visible per the shipped _open model). A Container ASSIGNS children
positions → the all-at-(0,0) stack is structurally impossible; no numeric
positions anywhere in hub.gd (the test_hub cost-literal gate holds).

F-2 (P2 freed-during-signal console ERROR) — mechanism choice: the
engine's own route-out-of-signal-frame. hub.gd re-targets the war-table
Start buttons at setup: it disconnects war_table's OWN bound start
callables and reconnects them through `_route_out_of_signal_frame`, which
re-fires the same Callable via `fn.call_deferred()`. The button press
emit finishes with the hub intact; the start crossing lands at idle time,
so main._mount's free happens while nothing emits. main.gd and
war_table.gd stay VERBATIM (the "if avoidable" clause holds — it IS
avoidable): a hub-side deferred ROUTER proxy was rejected because the
shipped hub_probe WAR leg asserts the spy synchronously and call_deferred
under `-s` flushes only at loop exit (VERIFIED empirically this card:
BEFORE-DEFER / AFTER-DEFER-QUEUED / DEFERRED-FLUSHED at exit).

F-3 (P2 world invisible) — mission.tscn ONLY (mission.gd untouched):
CameraRig reframed to a 3/4 view (0,58,46), ~48° pitch, framing the WHOLE
gatefall playfield (every lane waypoint, both cores, all spawners and the
hero battle space project inside the default 75° FOV at 1280x720 — gate
computes it stdlib-side); WorldEnvironment row added (background
0.055/0.065/0.085 vs ground albedo 0.22/0.24/0.27 → contrast; ambient
0.6 → shadow sides read; tonemap filmic). Sun node untouched.

OPEN-Q starter meta — from_save's FRESH branch (no save / foreign schema)
seeds the declared starter kit from DATA ONLY, zero literals: gold =
economy.json "starter": {"gold": 100}; deck = heroes.json roster in FILE
order (raw array door, mission._load_array precedent — W3a dict door
drops array files; header amended honestly). Seeded SILENTLY: direct
field writes, no mutator call, no `mutated` emit → no C13 write on fresh
boot (ack=0 first-boot reading holds; the kit persists with the first
real mutation — engine leg asserts file absent→present and write_seq
0→1 exactly there).

## Starter kit shipped + what pins it (recorded reading)

Starter gold = 100 — a DECLARED economy.json row; NOT balance tuning
(no service costs ≤100; fresh accounts hold no materials, so the first
purchases are mission-grown — the number is an honest non-zero meta
display, revisable in data alone). Starter deck = the full 3-hero roster
[warden, deadeye, embercaller] in heroes.json order = C4 swap order.
Pinned by: economy.json exact-key set (tests/test_data_schemas.py) +
fresh-boot engine leg (tests/test_persistence.py: temp user:// fresh →
boot graph → from_save → gold/deck match the data, silent-seed ack/seq
and file rows) + served fresh browser (GW_STATE gold=100, deck 3).

## Verification (all executed this session)

`python3 -m pytest tests/ -q`:
    190 passed in 21.40s        (prior 180 + 10 new green)
`python3 tools/check_hygiene.py` → check_hygiene: 0 hit(s)  (exit 0)

SERVED RUNTIME (fresh export via tools/export_web.sh EXPORT_EXIT=0,
server/server.py GW_PORT=8131, Playwright 1280x720, isolated headless):
- Fresh boot GW_STATE: gold=100, deck=[warden,deadeye,embercaller],
  saved_ack=0, schema 1, phase hub → OPEN-Q closed on the served product.
- Hub rows readable, no overlap: w13-hub-fresh.png (title / meta row /
  station bar / WAR TABLE + both Start entries as distinct rows).
- TWO hub→mission switches (two page sessions): console ERRORS = 0 both
  times (A9 recorded the freed-signal ERROR once per switch) → F-2
  VERIFIED served. Mission live: phase mission, green=300, core
  1000/1000; wave 0 spawned (alive=1 t=25.1); honest lose at t≈36.
- World visible at default zoom: w13-mission-build.png (ground/sky
  contrast, main core, sub_north, hero, HUD), w13-mission-combat.png
  (red enemies on the lane path approaching the core). F-3 VERIFIED.

## Planted-red transcripts (every gate shown RED-capable this card)

== F-1 ENGINE TIER: stacked tree through the real overlap check ==
rc = 1
GWLAYOUT-FAIL { "row0": [P: (0.0, 0.0), S: (121.0, 23.0)], "row1": [P: (0.0, 0.0), S: (66.0, 23.0)], "row2": [P: (0.0, 0.0), S: (78.0, 23.0)] }
(green leg, same check: title=(0,0) meta=(0,27) bar=(0,54) station=(0,89),
 buttons x=0,90,140,238,316 — four disjoint laid-out rows, GWLAYOUT-OK)

== F-1 SOURCE TIER: tampered hub.gd through the stacking gate ==
violations: ['station war not mounted in the PanelSlot']
clean tree: []

== F-3 FRAMING: sky-aimed rig through the frustum gate ==
outside-frustum points (planted): 28 of 28 -> [(-40,0,0), (-28,0,4), …]
outside-frustum points (shipped): 0 of 28

In-suite planted-red tests (run with the suite): test_hub_layout
planted-red ×3 (source tier, engine tier, framing) + starter zero-literal
gate; test_hub's existing cost-literal gate untouched and green.

## R-list (readings + deviations)

- R1 DECLARED scope addition: tests/test_data_schemas.py — the economy
  exact-key row (and one combined starter-shape assert, net-zero lines)
  rides WITH the DoD-allowed economy.json starter key: the pinned
  exact-set assertion makes the two DoD clauses (starter keys in
  economy.json + full-suite green) logically force this row. No other
  test file carries edits beyond the named starter-leg file
  (test_persistence.py) and the named new test (test_hub_layout.py).
- R2 F-1 reading: "distinct layout position per station" enforced the
  Godot-idiomatic way the brief names (rows/anchors/containers): one
  shared container slot (shipped one-visible model), disjoint laid-out
  header rows, origin-mounting RED. Per-station distinct origins were the
  CAUSE of the finding; per-station distinct SLOTS would re-stack in one.
- R3 No new .gd files → no new .uid needed (probe sources live inside the
  test files and run from temp dirs — clean-checkout identical).
- R4 Engine facts VERIFIED this card: under `-s`, add_child never
  dispatches _ready even with frames running (E5, re-proved: routed stays
  null at frames 1–4 while a child _process fires); boot_probe's explicit
  _ready() call remains the correct harness idiom; frames DO iterate
  under `-s` when the script keeps running → Container geometry computes
  (the engine-tier geometry leg rests on this); `-s` accepts absolute
  script paths (test-side temp probes); user args read via
  OS.get_cmdline_user_args().
- R5 docs/ARCHITECTURE.md economy data-table row (starter key) and the
  hub/Modules row (container layout) want a doc-sync line — the file was
  already DIRTY by another session's uncommitted change at this seat's
  start (static/ doctrine edit); NOT touched, NOT committed. Orchestrator
  doc-sync row recorded here for the closing pass.
- R6 mission.gd untouched (allowed for camera/light lines only — the
  scene nodes carried all of F-3; the C12 funnel stays word-for-word,
  matcher green). hub.tscn untouched (center watermark label is a sibling
  of the layout, never overlapped rows).
- R7 static/ re-exported for runtime evidence (gitignored artifacts —
  test_served re-passed against the fresh build; W12 reproducibility rule
  unchanged).

## Files (committed, sha 865b668)

godot/scripts/hub.gd (F-1 + F-2) · godot/scripts/game_state.gd (starter) ·
godot/scenes/mission.tscn (F-3) · godot/data/economy.json (starter key) ·
tests/test_hub_layout.py (new) · tests/test_persistence.py (starter leg) ·
tests/test_data_schemas.py (R1)

VERIFY_EXIT=0
