# W5 evidence — composition root + scene router + JS snapshot push + bridge contract

Card: MC 11274.1.12 / 11304. Commit: `dab4b9f008a609f948bc2b211163efd3eb313ecb`
(author `code (11304)`, 9 files: main.gd, hub.gd(+.uid), hub.tscn,
mission_stub.tscn, boot_probe.gd(+.uid), test_bridge_contract.py, conftest.py).
`Main.tscn` needed no change — already the real root Node wired to main.gd
(the row's shape; left untouched). `bridge.gd` NOT extended: the pinned
forward-only relay made an extension strictly unnecessary (declared).

## Gate 1 — full pytest suite (exit 0)

```
$ python3 -m pytest tests/ -q
........................................................................ [ 56%]
.......................................................                  [100%]
127 passed in 3.62s
PYTEST_RC=0
```

122 prior + 5 new legs (cfg shell contract / GW names shell+main / retired
names 0 raw hits in I8 scope / F2-3 engine bootstrap / boot_probe engine
tier). Hygiene: `check_hygiene: 0 hit(s)` (rc 0; notes informational, the
game_state.gd soft note is pre-existing).

## Gate 2 — boot-probe transcript (conftest engine-tier shape, real
temp user:// pre-seeded via save_probe write = a REAL from_save)

```
== save_probe write (seed, XDG_DATA_HOME=/tmp/tmp.zD9r8UQD5Y) ==
SAVE-PROBE-A ack=1 … ack=10
SAVE-PROBE-A negative=OK
SAVE-PROBE-A saved_ack=12
SAVE-PROBE-A detail={"ack":12,"diff":{},"ok":true}
SEED_RC=0
seed stderr bytes: 0

== boot_probe (same temp user://) ==
BOOT_RC=0
BOOT-PROBE-SNAP {"alive":0,"asc_points":1,"bank_count":1,"blue":0.0,"blue_max":0.0,"boss_hp":null,"cores":{"main":{"hp":0.0,"max":0.0},"subs":[]},"deck":[{"id":"deadeye","level":1},{"id":"warden","level":3},{"id":"embercaller","level":1}],"defense_cap":0,"defenses":0,"difficulty":"normal","equipped":{},"gold":30,"green":0,"green_cap":10000,"hero_hp":0.0,"hero_hp_max":0.0,"hero_id":"","loot_pending":0,"mission_id":"","outcome":null,"phase":"hub","phase_kind":"build","relics_assigned":0,"saved_ack":0,"schema":1,"t":0.0,"wave":0,"wave_remaining":0}
BOOT-PROBE-OK
boot stderr bytes: 0
```

from_save legs visible IN the read-back snapshot: gold=30 (50−20),
bank_count=1, deck 3 (warden level 3), schema=1, phase=hub, and
saved_ack=0 — boot mutates nothing, so the C13 write_seq mirror starts at
0 (mission-local noise spam guard). Fresh-home run also BOOT-PROBE-OK
(fresh-start I5 path), rc 0, stderr empty.

## Gate 3 — planted-red proof (the gate can go RED)

`GW_STATE` stripped from godot/web_shell.html
(`sed -i 's/GW_STATE/GW_RETIRED/g' godot/web_shell.html`):

```
>           assert name in shell, "GW name %r missing in web_shell.html" % name
E           AssertionError: GW name 'GW_STATE' missing in web_shell.html
tests/test_bridge_contract.py:60: AssertionError
=========================== short test summary info ============================
FAILED tests/test_bridge_contract.py::test_gw_names_present_in_shell_and_main
1 failed in 0.07s
```

Restored with `git checkout -- godot/web_shell.html` (2 GW_STATE hits back),
re-run: `1 passed in 0.01s`. Full suite re-verified green after restore
(Gate 1 above ran on the restored, committed tree).

## Engine facts VERIFIED this gate (add to the E-list for later waves)

- E4: off-web the `JavaScriptBridge` singleton EXISTS but is NEUTERED —
  `call("get_object", …)` = "Nonexistent function" SCRIPT ERROR on stderr.
  Existence is NOT the guard; `OS.has_feature("web")` is (main.gd).
- E5: under `-s` the main loop never processes a frame, so `add_child`
  during a SceneTree harness `_init` does NOT dispatch `_ready` — the
  harness must drive the real `_ready()` (boot_probe.gd; the W1 main.gd
  stub never proved otherwise since its _ready only printed).
- Boot fail-fast reads the pinned STEMS at FILE level (exists + JSON
  parses): the W3a dict door deliberately drops array-shaped files
  (heroes/towers/enemies/items/mods), so a table(stem)-empty check
  false-REDs on healthy data (caught by the fresh boot-probe run, stderr
  BOOT_VALIDATE_FAIL table=heroes). The deep validate static ships with
  the validate_probe row.

## Scope note

Commit touches ONLY: main.gd, hub.gd(+.uid), hub.tscn, mission_stub.tscn,
boot_probe.gd(+.uid), test_bridge_contract.py, conftest.py (the brief's
sanctioned helper extension — run_probe_script). hub.gd.uid rides hub.gd
under the same `.uid`-artifact reading the row names for boot_probe.
Readings (router boots to hub — no title.tscn in the pinned scene list;
NOT-BUILT stub fallback for the pinned mission path; read_input()
paraphrase = forward-only relay) are in the commit message.

VERIFY_EXIT=0
