# DA-VERDICT — T3 gate over the Gatewardens v1 architecture (MC 11274.1.3 / card 11281)

Target: `DESIGN-draft.md` (this dir). Reviewer: devils-advocate profile, 2026-10-25.
Reads: DESIGN-draft.md, LEDGER.md, DD2-MECHANICS.md (all in this dir / repo root); the actual
claimed sources under /home/claudecode/Games/hollow_dawn_3d and /home/claudecode/Games/vampire_survivor;
three empirical experiments with the pinned binary
`/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64` (exists, VERIFIED), scratch in
`.tmp/autoload_test`, `.tmp/phys_test`, `.tmp/i1_regex_test.py` of this audit dir.

## Findings

### F1 — P0 — Autoloads × the `-s` SceneTree golden harness are mutually exclusive (Placement plan `scripts/` table, sim/sim_headless.gd + sim/save_probe.gd rows, C1, I6)
The design introduces 4 autoloads (Data, GameState, SaveStore, Bridge), mandates C1 ("every
consumer gets tables ONLY via `Data.table(name)`" — i.e. scene scripts reference the autoload
identifier), and claims sim_headless "loads the real Main.tscn … extends hollow_dawn sim_headless
pattern" (`godot --headless -s` SceneTree script), with save_probe "writes a known meta state via
SaveStore". EMPIRICAL REFUTATION: a minimal project with `[autoload] Data=...`, run as
`Godot_v4.7.2 --headless -s probe.gd` (probe extends SceneTree, loads a scene whose script calls
`Data.table()`), prints `INIT: has_autoload_singleton=false` then
`SCRIPT ERROR: Compile Error: Identifier not found: Data` — the scene script fails to COMPILE in
`-s` mode. Autoload identifiers are not registered under a custom-SceneTree `-s` run. The two
source repos — whose proven harness this claims to EXTEND — have **zero autoloads**:
`hollow_dawn_3d/godot/project.godot` and `vampire_survivor/godot/project.godot` contain no
`[autoload]` section; VS `main.gd:21-42` composes `GameState.new()` / `GameWorld.new()` /
`preload(...).new()`. The harness pattern works precisely because there are no autoloads. As
specified, `test_sim_golden` and `test_persistence` (the second tier the whole test story leans on)
cannot load Main.tscn at all. Fix direction: follow the sources — class_name RefCounted statics +
an explicit composition root; or drop the "loads real Main.tscn under -s" claim and redesign the
golden tier. (Scratch repro: `.tmp/autoload_test`.)

### F2 — P1 — No engine tick exists under the `-s` harness; mission.gd is `_process`-driven (sim/sim_headless.gd row, scripts/mission.gd row, I7)
`mission.gd` gates spawns in `_process`. Under `-s`, `_process` never runs, and manual stepping is
impossible: probe run of `iterate(1.0/60.0)` inside a SceneTree subclass on Godot 4.7.2 →
`SCRIPT ERROR: Parse Error: Function "iterate()" not found in base self` (scratch
`.tmp/phys_test/probe.gd`). hollow_dawn solved this by its own manual funnel — its sim_headless
header says it "drives main.gd's real _step loop manually at the fixed 1/60 delta". The gatewardens
module table has NO `_step(delta)` contract on mission/phase/hero/defense — none of the driving
interfaces exist. Also unspecified: the RNG seed for the golden run (crit rolls via
`hero_hit(...,roll)` and SimLoot rngs — who seeds what, so fixtures are byte-equal?). Two builders
will invent two different drive-APIs. Fix: name the step-funnel contract (one method per owning
module), pin the seed source.

### F3 — P1 — The server trim is impossible as written (Placement plan `server/` rows, C10, Rejected-alternatives "Leaderboard/server-side profile")
Design: "server.py + static_app.py trim, api.py/db.py DROPPED" and "static_app.py copied verbatim
from VS". But `vampire_survivor/server/static_app.py:13` is `from api import send_error_json`, and
`vampire_survivor/server/server.py:15-17` imports `api`, `static_app`, and `db` (`from db import
Database`). Verbatim copy + dropped api.py = ImportError, server never starts; C10's 404 shape
(`{"error":"NOT_FOUND"}`) is produced by `api.send_error_json`. Two builders: one writes an ad-hoc
shim, one keeps a stub api.py — different shipped files, different test_served. Fix: specify the
trimmed server explicitly (own `send_error_json`, static-only dispatcher) or name the kept api.py
subset.

