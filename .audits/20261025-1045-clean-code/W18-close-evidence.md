# W18 close evidence — Windows desktop export shipped on the v1 release (MC card 11437 / workspace 11274)

PROBE: sha256sum /home/claudecode/Games/gatewardens/build/Gatewardens.exe => ^a979c386a4b29b7df79eedb33dccbe82dd2dd68268e842fd0a290b8ff1ef37a3
PROBE: grep -c 'embed_pck=true' /home/claudecode/Games/gatewardens/godot/export_presets.cfg => ^1$
PROBE: grep -c 'Windows Desktop' /home/claudecode/Games/gatewardens/godot/export_presets.cfg => ^2$
PROBE: grep -c 'export-release "Windows Desktop"' /home/claudecode/Games/gatewardens/tools/export_windows.sh => ^1$
PROBE: grep -c 'W18' /home/claudecode/Games/gatewardens/LEDGER.md => ^1$
PROBE: grep -c 'No monetization, ever' /home/claudecode/Games/gatewardens/README.md => ^1$
PROBE: grep -c '222 passed' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W18-suite-final.log => ^1$
PROBE: grep -c 'check_hygiene: 0 hit' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W18-hygiene-final.log => ^1$
PROBE: grep -c 'RTX 2060' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W18-vm120-run.log => ^2$
PROBE: grep -c 'PID=12272' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W18-vm120-run.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gw120-native.png => ^259d5fbaf472db683170d3a8d06ec287c87012a33a12b202b51c37b3f82e840e
PROBE: grep -c 'VERIFY_EXIT=0' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W18-close-evidence.md => ^2$

DOCS: LEDGER W18 row in commit eeec3152; RELEASE_NOTES "Windows download" + README Windows line
in the SAME commit, moved to the v1 tag; GitHub release v1 body re-rendered from that RELEASE_NOTES
(gh release edit --notes-file) and carries asset gatewardens-v1-windows.zip (38,197,534 B,
state=uploaded, size VERIFIED via gh api).

## What shipped (orchestrator re-verified THIS session, not the child's word)
- Commit eeec3152ce06b21b87933a9b5e09933bad0845ae (author "code (11437)"), exactly 6 files
  (export_presets.cfg, tools/export_windows.sh, .gitignore, RELEASE_NOTES.md, README.md, LEDGER.md),
  74 insertions; git show --stat re-run; pushed origin/main THROUGH the fleet pre-push secret scanner.
- build/Gatewardens.exe: 109,372,280 B, MZ header (od), PE machine 0x8664 AMD64, single
  self-contained file (embed_pck=true, no sidecar .pck); build/ gitignored, status clean after export.
- Orchestrator re-ran the FULL gate at the committed tree: 222 passed (152.46s), hygiene 0 hits.

## REAL-WINDOWS RUNTIME (the DoD row no Linux check can reach) — VERIFIED on VM120 (Win11 26300)
Single-file exe downloaded over private LAN (in-guest hash byte-identical to artifact), run on the
interactive session via scheduled task: verbose boot = Godot 4.7.2 + OpenGL 3.3 on NVIDIA RTX 2060,
Main/hub scenes load, --quit-after 600 exits clean; persistent run PID=12272 RESP=True; session-1
screenshot shows the live window "GATEWARDENS — HUB | gold 100 | bank 0 | deck 3" (fresh %APPDATA%
save). Full transcript: W18-vm120-run.log; screenshot: /home/claudecode/Games/gw120-native.png.
Test machine restored CLEAN (process, files, both scheduled tasks removed; re-tested absent).

## Known limits (stated honestly)
- Build is UNSIGNED: first run may raise SmartScreen (documented in RELEASE_NOTES: More info > Run anyway).
- Repo is PRIVATE: asset download needs a bryn1 GitHub login (unauthenticated curl 404 is expected, checked).
- Screenshot taken on the 1024x768 Basic-driver head; the game window rendered correctly there.

VERIFY_EXIT=0
