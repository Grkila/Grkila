import * as THREE from "three";
const P = new URLSearchParams(location.search);
const W = +(P.get("w") || 1920), H = +(P.get("h") || 600);
const FPS = +(P.get("fps") || 15);
const SAVE = P.get("save") === "1";
const canvas = document.createElement("canvas");
const C = { bg: 0x0a1118, floor: 0x0c151d, steel: 0xc6d0da, dark: 0x1a2632, teal: 0x79c8cb, amber: 0xf0b35a };
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.setClearColor(C.bg);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(C.bg, 11, 26);


// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0x9fb8cc, 0x0a1118, 0.75));
const key = new THREE.DirectionalLight(0xffffff, 2.1);
key.position.set(4, 9, 5);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
key.shadow.camera.left = -6; key.shadow.camera.right = 6;
key.shadow.camera.top = 6; key.shadow.camera.bottom = -6;
key.shadow.radius = 4;
scene.add(key);
const rim = new THREE.PointLight(C.teal, 18, 14, 2);
rim.position.set(-4, 3.5, -3);
scene.add(rim);
const warm = new THREE.PointLight(C.amber, 6, 8, 2);
warm.position.set(3, 1, 3);
scene.add(warm);

// ---------- materials ----------
const mSteel = new THREE.MeshStandardMaterial({ color: C.steel, metalness: 0.55, roughness: 0.32 });
const mDark = new THREE.MeshStandardMaterial({ color: C.dark, metalness: 0.4, roughness: 0.55 });
const mJoint = new THREE.MeshStandardMaterial({ color: C.amber, metalness: 0.3, roughness: 0.4, emissive: C.amber, emissiveIntensity: 0.15 });
const mLed = new THREE.MeshBasicMaterial({ color: C.teal });
const mGlow = new THREE.MeshBasicMaterial({ color: C.teal, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false });

function mesh(geo, mat, shadow = true) {
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = shadow;
  m.receiveShadow = shadow;
  return m;
}

// ---------- floor: PCB traces with travelling signal pulses ----------
const floor = mesh(new THREE.CircleGeometry(26, 64), new THREE.MeshStandardMaterial({ color: C.floor, roughness: 0.9, metalness: 0.1 }));
floor.rotation.x = -Math.PI / 2;
floor.castShadow = false;
scene.add(floor);

const grid = new THREE.GridHelper(40, 80, 0x1a2a38, 0x13202b);
grid.position.y = 0.002;
scene.add(grid);

// Seeded random so the board looks identical on every load.
let seed = 7;
const rand = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

const traces = [];
const tracePts = [];
const viaGeo = new THREE.RingGeometry(0.05, 0.085, 16);
const viaMat = new THREE.MeshBasicMaterial({ color: C.teal, transparent: true, opacity: 0.55 });
for (let i = 0; i < 34; i++) {
  const a = (i / 34) * Math.PI * 2 + rand() * 0.08;
  const r0 = 1.25 + rand() * 0.2;
  const p = [new THREE.Vector3(Math.cos(a) * r0, 0.01, Math.sin(a) * r0)];
  let dir = a;
  let pos = p[0].clone();
  const segs = 2 + Math.floor(rand() * 3);
  for (let s = 0; s < segs; s++) {
    const len = 0.8 + rand() * 2.6;
    pos = pos.clone().add(new THREE.Vector3(Math.cos(dir) * len, 0, Math.sin(dir) * len));
    p.push(pos);
    dir += (rand() < 0.5 ? -1 : 1) * Math.PI / 4;
  }
  traces.push(p);
  for (let s = 0; s < p.length - 1; s++) tracePts.push(p[s], p[s + 1]);
  const via = new THREE.Mesh(viaGeo, viaMat);
  via.rotation.x = -Math.PI / 2;
  via.position.copy(pos).setY(0.012);
  scene.add(via);
}
const traceLines = new THREE.LineSegments(
  new THREE.BufferGeometry().setFromPoints(tracePts),
  new THREE.LineBasicMaterial({ color: C.teal, transparent: true, opacity: 0.22 })
);
scene.add(traceLines);

