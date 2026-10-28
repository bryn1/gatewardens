# Gatewardens v1.2 QoL milestone — PLAN [type:plan MC 11607]

Base: origin/main tip `5304d87` (VERIFIED `git log` this session; clean-code W1-W3 landed,
LEDGER.md:102-117). Owner order verbatim 2026-10-28: **"Go on all 3"** — item 3 (clean-code) is
DONE (LEDGER:117); this doc plans items 1-2: camera (F6) + backlog bundle (F1-F5).
READ-ONLY run: no repo edits; scratch `/tmp/v12cam/` (camera probes + live kit capture
`kit_pts.txt`). Skill note: `negative-testing` + `reasoning-techniques` loaded;
`file-a-child-card` NOT loaded (leaf profile — SOUL: "you do not file cards");
`reuse-research-gate` NOT loaded (its own scope excludes executing an existing plan — prior work
here is LEDGER + docs/ARCHITECTURE.md + .audits/20261028-0758-clean-code/FINDINGS.md, all read
this session).

## DA-fix c1 (2026-10-28)

Replace-not-delete revision per the DA gate c1 verdict FIX
(`/home/claudecode/.local/state/knut-dispatch/card-11607.out/DA-verdict.md`): P2-1 (F2 guard
mechanism + W2 row), P3-1 (pin #10 on the F4 fallback split), P3-2 (F3 planted-red declared),
P4-a..e applied, none declined. F6 camera numbers and the wave structure are UNCHANGED — every
F6 row MATCHED the DA's independent re-derivation (incl. the live kit re-run on a scratch copy
carrying the candidate rig: min_margin 121.8 px).

## Standing constraints (binding, restated)

Length reason (file hygiene, owner 2026-09-23): the MC 11607 brief mandates ONE deliverable with
ONE section per feature + a single WAVES/DA-gate tail — splitting would scatter one plan's rows.

- ZERO monetization ever (MC 11274.1; LEDGER:3-5, A8).
- Replace-not-add: no second mechanism beside an existing one answering the same question.
- Golden fixtures `tests/fixtures/mission_gatefall_*.jsonl` byte-pinned: **no step below alters
  mission.step-observable sim behavior.** Every feature below lives in UI/hub/router/visual layer,
  or adds NEW pytest files over NEW legs — each section names which. (The fixture runner is
  mission.step-only: `godot/sim/sim_headless.gd:145 m.step(DT)`, run by tests/test_sim_golden.py:45
  `SIM = "res://sim/sim_headless.gd"` through conftest.py:44 `run_probe_script` — VERIFIED this
  session; the ARCHITECTURE row's "sim/sim_harness.gd" name is stale, the shipped runner is
  sim_headless — carry a doc-sweep row for that ARCHITECTURE line when the doc is next touched
  (DA P4-e).)
- File hygiene 250 soft / 400 hard (check_hygiene gate; LOC per the gate metric
  `text.split("\n")` incl. the trailing-newline empty element — mission.gd AT 400/400, DA P4-a;
  FINDINGS.md §1
  W4 watch row: this milestone MUST NOT grow mission.gd).
- Suite 222 green + grows (NEW tests expected; note FINDINGS.md BASELINE: green is load-fragile
  on a busy box — SZ-1; suite legs below stay on the documented timeout).
- Visuals verified browser + describe-image per MC 11509 D3 (game visuals stay outside executable
  acceptance — MC 11509 D3 explicitly names game visuals).
- Godot repo-canonical binary `/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64`.
- LOCKED pins (FINDINGS.md §5, :140-152): this plan touches NONE of the 11 pins as written. Where
  a feature's ONLY real path runs through a pin (F6 only), the plan says "OWNER DECISION" and
  quantifies — it does not presuppose the exception.

Wave assignments: see §WAVES at the end. Verification legs per feature named there.

---

## F1 — RETURN-TO-HUB

