"""Generate uniform project cards (SVG) for the profile README.

Run from the repository root: python gen_cards.py
"""
import base64, io, os, sys
from PIL import Image

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "assets", "cards")
os.makedirs(OUT, exist_ok=True)

ICON = {
    "robo": "M4 20h9M8.5 20v-2.5M8.5 17.5L12 10M12 10l6-3.5M18 6.5l2.2 2.6M18 6.5l.8-3.3M10.1 17.5a1.6 1.6 0 1 1-3.2 0a1.6 1.6 0 1 1 3.2 0M13.6 10a1.6 1.6 0 1 1-3.2 0a1.6 1.6 0 1 1 3.2 0",
    "auto": "M4 4h16v16H4zM4 8h16M7 11.5h6M7 14.5h6M7 17.5h6M16.5 12v.01M16.5 15v.01",
    "emb": "M7 7h10v10H7zM10 10h4v4h-4zM9.5 4v3M12 4v3M14.5 4v3M9.5 17v3M12 17v3M14.5 17v3M4 9.5h3M4 12h3M4 14.5h3M17 9.5h3M17 12h3M17 14.5h3",
    "ai": "M6.6 7.9l3.8 3.2M6.6 16.1l3.8-3.2M13.6 11.1l3.8-3.2M13.6 12.9l3.8 3.2M6.8 7a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0M6.8 17a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0M14 12a2 2 0 1 1-4 0a2 2 0 1 1 4 0M20.8 7a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0M20.8 17a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0",
}
COL = {"robo": "#f0b35a", "auto": "#6aa8ff", "emb": "#7fd38a", "ai": "#b9a2ff"}
NAME = {"robo": "ROBOTICS", "auto": "INDUSTRIAL AUTOMATION", "emb": "EMBEDDED", "ai": "AI &amp; LLM"}
SANS = "Segoe UI,Helvetica,Arial,sans-serif"
MONO = "Consolas,Menlo,monospace"


def icon(key, x, y, size, width=1.8):
    return (f'<g transform="translate({x} {y}) scale({size / 24})" fill="none" stroke="{COL[key]}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"><path d="{ICON[key]}"/></g>')


