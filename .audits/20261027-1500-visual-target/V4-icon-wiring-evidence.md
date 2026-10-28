# V4 icon wiring — build evidence (MC card 11549 / milestone 11462 / workspace 11274)

Date 2026-10-28 (UTC). Sole writer, shared checkout /home/claudecode/Games/gatewardens.
Binary: /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 (4.7.2).
Knut route = the PROBE read-backs below (repo not projects.yaml-bound; same route as cards
11466/11520/11517/11530). The grepped logs are COMMITTED under gen/ in this same commit.

PROBE: grep -c V4-ICONS-OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v4-icon-green.log => ^1$
PROBE: grep -c V4-ICONS-HUD /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v4-icon-green.log => ^1$
PROBE: grep -c V4-ICONS-COEXIST /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v4-icon-green.log => ^1$
PROBE: grep -c V4-ICON-FAIL /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v4-icon-red.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/sim/v4_icon_probe.gd => ^c98f8c2da5b532cf487cbbf913d1899247dbfc6c89b520e73d8c4ee079cc2ce6
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/scripts/sprite_bank.gd => ^70e83f82d818b5dfd801fea1a8218a67755b7f0228ffdf9c57088cd742c7b71a
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_hard.jsonl => ^5e37c4b089209e64

## What shipped (ONE commit, decoration over the existing mechanism)

- godot/scripts/sprite_bank.gd — the 8 icon ids (icon_ballista, icon_bombard, icon_hailspire,
  icon_blockade, icon_snare, icon_green, icon_wave, icon_core) joined THE ONE id->file TEXTURES
  map: texture_for(id) resolves them like any unit id (no second preload system; existing
  ids/tiers untouched). Presentation sizes ICON_PX=28 / ICON_GAP=6 live HERE (ui_tween.gd
  precedent): hud.gd and defense_panel.gd are I2-governed and carry ZERO new number literals.
- godot/scripts/defense_panel.gd — each class Button gets Button.icon from
  sprite_bank.texture_for(the icon id), icon_alignment LEFT, theme override
  icon_max_width=28 (the brief's ~28px). Explicit ICON_FOR map (the bank's sheet-map idiom,
  never a stem rule) covers ALL FIVE tower ids, so the declared family picker rides rows that
  already resolve. sync()/refresh() never touch icons; green-cost texts byte-identical (probe row).
- godot/scripts/defense_placer.gd — classes() rows now carry the winning row's data "id"
  (one line): the panel maps the icon from it, so "first row of class wins" keeps its single
  home in the placer instead of a second dedupe in the UI. Zero behavior change: every
  existing reader uses "class"/"name"/"cost" only.
- godot/scripts/hud.gd — icon_green beside the green count, icon_wave beside the wave
  counter, icon_core beside core HP: TextureRect CHILDREN of the three Labels (a Label is not
  a Container, so they never join the VBox layout — the pinned Label rects are untouched and
  their texts are NEVER edited), re-placed beside the laid-out text in the shipped refresh().
  Built before the shipped _ignore_mouse pass, so they take MOUSE_FILTER_IGNORE like every
  HUD control (test_mission_clicks GWMICE-FILTER leg re-run green in the 222).
- godot/sim/v4_icon_probe.gd (NEW) + gen/ logs (green + planted red); LEDGER row in this commit.
- The 8 icon PNG .import sidecars + the probe .gd.uid committed (clean-checkout determinism,
  the V1.1-a/.b sidecar precedent — these PNGs had NO code loader before this card).

## Honest-cut row (surfaced, not silent)

The brief row 2 says "each of the five tower Buttons". The SHIPPED build bar has THREE class
Buttons, not five: defense_placer.classes() lists one entry per distinct towers.json class
("tower", "blockade", "trap"), first row wins — the family picker is the placer header's own
DECLARED later frontend row. Wiring icons means: all three shipped buttons carry their icon
(Ballista->icon_ballista, Gate Blockade->icon_blockade, Barbed Snare->icon_snare, probe-proven
by pinned resource path); icon_bombard and icon_hailspire are registered on the bank and
probe-pinned at the TEX row, and the defense_panel ICON_FOR map already resolves them, so
bombard/hailspire buttons ride rows the moment the family picker adds them. Making five buttons
now would be the logic change this card forbids.

