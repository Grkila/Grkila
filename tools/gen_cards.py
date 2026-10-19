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


def scene_ladder():  # unused by the current grid; returns markup only
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
    """8051 slave answering a Modbus frame: a request packet travels in, bytes light up in order."""
    c = COL["emb"]
    pins = "".join(f'<path d="M{x} 70v-18M{x} 200v18" stroke="{c}" stroke-width="3"/>' for x in range(110, 211, 20))
    pins += "".join(f'<path d="M90 {y}h-18M230 {y}h18" stroke="{c}" stroke-width="3"/>' for y in range(95, 181, 20))
    frame = ["01", "03", "00", "00", "00", "0A", "C5", "CD"]
    boxes = ""
    for i, b in enumerate(frame):
        x, y = 285 + (i % 4) * 44, 98 + (i // 4) * 46
        boxes += (f'<rect x="{x}" y="{y}" width="38" height="32" rx="5" fill="#132230" stroke="#2f4254"/>'
                  f'<rect class="byte" style="animation-delay:{0.6 + i * 0.28:.2f}s" x="{x}" y="{y}" width="38" height="32" rx="5" fill="{c}" fill-opacity=".14" stroke="{c}"/>'
                  f'<text x="{x + 19}" y="{y + 21}" fill="#e9eef3" font-family="{MONO}" font-size="13" text-anchor="middle">{b}</text>')
    css = ('.byte{opacity:0;animation:byte 4.8s ease-in-out infinite}'
           '@keyframes byte{0%,8%{opacity:0}14%,70%{opacity:1}82%,100%{opacity:0}}'
           '.pkt{animation:pkt 4.8s ease-in-out infinite}'
           '@keyframes pkt{0%{transform:translateX(0);opacity:0}4%{opacity:1}12%{transform:translateX(30px);opacity:1}16%,100%{transform:translateX(30px);opacity:0}}'
           '.led{animation:led 1.2s steps(2,start) infinite}@keyframes led{to{opacity:.25}}')
    return grid(c) + pins + f'<rect x="90" y="70" width="140" height="130" rx="10" fill="#132230" stroke="{c}" stroke-width="2"/>' \
        f'<circle class="led" cx="108" cy="88" r="5" fill="{c}"/><text x="160" y="142" fill="{c}" font-family="{MONO}" font-size="20" font-weight="700" text-anchor="middle">8051</text>' \
        f'<path d="M248 135H278" stroke="{c}" stroke-dasharray="4 4" stroke-width="2"/>' \
        f'<circle class="pkt" cx="248" cy="135" r="4" fill="{c}"/>' + boxes + \
        f'<text x="285" y="84" fill="#93a4b5" font-family="{MONO}" font-size="11">MODBUS FRAME</text>', css


def scene_paths():
    """Ranked introduction paths: the best route draws itself, then its score appears."""
    c = COL["ai"]
    nodes = {"you": (70, 135), "a": (170, 70), "b": (170, 200), "c": (280, 110), "d": (280, 210), "e": (380, 60), "goal": (410, 150)}
    edges = [("you", "a"), ("you", "b"), ("a", "c"), ("b", "c"), ("b", "d"), ("c", "e"), ("c", "goal"), ("d", "goal"), ("e", "goal")]
    out = grid(c)
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        out += f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{c}" stroke-opacity=".35" stroke-width="1.5"/>'
    out += '<path class="best" d="M70 135L170 200L280 110L410 150" fill="none" stroke="#f0b35a" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
    for i, (k, (x, y)) in enumerate(nodes.items()):
        big = k in ("you", "goal")
        out += f'<circle cx="{x}" cy="{y}" r="{14 if big else 9}" fill="#132230" stroke="{"#f0b35a" if big else c}" stroke-width="2"/>'
        if k in ("b", "c"):
            out += f'<circle class="hop" style="animation-delay:{0.9 if k == "b" else 1.7}s" cx="{x}" cy="{y}" r="9" fill="none" stroke="#f0b35a" stroke-width="2.5"/>'
    out += f'<text x="70" y="171" fill="#93a4b5" font-family="{MONO}" font-size="11" text-anchor="middle">YOU</text>'
    out += f'<text x="410" y="186" fill="#93a4b5" font-family="{MONO}" font-size="11" text-anchor="middle">TARGET</text>'
    out += f'<g class="score"><rect x="300" y="226" width="150" height="26" rx="6" fill="#132230" stroke="#2f4254"/><text x="312" y="243" fill="#e9eef3" font-family="{MONO}" font-size="11">best path · score 0.87</text></g>'
    css = ('.best{stroke-dasharray:420;stroke-dashoffset:420;animation:draw 5s ease-in-out infinite}'
           '@keyframes draw{0%,8%{stroke-dashoffset:420}55%,88%{stroke-dashoffset:0}100%{stroke-dashoffset:-420}}'
           '.hop{opacity:0;animation:hop 5s ease-out infinite;transform-box:fill-box;transform-origin:center}'
           '@keyframes hop{0%,10%{opacity:0;transform:scale(1)}20%{opacity:1;transform:scale(1.25)}60%{opacity:.8;transform:scale(1)}90%,100%{opacity:0}}'
           '.score{opacity:0;animation:score 5s ease infinite}@keyframes score{0%,52%{opacity:0}60%,86%{opacity:1}96%,100%{opacity:0}}')
    return out, css


def scene_scada():
    """HMI view built from the SCADA app's real tags and alarm (Adresa1 AI sine, high limit 20)."""
    import math as _m
    c = COL["auto"]
    out = '<defs><clipPath id="trend"><rect x="176" y="44" width="290" height="132" rx="7"/></clipPath></defs>'
    out += '<rect width="480" height="270" fill="#0b141c"/><rect width="480" height="30" fill="#132230"/>'
    out += f'<text x="14" y="20" fill="#e9eef3" font-family="{SANS}" font-size="13" font-weight="600">SCADA · Monitor</text>'
    out += f'<circle class="scan" cx="396" cy="15" r="4" fill="#7fd38a"/><text x="406" y="19" fill="#7fd38a" font-family="{MONO}" font-size="10">SCAN 200ms</text>'
    tags = [("AI", "Adresa1", "63.4", "#6aa8ff"), ("AO", "Izlaz", "41.0", "#7fd38a"), ("DO", "Motor1", "ON", "#f0b35a"), ("DI", "Stop", "OFF", "#b9a2ff")]
    for i, (t, n, v, tc) in enumerate(tags):
        y = 42 + i * 36
        out += f'<rect x="12" y="{y}" width="150" height="28" rx="6" fill="#132230"/>'
        out += f'<rect x="20" y="{y + 6}" width="26" height="16" rx="4" fill="{tc}"/><text x="33" y="{y + 18}" fill="#0b141c" font-family="{MONO}" font-size="10" font-weight="700" text-anchor="middle">{t}</text>'
        out += f'<text x="54" y="{y + 18}" fill="#e9eef3" font-family="{MONO}" font-size="11">{n}</text><text x="154" y="{y + 18}" fill="#e9eef3" font-family="{MONO}" font-size="11" text-anchor="end">{v}</text>'
    out += '<rect x="174" y="42" width="294" height="136" rx="8" fill="#0f1b26"/>'
    out += "".join(f'<path d="M182 {60 + k * 22}H460" stroke="#1d2c3a"/>' for k in range(6))
    period = 2 * _m.pi * 22
    pts = " ".join(f"{182 + i},{110 - 52 * _m.sin(i / 22):.1f}" for i in range(0, int(278 + period) + 4, 3))
    out += f'<g clip-path="url(#trend)"><polyline class="wave" points="{pts}" fill="none" stroke="{c}" stroke-width="2.2"/></g>'
    out += f'<path d="M182 99.6H460" stroke="#dc5046" stroke-width="1.5" stroke-dasharray="5 4"/><text x="458" y="94" fill="#f06e64" font-family="{MONO}" font-size="9.5" text-anchor="end">HI 20</text>'
    out += '<g class="alarm"><rect x="12" y="192" width="456" height="30" rx="6" fill="#3c1416" stroke="#7a2a2c"/>'
    out += f'<circle cx="28" cy="207" r="5" fill="#ff6a5c"/><text x="42" y="211" fill="#ffd0c8" font-family="{MONO}" font-size="11">ALARM  Adresa1 &gt; 20  Kriticna temperatura</text></g>'
    out += f'<text x="14" y="248" fill="#7d8fa1" font-family="{MONO}" font-size="10.5">Tags 4  ·  Alarms 2  ·  Reports  ·  Alarm history</text>'
    css = (f'.wave{{animation:wave 4s linear infinite}}@keyframes wave{{to{{transform:translateX(-{period:.2f}px)}}}}'
           '.alarm{animation:alarm 1.6s steps(2,start) infinite}@keyframes alarm{to{opacity:.45}}'
           '.scan{animation:scan 1s ease-in-out infinite}@keyframes scan{50%{opacity:.25}}')
    return out, css


def scene_silverone():
    """Voice -> Gemini Live -> tool dispatch -> device action, with the fallback chain from the README."""
    c = COL["ai"]
    out = grid(c)
    out += '<rect x="26" y="26" width="104" height="196" rx="16" fill="#132230" stroke="#3a4f63" stroke-width="2"/><rect x="62" y="34" width="32" height="5" rx="2.5" fill="#3a4f63"/>'
    out += "".join(f'<rect class="bar" style="animation-delay:{i * 0.11:.2f}s" x="{46 + i * 9}" y="{118 - h / 2}" width="5" height="{h}" rx="2.5" fill="{c}"/>'
                   for i, h in enumerate([10, 26, 44, 30, 52, 36, 20, 12]))
    out += f'<rect x="38" y="160" width="80" height="26" rx="13" fill="{c}"/><text x="78" y="177" fill="#0b141c" font-family="{SANS}" font-size="11" font-weight="600" text-anchor="middle">"Call Ana"</text>'

    def node(x, y, w, label, sub, col, cls=""):
        return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="42" rx="9" fill="#132230" stroke="{col}"/>'
                f'<text x="{x + w / 2}" y="{y + 18}" fill="#e9eef3" font-family="{SANS}" font-size="12" font-weight="600" text-anchor="middle">{label}</text>'
                f'<text x="{x + w / 2}" y="{y + 33}" fill="#93a4b5" font-family="{MONO}" font-size="9.5" text-anchor="middle">{sub}</text>')
    out += f'<path d="M134 124H160" stroke="{c}" stroke-width="2"/><path d="M262 124H288" stroke="{c}" stroke-width="2"/>'
    out += node(162, 103, 98, "Gemini Live", "intent", c, "n1") + node(290, 103, 100, "Tool dispatch", "validate · run", "#f0b35a", "n2")
    for i, (lab, y) in enumerate([("call", 50), ("message", 103), ("alarm", 156)]):
        out += f'<path d="M392 124C410 124 404 {y + 15} 420 {y + 15}" fill="none" stroke="#3a4f63" stroke-width="1.5"/>'
        cls = ' class="act"' if i == 0 else ""
        out += f'<rect{cls} x="420" y="{y}" width="48" height="30" rx="7" fill="#132230" stroke="{"#7fd38a" if i == 0 else "#3a4f63"}"/><text x="444" y="{y + 19}" fill="{"#7fd38a" if i == 0 else "#93a4b5"}" font-family="{MONO}" font-size="9.5" text-anchor="middle">{lab}</text>'
    out += f'<path class="sig" d="M134 124H392C410 124 404 65 420 65" fill="none" stroke="#e9eef3" stroke-width="3" stroke-linecap="round"/>'
    out += f'<text x="162" y="214" fill="#7d8fa1" font-family="{MONO}" font-size="9.5">FALLBACK</text>'
    for i, lab in enumerate(["Live", "API", "A2A", "Legacy"]):
        x = 162 + i * 76
        out += f'<rect x="{x}" y="222" width="64" height="24" rx="12" fill="#132230" stroke="{c if i == 0 else "#3a4f63"}"/><text x="{x + 32}" y="238" fill="{"#e9eef3" if i == 0 else "#93a4b5"}" font-family="{MONO}" font-size="10" text-anchor="middle">{lab}</text>'
        if i < 3:
            out += f'<path d="M{x + 66} 234H{x + 74}" stroke="#3a4f63" stroke-width="1.5"/>'
    css = ('.bar{transform-box:fill-box;transform-origin:center;animation:bar .9s ease-in-out infinite alternate}'
           '@keyframes bar{from{transform:scaleY(.35)}to{transform:scaleY(1)}}'
           '.sig{stroke-dasharray:26 400;stroke-dashoffset:26;animation:sig 3.2s ease-in-out infinite}'
           '@keyframes sig{0%{stroke-dashoffset:26;opacity:0}6%{opacity:1}62%{stroke-dashoffset:-318;opacity:1}70%,100%{stroke-dashoffset:-318;opacity:0}}'
           '.n1{animation:n1 3.2s infinite}@keyframes n1{18%,30%{stroke-width:2.5}0%,12%,40%,100%{stroke-width:1}}'
           '.n2{animation:n2 3.2s infinite}@keyframes n2{38%,50%{stroke-width:2.5}0%,32%,60%,100%{stroke-width:1}}'
           '.act{animation:act 3.2s infinite}@keyframes act{62%,80%{fill:#7fd38a;fill-opacity:.25}0%,56%,90%,100%{fill-opacity:1}}')
    return out, css


