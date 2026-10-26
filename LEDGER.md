# Gatewardens LEDGER

Goal: clean-room DD2-style action tower defense, permanently free — no shop, no loot
boxes, no premium currency, no time gates, no battle pass (owner ruling 2026-10-25,
MC 11274.1). Stack: Godot 4.7.2 web export (pipeline reused from hollow_dawn_3d).

## Acceptance (REVISED 2026-10-25 after T1 research — original rows naming
## STR/DEX/INT/END stats, tower XP trees, and workshop base-building are RETIRED:
## those premises were CONTRADICTED by cited sources, see
## .audits/20261025-1033-dd2-decomposition/DD2-MECHANICS.md)

- A1 Combat: third-person hero — move/jump, two basic attacks, 4 abilities on ability
  mana (slow regen, full recharge each combat phase). No lock-on, no dodge (as original).
- A2 Heroes: level cap 50 + account-wide Ascension points (Offense/Defense/Utility);
  4-hero deck, hot-swap. v1 ships 3 heroes.
- A3 Defenses: green-mana economy (kills + wave completions, hard cap); place on buildable slots derived from lane geometry (open placement, no pads; confirm falls to first free slot),
  tier upgrades T1→T5 (50/100/150/200 base ratios), repair = base x 0.75 x missing-health, sell = total-spent x 0.75 x missing-health (cited wiki formulas; corrected 2026-10-25 per DA F12); per-map defense
  cap. Classes in v1: Towers (Ballista/Cannon/Frostbite-like), Blockades, Traps.
- A4 Mission: main core + sub-core, ground + air lanes, alternating build/combat phases
  (abilities refresh at phase start), 10 waves + boss wave; Campaign Normal|Hard.
- A5 Loot: direct enemy drops + one free Victory Chest per win. Rarities Worn→Sturdy→
  Powerful→Epic→Mythical→Legendary. Weapon rolls: primary/secondary stat + attack
  speed / shot type / projectile count.
- A6 Gear+services: weapon/armor/ring for heroes, Relics for towers; Mods with
  rarity-gated slots; hub NPCs: Blacksmith (Upgrade/Evolve/Reroll), Tinkerer (Tinkering
  = mod transfer), Training Dummies (DPS test), War Table (mission select), Stables
  (pet eggs → pet, v1 stretch row).
- A7 Meta persistence: hero XP/levels, ascension, gear bank — survives browser reload.
- A8 FREE-FOREVER: zero monetization of any kind, grep-checked; README states it.
- A9 Served locally, Playwright-verified full journey (wave 10 + boss kill, place/upgrade
  tower, loot pickup, equip, save+reload) + headless sim-number pytest with planted red.
- A10 Release doctrine (MC 11277): tag ships only with committed release notes +
  current README + doc-sync sweep at the tag.

## Status

