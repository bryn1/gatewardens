"""V-H served census (MC 12114): hero-region frame-diff silhouette count.

THE LOCKED RULE (derived + locked BEFORE any AFTER frame existed; same
|delta|>40 frame-diff idiom as VD-wave.log §4): a pixel is a CHANGED px
when max(|dR|,|dG|,|dB|) > 40 between two 1280x720 build-phase frames.
  HERO   (460,210,360x360) — the VD hero crop widened 300->360 so the
           re-tuned figure (BODY_OFFSET z 2.6 -> 6.5, projects ~50px
           lower) cannot escape it. GREEN = changed px in this crop
           between the f1a2c51 baseline frame (hero occluded by the
           merged V-A keep, byte-identical to the pre-V-D frame) and
           the AFTER frame; the planted-red (offset back into the keep
           box) must drive it back to ~0 — that is the RED proof.
  MARK   (0,0,520,116)     — non-vacuity control: the coach/marker strip
           carries the running wave countdown, so it changes between any
           two live runs regardless of the hero knob.
  SELF   — a frame diffed against itself must count 0 (metric sanity).
Same rects on every frame (locked in vh-served-12114.cjs).
Usage: vh-census-12114.py frameA.png frameB.png [...]
Prints pairwise rows for consecutive pairs given on the command line.
"""
import sys
from PIL import Image

CROPS = {
    "HERO": (460, 210, 360, 360),
    "MARK": (0, 0, 520, 116),
}


def changed_px(imA, imB, rect):
    x, y, w, h = rect
    a = imA.crop((x, y, x + w, y + h))
    b = imB.crop((x, y, x + w, y + h))
    n = 0
    for pa, pb in zip(a.getdata(), b.getdata()):
        if max(abs(pa[0] - pb[0]), abs(pa[1] - pb[1]),
               abs(pa[2] - pb[2])) > 40:
            n += 1
    return n


if __name__ == "__main__":
    paths = sys.argv[1:]
    for p in paths:
        im = Image.open(p).convert("RGB")
        print("SELF %s HERO=%d" % (p, changed_px(im, im, CROPS["HERO"])))
    for i in range(len(paths) - 1):
        a = Image.open(paths[i]).convert("RGB")
        b = Image.open(paths[i + 1]).convert("RGB")
        print("DIFF %s vs %s: HERO=%d MARK=%d" % (
            paths[i].rsplit("/", 1)[-1], paths[i + 1].rsplit("/", 1)[-1],
            changed_px(a, b, CROPS["HERO"]), changed_px(a, b, CROPS["MARK"])))
