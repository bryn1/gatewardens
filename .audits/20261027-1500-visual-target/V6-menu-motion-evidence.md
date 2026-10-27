# V6 menu-motion — build evidence (MC card 11530 / milestone 11462 / workspace 11274)

Date 2026-10-27 (UTC). Sole writer, shared checkout /home/claudecode/Games/gatewardens.
Binary: /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 (4.7.2).

## What shipped (the ONE shared mechanism)

- NEW godot/scripts/ui_tween.gd — the single tween helper. `enter(content, dir)`
  slides the newly-opened station's CONTENT box ~24px in from the navigation
  side + fades 0->1 over 0.15s (the brief's 0.12-0.18 band); `attach(button)`
  is the one-line hover/press scale 1.0->1.03->1.0 with a centred pivot.
  At rest every property it drives is IDENTITY (offset Vector2(0,0), modulate
  Color(1,1,1,1), scale Vector2(1,1)) and the tween ENDS on those values,
  with the finished callback re-pinning them — a settled panel is pixel-
  identical to a never-animated one.
- godot/scripts/hub.gd — `_open()` starts the enter tween on the opened
  panel's content box (each station's single child); direction follows the
  tab-bar order. One-line `UITWEEN.attach(b)` on the six tab-bar buttons.
  Same handlers, same signals, same synchronous visibility flip — zero
  logic change.
- godot/scripts/defense_panel.gd — one-line `UITWEEN.attach(b)` on the
  class buttons + the shared `_action()` builder (Upgrade/Repair/Sell/
  Assign/Unassign).
- godot/scripts/hud.gd NOT touched — declared reading: the HUD carries NO buttons
  by its own pinned read-only contract (hud.gd header, W17b: every Control
  under $Root is MOUSE_FILTER_IGNORE), so "shop/action buttons (hud)"
  resolves to the defense panel only; a hover on an IGNORE-mouse overlay
  can never fire.
- NEW godot/sim/v6_tween_probe.gd — headless proof (below).
- LEDGER row in the same commit.

## Replace-not-add statement

`grep create_tween|Tween over godot/**/*.gd` BEFORE the change: ZERO
animation sites (only the word "between" in three comments). No UI script
animated anything, so ui_tween.gd EXTENDS the empty slot — it is not a
second mechanism beside an old one; it is the one path every menu motion
now rides (bank_list.gd static-helper precedent, same call shape).

## Declared readings (surfaced, not silent)

1. BRIEF NAME vs ENGINE: Godot 4.7.2 Control has NO `position_offset`
   property (VERIFIED: tween_property rejects it; get_property_list shows
   the family). The engine's visual-only motion family is
   `offset_transform_enabled` / `offset_transform_position` /
   `offset_transform_visual_only` (+ `pivot_offset_ratio` for centred
   scale) — used instead, and with `visual_only = true` the engine keeps
   layout, input and EVERY get_global_rect() pinned THROUGH the animation
   (probe prints the same rect mid-tween and at rest) — strictly stronger
   than the brief's "at-rest pixel-identical".
2. `.from()` LAZINESS (VERIFIED by probe row V6-ATREST-START): the tween
   carries its start values and the engine applies them on the FIRST
   processed frame — the switch frame itself writes NOTHING, so an `-s`
   leg that never pumps frames still measures pixel-rest geometry (this
   is what keeps every existing -s probe/test byte-stable).
