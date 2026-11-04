#!/usr/bin/env python3
"""V-G census (MC 12115): the pair's per-region BEFORE/AFTER delta table.

THE LOCKED RULE — every metric window is REUSED from the card that proved it
(no new measure, so the tables stay comparable with the W1/W2 rows):
  void   max(r,g,b) < 60                      (vf_census_12111.py silhouette)
  black  max(r,g,b) < 25                      (the black-blob watch: unlit
          faces painted pure black — the VA shadow-ruling failure mode)
  warm   (r-b)>=55 and r>=100 and (g-r)<8     (vc-census-12110.py)
  ghost  (g-r)>=8 and b>=120                  (vc-census-12110.py ghost arrows)
  pine   70<=g<=170 and g>=r+25 and g>=b+25   (vf_census_12111.py canopy)
  delta  per-pixel max(|dR|,|dG|,|dB|) > 40 vs the FIRST frame on the line
          (the VD/VF/VH frame-diff idiom)
Regions are the cards' declared rects, byte-identical across every frame in
this run (the camera never moved: zero wheel events, L4): TOP-STRIP/CENTER/
CORE-REGION/GATE-REGION (census-12081), PATH-A/B/C (vc), DECOR (vf), HERO
(vh), PANEL/SKY (VE census rows).
Usage: vg-census.py label.png [more.png ...]  — rows per region per frame;
the delta is measured against the first frame given (the BEFORE side)."""
import sys
from PIL import Image

RECTS = {
    "TOP-STRIP":   (340, 90, 880, 150),
    "CENTER":      (420, 250, 860, 500),
    "CORE":        (540, 246, 740, 420),
    "GATE":        (260, 266, 392, 396),
    "PATH-A":      (620, 225, 735, 325),
    "PATH-B":      (365, 360, 590, 415),
    "PATH-C":      (865, 520, 1005, 595),
    "DECOR":       (340, 40, 900, 160),
    "HERO":        (460, 210, 820, 570),
    "PANEL":       (904, 28, 1150, 470),
    "SKY":         (0, 0, 1280, 55),
}


def counts(px):
    c = dict(void=0, black=0, warm=0, ghost=0, pine=0)
    for r, g, b in px:
        if max(r, g, b) < 60:
            c["void"] += 1
        if max(r, g, b) < 25:
            c["black"] += 1
        if r - b >= 55 and r >= 100 and g - r < 8:
            c["warm"] += 1
        if g - r >= 8 and b >= 120:
            c["ghost"] += 1
        if 70 <= g <= 170 and g >= r + 25 and g >= b + 25:
            c["pine"] += 1
    return c


def main(paths):
    frames = [(p.split("/")[-1], Image.open(p).convert("RGB")) for p in paths]
    ref = frames[0][1]
    for name, (lbl, im) in enumerate(frames):
        print(f"== {lbl}")
        for reg, (x0, y0, x1, y1) in RECTS.items():
            c = counts(im.crop((x0, y0, x1, y1)).getdata())
            d = 0
            if name:
                a, b = im.crop((x0, y0, x1, y1)).load(), ref.crop((x0, y0, x1, y1)).load()
                d = sum(1 for y in range(y1 - y0) for x in range(x1 - x0)
                        if max(abs(a[x, y][i] - b[x, y][i]) for i in range(3)) > 40)
            row = " ".join(f"{k}={v}" for k, v in c.items())
            print(f"{reg:10s} ({x0},{y0},{x1},{y1}) {row} delta_vs_before={d}" if name
                  else f"{reg:10s} ({x0},{y0},{x1},{y1}) {row}")
        full = 0
        if name:
            full = sum(1 for pa, pb in zip(im.getdata(), ref.getdata())
                       if max(abs(pa[i] - pb[i]) for i in range(3)) > 40)
        print(f"{'FULL':10s} delta_vs_before={full}" if name else f"{'FULL':10s} —")


if __name__ == "__main__":
    main(sys.argv[1:])
