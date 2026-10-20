"""Build animated WebP project cards: card chrome from gen_cards.py over animation frames.

usage: python tools/raster_cards.py <slug> <frames_glob> <fps> [first] [last]
Needs pillow and resvg_py. Writes assets/cards/<slug>.webp and assets/cards/light/<slug>.webp.
"""
import glob, io, os, subprocess, sys, tempfile
import resvg_py
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import gen_cards as G          # noqa: E402  (card template and copy)
import theme_light as TL       # noqa: E402  (dark -> light palette)

S = 2                          # render at 2x for sharp text
CW, CH, MH, R = 480 * S, 384 * S, 270 * S, 14 * S

COPY = {
    "gripper": ("robo", "Adaptive gripper", "Thesis: magnetic slip sensing, about 90 ms reaction", "ESP32 · FreeRTOS · FFT · Python",
                "Adaptive gripper: thesis project with magnetic slip sensing, shown catching a sponge."),
    "airlock": ("emb", "Airlock HIL testbench", "Rover airlock firmware with hardware-in-the-loop tests", "C++ · ESP32 · Python",
                "Airlock HIL testbench: a rover passes through a three-zone airlock."),
    "gridlab": ("ai", "GridLab", "EV Days hackathon: EV charging on a city power grid", "Python · pandapower · RL · MCP",
                "GridLab: the 3D Novi Sad scene from its presentation, with EV cars driving and charging across the grid."),
}


def overlay(slug, light):
    key, title, desc, tech, alt = COPY[slug]
    tmp = tempfile.mktemp(suffix=".svg")
    G.card(slug, key, title, desc, tech, None, alt, out_path=tmp)
    if light:
        TL.convert(tmp, tmp)
    png = bytes(resvg_py.svg_to_bytes(svg_path=tmp, zoom=S))
    os.remove(tmp)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def main():
    slug, pattern, fps = sys.argv[1], sys.argv[2], float(sys.argv[3])
    frames = sorted(glob.glob(pattern))
    if len(sys.argv) > 5:
        frames = frames[int(sys.argv[4]):int(sys.argv[5])]
    mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW - 1, CH - 1], R, fill=255)
    media_mask = Image.new("L", (CW, CH), 0)
    media_mask.paste(mask.crop((0, 0, CW, MH)), (0, 0))
    for light in (False, True):
        ov = overlay(slug, light)
        with tempfile.TemporaryDirectory() as td:
            for i, f in enumerate(frames):
                fr = Image.open(f).convert("RGB")
                # cover-fit into the media area
                k = max(CW / fr.width, MH / fr.height)
                fr = fr.resize((round(fr.width * k), round(fr.height * k)), Image.LANCZOS)
                x0, y0 = (fr.width - CW) // 2, (fr.height - MH) // 2
                fr = fr.crop((x0, y0, x0 + CW, y0 + MH))
                canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
                canvas.paste(fr, (0, 0), media_mask.crop((0, 0, CW, MH)))
                canvas.alpha_composite(ov)
                canvas.save(os.path.join(td, f"c{i:04d}.png"))
            out = os.path.join("assets", "cards", "light" if light else "", f"{slug}.webp")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(td, "c%04d.png"),
                            "-c:v", "libwebp_anim", "-quality", os.environ.get("Q", "82"), "-compression_level", "6", "-loop", "0", out], check=True)
            print(out, os.path.getsize(out))


if __name__ == "__main__":
    main()
