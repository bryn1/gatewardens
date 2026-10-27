# W10 evidence — HUD + hero hot-swap UI (MC 11274.1.18 / card 11325)

## Commit
- `d9214a2208e40b4020ef82d3b4f1141fd6c04809` (author `frontend (11325)`), 6 files,
  733 insertions(+), ZERO deletions — `godot/scripts/hud.gd`(+`.uid`) `godot/scenes/hud.tscn`
  (new), `godot/sim/mission_smoke.gd` + `tests/test_hud.py` (extended/new), and
  `godot/scripts/mission.gd` (DECLARED hook lines only — R8). main.gd untouched (the
  router already routes mission.tscn; the mount rides the mission hook — DECLARED reading,
  the brief's "mission/main hooks" lists the allowed homes, not a demand for both).
  LEDGER.md untouched (parent integrates the row, W6–W9 idiom). .uid minted with the
  engine's own ResourceUID.create_id()/id_to_text() (temp `sim/_uidmint.gd` probe, run
  and removed pre-commit — the W8 idiom). File hashes: hud.gd 931b5de9… hud.tscn 7c920b84…
  smoke ec90e851… test 571624be…

## DoD — pytest tail + hygiene
```
$ python3 -m pytest tests/ -q            PYTEST_RC=0
........................................................................ [ 86%]
.......................                                                  [100%]
167 passed in 8.86s
$ python3 tools/check_hygiene.py         HYGIENE_RC=0
check_hygiene: 0 hit(s)
```
155 prior tests green unchanged + 12 new test_hud functions. Ceilings: hud.gd 242 (≤250
target, no header reason needed); test_hud.py 279 (≤600 test cap); mission_smoke.gd 614
and mission.gd 444 ride the gate's own first-line `# hygiene:` header rule (W7/W8
precedent — smoke kept whole as one test asset; mission hook lines only).

## HUD rows transcript (godot/sim/mission_smoke.gd, `-s`, XDG_DATA_HOME temp, seed 11274)
rc=0, stderr EMPTY (0 bytes both runs). Two independent runs byte-identical (cmp clean);
ALL prior W6–W9 legs byte-green in the same transcript (full order SEED→…→OK verified in
test_hud_engine_leg):
```
MISSION-SMOKE-HUD-BUILD wave=0 secs=25 text=Build: wave 1 in 25 s
MISSION-SMOKE-HUD-WAVE wave=0 text=Wave 1 / 11
MISSION-SMOKE-HUD-GREEN green=30 cap=10000 text=Green 30 / cap 10000
MISSION-SMOKE-HUD-BLUE active=warden blue=55.05 max=100.0 bar=55.05 ratio=0.5505
MISSION-SMOKE-HUD-HL slot=0 hero=warden
MISSION-SMOKE-HUD-HL slot=1 hero=deadeye
MISSION-SMOKE-HUD-HL slot=0 hero=warden
MISSION-SMOKE-HUD-BOSS visible=1 wave=10 hp=3500.0 max=3500.0 text=Warden Breaker 3500 / 3500
MISSION-SMOKE-HUD-BANNER outcome=lose text=DEFEAT
MISSION-SMOKE-OK
```
Every number re-derived by pytest from data: secs=ceil(waves[0].build_seconds)=25; "11"
=len(waves); green==the W8PANEL-ACT state green (chain-consistent); max==warden
heroes.json blue_max; boss hp==warden_breaker enemies.json hp[normal]=3500; banner maps
the shipped outcome field. The HL rows ARE the hot-swap proof: slot 0 (after the shipped
F2-10 auto down-swap) -> 1 (F2) -> 0 (F1), the highlight read BACK off the slot tint,
never recomputed.

## Planted reds (every gate proves it can fail)
- LIVE: one state write injected into hud.gd refresh (`m.blue = float(m.blue)`) →
  `FAILED tests/test_hud.py::test_hud_writes_no_state - AssertionError: hud.gd w...`
  (1 failed, 11 passed — the WRITE_RE source-truth leg) → line removed, 12 passed again.
