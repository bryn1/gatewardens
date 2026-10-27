# W4 evidence — core state objects + wiring factory + persistence

MC 11274.1.11 / card 11302 — build commit: **5a4a0e8dedb6b1b49b6952ab01fa2f9118c206a3**
(author `code (11302) <code@agent-town.local>`; 14 files —
scripts/{game_state,save_store,bridge}.gd(+.uid), sim/{gw_compose,save_probe}.gd(+.uid),
sim/sim_parse_probe.gd, tests/test_persistence.py, tests/test_purity.py,
docs/ARCHITECTURE.md conftest/I9 rows; 973 insertions, 3 deletions).

## DoD rows (evidence levels)

| row | level |
|---|---|
| `python3 -m pytest tests/ -q` exit 0 — 122 passed (prior 116 + 6 new persistence legs) | VERIFIED this session |
| parse leg stderr-strict + its planted-red proof | VERIFIED (transcripts below) |
| save_probe A→B fresh-process round-trip incl. materials (BN4) | VERIFIED (two subprocesses) |
| `tools/check_hygiene.py` | VERIFIED: 0 hits (informational note: game_state.gd 308 lines > soft 250, < 400 hard) |
| ONE commit, exact scope, author code (11302) | VERIFIED (git show --stat) |
| ARCHITECTURE conftest/I9 rows gain the preload-bind rule + EMPTY-stderr parse-leg truth IN PLACE (retired F14 claim rewritten, not appended) | VERIFIED (diff in commit) |

## Readings (pinned table over brief paraphrase — stop-condition precedent MC 11274.1.9/.10)

- **GWBridge** = `class_name GWBridge extends RefCounted` keyboard relay per the PINNED
  Modules row ("NO Node/`_input` here"; adds Digit4, KeyE, KeyN, F1–F3, mouse-button codes).
  The brief's item-3 Node + `_process` pump + JS snapshot push is the **main.gd row's** own
  `_js_eval` mechanism (W5), never the bridge's. The "GWBridge is the ONLY Node subclass you
  may add" constraint is permissive — zero Node subclasses were added.