**Today (VERIFIED).** Router: `main.gd:98 open_hub()` / `main.gd:105 start_mission()` mount one
`_routed` child of the persistent root (`main.gd:120-133 _mount`: `remove_child(_routed);
_routed.free()`). `open_hub()` is called ONCE at boot (`main.gd:93`). Mission end: outcome set in
`step_bookkeeping` (`mission.gd:267-270`, win-then-lose overwrite per F2-9), C13 commit exactly
once in `_end_mission` (`mission.gd:381-396`) — the HUD then shows the VICTORY/DEFEAT banner
(`hud.gd:163,242-244`, read-only display, pinned zero-Buttons contract LEDGER:68). The player is
stranded in the dead mission; reload is the only hub path (LEDGER:67 (a): "open_hub is boot-only;
state saves are committed on _end_mission, nothing lost").

**Contract (new, hub-route side — feature class: UI/router, no sim change).**
- Valid: `mission != null AND mission.outcome != null` → a "RETURN TO HUB" button (built in code
  by `main.gd`, a plain Control on a code-mounted CanvasLayer, bottom-center — NOT in hud.gd:
  HUD keeps its pinned display-only row) → click → deferred `open_hub()` → hub renders from the
  committed save. Route MUST be deferred (`call_deferred`/idle) — the engine fact + mechanism
  precedent is hub.gd's F-2 relay (`hub.gd:200-215`: free-inside-pressed-emit = console ERROR
  "Object was freed ... while a signal is being emitted"; deferred idle route is the shipped
  one-router answer, no second router).
- Invalid: button absent/click-starved while `outcome == null` (mid-mission) — the click path
  refuses; router state unchanged. Test asserts refusal + `main.mission` still the mission.
