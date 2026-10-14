"""Render the two monitor screen textures (HMI trend and LLM tool console) with PIL."""
import math, sys
from PIL import Image, ImageDraw, ImageFont

out = sys.argv[1]
W, H = 1280, 760
mono = ImageFont.truetype("consola.ttf", 26)
mono_s = ImageFont.truetype("consola.ttf", 20)
sans_b = ImageFont.truetype("segoeuib.ttf", 30)

# HMI: tag list, live trend with alarm limit, alarm banner
im = Image.new("RGB", (W, H), (12, 20, 28))
d = ImageDraw.Draw(im)
d.rectangle([0, 0, W, 56], fill=(20, 33, 46))
d.text((24, 12), "SCADA  ·  Monitor", font=sans_b, fill=(225, 235, 242))
d.text((W - 260, 18), "SCAN 200 ms", font=mono_s, fill=(120, 200, 140))
tags = [("Adresa1", "AI", "ADDR001", "63.4"), ("Izlaz", "AO", "ADDR009", "41.0"), ("Motor1", "DO", "ADDR005", "ON"), ("Stop dugme", "DI", "ADDR004", "OFF")]
col = {"AI": (106, 168, 255), "AO": (127, 211, 138), "DO": (240, 179, 90), "DI": (185, 162, 255)}
for i, (n, t, a, v) in enumerate(tags):
    y = 84 + i * 62
    d.rounded_rectangle([20, y, 400, y + 50], 8, fill=(19, 32, 45))
    d.rounded_rectangle([32, y + 11, 82, y + 39], 6, fill=col[t])
    d.text((41, y + 12), t, font=mono_s, fill=(10, 18, 26))
    d.text((96, y + 11), n, font=mono, fill=(225, 235, 242))
    d.text((300, y + 11), v, font=mono, fill=(225, 235, 242))
x0, y0, x1, y1 = 430, 84, W - 24, 520
d.rounded_rectangle([x0, y0, x1, y1], 10, fill=(15, 26, 37))
for k in range(1, 6):
    yy = y0 + k * (y1 - y0) / 6
    d.line([x0 + 10, yy, x1 - 10, yy], fill=(30, 46, 60), width=1)
lim = y0 + (y1 - y0) * 0.30
d.line([x0 + 10, lim, x1 - 10, lim], fill=(220, 80, 70), width=3)
d.text((x1 - 170, lim - 32), "HI LIMIT 20", font=mono_s, fill=(240, 110, 100))
pts = [(x0 + 10 + i, (y0 + y1) / 2 - 150 * math.sin(i / 70)) for i in range(0, x1 - x0 - 20, 3)]
d.line(pts, fill=(106, 168, 255), width=4)
d.rounded_rectangle([20, 560, W - 24, 640], 10, fill=(70, 22, 24))
d.text((44, 584), "ALARM  Adresa1 > 20   Kriticna temperatura", font=mono, fill=(255, 200, 190))
d.text((24, 680), "Tags 4   Alarms 2   History 128", font=mono_s, fill=(120, 140, 160))
im.save(f"{out}/screen_hmi.png")

# LLM / MCP console
im = Image.new("RGB", (W, H), (14, 12, 24))
d = ImageDraw.Draw(im)
d.rectangle([0, 0, W, 56], fill=(28, 24, 46))
d.text((24, 12), "agent  ·  MCP tools", font=sans_b, fill=(230, 225, 255))
lines = [
    ("> ", "run_scenario(strategy='capacity_aware', seed=7)", (185, 162, 255)),
    ("  ", "ok  48,000 EVs served, 0 voltage violations", (127, 211, 138)),
    ("> ", "read_plc_timing(block='FB_Publisher')", (185, 162, 255)),
    ("  ", "ok  mean 0.41 ms   max 0.62 ms", (127, 211, 138)),
    ("> ", "validate_workbook(sheet='CPC_AnaDO')", (185, 162, 255)),
    ("  ", "ok  706 objects checked", (127, 211, 138)),
    ("> ", "gripper.set_param(kp=1.8, band='40-120 Hz')", (185, 162, 255)),
    ("  ", "ok  slip reaction 90 ms", (127, 211, 138)),
]
for i, (p, t, c) in enumerate(lines):
    y = 90 + i * 56
    d.text((30, y), p, font=mono, fill=(120, 110, 160))
    d.text((64, y), t, font=mono, fill=c)
d.rectangle([64, 90 + 8 * 56 + 6, 78, 90 + 8 * 56 + 34], fill=(230, 225, 255))
cx, cy = 1080, 610
import random
random.seed(3)
nodes = [(cx + 120 * math.cos(a), cy + 80 * math.sin(a)) for a in [i * 0.9 for i in range(7)]]
for i, a in enumerate(nodes):
    for b in nodes[i + 1:i + 3]:
        d.line([a, b], fill=(110, 95, 170), width=2)
for n in nodes:
    d.ellipse([n[0] - 10, n[1] - 10, n[0] + 10, n[1] + 10], fill=(185, 162, 255))
im.save(f"{out}/screen_llm.png")
print("screens ok")

# PCB texture: solder mask, copper traces, pads, silkscreen
import random as R
R.seed(11)
W2, H2 = 1400, 900
im = Image.new("RGB", (W2, H2), (14, 74, 44))
d = ImageDraw.Draw(im)
for _ in range(9000):
    x, y = R.randrange(W2), R.randrange(H2)
    d.point((x, y), fill=(18 + R.randrange(8), 80 + R.randrange(10), 48 + R.randrange(8)))
for _ in range(90):
    x, y = R.randrange(80, W2 - 80), R.randrange(80, H2 - 80)
    pts = [(x, y)]
    for _ in range(3):
        if R.random() < 0.5: x += R.choice([-1, 1]) * R.randrange(40, 260)
        else: y += R.choice([-1, 1]) * R.randrange(40, 200)
        pts.append((max(40, min(W2 - 40, x)), max(40, min(H2 - 40, y))))
    d.line(pts, fill=(40, 120, 70), width=R.choice([6, 8, 12]), joint="curve")
for i in range(19):
    for row in (60, H2 - 60):
        d.ellipse([140 + i * 60 - 14, row - 14, 140 + i * 60 + 14, row + 14], fill=(200, 170, 90))
        d.ellipse([140 + i * 60 - 6, row - 6, 140 + i * 60 + 6, row + 6], fill=(30, 30, 30))
for _ in range(40):
    x, y = R.randrange(200, W2 - 200), R.randrange(160, H2 - 160)
    d.rectangle([x, y, x + 34, y + 18], fill=(200, 170, 90))
d.rectangle([520, 300, 900, 600], fill=(25, 25, 28))
for k in range(14):
    d.rectangle([500, 315 + k * 20, 520, 325 + k * 20], fill=(200, 170, 90))
    d.rectangle([900, 315 + k * 20, 920, 325 + k * 20], fill=(200, 170, 90))
sil = ImageFont.truetype("consolab.ttf", 46)
d.text((90, 120), "GRIPPER CTRL  v2", font=sil, fill=(235, 240, 235))
d.text((90, 180), "TLV493D  ESP32", font=ImageFont.truetype("consola.ttf", 34), fill=(225, 232, 225))
for k in range(4):
    d.rectangle([1050, 260 + k * 110, 1250, 330 + k * 110], outline=(235, 240, 235), width=4)
im.save(f"{out}/pcb.png")
print("pcb ok")
