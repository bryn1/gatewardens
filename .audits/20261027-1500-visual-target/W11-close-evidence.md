PROBE: grep -c 'SPRITEBANK-OK' /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-orchestrator.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/scripts/sprite_bank.gd => ^bde17b0ab03c085364b9c62173d527540de37d1fa850bf8442c3f23b191f8e1f
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/assets/v11/tower_ballista_T1.png => ^8626e5623df13030526765a78732bb314a4d931647381f9bd0647cf78d1d2eff
PROBE: grep -c 'res://assets/v11/hero_warden.png' /home/claudecode/Games/gatewardens/godot/scripts/sprite_bank.gd => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898

# W11-close (MC 11466) — orchestrator close evidence (V1.1-a sprite wiring)

Child commits (message-cleanup rewrite, trees identical): assets 15042b7, wiring d32c7d8 (pushed tip 3749a3b) (author "code (11466)"). Child pointer read;
everything below measured BY THE ORCHESTRATOR at the committed tree.

## 1. Mechanism (read, not summarized)
godot/scripts/sprite_bank.gd — 63 lines, ONE id->sheet preload map + make_sprite
factory; asked by exactly three draw sites (hero_pawn.gd:16, defense_obj.gd:67,
enemy_runner.gd:30 — grep-verified). Null answer keeps the greybox; the child's
_make_visual reads bank-first and RETURNS the sprite (no second render path):
defense_obj.gd:266-277 shows the replace-not-add shape verbatim.

## 2. Headless render proof — re-run BY ME this session
cmd: Godot_v4.7.2 --headless --path godot -s res://sim/v11_sprite_probe.gd
log: gen/probe-orchestrator.log — SPRITEBANK-TEX n=12 px=512, HEROES n=3,
SWAP active=1 visible=deadeye, TOWERS n=3, GREYBOX blockade=mesh trap=mesh,
ENEMIES n=6 boss_greybox=1, FLIP right=flipped left=plain, SPRITEBANK-OK rc 0.

## 3. Gates re-run BY ME at the committed tree
- python3 -m pytest -q -> 222 passed in 159.42s (pre-edit baseline 222).
- tools/check_hygiene.py -> 0 hit(s).
- fixture sha256: normal eafe3932f7d30898…, hard 5e37c4b089209e64… (byte-identical).

## 4. Runtime proof on the SERVED build (the product pixel check)
- tools/export_web.sh rebuilt at the tree; static/index.pck carries
  12/12 imported/<name>.png ctex entries (strings count, all names).
- Served at http://127.0.0.1:8124/static/index.html (localhost = Secure
  Context for the Godot web check; the 192.168.5.231 origin shows the
  documented Secure-Context error — pre-existing serving fact, not a
  regression; VM120 runs the native exe anyway).
- Driven via synthetic mouse events (browser_evaluate; page data never steered
  the session): hub -> War Table -> start gatefall normal -> build phase placed
  Ballista + Gate Blockade (HUD: "uid 1 tower T1 hp 200/200", "uid 2 blockade
  T1 hp 400/400"), wave 2/11 combat.
- gen/gw-v11-br-fight.png (sha 06d2da53…): the marching enemy column paints as
  TEXTURED SPRITES (orange/red skitterling flecks) — not the solid grey boxes
  of v1 screenshots; the gate_blockade keeps its box (correct: no sheet).
  gen/gw-v11-zoom.png = 2x crop of the same frame.

## 5. Honest limits (do not claim beyond these)
- Tower/hero SPRITE PIXELS were not readable on-screen at the game's fixed
  camera zoom in this pass — the towers I placed sat outside the framed area.
  Their SPRITE STATE is tree-VERIFIED (probe TOWERS n=3 + heroes + flip);
  their VISIBLE READABILITY at framing is a V1 (stylized world + camera
  framing) item — next batch, tracked in VISUAL-TARGET.md.
- xvfb software-GL pixel-capture attempt (gen/v11_shot.gd.abandoned) never
  produced frames in 10 min and was cancelled — NOT part of the proof; the
  browser run above is.
- F-1 (child finding, pre-existing, tests-side): conftest ensure_class_cache
  uses the no-op positional `--import <path>` form in 4.7.2; a fresh-cache
  copy is red at HEAD (10-11 failures, same class pre/post). Follow-up card
  filed separately (P2). Fleet gate here (imported shared checkout) is 222/222
  and exports are unaffected (pck carries the ctex; the served run above is
  the export, not a cached workspace).

## DoD rows (card 11466)
1. 12 sprites carry their sheet in the live draw path — probe n=12 + hero/tower/
   enemy legs; enemy sprites additionally seen painting on the served build. VERIFIED.
2. blockade/trap/boss keep greybox — probe GREYBOX + boss leg + served screenshot
   (blockade box beside sprite enemies). VERIFIED.
3. pytest 222 = baseline, hygiene 0, fixtures byte-identical — re-run by me. VERIFIED.
4. LEDGER V1.1-a row in the commit — in 4619bcb (git show). VERIFIED.
5. This file = orchestrator close evidence. DONE.

VERIFY_EXIT=0
