# Profile media

The project images come from the linked repositories. They show the existing software and hardware.

| File | Source |
| --- | --- |
| `gridlab-dashboard.png` | [GridLab screenshot](https://github.com/Grkila/gridlab-ev-grid-simulator/blob/main/artifacts/handoff/showcase/demand-dashboard.png) |
| `gripper-demo.gif` | [Accelerated balloon test](https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection/blob/main/docs/images/gifs/ballone_speedup.gif) |
| `gripper-still.png` | Frame at 9 seconds from the same source GIF. |
| `airlock-testbench.png` | [Airlock simulator screenshot](https://github.com/Grkila/Airlock-Control-System-HIL-Testbench/blob/main/docs/images/UI_screenshot.png) |
| `manipulator-panel.jpg` | [LabVIEW front panel](https://github.com/Grkila/Serial-Two-Joint-Robot-Manipulator-Simulation-and-Control/blob/main/docs/images/front_panel_overview.jpeg) |
| `scada-monitor.png` | [SCADA monitoring screenshot](https://github.com/Grkila/SCADA-Industrial-Automation-Assignment/blob/master/Screenshots/Monitor-tab.png) |
| `motion-analyzer.png` | [Motion analysis screenshot](https://github.com/Grkila/Differential-Motion-Analyzer/blob/main/screenshots/3_detection_in_progress_using_camera.png) |
| `engineering-banner.svg` | Original animated robot arm and signal trace. The illustration does not show measured data. |
| `silverone-flow.svg` | Original concept diagram of voice input and device actions. It is not an application screenshot. |
| `intro-paths.svg` | Original concept diagram of ranked introduction paths. It is not an application screenshot. |

The GIF uses seconds 3.2 to 11.2 of the accelerated source footage. It preserves that playback speed and uses 8 frames per second, a 420-pixel width, and a 96-color palette. It pauses for three seconds before each repeat. Screenshots are scaled to fit a 480-by-270 frame, with padding that preserves their proportions.

The README selects the still image when the browser requests reduced motion. All three SVGs disable their CSS animations for that preference. The header uses a slow 12-second movement cycle. The two concept diagrams use small, local movements.

To regenerate the GIF with FFmpeg, download the linked source as `gripper-source.gif`, then run:

```sh
ffmpeg -ss 3.2 -t 8 -i gripper-source.gif -filter_complex "[0:v]fps=8,scale=420:-1:flags=lanczos,tpad=stop_mode=clone:stop_duration=3,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" -loop 0 gripper-demo.gif
```

## Design references

The following READMEs informed the choice of a compact gallery and self-contained SVG motion. The profile's SVG artwork is original.

- [Navi's animated profile](https://github.com/navi3582/animated-github-profile): animation contained in repository SVG files.
- [Neon Pulse Banner](https://github.com/beydemirfurkan/awesome-github-profile/tree/main/templates/02-animated/neon-pulse-banner): a slow animated header as the main visual element.
- [Awesome GitHub Profile](https://github.com/beydemirfurkan/awesome-github-profile): compact layouts and project-focused examples.