// Arc-length tables so pulses move at constant speed along each trace.
const traceInfo = traces.map((pts) => {
  const lens = [0];
  for (let i = 1; i < pts.length; i++) lens.push(lens[i - 1] + pts[i].distanceTo(pts[i - 1]));
  return { pts, lens, total: lens[lens.length - 1] };
});
function pointOn(info, d, out) {
  let i = 1;
  while (i < info.lens.length - 1 && info.lens[i] < d) i++;
  const t = (d - info.lens[i - 1]) / (info.lens[i] - info.lens[i - 1]);
  return out.lerpVectors(info.pts[i - 1], info.pts[i], THREE.MathUtils.clamp(t, 0, 1));
}

const pulseGeo = new THREE.SphereGeometry(0.045, 10, 10);
const pulses = [];
for (let i = 0; i < 26; i++) {
  const m = new THREE.Mesh(pulseGeo, mGlow);
  const halo = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 10),
    new THREE.MeshBasicMaterial({ color: C.teal, transparent: true, opacity: 0.18, blending: THREE.AdditiveBlending, depthWrite: false }));
  m.add(halo);
  scene.add(m);
  pulses.push({ m, info: traceInfo[Math.floor(rand() * traceInfo.length)], ph: rand(), k: 1 + Math.floor(rand() * 2) });
}

// Scan ring that expands from the base, like a PLC scan cycle.
const scanRing = new THREE.Mesh(
  new THREE.RingGeometry(0.98, 1.0, 96),
  new THREE.MeshBasicMaterial({ color: C.teal, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })
);
scanRing.rotation.x = -Math.PI / 2;
scanRing.position.y = 0.015;
scene.add(scanRing);

// ---------- arm ----------
const L1 = 2.2;      // upper arm
const L2 = 1.8;      // forearm
const TOOL = 0.62;   // wrist axis to fingertip centre
const SHOULDER_Y = 1.05;

const arm = new THREE.Group();
scene.add(arm);

const base = mesh(new THREE.CylinderGeometry(0.85, 0.95, 0.3, 48), mDark);
base.position.y = 0.15;
arm.add(base);
const baseRing = new THREE.Mesh(new THREE.TorusGeometry(0.86, 0.018, 8, 64), mLed);
baseRing.rotation.x = Math.PI / 2;
baseRing.position.y = 0.3;
arm.add(baseRing);

const yaw = new THREE.Group();
yaw.position.y = 0.3;
arm.add(yaw);
const turret = mesh(new THREE.CylinderGeometry(0.5, 0.58, 0.55, 40), mSteel);
turret.position.y = 0.275;
yaw.add(turret);

function jointDisc(r, w) {
  const g = new THREE.Group();
  const drum = mesh(new THREE.CylinderGeometry(r, r, w, 32), mJoint);
  drum.rotation.x = Math.PI / 2;
  g.add(drum);
  const cap = new THREE.Mesh(new THREE.TorusGeometry(r * 0.62, 0.014, 6, 32), mLed);
  cap.position.z = w / 2 + 0.002;
  g.add(cap);
  const cap2 = cap.clone();
  cap2.position.z = -cap.position.z;
  g.add(cap2);
  return g;
}

function link(len, w, d) {
  // Tapered link built from a box plus a dark spine inlay.
  const g = new THREE.Group();
  const body = mesh(new THREE.BoxGeometry(w, len, d), mSteel);
  body.position.y = len / 2;
  g.add(body);
  const spine = mesh(new THREE.BoxGeometry(w * 0.35, len * 0.72, d + 0.02), mDark);
  spine.position.y = len / 2;
  g.add(spine);
  return g;
}

const shoulder = new THREE.Group();
shoulder.position.y = SHOULDER_Y - 0.3;
yaw.add(shoulder);
shoulder.add(jointDisc(0.32, 0.62));
shoulder.add(link(L1, 0.34, 0.38));

const elbow = new THREE.Group();
elbow.position.y = L1;
shoulder.add(elbow);
elbow.add(jointDisc(0.25, 0.5));
elbow.add(link(L2, 0.26, 0.3));