def card(slug, key, title, desc, tech, media, alt):
    W, H = 480, 384
    css = ""
    if isinstance(media, str):
        m = f'<image href="{embed(media)}" width="480" height="270" preserveAspectRatio="xMidYMid slice"/>'
    else:
        m, css = media()
    delay = (sum(map(ord, slug)) % 30) / 10
    css += (f'.sweep{{animation:sweep 5s ease-in-out {delay:.1f}s infinite}}'
            '@keyframes sweep{0%{transform:translateX(-120px)}55%,100%{transform:translateX(600px)}}'
            '@media (prefers-reduced-motion:reduce){*{animation:none!important}.best{stroke-dashoffset:0!important}'
            '.score,.byte,.hop{opacity:1!important}.sig,.pkt{opacity:0!important}}')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">
<style>{css}</style>
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".9"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="#0f1922"/>
{m}
<rect y="270" width="{W}" height="{H - 270}" fill="#0f1922"/>
<rect y="269" width="{W}" height="2" fill="{COL[key]}"/>
<rect class="sweep" y="268.5" width="120" height="3" fill="url(#sw)"/>
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
card("scada", "auto", "SCADA application", "Tags, alarm limits, trends and history over simulated PLC data", "C# · WPF · SQL",
     scene_scada, "SCADA application: tags, alarms and live trends over simulated PLC data.")
