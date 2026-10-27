# W9 evidence — hub in full (MC 11274.1.16 / card 11323)
Build = commit f2c4e79c21bc7459d53c4280d0b79ebc6a6b609e (author code (11323) <code@agent-town.local>), 18 files: hub.gd placeholder superseded; gear_panel_ui.gd + item_row.gd + scenes/item_row.tscn + war_table.gd + blacksmith_ui.gd + tinkerer_ui.gd + dummy_range.gd (pinned Module-table names); godot/sim/hub_probe.gd; tests/test_hub.py; the 7 .gd.uid (engine ResourceUID mint); game_state.gd next_uid extension (declared, R3). hub.tscn NOT touched: the shipped root+script already route to the new hub.gd (declared, R1).

## DoD gate — final run at this commit
```
$ python3 -m pytest tests/ -q
155 passed in 6.95s
$ python3 tools/check_hygiene.py
check_hygiene: 0 hit(s)
```
PYTEST_EXIT=0 (139 prior + 16 new = 155), hygiene exit 0.

## Probe transcript — green (headless -s, seed 11274, stderr EMPTY: 0 bytes)
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

HUB-PROBE-BOOT bank=2 gold=911 mats=torn_hide:3,iron_bar:3,ember_core:2,
HUB-PROBE-EQUIP bank_after_first=1 bank_after_swap=1 returned=1 equipped=twin_fang relic_refused=1 bank_after_relic=2
HUB-PROBE-UPGRADE cost=40 mats_dropped=torn_hide:2,iron_bar:1, upgraded=1 rarity=worn gold_left=871
HUB-PROBE-EVOLVE from=worn to=sturdy cost=600 refused=1 gold_left=271
HUB-PROBE-REROLL cost=120 stats_changed=1 mods_kept=1 rarity=powerful gold_left=151
HUB-PROBE-TINKERCAP refused=1 gold_unchanged=1 mods_unchanged=1
HUB-PROBE-TINKER moved=1 cost=150 mats_dropped=torn_hide:1,ember_core:1, source_mods=0 target_mods=1 gold_left=1
HUB-PROBE-DUMMY xp=6 level=1 absorbed=34.00 dps=34.00 invulnerable=1
HUB-PROBE-WAR maps=gatefall:[normal,hard,] start=gatefall difficulty=hard
HUB-PROBE-PANELS open=blacksmith
HUB-PROBE-CHEST bank_before=4 bank_after=5 gold_untouched=1 rarity=powerful shown=5
HUB-PROBE-OK
```
Determinism: two runs under different XDG_DATA_HOME user dirs -> byte-identical stdout (tests/test_hub.py::test_hub_probe_is_deterministic ships the same gate).

## Live planted-red — tinkerer mod_slots cap bypass (sim_inventory.gd line 118, `free <= 0 or` removed)
```
$ sed -i 's/if free <= 0 or not _can_pay(cost, mats):/if not _can_pay(cost, mats):/' godot/sim/sim_inventory.gd
$ godot --headless --path godot/ -s res://sim/hub_probe.gd   # RC=1, stderr empty (0 bytes)
HUB-PROBE-REROLL cost=120 stats_changed=1 mods_kept=1 rarity=powerful gold_left=151
HUB-PROBE FAIL tinkercap passed (cap bypassed): { "ok": true, "cost": { "gold": 150, "materials": { "torn_hide": 1.0, "ember_core": 1.0 } } } gold=1
$ git checkout -- godot/sim/sim_inventory.gd   # cap restored (line 118 verified)
$ godot --headless --path godot/ -s res://sim/hub_probe.gd   # RC=0
HUB-PROBE-OK
```
The TINKERCAP leg goes RED exactly on the bypass and green again on restore — the cap gate is proven, not decorative. (Source-tier planted reds — cost literal 600, duplicate show_item — ship inside tests/test_hub.py.)

## R-list (declared readings; the pinned table wins over brief paraphrases)
- R1 hub.tscn untouched: root already extends Control + binds hub.gd; panels are code-built in setup (W8 greybox idiom; E5: _ready is a no-op under -s, hub.setup driven by main).
- R2 Brief paraphrases NOT implemented (they don't exist in the shipped contract): rarity.json `colors` key (absent — item_row shows the rarity NAME and tints from an optional data-side map if one ever lands); SimInventory salvage_yield / unequip (absent — no second write mechanism beside the shipped C13 mutators; relic rows list and the shipped slot-mismatch equip refusal is the behavior, probe-asserted).
- R3 game_state.next_uid() extended (never rewritten): uid stamp now maxes over bank AND worn rows — a bank-only max re-stamps a uid a worn row still carries, and the pinned picked(uid) keys (item_row signal) would then hit the wrong row exactly when the mission-end chest bank_adds while gear is equipped. Save schema untouched (C6 carries no equipped key; fresh-boot bank-only sequences stamp identically — 139 prior tests unchanged).
- R4 Chest leg rides the SAME C13 mission-end commit (mission step (6) + _end_mission already wired by W6/W7): no new write mechanism, no mission.gd change; probe proves bank+1, gold untouched, tier = chest_tiers[0] (BN3), gear panel shows the grown bank after the return.
- R5 XP sink per pinned row: dummy carries absorbed/elapsed and NO hp key (unkillable by shape, declared); XP = xp.json enemy_xp_base.normal through the ONE add_hero_xp site; dps = absorbed/elapsed on the live tick clock. rng params on smith/tinkerer setups held per the pinned setup(...) injection shapes; tinkerer rng unused by the shipped static (declared).
- R6 hub_probe.gd carries `# hygiene:` (machine-row header text holds digits; mission_smoke idiom) and is outside the cost-literal gate's scope (test asset); the gate scopes the shipped hub layer (hub + 6 station scripts) — I2/I4 literals: 0 violations.
- R7 No new bridge codes (station map uses shipped Digit1-4/KeyE/Escape); no monetization vocabulary (I1 — gate shipped in test_hub.py, and a comment-word 'priced' was caught by it and reworded); cost math never in UI (I4: panels read costs from blacksmith.json and pay through the named mutators only).

## Probe rows reference (re-derived in test_hub.py from blacksmith/rarity/xp/items JSON, no test-side cost copies)
BOOT gold = upgrade.worn+evolve+reroll+tinkering + 1 = 911; UPGRADE 40 + torn_hide:2,iron_bar:1; EVOLVE 600, worn->sturdy, top-rung refused; REROLL 120 gold-only, mods kept; TINKERCAP refused (worn=0 slots); TINKER 150 + torn_hide:1,ember_core:1, final gold_left=1 (whole-chain exactness); DUMMY xp=6 level=1 dps==absorbed; WAR gatefall:[normal,hard] start_mission("gatefall","hard"); PANELS Digit3->blacksmith; CHEST bank 4->5 rarity=powerful.

VERIFY_EXIT=0