const wrist = new THREE.Group();
wrist.position.y = L2;
elbow.add(wrist);
wrist.add(jointDisc(0.17, 0.4));
const palm = mesh(new THREE.BoxGeometry(0.22, 0.22, 0.62), mDark);
palm.position.y = 0.2;
wrist.add(palm);
const fingerGeo = new THREE.BoxGeometry(0.12, 0.42, 0.07);
const fingerL = mesh(fingerGeo, mSteel);
const fingerR = mesh(fingerGeo, mSteel);
fingerL.position.y = fingerR.position.y = 0.5;
wrist.add(fingerL, fingerR);
const tipLed = new THREE.Mesh(new THREE.SphereGeometry(0.035, 10, 10), new THREE.MeshBasicMaterial({ color: C.amber }));
tipLed.position.set(0.12, 0.2, 0);
wrist.add(tipLed);
const tip = new THREE.Object3D();
tip.position.y = TOOL;
wrist.add(tip);

// ---------- stations and payload ----------
const CUBE = 0.46;
const PED_H = 0.62;
const PICK_H = PED_H + CUBE / 2;     // fingertip height when gripping
const LIFT_H = PICK_H + 1.15;
const REACH = 2.9;
const stations = [THREE.MathUtils.degToRad(-38), THREE.MathUtils.degToRad(62)];

function polar(psi, r, y) { return new THREE.Vector3(Math.cos(psi) * r, y, -Math.sin(psi) * r); }

for (const psi of stations) {
  const ped = mesh(new THREE.CylinderGeometry(0.42, 0.48, PED_H, 32), mDark);
  ped.position.copy(polar(psi, REACH, PED_H / 2));
  scene.add(ped);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.43, 0.012, 6, 48), mLed);
  ring.rotation.x = Math.PI / 2;
  ring.position.copy(polar(psi, REACH, PED_H + 0.002));
  scene.add(ring);
}

const cube = new THREE.Group();
const cubeBody = mesh(new THREE.BoxGeometry(CUBE, CUBE, CUBE), new THREE.MeshStandardMaterial({ color: 0x22313f, metalness: 0.2, roughness: 0.5 }));
cube.add(cubeBody);
cube.add(new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(CUBE + 0.005, CUBE + 0.005, CUBE + 0.005)),
  new THREE.LineBasicMaterial({ color: C.amber })));
const chipDot = new THREE.Mesh(new THREE.CircleGeometry(0.06, 16), new THREE.MeshBasicMaterial({ color: C.amber }));
chipDot.rotation.x = -Math.PI / 2;
chipDot.position.y = CUBE / 2 + 0.003;
cube.add(chipDot);
scene.add(cube);

// ---------- inverse kinematics ----------
// Solves yaw, shoulder, elbow, wrist for a fingertip at (psi, r, y) with the
// gripper pointing straight down. Angles are measured from vertical.
const q = { psi: 0, a1: 0, a2: 0, a3: 0 };
function solveIK(psi, r, y) {
  const wx = r, wz = y + TOOL - SHOULDER_Y;
  const D = Math.min(Math.hypot(wx, wz), L1 + L2 - 1e-3);
  const alpha = Math.atan2(wx, wz);
  const beta = Math.acos((L1 * L1 + D * D - L2 * L2) / (2 * L1 * D));
  const gamma = Math.acos((L1 * L1 + L2 * L2 - D * D) / (2 * L1 * L2));
  q.psi = psi;
  q.a1 = alpha - beta;          // elbow-up branch
  q.a2 = Math.PI - gamma;
  q.a3 = Math.PI - q.a1 - q.a2; // keep the tool vertical
  yaw.rotation.y = q.psi;
  shoulder.rotation.z = -q.a1;
  elbow.rotation.z = -q.a2;
  wrist.rotation.z = -q.a3;
}

function setGrip(g) {
  // g: 0 open, 1 closed on the payload
  const open = 0.42, closed = CUBE / 2 + 0.035;
  const z = THREE.MathUtils.lerp(open, closed, g);
  fingerL.position.z = z;
  fingerR.position.z = -z;
}