### F4 — P1 — The A9 journey step "equip" has no module; A6 "Relics for towers" has no interface anywhere (Module task breakdown, scripts/ table, GameState row)
A9 requires the Playwright journey to cover "equip". A6 lists "Relics for towers". The design's
mutator is `equip(hero,slot,item)` — hero-only; no defense-relic equip path exists in
defense_obj/mission/C3; and the module table ships NO inventory/equip panel (hub, war_table,
blacksmith_ui, tinkerer_ui, dummy_range, HUD+hot-swap, loot — no bank/equip UI). The journey
dead-ends at its own acceptance step; a builder adds an undeclared module mid-build. Fix: add the
gear panel module + a `equip_defense(...)`/relic contract, or amend A6/A9 in the LEDGER (owner-
visible), not silently.

### F5 — P1 — No save trigger is specified, and the browser-persistence path is tested nowhere in the claimed sources (C6, I5, scripts/save_store.gd row, test_persistence row)
C6 pins the write MECHANISM (tmp+rename) but no caller/trigger: who calls `write_save` — on every
mutator? mission end? hub close? A7's acceptance is BROWSER reload. The claimed source's save test
runs DESKTOP godot with `user://` redirected via XDG_DATA_HOME (hollow_dawn tests/test_save.py
docstring + `GODOT = os.environ.get("HD3D_GODOT", "/home/claudecode/Games/.tools/godot/...")`
leg); VS never used user:// at all (server-side sqlite for its meta). So test_persistence verifies
the desktop FS path while A7 ships IndexedDB-backed Web storage — first exercise is the A9 journey
with NO synchronization contract: C5 has no `saved`/dirty/write-ack field, so Playwright cannot
know the write landed before triggering reload → racy acceptance. Fix: name the save trigger,
expose the save ack in C5, and state the Web-flush rule (wait-for-ack before reload).