def embed(path):
    im = Image.open(os.path.join(ROOT, "assets", path)).convert("RGB")
    im = im.resize((480, 270), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def grid(col):
    lines = "".join(f'<path d="M{x} 0V270"/>' for x in range(0, 481, 24)) + "".join(f'<path d="M0 {y}H480"/>' for y in range(0, 271, 24))
    return f'<rect width="480" height="270" fill="#0d1821"/><g stroke="{col}" stroke-opacity=".07">{lines}</g>'


def scene_ladder():
    c = COL["auto"]
    rungs = []
    for i, y in enumerate([70, 125, 180]):
        rungs.append(f'<path d="M70 {y}H150M170 {y}H250M270 {y}H330M370 {y}H410" stroke="{c}" stroke-width="2.5"/>')
        rungs.append(f'<path d="M150 {y-16}V{y+16}M170 {y-16}V{y+16}" stroke="{c}" stroke-width="2.5"/>')
        if i != 1:
            rungs.append(f'<path d="M250 {y-16}V{y+16}M270 {y-16}V{y+16}" stroke="{c}" stroke-width="2.5"/>')
        else:
            rungs.append(f'<path d="M250 {y-16}V{y+16}M270 {y-16}V{y+16}M252 {y+14}L268 {y-14}" stroke="{c}" stroke-width="2.5"/>')
        rungs.append(f'<path d="M340 {y-18}a22 22 0 0 0 0 36M360 {y-18}a22 22 0 0 1 0 36" fill="none" stroke="#f0b35a" stroke-width="2.5"/>')
        rungs.append(f'<text x="160" y="{y-24}" fill="#93a4b5" font-family="{MONO}" font-size="11" text-anchor="middle">I0.{i}</text>')
        rungs.append(f'<text x="350" y="{y-24}" fill="#93a4b5" font-family="{MONO}" font-size="11" text-anchor="middle">Q0.{i}</text>')
    return grid(c) + f'<path d="M70 40V210M410 40V210" stroke="{c}" stroke-width="4"/>' + "".join(rungs) + \
        f'<path d="M70 70H150" stroke="#f0b35a" stroke-width="3" opacity=".9"/>'


def scene_modbus():
    c = COL["emb"]
    pins = "".join(f'<path d="M{x} 70v-18M{x} 200v18" stroke="{c}" stroke-width="3"/>' for x in range(110, 211, 20))
    pins += "".join(f'<path d="M90 {y}h-18M230 {y}h18" stroke="{c}" stroke-width="3"/>' for y in range(95, 181, 20))
    frame = ["01", "03", "00", "00", "00", "0A", "C5", "CD"]
    boxes = "".join(
        f'<rect x="{285 + (i % 4) * 44}" y="{98 + (i // 4) * 46}" width="38" height="32" rx="5" fill="#132230" stroke="{c if i < 2 else "#2f4254"}"/>'
        f'<text x="{304 + (i % 4) * 44}" y="{119 + (i // 4) * 46}" fill="{"#e9eef3" if i < 2 else "#93a4b5"}" font-family="{MONO}" font-size="13" text-anchor="middle">{b}</text>'
        for i, b in enumerate(frame))
    return grid(c) + pins + f'<rect x="90" y="70" width="140" height="130" rx="10" fill="#132230" stroke="{c}" stroke-width="2"/>' \
        f'<circle cx="108" cy="88" r="5" fill="{c}"/><text x="160" y="142" fill="{c}" font-family="{MONO}" font-size="20" font-weight="700" text-anchor="middle">8051</text>' \
        f'<path d="M248 135H278" stroke="{c}" stroke-dasharray="4 4" stroke-width="2"/>' + boxes + \
        f'<text x="285" y="84" fill="#93a4b5" font-family="{MONO}" font-size="11">MODBUS FRAME</text>'


def scene_paths():
    c = COL["ai"]
    nodes = {"you": (70, 135), "a": (170, 70), "b": (170, 200), "c": (280, 110), "d": (280, 210), "e": (380, 60), "goal": (410, 150)}
    edges = [("you", "a"), ("you", "b"), ("a", "c"), ("b", "c"), ("b", "d"), ("c", "e"), ("c", "goal"), ("d", "goal"), ("e", "goal")]
    best = {("you", "b"), ("b", "c"), ("c", "goal")}
    out = grid(c)
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        on = (a, b) in best
        out += f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{"#f0b35a" if on else c}" stroke-opacity="{1 if on else .35}" stroke-width="{3 if on else 1.5}"/>'
    for k, (x, y) in nodes.items():
        big = k in ("you", "goal")
        out += f'<circle cx="{x}" cy="{y}" r="{14 if big else 9}" fill="#132230" stroke="{"#f0b35a" if big else c}" stroke-width="2"/>'
    out += f'<text x="70" y="171" fill="#93a4b5" font-family="{MONO}" font-size="11" text-anchor="middle">YOU</text>'
    out += f'<text x="410" y="186" fill="#93a4b5" font-family="{MONO}" font-size="11" text-anchor="middle">TARGET</text>'
    out += f'<rect x="300" y="226" width="150" height="26" rx="6" fill="#132230" stroke="#2f4254"/><text x="312" y="243" fill="#e9eef3" font-family="{MONO}" font-size="11">best path · score 0.87</text>'
    return out


def card(slug, key, title, desc, tech, media, alt):
    W, H = 480, 384
    m = f'<image href="{embed(media)}" width="480" height="270" preserveAspectRatio="xMidYMid slice"/>' if isinstance(media, str) else media()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="#0f1922"/>
{m}
<rect y="270" width="{W}" height="{H - 270}" fill="#0f1922"/>
<rect y="269" width="{W}" height="2" fill="{COL[key]}"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#22313f"/>
{icon(key, 20, 286, 16)}
<text x="44" y="299" fill="{COL[key]}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.2">{NAME[key]}</text>
<path d="M444 288h10v10M443 299l11-11" fill="none" stroke="#7d8fa1" stroke-width="1.6" stroke-linecap="round"/>
<text x="20" y="328" fill="#e9eef3" font-family="{SANS}" font-size="20" font-weight="600">{title}</text>
<text x="20" y="351" fill="#b4c2d0" font-family="{SANS}" font-size="13.5">{desc}</text>
<text x="20" y="371" fill="#7d8fa1" font-family="{MONO}" font-size="11.5">{tech}</text>
</svg>'''
    open(os.path.join(OUT, f"{slug}.svg"), "w", encoding="utf-8").write(svg)


def mini(slug, key, title, tech, alt):
    W, H = 300, 76
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="#0f1922" stroke="#22313f"/>
<rect x="14" y="16" width="44" height="44" rx="10" fill="#132230" stroke="{COL[key]}" stroke-opacity=".5"/>
{icon(key, 24, 26, 24)}
<text x="72" y="35" fill="#e9eef3" font-family="{SANS}" font-size="15" font-weight="600">{title}</text>
<text x="72" y="55" fill="#7d8fa1" font-family="{MONO}" font-size="11">{tech}</text>
<path d="M270 18h8v8M269 27l9-9" fill="none" stroke="#7d8fa1" stroke-width="1.4" stroke-linecap="round"/>
</svg>'''
    open(os.path.join(OUT, f"{slug}.svg"), "w", encoding="utf-8").write(svg)


card("gripper", "robo", "Adaptive gripper", "Thesis: magnetic slip sensing, about 90 ms reaction", "ESP32 · FreeRTOS · FFT · Python",
     "gripper-still.png", "Adaptive gripper: thesis project with magnetic slip sensing. ESP32, FreeRTOS, FFT.")
card("manipulator", "robo", "Robot manipulator", "PID, fuzzy PID and sliding-mode control", "LabVIEW · Python · MediaPipe",
     "manipulator-panel.jpg", "Robot manipulator: two-joint control with PID, fuzzy PID and sliding-mode control.")
card("scada", "auto", "SCADA application", "Simulated PLC data, alarms and history", "C# · WPF · SQL",
     "scada-monitor.png", "SCADA application: monitoring with simulated PLC data, alarms and history.")
card("siemens", "auto", "Siemens S7 projects", "Practical PLC programming exercises", "S7-1200 · TIA Portal · Ladder",
     scene_ladder, "Siemens S7 projects: practical PLC programming in TIA Portal.")
card("airlock", "emb", "Airlock HIL testbench", "Rover airlock firmware with hardware-in-the-loop tests", "C++ · ESP32 · Python",
     "airlock-testbench.png", "Airlock HIL testbench: rover airlock firmware with a Python simulator.")
card("modbus", "emb", "Modbus on 8051", "Bare-metal Modbus slave: coils and registers", "C · 8051 · Modbus ASCII",
     scene_modbus, "Modbus on 8051: bare-metal Modbus slave in C.")
card("gridlab", "ai", "GridLab", "EV Days hackathon: EV charging on a city power grid", "Python · pandapower · RL · MCP",
     "gridlab-dashboard.png", "GridLab: EV charging scenarios and reinforcement learning on a synthetic Novi Sad grid.")
card("intro-paths", "ai", "Intro Path Discovery", "Finds and ranks introduction paths (team project)", "Python · LangGraph · Streamlit",
     scene_paths, "Intro Path Discovery: team project that finds and ranks introduction paths with LangGraph.")

mini("silverone", "ai", "SilverOne", "Gemini Live · Android", "SilverOne: Android voice assistant team project.")
mini("motion", "ai", "Motion Analyzer", "OpenCV · PyQt6", "Motion Analyzer: video motion detection with OpenCV.")
mini("panther", "robo", "Panther simulation", "ROS 2 Jazzy · Docker", "Panther simulation: ROS 2 setup in Docker.")
mini("husarion", "robo", "Husarion workspace", "ROS 2 · Gazebo", "Husarion workspace: ROS 2 controllers and Gazebo.")
mini("diabetes", "ai", "Diabetes classifier", "Python · scikit-learn", "Diabetes classification with ensemble models.")
mini("stock", "ai", "Stock indicators", "MATLAB · time series", "Stock indicators: MATLAB time-series features.")

for k in ICON:
    open(os.path.join(OUT, f"icon-{k}.svg"), "w", encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" role="img" aria-label="{NAME[k]}">{icon(k, 0, 0, 24)}</svg>')
print("ok")
