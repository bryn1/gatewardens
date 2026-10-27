# DA-verdict — pre-GA clean-code audit (MC 11274.1.23 / card 11339)

Full findings: REVIEW.md (this dir). Verdict basis:

- Four P1 findings are NOT refactor-reachable — they are missing/contradicted
  behavior, each pinned by contract or acceptance rows:
  defense placement unreachable in the served game (P1-1, while the A9 LEDGER
  journey row names "place/upgrade tower" and the served evidence ran a
  defense-less loss), relic equip absent despite R2 keeping it in v1 (P1-2),
  ascension points earnable but unspendable/unfelt (P1-3), Digit1..3 ability
  keys simultaneously hot-swap the hero (P1-4). Plus P2-10 (equip ok on an
  absent bank row) and P3-11 (uncapped dummy XP) need behavior decisions.
- The release-gate order (LEDGER §Release gate) puts the audit before the
  refactor run before GA; the refactor run is defined ZERO behavior change.
  A refactor-only pass + release docs therefore CANNOT close the P1 set —
  shipping the SHIP reading would GA a build whose named A9 acceptance legs
  (place/upgrade, and the F1 hot-swap mapping under the digit collision)
  were never exercised served.
- The mechanical/clean-code layer (ceilings-abuse exemption, phantom
  validate_probe chain, doc drift, I2 gate home, hard-mode golden, door/
  search/list duplication, vocabulary polish — REVIEW P2/P3/P4 refactor-safe
  set) is real but sequencable AFTER the P1 fix legs, in the refactor run.
- What holds and why this is not worse than FIX: suite mechanics are honest
  (planted-reds real, golden byte-stable with a mutation leg, probes E3-
  clean, C13 single write path verified, sim purity + monetization gates
  green, no autoloads, no retired-claim residue). The defects are coverage
  and wiring gaps at the served-product seam, not rot in the tested core.

# VERDICT: FIX
