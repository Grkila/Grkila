"""Write light-theme copies of the dark SVGs for GitHub light mode.

Run from the repository root after gen_cards.py: python tools/theme_light.py
Dark palette colours are swapped for GitHub light-palette equivalents; embedded
screenshots are untouched.
"""
import glob, os, re

MAP = {
    # surfaces
    "#0f1922": "#ffffff", "#0b131b": "#ffffff", "#0f1b26": "#ffffff",
    "#0d1821": "#f6f8fa", "#0b141c": "#f6f8fa", "#132230": "#eef2f6",
    "#0f1b25": "#e9eef2", "#0c161f": "#dfe5eb",
    # lines and borders
    "#1d2c3a": "#e3e8ee", "#22313f": "#d0d7de", "#2f4254": "#c4ccd5", "#3a4f63": "#afb8c1",
    # text
    "#e9eef3": "#1f2328", "#b4c2d0": "#424a53", "#93a4b5": "#59636e", "#7d8fa1": "#6e7781",
    # domain colours, darkened for contrast on white
    "#f0b35a": "#9a6700", "#6aa8ff": "#0969da", "#7fd38a": "#1a7f37", "#b9a2ff": "#8250df",
    # stack layer gradient (teal to amber)
    "#79c8cb": "#1b7c83", "#91c4b4": "#3a7a6a", "#a9c09e": "#587852", "#c0bb87": "#76733b",
    "#d8b771": "#886d22",
    # alarm
    "#3c1416": "#ffebe9", "#7a2a2c": "#ff8182", "#ffd0c8": "#82071e", "#ff6a5c": "#cf222e",
    "#f06e64": "#cf222e", "#dc5046": "#cf222e",
}
PAT = re.compile("|".join(re.escape(k) for k in MAP), re.I)


def convert(src, dst):
    s = open(src, encoding="utf-8").read()
    # keep base64 image data untouched: only swap colours outside data URIs
    parts = re.split(r'(data:image/[^"]+)', s)
    parts = [p if p.startswith("data:image/") else PAT.sub(lambda m: MAP[m.group(0).lower()], p) for p in parts]
    s = "".join(parts).replace('fill="#000" opacity=".4"', 'fill="#8c959f" opacity=".25"')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    for f in glob.glob("assets/cards/*.svg"):
        convert(f, os.path.join("assets/cards/light", os.path.basename(f)))
    convert("assets/stack-isometric.svg", "assets/stack-isometric-light.svg")
    print("light theme ok")
