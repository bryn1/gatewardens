#!/usr/bin/env python3
"""V-F P6 census (MC 12111) — DECOR region (340,40)-(900,160), the
north-rim band the DC-SCREEN probe leg pins its canopy tops inside.
Rows per frame: pine-green px (declared window, sampled from the served
AFTER frame: canopy pixels measured (53,97,37)..(77,132,50); the window
g>=70,g<=170,g>=r+25,g>=b+25 excludes the void (42,27,15) and the warm
stone (136,83,53) STRUCTURALLY, not tuned), void px (max channel <60 =
the bg colour family, the V-A silhouette metric), and the silhouette
delta against a reference frame (per-pixel max-channel diff >40).
Controls: BEFORE (v16-before-build.png, the plan's F-BUILD) and the
same-session DECOR-OFF control export — the non-vacuity pair (kb
2c3ab44b). Usage: vf_census_12111.py AFTER [CONTROL [BEFORE]]"""
import sys
from PIL import Image

RECT = (340, 40, 900, 160)


def crop(path):
    return Image.open(path).convert("RGB").crop(RECT)


def rows(path, ref=None):
    im = crop(path)
    px = list(im.getdata())
    green = sum(1 for r, g, b in px if 70 <= g <= 170 and g >= r + 25
                and g >= b + 25)
    void = sum(1 for r, g, b in px if max(r, g, b) < 60)
    line = "%s green=%d void=%d" % (path, green, void)
    if ref is not None:
        a, b = crop(path).load(), crop(ref).load()
        w, h = crop(path).size
        delta = sum(1 for x in range(w) for y in range(h)
                    if max(abs(a[x, y][0] - b[x, y][0]),
                           abs(a[x, y][1] - b[x, y][1]),
                           abs(a[x, y][2] - b[x, y][2])) > 40)
        line += " delta_vs_%s=%d" % ("/".join(ref.split("/")[-2:]),
                                     delta)
    print(line)


if __name__ == "__main__":
    after = sys.argv[1]
    control = sys.argv[2] if len(sys.argv) > 2 else None
    before = sys.argv[3] if len(sys.argv) > 3 else None
    rows(after, control)
    if control:
        rows(control, before)
    if before:
        rows(before)
