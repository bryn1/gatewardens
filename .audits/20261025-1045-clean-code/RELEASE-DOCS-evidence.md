# RELEASE-DOCS evidence — MC 11409 (v1 release docs, workspace 11274) — tech-writer, 2026-10-27

PROBE: grep -c 'VERIFY_EXIT=0' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/RELEASE-DOCS-evidence.md => ^2$
PROBE: grep -c '222 passed' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/RELEASE-DOCS-evidence.md => ^4$
PROBE: grep -c 'check_hygiene: 0 hit' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/RELEASE-DOCS-evidence.md => ^2$
PROBE: grep -c 'v1 (GA)' /home/claudecode/Games/gatewardens/README.md => ^1$
PROBE: grep -c 'No shop. No loot boxes.' /home/claudecode/Games/gatewardens/README.md => ^1$
PROBE: grep -c '222' /home/claudecode/Games/gatewardens/README.md => ^1$
PROBE: grep -c 'Known limits' /home/claudecode/Games/gatewardens/RELEASE_NOTES.md => ^2$
PROBE: grep -c 'What shipped' /home/claudecode/Games/gatewardens/RELEASE_NOTES.md => ^1$
PROBE: grep -c 'How to build' /home/claudecode/Games/gatewardens/RELEASE_NOTES.md => ^1$
PROBE: grep -c 'gacha' /home/claudecode/Games/gatewardens/RELEASE_NOTES.md => ^0$
PROBE: grep -c 'gacha' /home/claudecode/Games/gatewardens/README.md => ^0$
PROBE: grep -c 'SUPERSEDED in part by W17g' /home/claudecode/Games/gatewardens/LEDGER.md => ^1$
PROBE: grep -c 'FIXED by W17g' /home/claudecode/Games/gatewardens/LEDGER.md => ^1$
PROBE: grep -c '11409 release docs' /home/claudecode/Games/gatewardens/LEDGER.md => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/RELEASE_NOTES.md => ^de8592a09cb5def87fbfda698518c0e5c92b5a2bf25dab747dc7ccb006bda518
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912

Repo /home/claudecode/Games/gatewardens, branch main, base HEAD cbfe6ff (chain
0afe00c → e839fa1 → 47287d3 → cbfe6ff VERIFIED via git log this session).
Release-docs commit: 00c5999 (author+committer tech-writer (11409)
<tech-writer@agent-town.local>; NOT pushed — `git branch -r --contains HEAD` = 0 branches).

## 1. The commit — git show --stat 00c5999 (exactly 3 files, no .audits)

```
 LEDGER.md        |   5 +--
 README.md        |   2 +-
 RELEASE_NOTES.md | 102 +++++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 106 insertions(+), 3 deletions(-)
```

## 2. Re-runs BY ME (tech-writer) on the final docs tree

