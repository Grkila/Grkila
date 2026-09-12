# Hi, I'm Dušan Grković

I'm an electrical and computer engineer who works across embedded systems, robotics, and industrial automation. I build firmware and electronics, then develop the software to measure, test, and control them.

My projects range from a magnetic slip-sensing gripper to EV charging simulations and AI applications. I like work where software has a clear connection to the physical system.

At CERN, I spent June to August 2026 building an OPC UA PubSub publisher, PLC timing tools, and a UNICOS workbook MCP server. My [CERN technical report](https://repository.cern/records/b6jfa-g7j31) covers the publisher.

I'm now studying for an M.Sc. in Computing and Control Engineering at the University of Novi Sad.

<p>
<a href="https://linkedin.com/in/dusan-grkovic"><img src="assets/button-linkedin.svg" alt="LinkedIn" height="38" /></a>
<a href="mailto:dusangrkovic2002@gmail.com"><img src="assets/button-email.svg" alt="Email" height="38" /></a>
<a href="https://github.com/Grkila?tab=repositories"><img src="assets/button-github.svg" alt="GitHub repositories" height="38" /></a>
</p>

<img src="assets/engineering-four-panels.svg" alt="Animated robotics, PLC scanning, microcontroller signals, and an LLM network." width="100%" />

<details>
<summary><strong>Show more: technologies and tools I use</strong></summary>

These cover my independent builds, team projects, and university coursework.

| Area | Technologies and tools |
| --- | --- |
| Languages | C, C++, Python, TypeScript, Java, C#, MATLAB, Bash, VHDL, SCL, Ladder Logic |
| Embedded systems | ESP32, STM32, AT89C51RC2 / 8051, FPGA, FreeRTOS, interrupts, GPIO, PWM, ADC/DAC, bare-metal firmware |
| Industrial automation | Siemens S7-1200 / S7-1500, TIA Portal, WinCC, UNICOS-CPC / UCPC, PLC programming, SCADA |
| Control and simulation | PID, fuzzy PID, sliding-mode control, MATLAB/Simulink, LabVIEW, real-time control, system modeling, FFT, signal filtering |
| Robotics | ROS 2 Jazzy, Gazebo, NVIDIA Isaac Sim, NI sbRIO / cRIO, sensor fusion, IMU-based heading control, FOC BLDC drives |
| Communications | OPC UA PubSub / UADP, Modbus ASCII, CAN, MQTT, Ethernet, TCP/IP, UDP, Wi-Fi, Bluetooth, ESP-NOW, UART, SPI, I2C |
| Testing and measurement | HIL, SIL, Python test automation, data acquisition, live telemetry, data logging, PLC timing, JTAG, oscilloscopes, logic analyzers, Wireshark / Tshark |
| Electronics and mechanical design | Altium Designer, PCB design, LTspice, Fusion 360, AutoCAD, CAD, FDM 3D printing |
| Computer vision and data | OpenCV, MediaPipe, NumPy, Pandas, scikit-learn, Matplotlib, Seaborn, PyQt6 |
| AI and simulation projects | LangGraph, Gemini Live, MCP, Streamlit, pandapower, OpenStreetMap, Gymnasium, Stable-Baselines3, PyTorch |
| Applications and storage | WPF, MVVM, Entity Framework, SQL Server / LocalDB, SQLite, Firebase |
| Development tools | Git, GitLab, SVN, Docker, Linux, VS Code, VS Code extensions, Keil uVision, Arduino tooling, Android Studio, Quartus Prime, cloud deployment |

</details>

## Project showcase

<table>
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/gridlab-ev-grid-simulator">GridLab</a></h3>
<a href="https://github.com/Grkila/gridlab-ev-grid-simulator"><img src="assets/gridlab-dashboard.png" alt="GridLab project preview" width="420" /></a>
<p>EV charging scenarios, controller comparisons, and reinforcement learning on a synthetic Novi Sad grid. Built with our EV Days team.</p>
<p><sub>Python · pandapower · MCP</sub></p>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection">Adaptive gripper</a></h3>
<a href="https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection"><picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/gripper-still.png" /><img src="assets/gripper-demo.gif" alt="Adaptive gripper project preview" width="420" /></picture></a>
<p>My thesis: magnetic slip sensing, custom electronics, and ESP32 firmware. About 90 ms minimum reaction time.</p>
<p><sub>ESP32 · FreeRTOS · FFT</sub></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/Airlock-Control-System-HIL-Testbench">Airlock testbench</a></h3>
<a href="https://github.com/Grkila/Airlock-Control-System-HIL-Testbench"><img src="assets/airlock-testbench.png" alt="Airlock testbench project preview" width="420" /></a>
<p>Rover airlock firmware with a Python simulator and hardware-in-the-loop validation. Part of my NSpace work.</p>
<p><sub>C++ · ESP32 · Python</sub></p>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/Serial-Two-Joint-Robot-Manipulator-Simulation-and-Control">Robot manipulator</a></h3>
<a href="https://github.com/Grkila/Serial-Two-Joint-Robot-Manipulator-Simulation-and-Control"><img src="assets/manipulator-panel.jpg" alt="Robot manipulator project preview" width="420" /></a>
<p>A two-joint robot simulation with PID, fuzzy PID, sliding-mode control, and hand-tracking input.</p>
<p><sub>LabVIEW · Python · MediaPipe</sub></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/SCADA-Industrial-Automation-Assignment">SCADA application</a></h3>
<a href="https://github.com/Grkila/SCADA-Industrial-Automation-Assignment"><img src="assets/scada-monitor.png" alt="SCADA application project preview" width="420" /></a>
<p>An academic monitoring application with simulated PLC data, configurable alarms, and recorded history.</p>
<p><sub>C# · WPF · SQL</sub></p>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/Differential-Motion-Analyzer">Motion Analyzer</a></h3>
<a href="https://github.com/Grkila/Differential-Motion-Analyzer"><img src="assets/motion-analyzer.png" alt="Motion Analyzer project preview" width="420" /></a>
<p>Desktop video analysis with motion detection, adjustable regions, and annotated video export.</p>
<p><sub>Python · OpenCV · PyQt6</sub></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/gdg-accessibility-agent">SilverOne</a></h3>
<a href="https://github.com/Grkila/gdg-accessibility-agent"><img src="assets/silverone-flow.svg" alt="SilverOne project preview" width="420" /></a>
<p>Shared Android assistant project with voice input, device actions, and service fallbacks.</p>
<p><sub>Java · Gemini Live · Firebase</sub></p>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/Grkila/Intro-Path-Discovery">Intro Path Discovery</a></h3>
<a href="https://github.com/Grkila/Intro-Path-Discovery"><img src="assets/intro-paths.svg" alt="Intro Path Discovery project preview" width="420" /></a>
<p>Shared AI project that finds introduction paths through connection data and ranks them with explicit scoring rules.</p>
<p><sub>Python · LangGraph · Streamlit</sub></p>
</td>
</tr>
</table>

<sub>The gripper preview uses accelerated test footage. The two AI previews are concept diagrams. Select any card for code and project details.</sub>

### More projects

<p>
<a href="https://github.com/Grkila/Siemens-S7-Practical-Programming-Projects"><img src="assets/project-siemens.svg" alt="Siemens S7: PLC programming · TIA Portal" width="270" height="68" /></a>
<a href="https://github.com/Grkila/MODBUS-for-intel-8051-microcontroller"><img src="assets/project-modbus.svg" alt="Modbus on 8051: Serial communication · Modbus ASCII" width="270" height="68" /></a>
<a href="https://github.com/Grkila/Husarion-panther-sim-setup"><img src="assets/project-ros.svg" alt="Panther simulation: ROS 2 setup · Docker" width="270" height="68" /></a>
<a href="https://github.com/Grkila/Stock-price-prediction"><img src="assets/project-stock.svg" alt="Stock indicators: MATLAB · Time-series features" width="270" height="68" /></a>
<a href="https://github.com/Grkila/Diabetes-prediction-using-machine-learning"><img src="assets/project-diabetes.svg" alt="Diabetes classification: Python · Ensemble model experiments" width="270" height="68" /></a>
<a href="https://github.com/Grkila/husarion_ws"><img src="assets/project-husarion.svg" alt="Husarion workspace: ROS 2 · Controllers and Gazebo" width="270" height="68" /></a>
</p>

## A bit about me

I led NSpace's embedded and robotics sub-team at ERC 2025, where we placed seventh in the Remote Formula.

My gripper thesis received a departmental nomination for the Pupin Award. I also received the Dositeja Scholarship.
