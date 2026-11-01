"""v1.5 W-R v5_fx_probe baseline pin (MC 11897 / V15-PLAN-c2 §3 W-R —
the declared-not-run debt paid AT the v1.5 W1-final tree 0d3c506).

MEASURED TRUTH at the final tree (three byte-identical processes — the
documented-command kit run TWICE + an independent replicated-census
diagnostic, .audits/20261101-0843-v15-plan/gen/): the kit is RED. The
ART leg never completes — fx_proj_ice NEVER goes live in the full
40,000-frame walk — so CAP/SETTLE/TEARDOWN/OK never print and rc=1.
The re-declared baseline is therefore the measured RED transcript
(gen/probe-v5-fx-v15-red.log), never a fabricated green; the 2026-10-27
green baseline file stays untouched beside it (DOC-TAIL rule — this
file gives it teeth: leg 3 pins its sha256, a quiet overwrite goes RED).

CAUSE, attributed by counter-runs (WR-wave.log): the break landed with
G6 (3fe513a, 2026-10-29 — two days AFTER the baseline's last green run
at the 2026-10-28 tip, byte-reproduced here). G6's damage numbers ride
the same MAX_FX=64 cap ("numbers COUNT toward the same cap") — every
hp drop now costs TWO fx nodes (spark + number) in _observe_enemies,
which runs BEFORE _observe_fires inside one fx_step; the fires pass
then walks defense_list in placement order and the cap is spent, so
tracers starve (n=848-by-frame-270 baseline era -> 362 in 40,000 frames
now) and the hailspires (placed last) spawn ice ZERO times. The shipped
known-limit wording declares the starvation direction BACKWARDS
("numbers can be starved by tracers/sparks"; measured: numbers+sparks
starve the tracers) — FINDING 11897-F1/F2 routed via WR-wave.log; the
fix (kit license shape vs cap priority — cap priority is a PINNED cost
rule per V15-PLAN §2 row 8d) is NOT this test card's to make.

W-K NEUTRALITY (the plan's "expected zero at rest — declared, then
MEASURED"): the kit probe crosses no kit-assign (grep: zero
assign_relic calls, pinned by leg 4), and the byte-identical machine
rows at the G6 tip (no kit pass exists there) vs 0d3c506 ARE the
measurement — _observe_kits contributes ZERO to every counter.

P7 precedent honored (test_kit_fx.py): this file pins a FINDING as the
measured shipped shape with a RE-PIN CLAUSE — when 11897-F1 is fixed,
the kit goes GREEN and the OLD rows here MUST REDDEN FIRST (red
transcript archived BEFORE re-pinning; fleet law). DECLARED reading of
the brief's "runs the kit via the documented command" row: the kit
itself stays OUT of the pytest tier by standing ruling MC 11575 W3
DC-1 (manual kits + the hand-driven E5 pump; the red walk is also a
40k-frame multi-minute engine loop); the live kit runs are THIS card's
hand legs — archived byte-for-byte (run1/run2 + attribution) — and
this wrapper pins their re-declared transcript. Doctored-COPY
planted-reds run the legs against tmp copies (GW_V5FX_BASELINE, the
GW_GODOT env-override precedent): transcripts in WR-wave.log.

Legs: 1 machine-row pins vs the re-declared file (markers, FAIL row,
NO V5FX-OK, row order, the CAP/SETTLE/TEARDOWN rows absent-at-RED);
2 counter pins (the DoD's "counters" clause — shifts need a re-run +
re-pin, never a silent edit); 3 old-baseline integrity (sha256 + its
green rows intact — the never-quietly-overwrite rule made mechanical);
4 written-cause source truth (fx_step order, numbers-count-to-cap,
PROJ_FOR ice pin, ART sheet files exist, kit probe zero-at-rest,
MAX_FX probe==director 64).
"""

import hashlib
import os
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for greps)

GEN = Path(conftest.repo_path(".audits", "20261101-0843-v15-plan", "gen"))
BASELINE = Path(os.environ.get("GW_V5FX_BASELINE",
                               GEN / "probe-v5-fx-v15-red.log"))
OLD_BASELINE = Path(conftest.repo_path(
    ".audits", "20261027-1500-visual-target", "gen",
    "probe-v5-fx-green.log"))
# The 2026-10-27 green baseline must stay byte-untouched (versioned-
# truth + DOC-TAIL rule): pin its sha256, a quiet overwrite goes RED.
OLD_SHA256 = "d65d6b598a3424a83abb48576e1a1378b3f6a4be24ff6672bf7215cd9cf135fa"

GODOT = Path(conftest.repo_path("godot"))

# The re-declared machine rows (2026-11-01 at 0d3c506, deterministic:
# three independent byte-identical processes — see WR-wave.log §2).
V15_ROWS = [
    "V5FX-MOUNT child=1 after_runner=1",
    "V5FX-TRACER n=362 frames=40000",
    "V5FX-SPARK n=79725",
    "V5FX-POOF n=7",
    "V5FX-FAIL fx sheet never seen on a live node (id=fx_proj_ice "
    "path=res://assets/v11/fx_proj_ice.png)",
]


