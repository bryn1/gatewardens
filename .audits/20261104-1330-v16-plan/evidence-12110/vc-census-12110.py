"""V-C served census (MC 12110): PATH-REGION ghost/road pixel counts.

THE LOCKED RULE (derived + locked on the two CONTROL frames — the
v1.6 BEFORE frame and the V-A build frame, both of which still carry
the translucent ghost arrows — BEFORE any AFTER frame existed):

  ghost-cyan px : (G - R) >= 8 AND B >= 120
                  (the BAND_COLOR(0.55,0.8,1.0,0.30) blend raises G
                  above R and B above 120 on ANY warm ground; warm
                  stone/road/grass/white-text all fail it — grass has
                  B < 120, white text has G-R < 8)
  warm-road px  : (R - B) >= 55 AND R >= 100 AND (G - R) < 8
                  (the ROAD_TINT-scaled ground_path sheet AND the warm
                  floor both live here — this row is a presence floor,
                  not a road-identity claim; road identity is carried
                  by the ghost->~0 census + the LB-ROAD machine rows +
                  the describe-image literal reads)

Crops are the three declared PATH-REGION rects (1280x720 coords,
named in vc-served-12110.cjs) — the same rects on every frame.
Usage: vc-census-12110.py frame.png [frame2.png ...]
"""
import sys
from PIL import Image

CROPS = {
    "PATH-A": (620, 225, 115, 100),   # centre lane, arch excluded
    "PATH-B": (365, 360, 225, 55),    # left corridor strip
    "PATH-C": (865, 520, 140, 75),    # lower-right strip
}


def census(path):
    im = Image.open(path).convert("RGB")
    rows = []
    for name, (x, y, w, h) in CROPS.items():
        px = im.crop((x, y, x + w, y + h)).getdata()
        ghost = warm = 0
        for (r, g, b) in px:
            if g - r >= 8 and b >= 120:
                ghost += 1
            elif r - b >= 55 and r >= 100 and g - r < 8:
                warm += 1
        rows.append((name, len(px), ghost, warm))
    return rows


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print("== " + path)
        for name, n, ghost, warm in census(path):
            print("%s n=%d ghost=%d warm=%d" % (name, n, ghost, warm))