### F6 — P2 — I2 literal-whitelist is not realistic for the scripts it governs, and its scope does not cover MUST HOLD 2's claim (Invariants I2)
Measured on the closest real analogue in the repo that inspired this design,
`vampire_survivor/godot/scripts/world.gd` (script-style extraction, comments+strings stripped):
**91 numeric literals, 52 outside `{0,1,2,-1,0.5}`, 30 distinct** (0.015, 0.06, 0.22, 0.25, 0.7,
1.3, 3.0, 4.0, 5.0, 8.0, 12.0, 16.0, 60.0 …) — feel/interp/timer/index constants, not balance. A
4-ability kit needs 3 and 4; hero_combat has 4-ability indices; interpolation constants are banned.
The predictable builder move when the gate goes red: widen the whitelist in check_hygiene.py (gate
rots, code unchanged). And the gate LAUNDERS balance instead of catching it: nothing forbids a
non-enumerated module (hero_controller.gd — which carries no gravity/jump fields in heroes.json or
balance.json, so gravity/jump balance MUST live there) or a scripts/tuning.gd holding the numbers;
`"3.5".to_float()` string literals pass any integer/float-literal regex; sim/*.gd formulas are
unchecked by the whitelist. MUST HOLD 2 as stated ("numbers OUT of .gd sources") is mechanized only
over 5 named files. Fix: govern FEEL params via a data table too, or restate I2 as the weaker true
claim; extend the grep or accept the hole on the record.

### F7 — P2 — Duplicate stat sources: two builders would wire blue regen and start-green differently (data/economy.json vs data/heroes.json rows, C7)
`economy.json blue:{regen_per_sec:float, refill_on_phase_start:true}` AND `heroes.json base:{…,
blue_regen}` — `tick_blue(blue,regen,cap,dt)`: the regen argument's source is nowhere named
(global? per-hero? sum? override?). Same for `economy.json green:{start}` vs C7 map `start_green`,
and `defense_cap_default` vs C7 `defense_cap` (fallback relation unstated). C4/C3 don't pick. This
is exactly the "interface underspecified enough that two builders implement it differently" test.

### F8 — P2 — Mid-mission hero hot-swap (attack surface 4): the seam is one clause deep (scripts/hero_controller.gd row, C4, C5)
The entire spec is "deck swap calls GameState/mission re-parent pawn" plus bridge keys F1–F3.
Unspecified: whether blue is shared (C4 says "mission-local blue" — ONE pool) while
`base.blue_max` differs per hero → clamp rule on swap (swap into a squier hero with a mage pool:
over-cap?); hero HP carry-over (C5 exposes hero_hp/hero_hp_max per active hero — swap restores the
SWAPPED-TO hero's saved HP? from where — mission-local table?); ability cooldowns per hero vs
global; in-flight projectiles owned by the swapped-out pawn; camera rig continuity. Named attack
surface — REFUTED: two builders will ship visibly different swap semantics.

### F9 — P2 — The web_head.js ↔ export_presets.cfg duplication is inherited, mis-described, and its test pins presence, not identity (EXTENDED paragraph, I8, test_bridge_contract)
Verified state of the sources: VS `godot/web_head.js` exists AND the same JS is inlined in
`godot/export_presets.cfg` `html/head_include` — VS's own `docs/ARCHITECTURE.md:82-83` admits "the
cfg string mirrors godot/web_head.js (escape-aware…)"; no sync mechanism exists (grep for web_head
in VS *.py/*.sh returns only docs). And hollow_dawn — the repo the design says to take preset.0
from — has NO web_head.js file at all; its cfg carries inline **VS-branded** JS (`__vsSnapshot`,
`vsHost`, `vsShowSubmit`, `fetch("/api/highscores")`) — a "copy preset.0" builder imports dead
leaderboard JS calling an endpoint v1 drops, and I8 would go red on it. The design's I8/test
require only PRESENCE of GW_STATE/__gwSnapshot/gwHost in web_head.js AND the cfg — both may be
present and different: the shipped export carries whatever is inline in the cfg at export time, so
a stale bridge passes the test. Fix: single-source the head JS (generate the cfg string or use
custom_html_shell), and make test_bridge_contract assert content identity.

### F10 — P2 — I1 monetization word-gate: measured false negatives AND false positives (Invariants I1; named attack surface 5)
Ran the regex as written against candidate words (`.tmp/i1_regex_test.py`):
- FALSE NEGATIVES (paywall seams that pass): `lockbox`, `lockbox_keys`, `cash_store`,
  `purchase_item`, `iap_id`, `paywall`, `wallet`, `store_id`, `unlock_with_keys`, `monetize`. Note
  `loot.?box` does NOT match **`lockbox`** — the exact mechanism of DD2's own monetization
  inventory row 4 (DD2-MECHANICS §10: Lockboxes, key-gated) passes the gate named after it.
  `shop\b` also misses identifiers `ShopPanel`/`Shopkeeper`/`BlacksmithShopZone` (no word boundary
  mid-identifier) while flagging a bare UI string "Shop" — inverted from intent. `buy_` matches
  neither `buyItem` nor `buyback`.
- FALSE POSITIVES (legit words that trip `(?i)gem` substring): `lane_management`,
  `engagement_ring`, `arrangement.json` — a red gate on benign identifiers gets the gate disabled.
- The wrapped pattern in the design itself (`…|key_count|real.?` / `money|…` across lines 191-192)
  contains a line break inside `real.?money`; copied literally it can never match "real money".
The design's REAL defense is structural (no key/timer/paid-currency fields in C6/C8/C9 — this
verified true and is the stronger claim). Fix the word list (`lockbox|purchase|cash|iap|wallet`,
drop bare `gem` for `\bgem\b`) or label I1 as a tripwire with named holes.

### F11 — P2 — I8's "VS_STATE/vsHost absent repo-wide" is unsatisfiable (Invariants I8)
The design draft itself (line 212), DD2-MECHANICS, and every VS doc quoted in this audit contain
`VS_STATE`/`__vsSnapshot`/`vsHost`. A repo-wide grep includes `.audits/**` and `docs/**` → the
gate is red forever and will be scoped out ad hoc by a builder. Pin the scope: `godot/ server/
static/ README.md` (+ the export cfg), with `.audits` explicitly exempt.

### F12 — P2 — C3 repair/sell formulas deviate from the cited ground truth (Contracts C3 vs DD2-MECHANICS §4)
Ground truth (DD2-MECHANICS §4, VERIFIED quote): repair = "Base Green Mana Cost * 75% * % of
missing health"; sell = "Total Green Mana Cost * 75% * % of missing health". Design C3:
`repair_cost(total_spent, missing_ratio, 0.75)` (base-vs-total ambiguous — parameter named
"base_total" vs prose "total_spent") and `sell_value(base_total, 0.75)` — **the missing-health
factor is dropped from sell entirely**, so a fully damaged tower still sells at 75% of total spent,
which removes the DD2 damage penalty and opens a cheap-repair/full-value-sell seam. LEDGER A3 says
only "repair/sell at 75%" — name which is authoritative (LEDGER simplification or the cited wiki
formula) and pin the signature.

### F13 — P3 — C5 snapshot has no mission-outcome/victory/game-over/boss field (Contracts C5)
The A9 "wave 10 + boss kill" assertion can only be inferred (wave/alive churn, then hub phase +
bank_count after the chest) — indirect and builder-divergent. One field (`outcome:"win|lose|null"`,
or `boss_hp` during wave 11) closes the journey's weakest assertion.

### F14 — P3 — The clean-checkout class-cache quirk of the inherited harness is not carried (tests/conftest row)
hollow_dawn's test_save.py had to add `ensure_class_cache()` (`godot --headless --import` before
any `-s` run) because `class_name` resolution dies on a fresh checkout without
`godot/.godot/global_script_class_cache.cfg` (its own comment: "VERIFIED: preload alone cannot
dodge it"). The gatewardens design — which leans on `class_name` for all of sim/ (I8) — does not
mention it; a fresh-clone run dies at parse.

### F15 — P3 — LEDGER acceptance rows silently absent from the design: A6 "Stables (v1 stretch row)" and A10 release-doctrine appear nowhere in the module table or invariants
Stretch is optional but must be named as deferred (the design's file list has no pets/stables
seam at all); A10 (release notes + README + doc-sync at tag) has no owning row. A retired/deferred
row that survives silently is CONTRA-DOCTRINE (fleet rule: rewrite or mark, never leave standing).

### F16 — P3 — Small underspecifications that split builders
C1 half-introduces `Data.map(id)` (appears in prose only, absent from the data_registry interface);
`lane_path.advance(pos:Vector2, …)` vs C7's `[x,y,z]` waypoints — which plane the Vector2 lives in
and how y=flight-height projects is unstated; `SimTables.validate` has no named caller (boot-time
fail-fast? test-only?); test_waves wording "10 waves" vs C8 "11 entries, index 10 boss".

## Named attack surfaces — explicit dispositions
1. I2 literal-whitelist realism: REFUTED — see F6 (measured 52/91 violations in the closest
   shipped combat script; bypass paths enumerated; scope ≠ MUST HOLD 2 as claimed).
2. Sim purity / `-s` runnability: REFUTED — see F1 (autoloads compile-fail scenes under `-s`,
   empirically) and F2 (`iterate()` unexposed in Godot 4.7 GDScript → `_process`-driven mission is
   unsteppable); the statics-only sim files themselves ARE pure and runnable — the failure is the
   harness tier the purity claim exists to serve.
3. One map + 11 waves vs A9: no refutation found for: the map/wave COUNT itself — because A4 pins
   exactly "10 waves + boss wave", C8 matches it, and one map exercises every C1–C10 contract; the
   A9 JOURNEY surface, however, is refuted at three named steps (equip: F4; save+reload sync: F5;
   outcome assertion: F13).
4. Hot-swap F1–F3 re-parent seam: REFUTED — see F8 (blue pool vs per-hero blue_max clamp, HP
   carry-over, cooldown ownership, in-flight projectiles: all unspecified).
5. Monetization word-gate I1: REFUTED both directions — see F10 (measured false negatives including
   `lockbox`, measured false positives via `gem` substring; structural absence of paid fields in
   C6/C8/C9 verified TRUE and is the real guard).

## Claims checked TRUE (so the gate is not one-sided)
- export preset facts: preset.0 Web, `variant/thread_support=false`, `export_path="../static/index.html"` — both repos, VERIFIED by reading `*/godot/export_presets.cfg`.
- "VS main.gd:84 mechanism": exact — `grep -n '__vsSnapshot' vampire_survivor/godot/scripts/main.gd` → line 84.
- VS bridge relay (`on_key`, `held`, `drain_presses`, `move_vector`) — VERIFIED in `vampire_survivor/godot/scripts/bridge.gd`.
- C10 static contract: `.wasm → application/wasm`, `.pck → application/octet-stream`, realpath jail, 404 NOT_FOUND, NUL-byte guard — VERIFIED in `vampire_survivor/server/static_app.py` (modulo the api-import breakage, F3).
- Source-truth regex test style ("test_game_numbers.py") — exists in both repos' tests/.
- "web export x2" rule — VS README line 19 (`run twice`).
- Godot 4.7.2 binary present at the path the inherited tests pin; both repos' `config/features` = "4.7".
- hollow_dawn save pattern (tmp+rename, quarantine, SAVE_LOAD_FAIL marker) — real, but it is a
  `class_name DawnWell extends RefCounted` statics class, NOT an autoload (F1's fix direction).

## What fails which invariant
- MUST HOLD "sim purity guarantees headless-runability" (design I6/test story): FAILS as shipped
  for the harness tier (F1/F2), not for the sim statics.
- MUST HOLD 2 (numbers out of .gd): PARTIALLY mechanized at best (F6); duplicated sources (F7)
  contradict "one data truth".
- MUST HOLD 1 (zero monetization): structural schema claim holds; the named gate has holes (F10).
- A9 (journey) and A7 (browser reload) as accepted: not achievable with the module set as designed
  (F4, F5, F13).
- A10: unowned (F15).

## Verdict rationale
The decomposition (data/sim/scene split, contracts C1–C10, reuse targets) is genuinely good and
most EXTEND claims check out. But F1 is a proven, load-bearing impossibility in the design AS
WRITTEN, and F2–F5 each break a named acceptance row. None requires a redesign — all are
specification fixes in the design doc plus one mechanism decision (drop autoloads → statics +
composition root, exactly what both source repos already do). That is FIX territory, not
RECONSIDER.

# VERDICT: FIX