| Phase | State |
|---|---|
| P0 T1 DD2 mechanics decomposition | DONE — MC 11274.1.1 VERIFIED (knut) 2026-10-25 |
| P0 T2 architecture DESIGN-draft.md | DONE — MC 11274.1.2 VERIFIED (knut) 2026-10-25 |
| P0 T3 DA gate round 1 | DONE — MC 11274.1.3 VERIFIED, verdict FIX (16 findings) |
| P0 T4 architecture revision DESIGN-draft-c2.md | DONE — c2 written 2026-10-25 |
| P0 T5 DA gate round 2 | DONE — verdict FIX (F8 residue + 12 new P2/P3) |
| P0 T6 architecture revision c3 | DONE — 13/13 rulings applied 2026-10-25 |
| P0 T7 DA gate round 3 (FINAL) | DONE — **SHIP** (3rd fresh reviewer, empirical re-probes) |
| PIN | DESIGN PINNED: docs/ARCHITECTURE.md (c3 + pin header) committed 2026-10-25 |
| BUILD W1 scaffold | DONE — commit 7b0fea7, pytest 8 green incl planted-red, real export sanity 6321 B live page (MC 11274.1.7) |
| BUILD W2 data files + schema tests | DONE — commit 795f61f, 67 pytest green, 3 planted-red proofs (MC 11274.1.8) |
| BUILD W3a sim core A | DONE — commit f276f2b, 86 pytest green, parse-probe leg live (MC 11274.1.9) |
| BUILD W3b sim core B | DONE — commit de3b044, 116 pytest green (MC 11274.1.10) |
| BUILD W4 core objects | DONE — commit 5a4a0e8, 122 pytest green, fresh-process save round-trip incl materials, parse leg stderr-strict (MC 11274.1.11) |
| BUILD W5 composition root + router + JS push | DONE — commit dab4b9f, 127 pytest green, headless boot probe green (MC 11274.1.12) |
| BUILD W6 mission scene core | DONE — commit 9532f56, 131 pytest green, funnel RED-proven, full headless doom-run (MC 11274.1.13) |
| BUILD W7 heroes | DONE — commit f51b966, 135 pytest green, first verified kill/blue/cooldown/swap (MC 11274.1.14) |
| BUILD W8 defenses | DONE — commit 26575a1, 139 pytest green, win path live (tower kills via slot-3 single site) (MC 11274.1.17; card 11322 cancelled — brief-probe paraphrased the pinned file name, re-filed 11324, trail on both cards) |
| BUILD W9 hub full | DONE — commit f2c4e79, 155 pytest green, 11-leg hub probe incl next_uid fix (MC 11274.1.16) |
| BUILD W10 HUD + hot-swap UI | DONE — commit d9214a2, 167 pytest green, read-only gate live (MC 11274.1.18) |
| BUILD W11 golden sim | DONE — commit 338720e, 172 pytest green, golden full-mission WINS byte-stable (MC 11274.1.19) |
| BUILD W11b P2 fix | DONE — commit 3a8c8b3, 175 pytest green, P2 closed (MC 11274.1.20) |
| BUILD W12 web export x2 + served contract | DONE — commit da64196, 180 pytest green, repro VERIFIED (9 files byte-identical A/B), doc-sync static/ (MC 11274.1.21) |
| A9 journey | PARTIAL — boot/hub/mission-live/lose/reload + F-1/F-2/F-3/starter fixes VERIFIED served (A9-journey.md, W13 evidence); wave-10+boss/place/upgrade/loot/equip/save+reload browser legs NOT yet run — golden proves them headless only. Full-browser journey leg REQUIRED before GA tag (per MC 11274.1.24 doc-sweep) |
| BUILD W13 journey-fix (hub layout+signal lifecycle+world visibility+starter data) | DONE — commit 865b668, 190 pytest green, A9 re-journey PASS (0 console errors, visible world, data starter live) (MC 11274.1.22) |
| CLEAN-CODE AUDIT | DONE — REVIEW.md, VERDICT FIX (4 P1 behavior gaps + refactor-safe set; MC 11274.1.23) |
| BUILD W14 P1 behavior legs | DONE — commit 1067391, 190 pytest green, golden byte-unchanged, all 4 P1 + P2-10 + P3-11 closed (MC 11274.1.25) |
| BUILD W15 hard-difficulty golden fixture | spawning |
| BUILD W15 hard-difficulty golden fixture | pending W14 |
| REFACTOR RUN (REVIEW.md refactor-safe set, zero behavior change) | pending W15 |
| FULL browser journey pre-GA (boss/place/loot/equip/save-reload served) | pending W16 |
| RELEASE DOCS + TAG (A10, MC 11277 rows) | pending W17 |

## Gate rounds log

- round 1 — FIX (MC 11274.1.3 VERIFIED) — the one thing that changed: design as written broke its own headless test tier (autoloads compile-fail under `-s`, proven) → c2 drops autoloads for statics + composition root, pins a step-funnel contract, names the server trim, adds gear-panel + save-ack, fixes the gates' word-list/scope. Rulings by orchestrator: cited wiki repair/sell formulas are authoritative for C3 (A3 row below corrected accordingly).

- round 2 — FIX (MC 11274.1.4) — the one thing that changed: round-1 fixes verified landed 15/16 (F8 cooldown-tick scope only in the ledger, NOT-FIXED), and the round-1 FIX's own replacement mechanism proved a NEW trap — custom_html_shell with a head-JS-only shell silently exports a dead 125-byte index.html (proven probe); plus a randf-gate that bans the rng calls C12 requires, a golden/hub-RNG/chest under-spec, two composition roots, an orphaned material economy, and an unobservable relic leg → c3 with rulings below.

## c3 rulings (orchestrator, 2026-10-25 — mechanical, no scope change)

