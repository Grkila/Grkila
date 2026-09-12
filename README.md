# Hi, I'm Dušan Grković

I build embedded systems, robotics projects, and software for industrial automation. That includes firmware, custom electronics, and tools to test how they work together.

My newer projects explore EV charging simulation and AI applications. The hardware is still a big part of what I do.

[LinkedIn](https://linkedin.com/in/dusan-grkovic) · [Email](mailto:dusangrkovic2002@gmail.com) · [All repositories](https://github.com/Grkila?tab=repositories)

<img src="assets/signal-path.svg" alt="A signal path connects sensing, control, and action." width="100%" />

## Recently

I spent June to August 2026 at CERN as a summer student in industrial communications. I built and tested an OPC UA PubSub publisher for the UNICOS control framework.

The work also included a VS Code extension for PLC execution timing and a TypeScript MCP server for UNICOS specification workbooks. I analyzed 706 cooling and ventilation specifications across 20 device families to inform the publisher design.

[CERN technical report](https://repository.cern/records/b6jfa-g7j31)

I'm also studying for an M.Sc. in Computing and Control Engineering at the University of Novi Sad, which I started in December 2025.

## Selected projects

### GridLab · EV charging and grid simulation

GridLab lets you build a charging scenario, compare controllers, and inspect demand on the grid.

Our team built it for the Schneider Electric EV Days Challenge. It combines OpenStreetMap data with pandapower and includes reinforcement learning experiments. Model Context Protocol (MCP) tools connect the simulator to Codex workflows.

The network is a synthetic model of the Novi Sad grid. Its results depend on the scenario and grid assumptions.

<a href="https://github.com/Grkila/gridlab-ev-grid-simulator">
  <img src="assets/gridlab-dashboard.png" alt="GridLab results show city demand, EV charging demand, and vehicle states at a selected time." width="680" />
</a>

Python · pandapower · OpenStreetMap · Reinforcement learning · MCP

[Explore the project](https://github.com/Grkila/gridlab-ev-grid-simulator) · [Application tour](https://github.com/Grkila/gridlab-ev-grid-simulator#application-tour)

### Adaptive gripper · Detecting slip with a magnetic sensor

For my bachelor's thesis, I built a gripper that detects early slip through micro-vibrations and adjusts its grip force.

I developed the electronics, ESP32 firmware, and Python telemetry app. I also adapted the mechanical design to integrate a TLV493D magnetic sensor.

The system samples at 2 kHz and analyzes vibrations in the 40-120 Hz band. The documented minimum reaction time is about 90 ms.

<a href="https://www.youtube.com/watch?v=gOe6JvAW2Xo">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="assets/gripper-still.png" />
    <img src="assets/gripper-demo.gif" alt="The physical gripper holds a balloon while the telemetry app shows sensor signals and slip status." width="420" />
  </picture>
</a>

<sub>Excerpt from the accelerated test footage. The GIF plays once. Select the image for the full video.</sub>

ESP32 · FreeRTOS · FFT · Custom PCBs · Python · Fusion 360

[Code and hardware](https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection) · [Watch the demo](https://www.youtube.com/watch?v=gOe6JvAW2Xo) · [Test results](https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection#test-results)

### Rover control and robot simulation

| Airlock control and HIL testing | Two-joint robot manipulator |
| --- | --- |
| [![Airlock simulator with rover zones, gate states, and serial monitoring.](assets/airlock-testbench.png)](https://github.com/Grkila/Airlock-Control-System-HIL-Testbench) | [![LabVIEW panel for the robot manipulator simulation and controller settings.](assets/manipulator-panel.jpg)](https://github.com/Grkila/Serial-Two-Joint-Robot-Manipulator-Simulation-and-Control) |
| I built ESP32 firmware and a Python testbench for a three-zone rover airlock. The hardware-in-the-loop (HIL) setup emulates sensors and checks controller outputs. | I modeled a two-joint arm and compared PID, fuzzy PID, and sliding-mode control. The project includes a Python hand-tracking interface that sends commands to LabVIEW over UDP. |
| C++ · ESP32 · Python · HIL | LabVIEW · Python · MediaPipe · Control systems |
| [Code and testbench](https://github.com/Grkila/Airlock-Control-System-HIL-Testbench) | [Code and documentation](https://github.com/Grkila/Serial-Two-Joint-Robot-Manipulator-Simulation-and-Control) |

I led NSpace's embedded software and robotics sub-team for ERC 2025. We placed seventh out of 25 teams in the Remote Formula.

The rover work also included a [Docker environment for ROS 2 and Gazebo](https://github.com/Grkila/Husarion-panther-sim-setup) and cloud deployment of NVIDIA Isaac Sim.

## AI applications

- **[SilverOne](https://github.com/Grkila/gdg-accessibility-agent):** An Android assistant for voice and text control. It uses Gemini Live, a deterministic tool dispatcher, and fallback paths when services fail. Java · Android · Gemini Live · Firebase.
- **[Intro Path Discovery](https://github.com/Grkila/Intro-Path-Discovery):** An application that finds and ranks introduction paths through LinkedIn connection data. It combines language agents with explicit scoring rules. Python · LangGraph · Streamlit · SQLite.

Both links point to forks of shared projects. Their repositories contain the source and upstream history.

## More projects

| Project | What it does |
| --- | --- |
| [SCADA application](https://github.com/Grkila/SCADA-Industrial-Automation-Assignment) | Academic C# and WPF application with simulated PLC data, alarms, and SQL-backed history. |
| [Siemens S7 programming](https://github.com/Grkila/Siemens-S7-Practical-Programming-Projects) | S7-1200 exercises in TIA Portal, with project files and lab documentation. |
| [Modbus ASCII on 8051](https://github.com/Grkila/MODBUS-for-intel-8051-microcontroller) | Bare-metal C implementation with UART interrupts, LRC checks, and read/write operations on coils and registers. |
| [Differential Motion Analyzer](https://github.com/Grkila/Differential-Motion-Analyzer) | PyQt6 and OpenCV desktop app with motion detection, region selection, and annotated video export. |

<details>
<summary>Earlier work in data analysis</summary>

- [Diabetes prediction](https://github.com/Grkila/Diabetes-prediction-using-machine-learning): data preparation, ensemble models, and classification evaluation.
- [Financial indicator analysis](https://github.com/Grkila/Stock-price-prediction): MATLAB scripts that prepare technical indicators and features from market data.

</details>

## Tools I use

| Area | Tools and methods |
| --- | --- |
| Embedded systems | C/C++, ESP32, STM32, FreeRTOS, I2C/SPI/UART, Altium Designer |
| Industrial automation | Siemens S7, TIA Portal, UNICOS-CPC, OPC UA PubSub, SCADA, C#/WPF |
| Robotics and control | LabVIEW, MATLAB/Simulink, ROS 2, Gazebo, Isaac Sim, PID, fuzzy control, sliding-mode control |
| Software and testing | Python, TypeScript, Git, Docker, Linux, OpenCV, HIL and SIL testing |

## A little background

I graduated from the University of Novi Sad in December 2025 with a B.Sc. with Honours in Electrical and Computer Engineering. My GPA was 9.11/10.

My department nominated my gripper thesis for Matica srpska's Pupin Award. I also received the Dositeja Scholarship.

Other highlights include first place at the 2025 EESTech Challenge local round and the 2023 Origin Case Study. Outside technical projects, I led the EESTEC LC Novi Sad HR team and helped organize its events.

If you're working on robotics, controls, or a related project, [send me an email](mailto:dusangrkovic2002@gmail.com).