- In-repo planted-reds (in-memory, no file touch): `state.add_hero_xp`+`place_defense`
  injection goes the mutator-family matcher RED; `m.blue = 0.0` goes the write matcher
  RED; `var _planted := 12` goes the I2 literal matcher RED ([12.0]).
- Live lesson shipped as code: the first scene draft parented HeroBar/BossBar/Banner to
  the CanvasLayer while the script read `Root/...` — the setup() $-lookups errored to
  stderr (gate: EMPTY stderr, W4 ruling) and the smoke hung with error spam, caught by
  the run, fixed (R9).

## R-list (readings; pinned table wins, MC 11274.1.9–.16 precedent)
- R1 Pinned Modules row (hud.gd: "HP/blue/green bar, wave/phase label, defense count,
  loot toast — renders injected state only, no logic") is the contract; the brief's
  hero-bar/boss/banner set rides the breakdown's "HUD + hot-swap deck UI" row (no
  separate file is pinned for it). Defense count ships. **Loot toast DECLARED OPEN**:
  it renders pickup EVENTS; scripts/loot_pickup.gd (W11) does not exist and inventing
  an event source beside the pinned C12 funnel = a second mechanism (W8 item_row
  precedent: declared, not faked).
- R2 HERO BAR = ONE SLOT PER DECK MEMBER (deck array order = shipped C4 swap order;
  the seeded deck is 3, A2 ships 3 heroes). F1–F3 hints sit on the first three slots —
  those are the shipped SWAP_KEYS; a 4th hint would invent an input code (task: none).
  The brief's "4-slot deck" is its paraphrase of the 4-hero deck; v1 ships 3.
- R3 Blue is ONE deck pool (C4): the bar renders on the ACTIVE slot with
  mission.blue_max — the shipped swap clamp becomes visible with zero math here.
- R4 Build countdown READS phase_controller.build_timer (the phase machine owns the one
  timer; the HUD never duplicates a countdown). PhaseController is a mission child, so
  the HUD reads it through the injected root — no new dependency edge.
- R5 Wave total via SimWave.total_waves(waves_file); display = shipped 0-based index +1.
  No "11" literal anywhere (I2 structural set only — pytest gates).
- R6 Boss bar visible exactly while C5 boss_hp != null (F13); name + max read the boss
  entity record (def.name, hp_max — the C2 data path). The smoke reaches the boss wave
  with the harness license (boot_probe drives-real-entry-points): writes the wave index
  + calls the real start_wave; the funnel fills m.boss/boss_hp through the shipped
  step-(4)/(5) paths untouched.
- R7 Cooldown pips render mission.hero_state.cooldowns as-is — frozen inactive arrays
  (F2-8) are visible, the HUD never ticks or clears them. ACTIVE/DOWN are slot tints;
  highlight_index() reads the tint back, so the HL rows prove the WIDGET moved, not a
  re-derived number. Banner copy: "win"->"VICTORY", "lose"->"DEFEAT", null->hidden —
  the outcome field has no other value; zero invented states.
- R8 mission.gd carries ONLY the declared hook: HUD_SCENE preload const + 6 hook lines
  at the tail of setup() (instantiate -> name "HUD" -> add_child -> setup(self));
  _process stays step(d) only (pinned funnel matcher untouched — asserted green).
  E5 order honored: the hook runs inside setup(), and hud._ready is the router-safe
  no-op (add_child fires _ready before setup injection — the mission precedent).
- R9 I4 enforcement: hud.gd makes ZERO shipped-mutator calls (add_/spend_/consume_/
  set_/equip/place_ families over comment/string-blanked code; add_child exempted as
  node plumbing — the same call the shipped hero rig and hook use), ZERO writes to
  m/mission/state, and no input consumer (F1–F3 stay the mission's step-(5) legs; the
  swap "reflects instantly" because _process refreshes off the SAME state the mission
  mutates — no new press consumer is invented, "no new input codes" honored).
- R10 Nothing else touched: game_state/bridge/sim statics/wave+hero data byte-identical;
  hub + station files untouched; .audits stays untracked (repo idiom).

VERIFY_EXIT=0