- **saved_ack is NOT persisted**: the pinned C6 `[meta2]` list = {gold, deck_json,
  completed_json, materials_json} carries no ack row; C13 mirrors the IN-MEMORY `write_seq`
  into C5 `saved_ack` via the compose listener. `test_c6_key_list_is_exact…` pins the exact
  (section,key) set AND the saved_ack absence (brief item 2's extra row superseded).
- **GWSaveStore API per pinned row**: `write(d:Dictionary)->bool`, `load_save()->Dictionary`,
  `var write_seq` (brief's `read()->dict|null` paraphrase is not the pinned name; {} =
  missing/corrupt/foreign = fresh start). ctor `(user_path="user://gatewardens.cfg", _rng=None)`
  per the brief, rng accepted-unused.
- **Wiring**: `GWCompose.StateCommit` listener connected to `state.mutated` (signal-to-callable
  — the brief's "…-style"). WHY not the compose_test lambda: VERIFIED leak below. WHY the
  listener is anchored at `state.commit_listener`: a Godot signal keeps only an ObjectID on a
  RefCounted method target — the inline `StateCommit.new(…).commit` form died at the end of
  build_graph and every emit reached nothing (VERIFIED this gate: write_seq stayed 0). The
  listener holds the state back via WeakRef only — no leak cycle either way.
- **JSON float-normalization (named limitation)**: Godot `JSON.parse_string` returns EVERY
  number as float, so a re-stringified *_json blob prints int 3 as 3.0 (VERIFIED:
  `stringify(parse(s)) != s` on a bank row). I5 byte-equality is therefore enforced at the
  FILE leg (load_save dict vs expected, byte-strict — ConfigFile returns blobs verbatim);
  the STATE leg (from_save→to_save) compares blobs semantically. Both legs must pass for
  `roundtrip=OK`.
- **Probe temp path**: XDG_DATA_HOME redirection (named by the arch save_probe row;
  user:// resolves under $XDG_DATA_HOME/godot/app_userdata/Gatewardens/ — VERIFIED); mode
  from `--` user args with GW_SAVE_PROBE env fallback (the brief's "args or env").
- **`.uid` sidecars**: generated via `godot --headless --editor --quit --path godot/` — that
  invocation aborts at exit in this headless export build (rc 134) AFTER writing the uid
  files; committed sidecars match the W3 idiom (all 5 new .gd files, 5 .uid files).
- `quit()` under `-s` does NOT abort the running function (VERIFIED: FAIL rows continued
  into a quit(0)) — probe legs early-return and each path calls quit() exactly once.

## Leak evidence (round-3 compose_test lambda form, re-run this gate)

```
$ godot --headless --path .audits/…/.tmp/compose_test -s res://probe.gd   # stderr:
WARNING: 6 ObjectDB instances were leaked at exit (run with `--verbose` for details).
ERROR: 3 resources still in use at exit (run with --verbose for details).
```

GWCompose A/B legs: 0-byte stderr (transcripts below) — the StateCommit wiring does not leak.

## pytest tail (full suite, exit 0)

```
$ python3 -m pytest tests/ -q
........................................................................ [ 59%]
..................................................                       [100%]
122 passed in 3.09s
```

## check_hygiene

```
$ python3 tools/check_hygiene.py | tail -1
note: godot/scripts/game_state.gd 308 lines > soft 250
check_hygiene: 0 hit(s)
```

(soft-250 note is informational — the C5 snapshot dict is one literal by design; hard
ceiling 400 respected, no `# hygiene:` exemption used.)

## save_probe invocation A (write leg — fresh process #1)

```
$ XDG_DATA_HOME=/tmp/gw_probe_home godot --headless --path godot/ -s res://sim/save_probe.gd -- write
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

SAVE-PROBE-A ack=1
SAVE-PROBE-A ack=2
SAVE-PROBE-A ack=3
SAVE-PROBE-A ack=4
SAVE-PROBE-A ack=5
SAVE-PROBE-A ack=6
SAVE-PROBE-A ack=7
SAVE-PROBE-A ack=8
SAVE-PROBE-A ack=9
SAVE-PROBE-A ack=10
SAVE-PROBE-A negative=OK
SAVE-PROBE-A saved_ack=12
SAVE-PROBE-A detail={"ack":12,"diff":{},"ok":true}
```

rc=0, stderr bytes=0 (no leak warnings). gold via `spend_gold` (BN2), materials, bank,
deck, completion and asc all fired; the refused overspend/overconsume emitted per the
pinned unconditional-emit contract (ack 11–12) while changing no values (`negative=OK`).

## save_probe invocation B (read leg — SEPARATE fresh process #2, BN4)

```
$ XDG_DATA_HOME=/tmp/gw_probe_home godot --headless --path godot/ -s res://sim/save_probe.gd -- read
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

SAVE-PROBE-B detail={"ack":0,"diff":[],"ok":true}
SAVE-PROBE-B roundtrip=OK
```

rc=0, stderr bytes=0. File leg byte-equal (all 9 C6 keys incl. materials_json); state leg
semantic-equal.

## planted-red: parse-leg stderr gate (W3b ruling, brief item 7)

Planted `godot/sim/sim_zz_planted.gd` (syntax error + printerr), ran
`python3 -m pytest tests/test_purity.py::test_parse_leg_all_modules_parse -q`:

```
>       assert proc.stderr == "", \
            "parse leg stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
E       AssertionError: parse leg stderr must be EMPTY (true parse signal):
E         SCRIPT ERROR: Parse Error: Expected parameter name.
E                   at: GDScript::reload (res://sim/sim_zz_planted.gd:2)
E                   GDScript backtrace (most recent call first):
E                       [0] _init (res://sim/sim_parse_probe.gd:37)
E         ERROR: Failed to load script "res://sim/sim_zz_planted.gd" with error "Parse error".
E            at: load (modules/gdscript/gdscript_resource_format.cpp:46)
E            GDScript backtrace (most recent call first):
E                [0] _init (res://sim/sim_parse_probe.gd:37)
tests/test_purity.py:92: AssertionError
FAILED tests/test_purity.py::test_parse_leg_all_modules_parse - AssertionErro...
1 failed in 0.68s
RED pytest rc=1
```

The RED fired on the NEW stderr assert (tests/test_purity.py:92 — checked BEFORE rc), i.e.
on the true parse signal, exactly the false-green class the W3b finding named. Planted file
removed; restored run:

```
.                                                                        [100%]
1 passed in 0.63s
GREEN pytest rc=0
```

## Negative legs shipped in tests/test_persistence.py (all green in the suite above)

- overspend/overconsume refused with zero state change (probe A `negative=OK` row)
- ack strictly grows per mutator AND keeps growing across the second write (ack rows +
  saved_ack > last emitted ack)
- readable-but-garbage save: pinned schema guard fresh-starts, B FAILs, NO crash (I5)
- unreadable save: `SAVE_LOAD_FAIL` + `*.corrupt` copy kept via RENAME (DawnWell move — a
  copy could not read an unreadable file), B takes the no_save fresh-start path (C6/I5)
- C6 exact (section,key) set + saved_ack non-persistence; C5 all 29 key literals; every
  C13 mutator (incl. BN2 spend_gold) carries `mutated.emit`

## Known limits on the record

- JSON blob interiors are float-normalized by the parser (file leg is the byte gate — above).
- Soft-250 exceeded by game_state.gd (308) — the C5 dict + pinned mutator set is one file's
  worth of contract; split would move the split decision into W5+ with new files.
- `saved_ack` mirrors write_seq in-memory only; a fresh process starts at 0 (the C5
  consumer polls a DELTA within a session, A7/C13 rule — never a cross-process compare).
- Browser (IndexedDB user://) leg rides the W9 served journey, not this desktop probe.

VERIFY_EXIT=0
