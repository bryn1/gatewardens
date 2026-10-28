PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261028-1500-v12-plan/F4-wave.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/.audits/20261028-1500-v12-plan/gen/f4-bombard-placed.png => ^4cfa46a98a5ae392a9ee5fe39986d3fe2272a8262c066bca47de2b77a3fbd7cd
PROBE: grep -c place_id /home/claudecode/Games/gatewardens/godot/scripts/defense_placer.gd => ^4$

# 11616 close — F4 shop family picker (v1.2 W3)

Commit cf56d55 (author coder (11616), pathspec-only 5 files): place_id/row_for_id resolve towers.json data ids and
end at THE one mission.place_defense application site (place(class) delegates; ONE call site, source-truth-pinned);
panel picker buttons ride the existing row loop + icons (sprite_bank.gd:47-48) + W17e sync; ZERO new literals.
LOC watch held: defense_panel.gd 373->399/400 (split fallback NOT triggered -> pin-#10 evaluated-not-fired, cited);
placer 228/400. Contract legs + planted-red (swap family mapping -> RED, revert green) in F4-wave.log.
ORCHESTRATOR re-measured at committed tree: pytest 231 passed 165.95s (own run), hygiene 0 hits, fixtures diff EMPTY.
SERVED-BROWSER LEG (MC 11509 D3): FRESH web export at cf56d55 served on 127.0.0.1:8124; mission live; panel shows
"Bombard (160)" + "Hailspire (140)" rows with committed icons (f4-panel.png); row-click + tile-click flow (pointer-event
sequence, hub-start idiom) -> green 300->140 EXACTLY -160, "Defenses 1 / cap 60", DEFENSES row "uid 1 tower T1 hp
260/260", Bombard row DIMS (unaffordable) while Hailspire stays selectable (f4-bombard-placed.png). Honest intermediate:
first attempt DEFEATED (idle between tool calls let waves through undefended — shipped loss logic working, frame kept).
0 console errors throughout.

VERIFY_EXIT=0