3. OUTGOING FADE HONEST CUT (the brief's fallback clause): the leaving
   panel keeps the shipped synchronous hide. godot/sim/hub_probe_stations.gd
   asserts the previous station's `visible == false` in the SAME
   synchronous call (:93), so deferring the flip into a leave-fade IS the
   logic change this card forbids, and a fade tween on a hidden root would
   render nothing — theater, not motion. Declared in ui_tween.gd +
   hub._open comments. Every panel still animates: the station you
   navigate TO slides + fades; no panel is completely static.
4. I2 governance: ui_tween.gd is a presentation helper carrying motion
   constants (24px/0.15s/1.03) — NOT added to GOVERNED_LITERALS (that set
   guards BALANCE numbers); hub.gd/defense_panel.gd edits introduce zero
   number literals (checked: hygiene 0).

## Probe — green run (after, this session, rc 0)

    V6-PROBE-BOOT panels=6 open=war
    V6-TWEEN-START running=1 visible war=0 black=1
    V6-ATREST-START off=0,0 mod=1,1,1,1
    V6-TWEEN-MID frames=22 min_alpha=0.04444444552064 max_offx=22.9333324432373
    V6-REST-RECT black=[P: (0.0, 89.0), S: (633.0, 159.0)] same_as_pre=true
    V6-REST roundtrip_rect=same visibility=1
    V6-HOVER in=(1.03, 1.03) out=(1.0, 1.0) moved=1 rect=[P: (140.0, 54.0), S: (94.0, 31.0)]
    V6-PRESS down=(1.03, 1.03) up=(1.0, 1.0) under=false rect=[P: (140.0, 54.0), S: (94.0, 31.0)]
    V6-OK

Rows prove, with concrete pinned values (never the tested mechanism as
oracle — asserts are property VALUES + per-frame OBSERVED motion
min/max; the tween's is_running() is only the required start flag and
the scan stop-condition): (a) a tab switch through the shipped
`handle_press` route STARTS a tween on the content node (running=1) and
the rest values are UNTOUCHED on the switch frame; (b) it SETTLES to
exact rest (offset (0,0), modulate (1,1,1,1)); (c) the at-rest layout is
UNCHANGED — the bar button rect is byte-identical across the switch
(same_as_pre=true) and the panel content box returns to the byte-same
rect after a switch-and-back round trip + reopen (visibility=1 leg).
The GEAR leg direction bug the probe caught (left-slides travel NEGATIVE
x; a plain max never saw it — first run went red "GEAR never moved"),
fixed with absf + a comment: the mid-scan guards are real.
ENGINE FACTS (4.7.2, this run): pivot_offset_ratio is a Vector2;
Node.is_tween_running and SceneTree.is_tween_valid DO NOT exist —
Tween.is_running() is the available flag.

## Probe — planted RED beside the green (rc 1)

One-line plant in ui_tween.gd `_at_rest` (rest re-pin to Vector2(7.0,0)):

    V6-PROBE-BOOT panels=6 open=war
    V6-TWEEN-START running=1 visible war=0 black=1
    V6-ATREST-START off=0,0 mod=1,1,1,1
    V6-TWEEN-MID frames=22 min_alpha=0.04444444552064 max_offx=22.9333324432373
    V6-FAIL MID did not settle to rest: off=(7.0, 0.0) mod=(1.0, 1.0, 1.0, 1.0)
    exit code 1

Plant reverted; green re-run above is post-revert.

## v11_sprite_probe before AND after (9 rows + SPRITEBANK-OK both)

BEFORE (detached temp worktree at HEAD 88bf834, /tmp/gw-v6-base, removed):
SPRITEBANK-TEX n=12 px=512 / HEROES n=3 / SWAP active=1 visible=deadeye /
TOWERS n=3 / TIER ballista=T2 hailspire=T3 / GATEART blockade=sprite
trap=sprite / ENEMIES n=6 boss_greybox=1 / FLIP right=flipped left=plain /
SPRITEBANK-OK (rc 0).
AFTER (shared checkout, this change): the same 9 rows (grep -c SPRITEBANK
= 9, rc 0).

## Gates

- Baseline BEFORE the change (clean, this session): 222 passed (162.63s);
  check_hygiene 0 hits; fixtures sha256 eafe3932f7d30898… / 5e37c4b089209e…
  (match the pinned eafe3932/5e37c4b0). One intermediate run showed
  1 failed/221 passed — cause: MY throwaway semantics-scratch script in
  godot/sim/ breaking the session's editor import cache mid-run; deleted,
  re-baselined clean at 222 (transient, not shipped, not a product defect).
- AFTER (with this change, this session): `python3 -m pytest -q` =
  **222 passed** in 159.14s; `python3 tools/check_hygiene.py` =
  **0 hit(s)**; fixtures sha256 UNCHANGED:
  eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912 /
  5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628.
  Commands (repo root):
      python3 -m pytest -q
      python3 tools/check_hygiene.py
      sha256sum tests/fixtures/mission_gatefall_{normal,hard}.jsonl
      godot --headless --path godot -s res://sim/v6_tween_probe.gd
      godot --headless --path godot -s res://sim/v11_sprite_probe.gd

VERIFY_EXIT=0