## Declared readings

1. ENGINE FACT (4.7.2, VERIFIED by a red run this card): Button has NO add_theme_constant;
   the 4.x API is add_theme_constant_override. The probe's SHOP row reads the effective
   get_theme_constant("icon_max_width")==28 back as a pinned value.
2. HUD beside = RIGHT of the label text: $Root/TopLeft starts at x=16, so a left placement
   would clip off-canvas. The probe asserts icon.position.x == laid-out label width + 6.0 and
   label.size.x > 0 (layout ran on the served-canvas mirror) and icon.size == Vector2(28,28).
3. ui_tween COEXISTENCE (brief row: state it): Button.icon is drawn inside the button's own
   canvas item, so the V6 hover scale 1.0->1.03->1.0 scales the icon WITH the button — nothing
   to coexist around. PROOF row V4-ICONS-COEXIST: full hover-in + hover-out cycle driven by
   the Button's own mouse signals on a class button, observed max scale > 1 (moved=1), settles
   at scale (1,1) with the icon's pinned resource path intact (icon=ok).
4. Probe boot idiom: mission_clicks.gd, not v6's router boot — E5: the router-added mission
   never dispatches _ready under -s (the first probe run went RED on exactly this: no class
   buttons). mission.tscn instantiated, m._ready() + m.setup(...) driven directly (pinned seed
   11274), served canvas root.size=1280x720, frame pump = scripted MainLoop._process.
5. Pins are concrete committed RESOURCE PATHS + byte-exact texts declared in the probe — never
   sprite_bank/sync as oracle (fleet lesson, v11 TIER leg).

## Probe — green run (rc 0), gen/probe-v4-icon-green.log

    V4-ICONS-BOOT buttons=3 phase=build
    V4-ICONS-TEX n=8 px=512
    V4-ICONS-SHOP n=3 paths=left=28
    V4-ICONS-TEXT n=3 byte-exact
    V4-ICONS-HUD n=3 beside=1
    V4-ICONS-COEXIST moved=1 rest=1 icon=ok scale=(1.0, 1.0)
    V4-ICONS-OK

## Probe — planted RED beside the green (rc 1), gen/probe-v4-icon-red.log

One-line plant: the trap button's PINNED expected icon path set to icon_blockade.png (wrong
id pinned — the brief's plant shape). The pinned-path assert reads the real button icon, so:

    V4-ICONS-BOOT buttons=3 phase=build
    V4-ICONS-TEX n=8 px=512
    V4-ICON-FAIL class button icon drift: trap

Plant reverted (probe sha256 re-verified c98f8c2d… identical to the green run), green re-run
above is post-revert.

## Gates

- Baseline BEFORE the change (clean, this session): python3 -m pytest -q = 222 passed
  (162.78s); check_hygiene.py = 0 hits; fixtures sha eafe3932f7d30898… / 5e37c4b089209e…;
  v11_sprite_probe 9 rows + SPRITEBANK-OK rc 0; v6_tween_probe 9 rows + V6-OK rc 0.
- AFTER (with this change, this session): python3 -m pytest -q = **222 passed** (160.70s);
  check_hygiene.py = **0 hit(s)**; golden fixtures BYTE-IDENTICAL:
  sha256sum tests/fixtures/mission_gatefall_normal.jsonl =
  eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912;
  sha256sum tests/fixtures/mission_gatefall_hard.jsonl =
  5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628;
  v11_sprite_probe re-run: 9 rows + SPRITEBANK-OK rc 0
  (gen/v11-sprite-probe-after-11549.log); v6_tween_probe re-run: 9 rows + V6-OK rc 0
  (gen/v6-tween-probe-after-11549.log); v4_icon_probe green + planted-red above.
- File hygiene: hud.gd 327 / defense_panel.gd 372 / sprite_bank.gd 111 / defense_placer.gd
  201 / v4_icon_probe.gd 210 lines — all under the 400 hard ceiling.
- Zero logic change: same handlers, same texts (probe byte-exact row), same signals; the
  classes() "id" key is unread by every existing site.

VERIFY_EXIT=0
