# Profile media

The project images come from the linked repositories. They show the existing software and hardware.

| File | Source |
| --- | --- |
| `gridlab-dashboard.png` | [GridLab screenshot](https://github.com/Grkila/gridlab-ev-grid-simulator/blob/main/artifacts/handoff/showcase/demand-dashboard.png) |
| `gripper-demo.gif` | [Accelerated balloon test](https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection/blob/main/docs/images/gifs/ballone_speedup.gif) |
| `gripper-still.png` | Frame at 9 seconds from the same source GIF. |
| `airlock-testbench.png` | [Airlock simulator screenshot](https://github.com/Grkila/Airlock-Control-System-HIL-Testbench/blob/main/docs/images/UI_screenshot.png) |
| `manipulator-panel.jpg` | [LabVIEW front panel](https://github.com/Grkila/Serial-Two-Joint-Robot-Manipulator-Simulation-and-Control/blob/main/docs/images/front_panel_overview.jpeg) |
| `signal-path.svg` | Original vector diagram for this profile. The moving signal is decorative and does not show measured data. |

The GIF uses seconds 3.2 to 11.2 of the accelerated source footage. It preserves that playback speed and uses 8 frames per second, a 420-pixel width, and a 96-color palette. It plays once.

The README selects the still image when the browser requests reduced motion. The SVG also respects that preference. Its animation lasts four seconds and plays once.

To regenerate the GIF with FFmpeg, download the linked source as `gripper-source.gif`, then run:

```sh
ffmpeg -ss 3.2 -t 8 -i gripper-source.gif -filter_complex "[0:v]fps=8,scale=420:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" -loop -1 gripper-demo.gif
```
