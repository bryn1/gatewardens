# Gatewardens v1.1 — VISUAL TARGET (owner ruling 2026-10-27)
Owner order (verbatim): "Find dungen defenders youtube clip and set that as a Goal in visuals.
Gpu 3090 free use to achieve it"
Reference clip: "Dungeon Defenders 2 - Gameplay (PC/UHD)" — https://www.youtube.com/watch?v=o03yurQghcQ
Anchor frame (saved, sha256 bfcda8c9): frames/maxresdefault.jpg (1280x720, Trendy Entertainment art —
STYLE REFERENCE ONLY; clean-room wall stands: we generate our OWN art with the 3090, no ripped assets).

## The bar, read from the anchor frame (measurable rows)
V1 WORLD: warm stylized terrain — tan stone-plaza ground with painted path, lush grass tufts,
    rounded toy-village buildings along the map edge; NOT a flat grey trapezoid.
V2 UNITS: chunky cartoon characters with big readable silhouettes + outlines: 3 distinct hero
    sprites (archer/warden/mage vibe), grunt + boss enemy sprites, all visible as characters
    (NOT colored squares/dots).
V3 TOWERS: whimsical "machine" towers with personality and visible tier growth T1->T3
    (ballista/cannon/ice vibe), NOT 8px green ticks.
V4 HUD: DD2-style layout — top-left hero portrait + chunky HP bar; wave/boss bar top-center;
    right-side wave counter + core-HP; BOTTOM ability/tower bar: numbered slots with icon art,
    green-cost badges, cooldown sweeps. (We already show the DATA — this row is about the
    framed, icon-bearing presentation.)
V5 FX: visible attack projectiles (arrow/bolt/crystal), hit spark, death poof, tower
    glow when firing; ability flashes.
V6 MENUS: DD2 cartoon-panel styling (warm wood/stone frame, chunky buttons) + tweens —
    panels slide/fade on tab switch (today: static, pixel-proved 19px change), button
    hover/press scale.
V7 FIDELITY: 60fps served (web) AND native Windows exe, screenshots side-by-side vs anchor.

## Means (owner-authorized GPU)
All art GENERATED on the fleet 3090 via imagegen (Qwen-Image t2i/edit, transparent cutouts for
sprites/icons), palette-anchored from the anchor frame; wired into the EXISTING Godot scenes
(replace greybox meshes with textured quads/sprites where possible, one mechanism per concern,
no new render path). Suite (222) + hygiene stay green; golden fixtures untouched (sim never
visuals-side).

## Delivery
v1.1: sprite pass -> terrain/HUD pass -> FX/tween pass; each pass screenshot-VERIFIED served +
on VM120; release docs per MC 11277; tag v1.1.

DoD: rows V1-V7 are TRUE in the shipped build, each with a served-browser screenshot AND a
VM120 native-exe screenshot attached to the card trail, AND `python3 -m pytest -q` prints
222 passed (or the agreed updated count) AND check_hygiene 0 hits AND golden fixtures' sha256
unchanged (eafe3932/5e37c4b0) AND git tag v1.1 exists on a commit whose README + RELEASE_NOTES
match reality (MC 11277) AND all art files under godot/assets/ trace to an imagegen 3090 run
(evidence lists prompt + sha per asset).
