# P5b ring-band census (MC 11852): cool SELECTED-band pixels in the tower
# region, per frame. SELECTED_COLOR(0.35,0.8,1.0,0.55) over tan ground ->
# blue-dominant cool band; the RING_COLOR yellow is counted apart. Region
# excludes the panel/HUD. Baseline = no ring frames (00, 06).
import sys
from PIL import Image

X0, Y0, X1, Y1 = 150, 240, 520, 500     # tower-slot world region


def census(path):
    px = Image.open(path).convert("RGB").load()
    cool = yellow = 0
    for y in range(Y0, Y1):
        for x in range(X0, X1):
            r, g, b = px[x, y]
            if b > r + 40 and g > r + 20 and b > 140:
                cool += 1
            if r > 200 and g > 170 and b < r - 90:
                yellow += 1
    return cool, yellow


for name in sys.argv[1:]:
    c, y = census(name)
    print(f"{name}: cool={c} yellow={y}")