// ---------- motion program ----------
// Each step: [duration s, psi, r, y, grip, carrying]
function program(from, to) {
  const A = stations[from], B = stations[to];
  return [
    [1.2, A, REACH, LIFT_H, 0, false],
    [0.9, A, REACH, PICK_H, 0, false],
    [0.45, A, REACH, PICK_H, 1, false],
    [0.9, A, REACH, LIFT_H, 1, true],
    [1.8, B, REACH, LIFT_H, 1, true],
    [0.9, B, REACH, PICK_H, 1, true],
    [0.45, B, REACH, PICK_H, 0, false],
    [0.9, B, REACH, LIFT_H, 0, false],
    [1.1, (A + B) / 2, REACH - 0.9, LIFT_H + 0.5, 0, false],
  ];
}
const cycle = [...program(0, 1), ...program(1, 0)];
const SPEED = 1.25;
for (const st of cycle) st[0] /= SPEED;
const cycleLen = cycle.reduce((s, st) => s + st[0], 0);
const ease = (t) => t * t * (3 - 2 * t);

const cubeAt = [polar(stations[0], REACH, PICK_H), polar(stations[1], REACH, PICK_H)];
let cubeHome = 0;
cube.position.copy(cubeAt[0]);
const tipWorld = new THREE.Vector3();


function pose(t) {
  t %= cycleLen;
  let i = 0, start = 0;
  while (t > start + cycle[i][0]) { start += cycle[i][0]; i++; }
  const cur = cycle[i];
  const prev = cycle[(i - 1 + cycle.length) % cycle.length];
  const k = ease((t - start) / cur[0]);
  const psi = THREE.MathUtils.lerp(prev[1], cur[1], k);
  const r = THREE.MathUtils.lerp(prev[2], cur[2], k);
  const y = THREE.MathUtils.lerp(prev[3], cur[3], k);
  const g = THREE.MathUtils.lerp(prev[4], cur[4], k);
  solveIK(psi, r, y);
  setGrip(g);

  const carrying = cur[5];
  if (carrying) {
    tip.getWorldPosition(tipWorld);
    cube.position.copy(tipWorld);
    cube.rotation.y = psi;
    cubeHome = cur[1] === stations[0] ? 0 : 1;
  } else if (prev[5] && !carrying) {
    cubeHome = Math.abs(psi - stations[1]) < Math.abs(psi - stations[0]) ? 1 : 0;
    cube.position.copy(cubeAt[cubeHome]);
  }
  return g;
}



// ---------- four domains around the arm ----------
// Robotics = the arm itself; industrial automation = a PLC rack;
// embedded = a microcontroller on the board; AI = a floating LLM graph.
const D = { robo: 0xf0b35a, auto: 0x6aa8ff, emb: 0x7fd38a, ai: 0xb9a2ff };
traceLines.material.color.set(D.emb);
viaMat.color.set(D.emb);
for (const p of pulses) { p.m.material = new THREE.MeshBasicMaterial({ color: D.emb, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false }); p.m.children[0].material.color.set(D.emb); }
scanRing.material.color.set(D.emb);

const PLC_POS = polar(THREE.MathUtils.degToRad(158), 3.9, 0);
const CHIP_POS = polar(THREE.MathUtils.degToRad(-100), 2.7, 0);
const LLM_POS = polar(THREE.MathUtils.degToRad(12), 4.6, 3.0);

// PLC rack: cabinet, DIN rail, CPU plus I/O modules with status LEDs.
const plc = new THREE.Group();
const cab = mesh(new THREE.BoxGeometry(2.5, 1.75, 0.75), mDark);
cab.position.y = 0.875;
plc.add(cab);
const rail = mesh(new THREE.BoxGeometry(2.3, 0.07, 0.05), mSteel);
rail.position.set(0, 0.95, 0.4);
plc.add(rail);
const mModule = new THREE.MeshStandardMaterial({ color: 0xcfd7df, metalness: 0.15, roughness: 0.55 });
const mCpu = new THREE.MeshStandardMaterial({ color: 0x24384a, metalness: 0.3, roughness: 0.5 });
const plcLeds = [];
for (let i = 0; i < 7; i++) {
  const mod = mesh(new THREE.BoxGeometry(i === 0 ? 0.44 : 0.26, 1.2, 0.14), i === 0 ? mCpu : mModule);
  const x = i === 0 ? -0.9 : -0.6 + i * 0.3;
  mod.position.set(x, 0.95, 0.47);
  plc.add(mod);
  const n = i === 0 ? 2 : 4;
  for (let k = 0; k < n; k++) {
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.032, 8, 8), new THREE.MeshBasicMaterial({ color: k % 2 ? D.emb : D.auto }));
    led.position.set(x + (i === 0 ? -0.1 : 0), 1.4 - k * 0.11, 0.55);
    plc.add(led);
    plcLeds.push({ led, ph: rand(), k: 2 + Math.floor(rand() * 5), on: k % 2 ? D.emb : D.auto });
  }
}
const plcGlow = new THREE.PointLight(D.auto, 4, 4, 2);
plcGlow.position.set(0, 1.2, 1.2);
plc.add(plcGlow);
plc.position.copy(PLC_POS);
plc.lookAt(0, 0, 0);
scene.add(plc);

