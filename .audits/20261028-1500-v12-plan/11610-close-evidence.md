PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261028-1500-v12-plan/F5-wave.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/.audits/20261028-1500-v12-plan/gen/f5-frame-a.png => ^5898a3f6b9300c742e8809a4f522752d02ab20b0659293218be154b78bb0f8e3
PROBE: sha256sum /home/claudecode/Games/gatewardens/.audits/20261028-1500-v12-plan/gen/f5-frame-b.png => ^06ffabeca94c135149450992a7326a31847ddb1e895b98a6b6f0f5e11d703c0e
PROBE: grep -c BOB_AMP /home/claudecode/Games/gatewardens/godot/scripts/enemy_anim.gd => ^2$

# 11610 close — F5 procedural enemy walk (v1.2 W1)

Commit 9eb5184 (author coder (11610)): NEW godot/scripts/enemy_anim.gd (82 L pure phase/bob/sway, constants
declared w/ rationale, ONE mechanism — reuse-check greps fx_director+ui_tween logged) + enemy_runner.gd mount
+11/-1 LOC 152->162 + tests/test_enemy_walk.py 6 legs. Engine proof (throwaway /tmp probe, NOT shipped kit):
5.0 vs 2.2 u/s -> DIFFERENT poses (0.172727 vs 0.229499), bobs oscillate spread ~0.22 <= BOB_AMP, sim rows
byte-equal no-anim walk, rc=0 stderr empty. v1_world_probe unchanged V1W-OK. Planted-red BOB_AMP->0: 2 legs
RED, reverted green. ZERO godot/sim/ or data/ in commit (git show --name-only). enemy_skitterling_run.png
finding row logged P4 (stays declared-unwired per plan decision (i)).
SERVED-BROWSER LEG (orchestrator, MC 11509 D3): FRESH web export at the W1 tip (NOT stale static/) served on
127.0.0.1:8124; mission started via full pointer-event sequence (hub click f5-hub.png -> live mission);
animated frame pair f5-frame-a/b.png sha256 DISTINCT from each other AND from hub; PIL diff bbox
(16,17)-(615,422) 1059 non-zero px = painting moves between frames; describe-image (qwen3.8-flash-next,
prompt_tokens=1035, 20.7s) literal read: DEFENSES/RELICS panel, Wave 1/11 + gold/cap HUD + hero bar [F1-F3]
rendered, 3D grid + spawner markers intact, no blank/garbled/overlap. 0 console errors whole session.
ORCHESTRATOR gates at combined tree: pytest 229 passed 165.69s (my own run), hygiene 0, fixtures diff EMPTY.

VERIFY_EXIT=0