def _machine_rows(text):
    return [ln for ln in text.splitlines() if ln.startswith("V5FX")]


def _num(rows, prefix, key):
    hits = [ln for ln in rows if ln.startswith(prefix)]
    assert len(hits) == 1, "expected exactly one %s row:\n%s" % (prefix, rows)
    m = re.search(r"\b%s=(\d+)" % key, hits[0])
    assert m, "no %s= in %r" % (key, hits[0])
    return int(m.group(1))


def test_v5fx_v15_machine_rows_pinned():
    """Leg 1: the re-declared baseline is the measured RED shape,
    row-for-row, in kit print order (V5FX-FAIL LAST, V5FX-OK absent —
    the CAP/SETTLE/TEARDOWN rows are UNREACHED, pinned absent: a kit
    that starts reaching them has changed shape -> RE-PIN, do not
    let it false-green beside these rows)."""
    rows = _machine_rows(BASELINE.read_text(encoding="utf-8"))
    assert rows == V15_ROWS, \
        "re-declared v15 baseline rows drifted (re-run the kit, archive " \
        "the transcript, re-pin together): %r" % rows
    ok = [ln for ln in rows if ln.startswith("V5FX-OK")]
    assert ok == [], "V5FX-OK in a RED baseline? rows=%r" % rows
    for tag in ("V5FX-CAP", "V5FX-SETTLE", "V5FX-TEARDOWN"):
        assert not any(ln.startswith(tag) for ln in rows), \
            "%s row present at the RED shape — leg order changed, " \
            "RE-PIN this file" % tag


def test_v5fx_v15_counters_pinned():
    """Leg 2 (the DoD counters clause): the deterministic counters are
    pinned; ANY shift needs a fresh kit run archived + a re-pin —
    never a silent edit (shifts without a cause = FINDING rows)."""
    rows = _machine_rows(BASELINE.read_text(encoding="utf-8"))
    assert _num(rows, "V5FX-TRACER", "n") == 362, rows
    assert _num(rows, "V5FX-TRACER", "frames") == 40000, rows
    assert _num(rows, "V5FX-SPARK", "n") == 79725, rows
    assert _num(rows, "V5FX-POOF", "n") == 7, rows
    assert "fx_proj_ice" in [ln for ln in rows
                             if ln.startswith("V5FX-FAIL")][0], rows


def test_v5fx_old_baseline_untouched():
    """Leg 3: the 2026-10-27 GREEN baseline stays byte-untouched next
    to the re-declared red (versioned-truth + 'never quietly
    overwrite') — sha256 + its green rows read back."""
    raw = OLD_BASELINE.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    assert got == OLD_SHA256, \
        "2026-10-27 baseline OVERWRITTEN (sha %s != %s) — restore it; " \
        "new runs land NEW files beside it" % (got, OLD_SHA256)
    rows = _machine_rows(raw.decode("utf-8"))
    assert "V5FX-TRACER n=848 frames=270" in rows, rows
    assert "V5FX-ART n=4 paths=pinned" in rows, rows
    assert rows[-1] == "V5FX-OK", rows


def test_v5fx_starvation_written_cause_source_truth():
    """Leg 4: the cause is pinned WHERE it lives, so a silent fix (or
    a silent deepening) cannot ride past this file: fx_step runs the
    drop-pass (spark + number per hp drop, both cap-gated) BEFORE the
    fires pass; numbers COUNT toward the cap (G6 truth); PROJ_FOR
    maps hailspire -> fx_proj_ice and that committed sheet exists;
    the kit probe crosses no kit-assign (W-K zero at rest); probe and
    director pin the SAME cap constant 64."""
    text = (GODOT / "scripts" / "fx_director.gd").read_text(
        encoding="utf-8")

    def body(name):
        start = text.index("func %s(" % name)
        nxt = text.find("\nfunc ", start + 1)
        return text[start:nxt if nxt > 0 else len(text)]

    step = body("fx_step")
    code = hyg.blank_code(step, "gd")
    assert code.index("_observe_enemies(") < code.index("_observe_fires("), \
        "fx_step order changed — if the drop-pass no longer pre-empts " \
        "the fires pass, 11897-F1 may be FIXED: re-run the kit first"
    num = body("_spawn_number")
    assert "_fx.size() >= MAX_FX" in num, \
        "numbers no longer count toward the cap — G6 shape changed"
    assert "MAX_FX := 64" in text and "MAX_FX := 64" in \
        (GODOT / "sim" / "v5_fx_probe.gd").read_text(encoding="utf-8"), \
        "the 64 cap moved in one file only — probe and director diverged"
    assert '"hailspire_tower": "fx_proj_ice"' in text, \
        "PROJ_FOR ice mapping changed — ART leg means a different sheet"
    assert (GODOT / "assets" / "v11" / "fx_proj_ice.png").exists(), \
        "the ART-pinned sheet file left the repo"
    probe = (GODOT / "sim" / "v5_fx_probe.gd").read_text(encoding="utf-8")
    assert "assign_relic" not in probe, \
        "kit probe now crosses a kit-assign — the zero-at-rest clause " \
        "is dead, re-derive the counter causes"
