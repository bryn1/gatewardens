# W-K served spark census (MC 11876): saturated spark-ORANGE pixels in the
# tower-region clip, per frame. fx_spark_hit = saturated orange star (low
# blue) over white-hot core; tan ground is desaturated (high blue) and is
# excluded. Control frame = pre-assign, identical clip.
import sys
from PIL import Image

def census(path):
    px = Image.open(path).convert("RGB").load()
    w, h = Image.open(path).size
    orange = core = 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 200 and 90 < g < 190 and b < r - 110:
                orange += 1
            elif r > 245 and g > 245 and b > 200 and b < 250:
                core += 1
    return orange, core

for name in sys.argv[1:]:
    o, c = census(name)
    print(f"{name}: orange={o} core={c}")