- F2-1: hygiene bans BARE randf()/randi() only; receiver-qualified rng.randf()/rng.randi() REQUIRED as the sanctioned draw path (state both rules).
- F2-2: fixture format pinned (seed line + scripted-input rows + expected-output rows, hollow_dawn analogue shape); main.gd carries the runtime RNG (seeded OS entropy) and is the HUB-rolls RNG owner (svc_reroll/tinkering receive it); victory chest rolls fire in mission step (6) loot BEFORE the C13 mission-end commit.
- F2-3: web_shell.html IS the full Godot 4.7 web template page with $GODOT_* tokens + GW JS inlined (not head-JS-only); test_bridge_contract asserts the shell/exported HTML contains the engine bootstrap ('$GODOT_URL' token in shell, 'new Engine' in exported index.html) + canvas element.
- F2-4: I1 says on its face 'tripwire over a named-token list, NOT closure; adding/renaming any field in C5/C6/C8/C9 requires a design-review row'; egg stays legal (deferred pets legit); premium-gating of eggs would re-enter via design review, recorded.
- F2-5: one shared engine-free factory `GWCompose.build_graph(tables)` (sim/gw_compose.gd, class_name RefCounted static) — main.gd _ready AND every -s probe call IT; sole-construction claim now about the factory's wiring.
- F2-6: MATERIALS join meta: GWGameState gains materials:{id:int}; C6 [meta2] gains materials_json; add_material/consume_material mutators emit mutated; blacksmith/tinkerer costs pay gold+materials (DD2 truth §7).
- F2-7: C5 gains relics_assigned:int (journey asserts delta +1 on assign, -1 on unassign).
- F2-8: cooldown-tick scope pinned IN C4: only the ACTIVE hero's cooldowns tick; inactive/downed cooldowns are frozen (survive swap unchanged).
- F2-9: same-tick win/lose precedence: LOSE wins (core/hero-death checked after boss kill in step 5 ordering — state it).
- F2-10: auto-swap 'next healthy' = deck array order starting AFTER the fallen hero, wrap-around once.
- F2-11: equip() returns {ok, bank}; a replaced item ALWAYS returns to the bank inside SimInventory.equip (contract, not UI).
- F2-12: shared list/row widget scenes/item_row.tscn + scripts/item_row.gd named; gear bank list AND relic picker both instantiate it.

## Build notes carried (from DA-VERDICT-c3, P3, number-gate-gated)

BN1 check_hygiene must strip comments/strings before the bare-rand scan; BN2 name spend_gold-shaped mutator on GWGameState (emits mutated); BN3 chest tier indexing from rarity.json chest_tiers; BN4 save_probe reload = fresh process (two invocations) per I5; BN5 down-swap fires same-tick at detection; BN6 rng.randf( receiver form is convention + test_purity positive-list, not mechanical enforcement.

## Contradicted finding (child-caught W3b, fix routed to W4)

Parse-probe false-greens on parse failure (non-null broken resource; stderr = true signal) and class_name refs don't resolve clean-checkout under --headless --import. Ruling: new cross-file binds use preload(); parse leg asserts EMPTY stderr; docs/ARCHITECTURE.md I9/conftest row gains the rule in W4's commit. Wave 5+ MUST bind by preload until editor-scan caching is proven here.

## Engine facts (VERIFIED, bind all later waves)

E1 a signal connection does NOT keep a RefCounted method-listener alive — anchor listeners (held callable/WeakRef); inline connect(obj.new(...).method) dead-ports emits. E2 JSON.parse_string float-normalizes all numbers — byte-equality enforced at the save-FILE leg; state re-encode compares _json blobs semantically. E3 quit() under -s does not abort the running frame — probes early-return explicitly. E4 off-web JavaScriptBridge EXISTS but is NEUTERED (get_object -> stderr) — guard with OS.has_feature("web"), never singleton existence. E5 under -s add_child does NOT dispatch _ready — harnesses drive _ready directly (boot_probe precedent). E6 CharacterBody3D: `var velocity` shadows the built-in -> parse error -> -s probe _init aborts and process HANGS (null-child spam); use `vel` + manual integration (hero_runner/enemy_runner idiom).

## Release gate (owner doctrine MC 11277 + MC 11318)

v1 GA requires IN ORDER: full suite + A9 journey green -> CLEAN-CODE AUDIT (findings-only) -> REFACTOR run (zero behavior change, suite green) -> release-notes artifact + README current + doc-sync sweep -> tag/release. No GA on a dirty base.

## Findings open (pre-GA)

[CLOSED W11b 2026-10-26, commit 3a8c8b3, MC 11274.1.20: guard fixed to the sell() shape, negative legs shipped.]

## Open questions

- v1 mission count: one map polished first, 2–3 total? (design child decides shape)
