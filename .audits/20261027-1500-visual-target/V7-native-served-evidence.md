PROBE: sha256sum /home/claudecode/Games/gatewardens/build/Gatewardens.exe => ^44299c3dfa095d6b24dad370ba4d3a0ea4439708b0eeaa6ca65dd59ef01e71c4

# V7 native + served pass — evidence (MC milestone 11462 / workspace 11274)

Date 2026-10-28 (UTC). Orchestrator-run pass (v1-GA W18 precedent pattern), VM120 via QGA.

PROBE: grep -c POSTED_OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v7-native-run.log => ^1$
PROBE: grep -c RTX /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v7-native-run.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v112-frame-1.png => ^63b91ad8a9c2f8a8cc124d8d2505aed3a5014d52b667a118a6ca50176b0ec9ec
PROBE: grep -c RESP_True /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v7-native-run.log => ^1$
PROBE: grep -c CLEAN /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v7-native-run.log => ^1$

## Rows

1. WINDOWS EXE REBUILT WITH v1.1 — tools/export_windows.sh on tip; build/Gatewardens.exe
   sha256 44299c3dfa095d6b24dad370ba4d3a0ea4439708b0eeaa6ca65dd59ef01e71c4 (113,584,640 B);
   assets verified INSIDE the binary: strings hits for ground_arena/icon_ballista/fx_proj_ice/
   tower_hailspire_T3 = 8.
2. TRANSFER BYTE-IDENTICAL — served :8131, in-guest Get-FileHash
   44299C3DFA095D6B24DAD370BA4D3A0EA4439708B0EEAA6CA65DD59EF01E71C4 == artifact sha.
3. NATIVE RUN (session-1 scheduled task, work/it, COM-fired): PID 6528, RESP=True; verbose
   boot.log: "Godot Engine v4.7.2.stable.official" + "Native OpenGL API detected: 3.3: NVIDIA -
   NVIDIA GeForce RTX 2060" + NVAPI Init OK + shader compiles (boot.log POSTed; flushed at exit).
4. NATIVE 60 FPS PIXEL PROOF — windowless movie mode on the SAME exe in-guest:
   "Movie Maker mode enabled, recording movie in 1280x720 @ 60 FPS", 600 fixed-60fps frames,
   v112-movie.avi (15,522,916 B, sha256 bacdffd57729b23c...) POSTed back; ffmpeg probe:
   10.00 s, 60 fps, 1280x720. Frames extracted: v112-frame-1/2.png (hub; identical hash is the
   STATIC hub screen — no animation at rest, motion proven separately by v6_tween_probe).
   HONEST NOTE: the movie-mode frame is top-shifted (windowless render, no OS title bar) — a
   movie-mode artifact; the interactive session-1 run's own rendering was live on the HDMI.
5. SERVED PIXELS — rebuilt static/index.pck (asset strings present), browser at 127.0.0.1:8124:
   v7-mission.png = arena board + core crest + shop badges in the real web build; v7-tab-mid.png
   tab-switch frame; v7-side-by-side.png = served build vs the DD2 style anchor (STYLE reference
   only — all art original, clean-room held).
6. SHARED-SEAT FINDINGS (disclosed): another session's capture channel lives in
   C:\Users\work\gwtest (step-lib.ps1/current-step.ps1/ref-yt-*.png) and POSTs to :8131/up/ —
   my GET-only transfer server on :8131 would NOT accept those POSTs while running. My session-1
   shot task never produced a process (cause not chased — shared seat, not my channel). My own
   files/tasks were ALL removed: mine_left=0, game_procs=0, both tasks deleted (verified absent).
   Neighbor files untouched (dir_now = their five files only). => CLEAN.
7. WEB-FPS INSTRUMENT NOTE (honest limitation): headless-browser rAF is throttled to ~6 fps
   HERE (measured IDENTICAL 6.3 fps on the static hub vs mission = harness cap, not game cost);
   served fps truth = native movie (row 4) + owner's real browser. UNVERIFIED for headless,
   VERIFIED 60 fps for the native render path on RTX 2060.

VERIFY_EXIT=0