// Microcontroller: QFP package with pins and a printed top.
const chip = new THREE.Group();
const chipBody = mesh(new THREE.BoxGeometry(1.25, 0.16, 1.25), new THREE.MeshStandardMaterial({ color: 0x141d26, roughness: 0.6, metalness: 0.2 }));
chipBody.position.y = 0.1;
chip.add(chipBody);
const pinGeo = new THREE.BoxGeometry(0.05, 0.03, 0.2);
for (let side = 0; side < 4; side++) {
  for (let j = 0; j < 9; j++) {
    const pin = mesh(pinGeo, mSteel, false);
    const off = -0.48 + j * 0.12;
    const a = (side * Math.PI) / 2;
    pin.position.set(Math.cos(a) * 0.72 - Math.sin(a) * off, 0.03, Math.sin(a) * 0.72 + Math.cos(a) * off);
    pin.rotation.y = -a + Math.PI / 2;
    chip.add(pin);
  }
}
const chipTex = (() => {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d");
  g.fillStyle = "#141d26"; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = "#7fd38a"; g.globalAlpha = 0.5; g.lineWidth = 3; g.strokeRect(34, 34, 188, 188);
  g.globalAlpha = 1; g.fillStyle = "#7fd38a";
  g.beginPath(); g.arc(58, 58, 9, 0, Math.PI * 2); g.fill();
  g.font = "600 54px 'IBM Plex Mono'"; g.textAlign = "center"; g.fillText("MCU", 128, 148);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
})();
const chipTop = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.2), new THREE.MeshBasicMaterial({ map: chipTex }));
chipTop.rotation.x = -Math.PI / 2;
chipTop.position.y = 0.181;
chip.add(chipTop);
chip.position.copy(CHIP_POS);
chip.rotation.y = THREE.MathUtils.degToRad(-100 + 90);
scene.add(chip);

// Copper buses: chip -> arm base, PLC -> arm base, chip -> PLC.
function bus(a, b, mid) {
  const pts = [a.clone().setY(0.02), mid.clone().setY(0.02), b.clone().setY(0.02)];
  const lens = [0, pts[0].distanceTo(pts[1])];
  lens.push(lens[1] + pts[1].distanceTo(pts[2]));
  return { pts, lens, total: lens[2] };
}
const baseEdge = (p) => p.clone().setY(0).normalize().multiplyScalar(1.0);
const buses = [
  { info: bus(CHIP_POS, baseEdge(CHIP_POS), new THREE.Vector3(CHIP_POS.x, 0, baseEdge(CHIP_POS).z)), col: D.emb },
  { info: bus(PLC_POS, baseEdge(PLC_POS), new THREE.Vector3(baseEdge(PLC_POS).x, 0, PLC_POS.z)), col: D.auto },
  { info: bus(CHIP_POS, PLC_POS, new THREE.Vector3(PLC_POS.x, 0, CHIP_POS.z)), col: D.emb },
];
const busPulses = [];
for (const b of buses) {
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(b.info.pts), new THREE.LineBasicMaterial({ color: b.col, transparent: true, opacity: 0.55 })));
  for (let i = 0; i < 3; i++) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.06, 10, 10), new THREE.MeshBasicMaterial({ color: b.col, blending: THREE.AdditiveBlending, transparent: true }));
    scene.add(m);
    busPulses.push({ m, info: b.info, ph: i / 3, k: 2 });
  }
}