- Boundary: (1) same-tick win→lose overwrite (`mission.gd:267-270`) — button appears only after
  the full step() completes (input is processed between steps via the relay), so no torn state;
  (2) commit is once-gated by `committed` (`mission.gd:382`) — returning to hub fires NO second
  write; the hub simply reads state; (3) reload path stays (F1 adds a second, in-game exit to the
  same committed state — NOT a second save mechanism; (4) teardown (DA P4-c): the banner's
  CanvasLayer mounts UNDER the routed mission subtree, never as a sibling of `_routed` (it is not
  in mission.tscn — no pin #1 hit), so `_mount`'s `remove_child`+`free` tears it down with the
  mission, AND `open_hub()` hides any instance as a belt — a stale RETURN-TO-HUB button cannot
  survive into the hub.
- **OWNER DECISION — mid-mission abandon?** Two readings: (i) v1.2 ships END-OF-MISSION return
  only; mid-mission escape stays "reload" (saves already persist live — C13 mutated-writes,
  LEDGER:16); (ii) add an abandon button = must define rewards. **Recommendation: (i).** Abandon
  mid-run drags loot/XP semantics into scope (a loss already drops the tray, `mission.gd:288-289`
  — an abandon-as-lose button is cheap, but it invites "abandon at 99% to dodge the core-hit"
  play-testing we have no data on). If owner picks (ii): behavior = route through
  `mission._end_mission` with outcome="lose" (zero new money/loot paths — the loss leg already
  banks nothing), button gated by a confirm state.

**Files:** `godot/scripts/main.gd` (banner-mount + deferred route, ~25 LOC, 193→~218 gate-metric
✓), NEW
`tests/test_return_hub.py`. **NOT touched:** mission.gd (ceiling), hud.gd (pinned read-only),
mission.tscn (pin #1 ext-rows==4, test_mission_clicks.py:591), hub.gd, fixtures.
**Tests:** NEW `test_return_hub.py` engine tier (push_input click idiom,
test_mission_clicks.py:404 pattern): after `outcome="win"` + committed, click → `_routed` is hub,
`main.mission == null`, saved_ack unchanged (no second commit); planted-red: route synchronous
(emit-time free) → engine stderr non-empty → RED (W4 stderr-strict rule).
**Wave W2. Feature class: UI/hub/router — fixtures untouched (no sim/ edit).**

## F2 — BULK-SELL (bank loot)

**Today (VERIFIED).** The ONLY sell is the in-mission defense sell: placer → defense_obj.sell →
`SimEconomy.sell_value` (`defense_placer.gd:145-154`, `defense_obj.gd:248-250`,
`sim/sim_economy.gd:30`; pinned R1 formula, guarded test_economy_numbers.py:114). There is NO
item/bank sell anywhere — VERIFIED by grep `sell` over scripts+sim+data (only the defense rows)
and by the release-notes honesty line (LEDGER:115: "no shipped item salvage service"). Bank rows
live in `game_state.gd:55 var bank`, written ONLY through the named mutators (`bank_add` :109;
guarded by tests/test_hub.py:329 `test_no_bank_writes_beside_the_mutators` — a BAN-REGEX
`bank.append(|bank_add(` over the 8 HUB_LAYER scene-script files + a `mutated.emit(` source-scan,
NOT a named-mutator whitelist; VERIFIED read this session). Gold: `add_gold` /
`spend_gold` are the named mutators (`game_state.gd:138-150`).

**Contract (feature class: hub/meta UI + one new pure sim static + one new data key — fixtures
untouched, see money answer).** Hub gear panel gains a `SELL BANK` button: sells EVERY bank row,
one gold delta, one save commit.
- Valid: bank non-empty → `SimInventory.bulk_sell(bank, sell_values)` (NEW pure static, sim
  layer, returns `{gold:int, sold:int}` — pure, no RNG, purity-leg safe) → `GWGameState.sell_bank()`
  (NEW meta mutator): `bank = []`, `add_gold(total)` → `mutated` → C13 single write (the ONE
  save trigger — no new trigger mechanism).
- Invalid: **empty bank** → `{ok:false,"why":"empty"}`, bank/gold/save byte-identical (assert all
  three). Non-existent-uid / already-sold re-click = the same empty case idempotent (press twice:
  second refused, gold unchanged — negative-testing duplicates+repeats).
- "Non-sellable items": equipped gear is NOT in the bank (worn rows ride heroes, C6/C9 split,
  ARCHITECTURE:69) so bank-only sell structurally can't touch equipped gear — stated boundary;
  NO special classes exist (no egg rows in items.json — VERIFIED grep). Materials are NOT items
  (separate `materials` dict, game_state.gd:152-163) — out of scope, stated.
- **Money-delta location (replay-purity answer, the brief's question):** the delta lands in
  `GWGameState.add_gold` (`game_state.gd:138-141`), the meta layer, reached ONLY from the hub UI.
  Mission replay = scripted `mission.step()` rows (C12 funnel, `sim/sim_headless.gd:145`) — the funnel
  never calls game_state gold mutators (only `_end_mission` at commit time touches meta,
  `mission.gd:381-396`, and bulk-sell never edits mission files). Fixtures byte-unchanged;
  `test_sim_golden` stays green as the proof-leg.
- Pricing = DATA, not formula constants: NEW `rarity.json` key `sell_value: {worn:<g>,...}` (one
  int per ladder name). VERIFIED the schema gate tolerates it: `test_data_schemas.py:134` shape
  map checks presence+kind of NAMED keys — extra keys pass (check_shape body read). The exact-set
  trap (`assert set(...) == ...`) exists ONLY for `balance.feel` (test_data_schemas.py:199) —
  economy.json exact-shape (:172) is NOT touched. Values: owner/data-leg (suggest worn 2 →
  legendary 40, monotone with the ladder — I2: numbers in data).
- **OWNER DECISION — junk threshold vs all?** (i) single SELL BANK (all); (ii) sell-by-rarity-cap
  ("junk ≤ Powerful"). **Recommendation: (i)** — smallest contract, no new UI state; bank is
  small (chest-scale), and (ii) is a later filter, not a v1.2 QoL need. (If (ii): same mutator
  gains a max-rarity arg + one row — plan-compatible either way.)

**Files:** `godot/sim/sim_inventory.gd` (pure static), `godot/scripts/game_state.gd`
(365→~386 gate-metric ✓, mutator joins the named-mutator set — DA P2-1 CORRECTION: the
test_hub.py:329 `test_no_bank_writes_beside_the_mutators` guard is a BAN-REGEX (`bank.append(|
bank_add(`) over the 8 HUB_LAYER files plus a `mutated.emit(` source-scan — there is NO named
list to update, `game_state.gd` is not a HUB_LAYER file and `state.sell_bank(` matches none of
those patterns (DA probe; matches my own :329 read above); NO guard edit is required or made),
`godot/scripts/gear_panel_ui.gd` (170→~186 gate-metric,
button beside the bank list `gear_panel_ui.gd:32,97`), `godot/data/rarity.json` (+sell_value),
NEW `tests/test_bulk_sell.py`. **NOT touched:** defense sell path, economy.json, mission files.
**Tests:** NEW engine-tier leg (hub_probe idiom): single/multi-row gold = Σ sell_values, bank
empty after, save round-trip persists gold+empty bank, empty-bank refusal (all three unchanged),
double-press idempotence; source-truth leg (DA P2-1): grep in the new test that game_state.gd has
no `bank.append(`/inline `bank` write outside the sanctioned `bank_add`/`sell_bank`-clear, AND
re-run the UNEDITED test_hub.py green to prove sell_bank trips no :329 ban-regex (it is not a
HUB_LAYER file and the call string matches no pattern). Planted-red: sell writes bank WITHOUT
add_gold → gold assert RED.
**Wave W2. UI/hub/mount + pure static — fixtures untouched (no mission.step path).**

## F3 — RELIC-ASSIGN HARDENING

**Today (VERIFIED correct).** `mission_relics.gd:15-44` (C11): phase gate→`{"why":"phase"}`,
unknown defense→`"uid"`, relic not in pool→`"relic"`, double-assign BOTH directions (defense worn
OR relic owned)→`"taken"` (:24), unassign-clean→`"none"` (:37); pool semantics = clear, not move
(:39-40); sell-safe mirror via `live_count` (:71-76). Shipped negative coverage is REAL: the hub
probe asserts `assigned=1 refused_taken=1 refused_uid=1 refused_relic=1 refused_phase=1
refused_none=1 unequip=1 pool_intact=2` (hub_probe_mission.gd:97-98,159; test_hub.py:207-213
engine leg).
**Row = TESTS-ONLY LEG** — the task's "if implementation already correct" branch is the VERIFIED
branch (body read this session). The one uncovered negative: **stale uid across sell** —
"sell-safe (a sold defense's relic returns to the pool unassigned)" (`mission_relics.gd:69-70`)
is asserted for UNEQUIP (`pool_intact`), never for SELL (grep `sell` in hub_probe_mission.gd =
0 hits, VERIFIED). Per negative-testing (duplicates/stale-state/invalid-transition classes):
- assign(d,s) → `placer.sell(d)` → `relic_owner(m,s)==0`, `pool_row(m,s)` still pool-resident,
  `live_count`/C5 `relics_assigned` drop by 1 (C5 mirror read back through snapshot_json, not
  just the field — read-what-reached-the-world rule);
- assign to the SOLD uid → `{"ok":false,"why":"uid"}`;
- assign the sold defense's relic to a DIFFERENT live defense in the same build phase → ok:true
  (re-use after sell), then combat phase → new assign refused "phase" (transition gate);
- idempotence: unassign twice → second `"none"`; gold/pool unchanged across the sequence.
- "Assign to locked slot": C11 ships NO slot-locking (one relic per defense; mod-slot rarity
  gating is a DIFFERENT concern, items.json:397 rarity_min) — declared N/A rather than invented.

**Files:** NEW `tests/test_relic_negatives.py` ONLY (engine tier over the real mission.tscn,
test_hub.py:118 pattern). Zero implementation files. **Wave W1. Tests-only leg — fixtures
untouched (probe-level engine runs never write them).**
**Planted-red leg (P3-2, resolves the blanket "every gate proves it can go RED" row vs a
tests-only card):** the card mutates ONE asserted relic rule in a THROWAWAY scratch copy of the
engine tree (`/tmp`, never the repo — the tests-only contract forbids a repo edit), then runs the
new test file against it: (a) in a scratch copy of `mission_relics.gd`, drop the double-assign
guard at `:24` (so `assign` returns ok on a taken relic) → the `refused_taken` leg goes RED; or
(b) in the scratch copy, make the sell path leave the sold defense in `m.defense_list` (sell-safety
is that removal — `live_count` :71-76 and `relic_owner` :61-65 simply stop seeing the sold row, so
its relic is unowned again) → the new stale-uid/sell-return leg goes RED (relic still reads
owned, `relics_assigned` fails to drop). Green run beside the red run = the assertion bites. This
is the sanctioned way a tests-only card earns its planted-red evidence without touching product
code.

## F4 — FAMILY PICKER (bombard + hailspire shop buttons)

**Today (VERIFIED).** `classes()` returns ONE row per class, first-row-wins (`defense_placer.gd:
44-54`; towers rows: ballista/tower/100, bombard/tower/160, hailspire_tower/tower/140,
gate_blockade/50, barbed_snare/80 — VERIFIED from data), so the tower class button always places
the BALLISTA; the family picker is the placer's own DECLARED later row (`defense_placer.gd:40`).
Icons committed + TEX-pinned: `sprite_bank.gd:47-48` (`icon_bombard`, `icon_hailspire`; LEDGER:80
"icon-ready for the picker rows"). Placement TODAY = `placer.place(class_id, tier, slot=-1)` →
`row_for(class)` → ghost→`first_free()` fall-through (`defense_placer.gd:109-122,57-61,80-84`) →
`mission.place_defense(row, 1, at)` — THE ONE application site (cap + can_afford + single green
spend, `mission.gd:321-342`; C12 step (5) input is the sanctioned crossing).

**Contract.** Two build-bar buttons (icons pinned above), visible only in build phase: press =
place THAT family's T1 at the current placement selection — i.e. the SAME resolution order the
existing class buttons use (armed ghost, else first free slot; `defense_placer.gd:115-119`).
Reuse the EXISTING path: extend the placer with `row_for_id(id)` + `place_id(tower_id, tier,
slot=-1)` which resolves the row by id and then runs the IDENTICAL gate sequence ending at
`m.place_defense` — no second placement mechanism; `place()` keeps its class semantics (it may
delegate to `place_id` on the winner's id — one implementation of the gates, replace-not-add).
- Valid: build phase, affordable, slot free → placed, ghost/panel refresh, green delta via the
  application site (the panel re-reads state — it owns no cost math, defense_placer.gd:1-22 row).
- Invalid: non-build → `{"why":"phase"}`; no free slot → `{"why":"slot"}`; cap → `"cap"`; green
  short → `"green"`; unknown id → `{"why":"id"}` (NEW refusal string — add to the refusal test).
- Boundary: button disabled-state rides the W17e poll-sync mechanism (`defense_panel.gd:274`
  pattern — enabled flags from poll, NOT from pressed handlers, W17b false-green class); rapid
  double-press = two places or refusal, never a partial (each press runs the whole gate chain).
- LOC watch: defense_panel.gd is 373/400 gate-metric (372 by `wc`, +1 trailing-newline empty
  element — DA P4-a); +2 buttons +2 handlers ≈ +25
  LOC → lands ~398/400 → fits but tight (fallback TRIGGERS if the diff lands >400). fallback
  declared: W16-style split of the action-button block into a
  sibling file IN THE SAME CARD if the diff overflows. **P3-1 (LOCKED pin #10, FINDINGS §5 row
  10, VERIFIED read this session: "`tools/check_hygiene.py:78-83 GOVERNED_LITERALS` path-set +
  tests importing STRUCT_VALS from the gate — a SPLIT of a governed file must update the set in
  the same commit"): unlike the W16 mission split (mission.gd is NOT in the governed set — its
  siblings are absent from it), defense_panel.gd IS a member (`check_hygiene.py:83`), so if the
  split is taken the NEW sibling file MUST be added to `GOVERNED_LITERALS` in the SAME commit —
  `literal_violations` runs only over set members (`:227`), so moving governed code out without
  registering the sibling silently drops I2 governance (the moved literals become ungoverned).
  The F4 card's acceptance carries a grep: the sibling name present in the GOVERNED_LITERALS
  tuple, as a green-test leg.**

**Files:** `godot/scripts/defense_placer.gd` (row_for_id + place_id), `godot/scripts/
defense_panel.gd`, NEW `tests/test_family_picker.py`. **NOT touched:** mission.gd, data (icons
already registered), sprite_bank (TEX pins — adding rows there needs the V4 test-sync, avoided:
icons already pinned).
**Tests:** NEW engine leg: place_id("bombard") ok + green -160 via C5; place_id("hailspire_tower")
ok -140; the 4 refusals + new "id"; class-button path unchanged (`place("tower")` still ballista —
replace-not-add guard); planted-red: place_id bypasses cap check (calls place_defense with slot
skip) → cap assert RED. Browser+describe-image leg: buttons show icons (not text-only), click
placements visible in-world. **Wave W3. UI/mount + placer gate — fixtures untouched (placement
application site unchanged; C12 word-for-word).**

## F5 — ENEMY WALK ANIMATION — DECISION: (i) PROCEDURAL

**Today (VERIFIED).** 7 enemy ids (skitterling, ash_bandit, bone_lobber, husk_brute, cinder_wisp,
gale_harpy, warden_breaker — VERIFIED from enemies.json). Committed visual: static per-enemy
sheets + ONE committed-but-DECLARED-UNWIRED run pose `enemy_skitterling_run.png`
(`sprite_bank.gd:80`: "a run pose for the later animation card"). Visual update path (the mount
point): `enemy_runner.gd:122-146 step()` — per entity, per tick: `ent["node"].position =
mv["pos"]` (:136) + `SPRITE_BANK.face(...)` (:139); sheets built at spawn via
`SPRITE_BANK.make_sprite` (:56-57). Sim state = `ent["pos"]` (entity dicts); node position is a
downstream VISUAL only.

**Decision + argument.**
- (i) **RECOMMENDED — procedural step-bob/sway from move velocity, visual layer only.** A NEW
  un-governed helper `godot/scripts/enemy_anim.gd` owns the mechanism (amp/freq constants IN THE
  FILE — the declared ungoverned-visual precedent is fx_director, which owns its MAX_FX=64 and
  scale constants outside I2, FINDINGS §2; enemy_runner.gd IS I2-governed
  (check_hygiene.py:76-78 + FINDINGS.md:81) so it gains exactly ONE call line at :136-139 and NO
  literal). Mechanism: phase += |velocity|·delta; `node.position.y = pos.y + |sin(phase)|·amp`
  (+ optional ±sway on the billboard's roll — face() untouched); node offset NEVER writes
  `ent["pos"]` → sim rows byte-identical → goldens byte-identical (the test ASSERTS ent["pos"]
  unchanged). Uniform across all 7 enemies incl. boss. Determinism: pure function of accumulated
  path length — no RNG (purity untouched).
- (ii) REJECTED for v1.2 — 6 generated 2-frame sheets on the 3090: real budget (6+ renders, GPU
  window pauses the fleet verifier LLM per image_window semantics), and the failure class is
  PRECEDENTED: V1.1's DA-fix cycle was about pixel-kit honesty and CR-1 was a committed-but-
  UNWIRED skin claim (FINDINGS CR-1 P1) — more sheets = more claim-rot surface. Integration cost
  is worse: per-entity pose state + per-id texture swap = a SECOND visual path beside
  make_sprite (replace-not-add pressure), and 2-frame pop at variable walk speeds reads as
  strobe, not gait.
- (iii) REJECTED — hybrid gives ONE enemy a different motion language from the other six, and
  still pays both code paths. The skitterling sheet stays declared-unwired (honest, as today);
  if the owner wants it later, the natural home is an optional pose-map INSIDE the same anim
  helper — one mechanism, not two.
- Honest limitation: at the shipped ~13 px character height the bob is ±1-2 px — "alive shuffle",
  not limb gait. This composes with F6 (bigger read) and with any future sheet pass.
  Note: `balance.feel` is exact-set-pinned (test_data_schemas.py:199) — constants go in the file,
  NOT in feel{} (avoids re-pinning the schema gate for a visual flourish).

**Files:** NEW `godot/scripts/enemy_anim.gd`, `godot/scripts/enemy_runner.gd` (ONE call line),
NEW `tests/test_enemy_walk.py`. **NOT touched:** data, sim/, sprite_bank (TEX pins), hud.
**Tests:** NEW engine leg: step N frames → node y oscillates (min≠max) while every ent["pos"]
equals the no-anim run (diff-the-two-runs assert); v5_fx_probe tracer rows unchanged (kit leg).
Planted-red: amp constant → 0 → y constant → RED (and ent-pos assert stays the golden-proxy).
**Verification:** browser: wave-1 screenshot mid-walk + describe-image ("enemies show vertical
shuffle; no jitter/teleport"). **Wave W1. Visual layer — fixtures untouched (visual-only write
path, asserted).**

## F6 — CAMERA: deeper read — MEASURED

**Instruments (VERIFIED this session).** Gate A (suite): `test_hub_layout.py:331-384` — 28 points
(`_map_points`: waypoints+cores+spawners+hero), MARGIN 0.92 on an angular model at FOV 75°
VERTICAL, forward = −Z-col (basis row-read). Gate B (manual kit): `v1_world_probe.gd:174-215` —
33 rows = the SAME 28 unique points + 5 waypoint-duplicate `:end` rows (probe set read VERIFIED),
projected through the REAL Camera3D with a 60 px edge floor. Live kit run this session:
`V1W-FRAME n=33 ... min_margin=113.6 worst=lane_g3:wp0 floor=60.0 → V1W-OK` (matches LEDGER:82).
Python replication (33 live kit pixel rows, /tmp/v12cam): engine = transpose-of-rows basis, FOV
75 vertical — median error 0.91 px, max 21.3 px ON THE SHIPPED RIG because the shipped basis is
**not orthonormal** (rows (0,0.667,0.667)/(0,−0.746,0.746), col1·col2 = −0.112 — the V1 nudge
numerals are sloppy; the two gates therefore measure different things, and Gate A is the
conservative one). Clean orthonormal candidates make transpose=inverse — model unambiguous.

**Audit numbers reproduced + extended (all computed via the test's OWN functions / live kit):**
- shipped worst (Gate A) = **0.9096** at (34,0,30) — 98.9 % of the 0.92 budget; baseline rig
  (0,58,46) worst = 0.8741 ("worst point already at 95.0 %" = 0.8741/0.92, LEDGER:82 ✓).
- **pure zoom, dolly-along-view: +1.00 % max** (origin 70.451→69.751 along-to-hero — matches the
  audit's "blocks > +4.58 % from baseline" exactly: 1.0355×1.010 = 1.0458 ✓).
- **pure zoom, FOV-shrink: +1.55 % max** (fov_min 74.15°, Gate-A bound). Both are noise: not a
  card's worth of change. **Verdict: no deeper read exists on the CURRENT rig via zoom.**
- **Re-aim rig route (higher+steeper, hero slant D, orthonormal, pitch families 48/52/55° —
  gain/margins are D-dominated, pitch nearly free):** char gain = 70.45/D (px height of a 2 u
  hero; shipped 13.3 px):

  | D | char gain | Gate B margin px (floor 60) | Gate A worst (limit 0.92) | verdict |
  |---|---|---|---|---|
  | 52 | +35.6 % | 28.6–32.4 | ≥0.931 | RED both gates |
  | 56 | +25.9 % | 62.8–68.9 | 0.849–0.863 | green, 3–9 px over kit floor — thin |
  | 60 | +17.5 % | 90.6–98.0 | 0.778–0.797 | green |
  | **64** | **+10.2 %** | **113.6–121.9** | **0.718–0.739** | **green — margins ≥ shipped (113.6)** |
  | 66/68 | +6.8/+3.7 % | 127–142 | 0.66–0.71 | green, small |

**Recommended single rig change (the row whose gate math passes WITH MARGIN):** pitch 48° hero-
aim, D = 64 → `CameraRig transform = Transform3D(1, 0, 0, 0, 0.669, 0.743, 0, -0.743, 0.669, 0,
47.47, 42.79)` — character **+10.2 %** (and +14 % vs the pre-V1 baseline), Gate B margin **121.9 px
≥ shipped 113.6** (binding point unchanged: lane_g3:wp0 — same geometry class, strictly safer),
Gate A worst **0.718 vs 0.92** (huge headroom). Zero gate edits, zero FOV change, zero sim/
touch; a steeper 52°/D64 variant is identical math if the owner prefers the angle. Aggressive
variant D=56 (+25.9 %) ships at only 63 px kit margin — NOT recommended first move.
**Visual honesty rows:** steeper+closer re-frames the arena (crest badges/banners unchanged —
billboards face camera; the top screen band shows background beyond the 160 u plane exactly as it
does today at 41.8°, describe-image leg compares side-by-side); the current rig's non-orthonormal
rows get REPLACED by an exact rotation (a latent-sloppiness fix, declared).
**⚠ OWNER DECISION (the plan cannot require it):** changing the rig string moves **LOCKED pin #3**
(`test_hub_layout.py:337-341` regex + `:398-403` planted literal `...0, 56.33, 44.14)`) — a
stale literal CANNOT false-green: `:403` `assert planted != read_text(...)` RED-LOUDS when the
replace no-ops (DA P4-d — the failure mode is loud, not silent; the re-pin is a required
documented step, not a hidden hazard). The sanctioned path for an intentional move is exactly ONCE, documented in the LEDGER
in the same commit — precedented (the V1 nudge moved it once, FINDINGS §5 row 3 note). If the
owner declines the re-pin, the honest answer stands: **no deeper read exists without weakening or
moving gate-owned strings — ship no camera change.** RECOMMENDATION: grant the one documented
re-pin, ship the D=64 rig.
**Files (if granted):** `godot/scenes/mission.tscn` (CameraRig transform row only — pin #4
lighting rows untouched; pin #1 ext-rows untouched), `tests/test_hub_layout.py` (the pin #3
literal re-pinned once + LEDGER row), LEDGER/RELEASE_NOTES rows. **Verification:** suite green
(both camera tests), `v1_world_probe` LIVE re-run printing min_margin ≥ 110 px, browser screenshot
at 1280×720 + describe-image vs the V1.1-b anchor (`v7-mission.png` side-by-side, "characters
read larger, whole arena + both cores + spawner markers still on screen").
**Wave W4 (owner-gate first). Visual layer — fixtures untouched (camera is not sim state).**

---

## WAVES (sequential; parallelizable pairs marked ∥; file-disjoint inside each wave)

| wave | cards | files (exclusive) | notes |
|---|---|---|---|
| **W1** | **F3 ∥ F5** | F3: tests/test_relic_negatives.py • F5: enemy_anim.gd NEW, enemy_runner.gd, tests/test_enemy_walk.py | zero risk: tests-only ∥ visual-only; disjoint |
| **W2** | **F2 ∥ F1** | F2: sim_inventory.gd, game_state.gd, gear_panel_ui.gd, rarity.json, tests/test_bulk_sell.py • F1: main.gd, tests/test_return_hub.py | disjoint. test_hub.py DELIBERATELY ABSENT from W2 (DA P2-1): its :329 guard is a ban-regex over the 8 HUB_LAYER files, and game_state.gd (a meta-mutator file, not HUB_LAYER) + `state.sell_bank(` trip none of it, so NO guard edit is needed — sell_bank is a NEW bank writer that the ban-regex does not and must not match (bank_add is the sanctioned mutator; sell_bank CALLS the sanctioned path, it does not write bank inline). If sell_bank is implemented as a bare `bank = []` it WILL trip nothing (regex looks for `bank.append(`/`bank_add(`) — the F2 card asserts via the NEW test_bulk_sell.py that sell_bank routes through the sanctioned bank clear, NOT by editing the guard. |
| **W3** | **F4** | defense_placer.gd, defense_panel.gd, tests/test_family_picker.py | alone: panel LOC watch (373→~398 gate-metric); fallback split adds the sibling to GOVERNED_LITERALS in-commit (pin #10, DA P3-1) |
| **W4** | **F6 (OWNER-GATED)** | mission.tscn, test_hub_layout.py (pin #3 re-pin ONCE), LEDGER, RELEASE_NOTES | spawns ONLY on the owner's documented re-pin grant; else closes "no ship" |

Parallel pairs are lane-safe (dsh max 8, Lane E pre-flight at spawn time per fleet doctrine).
Every card's acceptance: full suite green (222 + new), `python3 tools/check_hygiene.py` 0 hits,
golden fixtures byte-identical (`git diff --stat tests/fixtures/` empty), its own planted-red
evidence beside the green run, LEDGER row in-commit.

**Verification legs per MC 11509 D3 (visuals):** F4/F5/F6 carry browser (Playwright dogfood idiom:
serve via server/, click the real path, state read back through GW_STATE()/snapshot, PNG) +
describe-image rows; F1/F2 are behavior-gated (engine legs) + one journey screenshot each.

**DA-gate note (binding):** this doc goes to `devils-advocate` BEFORE any card spawns (workflow-
plan two-phase; the orchestrator holds the SHIP/FIX/RECONSIDER loop). Prime DA targets: F6's
pin-touch honesty + the two-gates-disagree finding, stated per the measured reproduction state
(DA P4-b — the earlier "~2.5×" shorthand is RETIRED here: no re-checkable factor exists): the
engine's pixel projection reproduces from the 33 live kit rows at MEDIAN ~1 px error (my 0.91 /
DA's 1.02; max 21-27 px, convention-dependent — the F6 basis finding), while Gate A's angular
ratio is a DIFFERENT quantity — a proxy whose px-equivalent varies per point, calibrated at the
V1 rig — so a gate passing Gate A says nothing numerical about Gate B px margins and vice versa;
a gate-quality finding this plan SURFACES but does not fix in scope; F1's deferred-route edge
(click during the flush); F2's refusal-string
naming; F5's ungoverned-constants declaration.

**Owner-decision summary (each with recommendation):** (1) F1 mid-mission abandon — rec: NO
(end-only). (2) F2 junk-threshold vs all — rec: SELL ALL bank. (3) F6 LOCKED-pin #3 re-pin for
the +10.2 % rig — rec: grant ONCE, documented, ship D=64/pitch 48°.

*Assumptions/deviations stated:* DoD read "F1 mission end → hub" as the in-game return route
(today: reload-only, LEDGER:67(a)); F3 "assign to locked slot" declared N/A (no slot-lock in
C12/C11 — mod-slot gating is items.json's concern, cited above); suite count quoted as the card's
222 with FINDINGS' SZ-1 load-fragility note carried; "33-point gate" in the brief = the PROBE's
33 rows (same 28 unique points) — Gate A carries 28 — both numbers shown in F6.

# PLAN-END
VERIFY_EXIT=0