card("silverone", "ai", "SilverOne", "Voice assistant: LLM intent, deterministic device tools", "Java · Gemini Live · Firebase · RAG",
     scene_silverone, "SilverOne: Android voice assistant team project with Gemini Live and tool dispatch.")
card("airlock", "emb", "Airlock HIL testbench", "Rover airlock firmware with hardware-in-the-loop tests", "C++ · ESP32 · Python",
     "airlock-testbench.png", "Airlock HIL testbench: rover airlock firmware with a Python simulator.")
card("modbus", "emb", "Modbus on 8051", "Bare-metal Modbus slave: coils and registers", "C · 8051 · Modbus ASCII",
     scene_modbus, "Modbus on 8051: bare-metal Modbus slave in C.")
card("gridlab", "ai", "GridLab", "EV Days hackathon: EV charging on a city power grid", "Python · pandapower · RL · MCP",
     "gridlab-dashboard.png", "GridLab: EV charging scenarios and reinforcement learning on a synthetic Novi Sad grid.")
card("intro-paths", "ai", "Intro Path Discovery", "Finds and ranks introduction paths (team project)", "Python · LangGraph · Streamlit",
     scene_paths, "Intro Path Discovery: team project that finds and ranks introduction paths with LangGraph.")

mini("siemens", "auto", "Siemens S7 projects", "S7-1200 · TIA Portal", "Siemens S7 projects: PLC programming in TIA Portal.")
mini("motion", "ai", "Motion Analyzer", "OpenCV · PyQt6", "Motion Analyzer: video motion detection with OpenCV.")
mini("panther", "robo", "Panther simulation", "ROS 2 Jazzy · Docker", "Panther simulation: ROS 2 setup in Docker.")
mini("husarion", "robo", "Husarion workspace", "ROS 2 · Gazebo", "Husarion workspace: ROS 2 controllers and Gazebo.")
mini("diabetes", "ai", "Diabetes classifier", "Python · scikit-learn", "Diabetes classification with ensemble models.")
mini("stock", "ai", "Stock indicators", "MATLAB · time series", "Stock indicators: MATLAB time-series features.")

print("ok")