// LLM: nodes on a sphere, nearest-neighbour edges, glowing core.
const llm = new THREE.Group();
const nodePos = [];
const NN = 18;
for (let i = 0; i < NN; i++) {
  const y = 1 - (2 * (i + 0.5)) / NN, r = Math.sqrt(1 - y * y), th = i * 2.39996;
  nodePos.push(new THREE.Vector3(Math.cos(th) * r, y, Math.sin(th) * r).multiplyScalar(0.95));
}
const edgePts = [];
const edges = [];
nodePos.forEach((p, i) => {
  nodePos.map((q, j) => [j, p.distanceTo(q)]).filter(([j]) => j > i).sort((a, b) => a[1] - b[1]).slice(0, 3)
    .forEach(([j]) => { edgePts.push(p, nodePos[j]); edges.push([p, nodePos[j]]); });
});
llm.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(edgePts), new THREE.LineBasicMaterial({ color: D.ai, transparent: true, opacity: 0.45 })));
const llmNodes = nodePos.map((p, i) => {
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.065, 10, 10), new THREE.MeshBasicMaterial({ color: D.ai }));
  m.position.copy(p);
  llm.add(m);
  return { m, ph: rand() };
});
const core = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 1), new THREE.MeshBasicMaterial({ color: D.ai, wireframe: true, transparent: true, opacity: 0.8 }));
llm.add(core);
const coreGlow = new THREE.Mesh(new THREE.SphereGeometry(0.42, 16, 16), new THREE.MeshBasicMaterial({ color: D.ai, transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false }));
llm.add(coreGlow);
const tokens = [];
for (let i = 0; i < 8; i++) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.045, 8, 8), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  llm.add(m);
  tokens.push({ m, e: edges[Math.floor(rand() * edges.length)], ph: rand() });
}
llm.position.copy(LLM_POS);
scene.add(llm);
const llmLight = new THREE.PointLight(D.ai, 5, 6, 2);
llmLight.position.copy(LLM_POS);
scene.add(llmLight);

// Arcs from the LLM down to the PLC and the arm turret.
const arcs = [PLC_POS.clone().setY(1.9), new THREE.Vector3(0, 1.15, 0)].map((end) => {
  const mid = LLM_POS.clone().lerp(end, 0.5).add(new THREE.Vector3(0, 0.9, 0));
  const curve = new THREE.QuadraticBezierCurve3(LLM_POS.clone(), mid, end);
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(40)),
    new THREE.LineDashedMaterial({ color: D.ai, dashSize: 0.12, gapSize: 0.1, transparent: true, opacity: 0.6 }));
  line.computeLineDistances();
  scene.add(line);
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 10), new THREE.MeshBasicMaterial({ color: D.ai }));
  scene.add(m);
  return { curve, m };
});

// Arm joints keep the robotics colour.
mJoint.color.set(D.robo);
mJoint.emissive.set(D.robo);

const tv = new THREE.Vector3();
function updateDomains(t, T) {
  const u = t / T;
  for (const p of busPulses) p.m.position.copy(pointOn(p.info, ((p.ph + p.k * u) % 1) * p.info.total, tv)).setY(0.06);
  for (const l of plcLeds) {
    const on = Math.sin(2 * Math.PI * (l.k * u + l.ph)) > -0.2;
    l.led.material.color.set(on ? l.on : 0x1b2733);
  }
  llm.rotation.y = 2 * Math.PI * u;
  llm.rotation.x = 0.25 * Math.sin(2 * Math.PI * u);
  core.rotation.y = -4 * Math.PI * u;
  coreGlow.material.opacity = 0.1 + 0.08 * Math.sin(2 * Math.PI * 4 * u);
  for (const n of llmNodes) n.m.scale.setScalar(0.8 + 0.5 * Math.max(0, Math.sin(2 * Math.PI * (3 * u + n.ph))));
  for (const k of tokens) k.m.position.lerpVectors(k.e[0], k.e[1], (k.ph + 3 * u) % 1);
  arcs.forEach((a, i) => a.curve.getPoint((i * 0.5 + 2 * u) % 1, a.m.position));
}

// ---------- capture: loop-exact timing, 2D overlay ----------
const T = cycleLen;
const camera = new THREE.PerspectiveCamera(+(P.get("fov") || 30), W / H, 0.1, 100);
const target = new THREE.Vector3(+(P.get("tx") || 0), +(P.get("ty") || 1.6), +(P.get("tz") || 0));
camera.setViewOffset(W, H, -W * +(P.get("ox") || 0.2), H * +(P.get("oy") || 0), W, H);
camera.updateProjectionMatrix();
const DIST = +(P.get("dist") || 12.5);
const AZ = +(P.get("az") || 0.62);
const EL = +(P.get("el") || 0.3);

