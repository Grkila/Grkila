"""Soft bloom for neon and LEDs: threshold bright pixels, blur, add back."""
import sys, os, glob
from PIL import Image, ImageFilter, ImageChops
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for p in sorted(glob.glob(os.path.join(src, "*.png"))):
    im = Image.open(p).convert("RGB")
    lum = im.convert("L").point(lambda v: 255 if v > 200 else int(v * 0.0))
    bright = Image.composite(im, Image.new("RGB", im.size), lum)
    glow = ImageChops.add(bright.filter(ImageFilter.GaussianBlur(6)), bright.filter(ImageFilter.GaussianBlur(18)))
    out = ImageChops.add(im, Image.eval(glow, lambda v: int(v * 0.45)))
    out.save(os.path.join(dst, os.path.basename(p)))
print("post ok", len(glob.glob(os.path.join(dst, '*.png'))))
