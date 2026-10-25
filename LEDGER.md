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
- A3 Defenses: green-mana economy (kills + wave completions, hard cap); place anywhere,
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
| BUILD | W1 scaffold: spawning — waves run SEQUENTIAL (shared checkout), deps per c3 module breakdown |

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

## Open questions

- v1 mission count: one map polished first, 2–3 total? (design child decides shape)