`python3 -m pytest -q` (unpiped, genuine rc):
```
222 passed in 148.84s (0:02:28)
REAL_PYTEST_RC=0
```
`python3 tools/check_hygiene.py`:
```
check_hygiene: 0 hit(s)
HYGIENE_RC=0
```
(An earlier piped run printed the same `222 passed` tail + hygiene 0 hits; that
run's PYTEST_RC line measured the pipe's tail, so the suite was re-run with
rc captured directly. The brief's "currently 222" CONFIRMED.)

## 3. Doc-sync sweep (tracked .md: LEDGER.md README.md docs/ARCHITECTURE.md + the new RELEASE_NOTES.md)

PRE-EDIT hits (`grep -n <pat> <tracked .md files>`), each with disposition:

| pattern | hits | disposition |
|---|---|---|
| `Not yet GA` | README:9 | FIXED — status line replaced (this commit) |
| `817f8d2` (as "main @") | README:9 | FIXED — SHA ref dropped (self-staling); status now SHA-free + wave/count-current |
| `190 pytest` | README:9; LEDGER:62,64 | README:9 FIXED; LEDGER rows are HISTORY rows (W13/W14 build records, per the sweep rule history keeps its numbers) — KEPT |
| `pre-GA` | README:9; LEDGER:67 (FULL-journey row title), LEDGER:112 (`## Findings open (pre-GA)` heading) | README:9 FIXED; LEDGER hits are historical titles (row records the pre-GA journey; the findings section is CLOSED-in-place) — KEPT as history |
| `freemium` / `IAP` / `DLC` | 0 | nothing to do |
| `gacha` / `price` / `purchase` | docs/ARCHITECTURE.md:216 ONLY | hygiene-negation (the I1 tripwire token list documenting the BAN) — KEPT verbatim |
| `premium currency` / `battle pass` | LEDGER:4 ONLY | owner-ruling negation in the goal line — KEPT |
| `213 passed` / `217 passed` / `218 passed` | 0 in .md (they live in .audits logs = trail, not docs) | nothing to do |
| `222` live claims | README:9 + RELEASE_NOTES x3 | all live count claims read 222 = the measured value |

POST-EDIT: `Not yet GA`/`817f8d2`/`190 pytest`/`freemium`/`IAP`/`DLC` → 0 hits
across RELEASE_NOTES.md, README.md, LEDGER.md, docs/ARCHITECTURE.md
(swept RELEASE_NOTES.md explicitly by file too — it was untracked at the time
of the list-based sweep). VS bridge names (VS_STATE/__vsSnapshot/vsHost, the
only hygiene rule that reads README.md): 0 hits in all three docs — suite
re-run confirms the test_bridge_contract I8 leg stayed green after the edit.

## 4. LEDGER edits (replace-not-delete, verified by grep after the commit)

- `grep -c 'SUPERSEDED in part by W17g/cbfe6ff' LEDGER.md` = 1 (A9-journey row,
  clause appended at row end; the historical text incl. the "no relic drops"
  wording stands).
- `grep -c '[FIXED by W17g: see BUILD W17g row]' LEDGER.md` = 1 (FULL-journey
  row limitation (b), appended inside the clause).
- `grep -c '^| 11409 release docs' LEDGER.md` = 1 (new row after the
  `RELEASE DOCS + TAG … pending W17` row; the tag half stays pending —
  orchestrator, MC 11277).

## 5. Known-limits lines → backing evidence (VERIFIED by reading these files this session)

| limit (RELEASE_NOTES) | evidence |
|---|---|
| (a) no return-to-hub; save commits at _end_mission | A9-journey-final.md "Journey-surfaced limitations" #1 |
| (b) ~150-item bank (loot_events:148); scroll fixed+VERIFIED served; no bulk-sell | A9-journey-final.md #2 + POST-REPORT UPDATE; W17g-evidence.md rounds 1–4 + ORCHESTRATOR SERVED VERIFICATION |
| (c) reload-within-~1s race; patient reload persists | A9-journey-final.md #3 (j4 bank-0 vs j3 152) |
| (d) relics drop to bank; hero slots weapon/armor/ring only; mission-side assign NOT click-verified v1 | A9-journey-final.md #4 |
| (e) full-durability defense Sell refunds 0, BY DESIGN | A9-journey-final.md #5; defense_obj.gd:50 pinned R1 |
| (f) greybox cosmetics (label overlap, center label) | A9-journey-final.md #6 |
| (g) both-mouse-buttons+held-skill lever untaught | A9-journey-final.md run j3 (golden line-12 lever) + FULL-journey LEDGER row (c) |
| victory 11/11 + zero console errors + ascension persists | A9-journey-final.md runs j3/j4 + Hub legs |
| equip-by-click served (bank 151→150) + persist across reload | W17g-evidence.md ROUND-3 + ORCHESTRATOR SERVED VERIFICATION (round 4, pck 244584) |

## 6. Brief-vs-reality contradictions (reality won; honesty law)

1. Brief line 29: ".audits/ is gitignored" — CONTRADICTED: .gitignore lists
   only .tmp/.godot/__pycache__/static/*; one .audits file (W16-evidence.md) is
   already tracked. Intent honored anyway: the commit staged exactly the three
   allowed paths explicitly; zero .audits files in it (stat above).
2. Brief line 14: "(b) … (Blacksmith salvage exists…)" — CONTRADICTED by the
   artifacts: NO item-salvage service ships. godot/scripts/gear_panel_ui.gd
   header (verbatim): the sim's "unequip"/"salvage_yield" statics "neither
   exists in the shipped sim_inventory contract … the v1 return path IS
   equip's replace-to-bank"; blacksmith.json declares only
   upgrade/evolve/reroll/tinkering (no salvage value anywhere, I2).
   RELEASE_NOTES (b) therefore names what DOES exist (Blacksmith
   upgrade/evolve/reroll, mission defense Sell, equip replace-to-bank) and
   states the missing bulk-sell as the limit — never a fake salvage.
3. Historical-probe drift note: W17g-evidence.md PROBE `grep -c 'W17g'
   LEDGER.md => ^1$` measured at card 11408's close; the two brief-mandated
   bracketed clauses add "W17g" to two more rows (count now 3). That probe is
   a point-in-time close-verification marker on a closed card, not a live-state
   row — recorded here so a re-read never mistakes it for a breakage.
4. Everything else in the brief's ground-truth section checked out as stated:
   chain/HEAD (git log), 222 passed (own run), hygiene 0 hits (own run),
   rarity ladder Worn→Legendary (rarity.json), 3 heroes (heroes.json),
   Gatefall 11 waves both difficulties (waves_*.json), six stations
   (A9 Hub legs), served equip/persist/scroll (W17g evidence).

UNVERIFIED kept as such: HARD difficulty has NO browser-journey evidence (only
the byte-stable headless golden win fixture) — RELEASE_NOTES says exactly that;
relic mission-side assign path (never click-verified) — says "not fully verified".

VERIFY_EXIT=0
