PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/scripts/sprite_bank.gd => ^6fcfe37453785130370b29439bdf4ddce03275149dc43af7e9eb2965beca6ead
PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/V7-native-served-evidence.md => ^1$
PROBE: grep -c POSTED_OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v7-native-run.log => ^2$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_hard.jsonl => ^5e37c4b089209e64
PROBE: grep -c v1.1 /home/claudecode/Games/gatewardens/README.md => ^1$

# MILESTONE 11462 close — Gatewardens v1.1 (DD2-referenced visuals, 3090-authorized)

## DoD evidence table (VISUAL-TARGET.md rows -> status)

| Row | Shipped | Card | Proof |
|---|---|---|---|
| V1 stylized world + framing | arena board floor + core crest + camera nudge (+3.55%, frustum-gated, 33 pts >=60px pinned) | 11559 knut-VERIFIED | v1_world_probe 5 rows + v1world_shot.png |
| V2 chunky sprites | 3 heroes + 6 enemies + the BOSS (warden_breaker sheet, DA-fix commit) original sprites, ONE bank | 11466 knut-VERIFIED + DA-fix | v11_sprite_probe boss_sheet leg (path-pinned, planted-red) + pixel zoom_f480 |
| V3 whimsical T1-T3 towers | ballista/bombard/hailspire T2/T3 skins wired through shipped upgrade() | 11520 knut-VERIFIED | TIER row path-pinned + served runtime shots |
| V4 icon HUD | 8 badges on bank; 3 shop buttons pinned; green/wave/core emblems; labels byte-identical | 11549 knut-VERIFIED | v4_icon_probe 7 rows + v5fx_f180 visible |
| V5 combat FX | tracers/sparks/poofs via visual-only observer, sim diff ZERO files | 11552 knut-VERIFIED | v5_fx_probe 9 rows (848/318/5) + f270 zoom |
| V6 menu tweens | shared ui_tween helper, tab slide+fade, hover/press, at-rest stable | 11530 knut-VERIFIED | v6_tween_probe 9 rows + planted-red |
| V7 60fps served+exe | fresh exe on RTX 2060, movie 1280x720@60fps 10.00s + served pixels + side-by-side; DA-fix re-run: new exe (f114ca86) byte-identical on VM120 + movie POSTED_OK + boss billboard pixel-proven | this file (orchestrator pass) + DA-fix addendum in V7 file | V7-native-served-evidence.md, v112-boss-near.png |

Doctrine rows: art 3090-authorized, clean-room (style reference only; prompt record
gen/manifest-prompts.tsv — 24/36 assets with recovered prompts, the 12 batch-1 assets predate sidecar
recording and are recorded MISSING — honest gap; per-batch sha256 in manifest*.tsv); replace-not-add
(ONE sprite_bank, ONE ui_tween, visual-only fx observer; greybox FULLY exited at the DA-fix commit — the
warden_breaker boss sheet closed the last holdout); gates: 222 pytest + hygiene 0 + golden fixtures
byte-identical ON EVERY child close (orchestrator re-ran each); MC 11277 release rows met AT
the tag (notes artifact + README current + grep-to-zero sweep).

Ship artifacts: tag v1.1 -> fd5cd53 (MOVED from 1f85125 by the DA-fix loop; LEDGER row records the move), release
https://github.com/bryn1/gatewardens/releases/tag/v1.1 with Gatewardens.exe (sha256
f114ca86a9c04337d86f03c32f9cfdce2c63f85606a56fdf890981b7e158c106; pre-DA build 44299c3d… superseded at the tag move) — byte-identical transfer (both builds) +
live run + RESP=True + native 60fps movie VERIFIED on VM120 (re-run at the DA-fix tip, F114CA86 in-guest) +
BOSS-PIXELS painted in-game (v112-boss-near.png, kit-declared nudge) (seat restored CLEAN, shared-session
findings disclosed in V7 evidence). Honest limits shipped with the release (poof colour
separation, outgoing-tab hard cut, 3-button bar, zoom gate, headless-rAF instrument note) — see
RELEASE_NOTES v1.1 section.

VERIFY_EXIT=0