const out = document.createElement("canvas");
out.width = W; out.height = H;
out.style.width = W / 2 + "px";
document.body.appendChild(out);
const ctx = out.getContext("2d");
const S = W / 960;

// Shared 24x24 icon set (the README cards use the same paths).
const ICON = {
  robo: "M4 20h9M8.5 20v-2.5M8.5 17.5L12 10M12 10l6-3.5M18 6.5l2.2 2.6M18 6.5l.8-3.3M10.1 17.5a1.6 1.6 0 1 1-3.2 0a1.6 1.6 0 1 1 3.2 0M13.6 10a1.6 1.6 0 1 1-3.2 0a1.6 1.6 0 1 1 3.2 0",
  auto: "M4 4h16v16H4zM4 8h16M7 11.5h6M7 14.5h6M7 17.5h6M16.5 12v.01M16.5 15v.01",
  emb: "M7 7h10v10H7zM10 10h4v4h-4zM9.5 4v3M12 4v3M14.5 4v3M9.5 17v3M12 17v3M14.5 17v3M4 9.5h3M4 12h3M4 14.5h3M17 9.5h3M17 12h3M17 14.5h3",
  ai: "M6.6 7.9l3.8 3.2M6.6 16.1l3.8-3.2M13.6 11.1l3.8-3.2M13.6 12.9l3.8 3.2M6.8 7a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0M6.8 17a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0M14 12a2 2 0 1 1-4 0a2 2 0 1 1 4 0M20.8 7a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0M20.8 17a1.8 1.8 0 1 1-3.6 0a1.8 1.8 0 1 1 3.6 0",
};
const HEX = { robo: "#f0b35a", auto: "#6aa8ff", emb: "#7fd38a", ai: "#b9a2ff" };
function icon(key, x, y, size) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(size / 24, size / 24);
  ctx.strokeStyle = HEX[key];
  ctx.lineWidth = 1.8;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.stroke(new Path2D(ICON[key]));
  ctx.restore();
}
function pill(key, label, x, y) {
  ctx.font = `500 ${12.5 * S}px "IBM Plex Sans"`;
  const w = ctx.measureText(label).width + 44 * S, h = 30 * S;
  ctx.fillStyle = "rgba(17,28,39,0.9)";
  ctx.strokeStyle = HEX[key] + "66";
  ctx.lineWidth = S;
  ctx.beginPath(); ctx.roundRect(x, y, w, h, 15 * S); ctx.fill(); ctx.stroke();
  icon(key, x + 10 * S, y + 6 * S, 18 * S);
  ctx.fillStyle = "#e9eef3";
  ctx.fillText(label, x + 34 * S, y + 19.5 * S);
  return w;
}
const pv = new THREE.Vector3();
function tag(key, label, pos, dy) {
  pv.copy(pos).project(camera);
  const x = (pv.x * 0.5 + 0.5) * W, y = (-pv.y * 0.5 + 0.5) * H;
  const ty = y + dy * S;
  ctx.strokeStyle = HEX[key] + "aa";
  ctx.lineWidth = S;
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, ty); ctx.stroke();
  ctx.fillStyle = HEX[key];
  ctx.beginPath(); ctx.arc(x, y, 2.5 * S, 0, Math.PI * 2); ctx.fill();
  ctx.font = `600 ${10 * S}px "IBM Plex Mono"`;
  ctx.letterSpacing = `${1.2 * S}px`;
  const w = ctx.measureText(label).width + 30 * S, h = 20 * S;
  const bx = x - w / 2, by = dy < 0 ? ty - h : ty;
  ctx.fillStyle = "rgba(10,17,24,0.82)";
  ctx.strokeStyle = HEX[key] + "88";
  ctx.beginPath(); ctx.roundRect(bx, by, w, h, 4 * S); ctx.fill(); ctx.stroke();
  icon(key, bx + 5 * S, by + 3 * S, 14 * S);
  ctx.fillStyle = HEX[key];
  ctx.fillText(label, bx + 23 * S, by + 14 * S);
  ctx.letterSpacing = "0px";
}

const tmp = new THREE.Vector3();
function frame(t) {
  const g = pose(t % T);
  for (const p of pulses) p.m.position.copy(pointOn(p.info, ((p.ph + p.k * t / T) % 1) * p.info.total, tmp)).setY(0.04);
  const s = (t / (T / 5)) % 1;
  scanRing.scale.setScalar(1 + s * 9);
  scanRing.material.opacity = 0.35 * (1 - s);
  baseRing.material.color.set(D.robo);
  tipLed.material.color.set(g > 0.5 ? D.robo : 0xffffff);
  updateDomains(t, T);

  const az = AZ + 0.1 * Math.sin((2 * Math.PI * t) / T);
  camera.position.set(target.x + Math.sin(az) * Math.cos(EL) * DIST, target.y + Math.sin(EL) * DIST, target.z + Math.cos(az) * Math.cos(EL) * DIST);
  camera.lookAt(target);
  renderer.render(scene, camera);

  ctx.drawImage(canvas, 0, 0);
  const fade = ctx.createLinearGradient(0, 0, W * 0.62, 0);
  fade.addColorStop(0, "rgba(10,17,24,0.97)");
  fade.addColorStop(0.62, "rgba(10,17,24,0.88)");
  fade.addColorStop(1, "rgba(10,17,24,0)");
  ctx.fillStyle = fade;
  ctx.fillRect(0, 0, W, H);

  tag("auto", "PLC", PLC_POS.clone().setY(1.78), -26);
  tag("emb", "MCU", CHIP_POS.clone().setY(0.2), 26);
  tag("ai", "LLM", LLM_POS.clone().setY(LLM_POS.y + 1.0), -14);
  tag("robo", "ARM", new THREE.Vector3(0, 0.32, 0).add(polar(THREE.MathUtils.degToRad(-60), 0.9, 0)), 30);

  const x = 52 * S;
  ctx.fillStyle = "#7fd38a";
  ctx.beginPath(); ctx.arc(x + 4 * S, 92 * S, 4 * S, 0, Math.PI * 2); ctx.fill();
  ctx.font = `500 ${11.5 * S}px "IBM Plex Mono"`;
  ctx.letterSpacing = `${1.4 * S}px`;
  ctx.fillStyle = "#b4c2d0";
  ctx.fillText("ELECTRICAL & COMPUTER ENGINEER · NOVI SAD", x + 18 * S, 96 * S);
  ctx.letterSpacing = "0px";
  ctx.font = `400 ${68 * S}px "Instrument Serif"`;
  ctx.fillStyle = "#e9eef3";
  ctx.fillText("Dušan Grković", x - 3 * S, 160 * S);
  ctx.font = `400 ${15 * S}px "IBM Plex Sans"`;
  ctx.fillStyle = "#b4c2d0";
  ctx.fillText("Firmware, control, and the software that ties machines together.", x, 192 * S);
  let px = x;
  px += pill("robo", "Robotics", px, 214 * S) + 8 * S;
  pill("auto", "Industrial automation", px, 214 * S);
  px = x;
  px += pill("emb", "Embedded systems", px, 252 * S) + 8 * S;
  pill("ai", "AI & LLM tools", px, 252 * S);
}

await document.fonts.load(`68px "Instrument Serif"`);
await document.fonts.load(`500 14px "IBM Plex Mono"`);
await document.fonts.load(`600 14px "IBM Plex Mono"`);
await document.fonts.load(`400 14px "IBM Plex Sans"`);
await document.fonts.load(`500 14px "IBM Plex Sans"`);
chipTex.needsUpdate = true;

if (SAVE) {
  const N = Math.round(T * FPS);
  for (let i = 0; i < N; i++) {
    frame(i / FPS);
    const blob = await new Promise((r) => out.toBlob(r, "image/png"));
    await fetch(`/frame?name=f${String(i).padStart(4, "0")}.png`, { method: "POST", body: blob });
  }
  document.title = "DONE " + N;
} else {
  const at = P.get("t");
  frame(at ? +at : 0);
  if (P.get("snap")) {
    const blob = await new Promise((r) => out.toBlob(r, "image/png"));
    await fetch(`/frame?name=${P.get("snap")}.png`, { method: "POST", body: blob });
    document.title = "SNAP";
  }
}
