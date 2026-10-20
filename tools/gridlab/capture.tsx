// Deterministic frame capture of the presentation's City scene for the profile card.
import * as THREE from 'three';
import { projectCoordinate as project, buildRoadPath, sampleRoadPath } from './roadMotion';
const W = 1920, H = 1080, FPS = 12, T = 12, N = FPS * T;
const POST = 'http://127.0.0.1:8124/frame?name=';
(async () => {
  const geo = await (await fetch('/presentation/geography.json')).json();
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.setClearColor(0x071a19, 1);
  document.body.appendChild(renderer.domElement);
  const world = new THREE.Scene(); world.fog = new THREE.FogExp2(0x071a19, 0.014);
  const camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 150);
  world.add(new THREE.AmbientLight(0xb6ffe8, 1.8));
  const key = new THREE.DirectionalLight(0xe7fff8, 3); key.position.set(8, 20, 12); world.add(key);
  const rim = new THREE.DirectionalLight(0x40ffc3, 3); rim.position.set(-15, 8, -8); world.add(rim);
  const base = new THREE.Mesh(new THREE.BoxGeometry(31, 0.3, 28), new THREE.MeshStandardMaterial({ color: 0x0d2927, roughness: 0.8, metalness: 0.25 }));
  base.position.y = -0.25; world.add(base);
  const grid = new THREE.GridHelper(32, 32, 0x23534c, 0x163831); grid.position.y = -0.08; world.add(grid);
  const buildings = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ color: 0x70b4a3, roughness: 0.5, metalness: 0.28 }), geo.points.length);
  const m = new THREE.Object3D();
  geo.points.forEach(([lon, lat, power]: number[], i: number) => { const [x, z] = project(lon, lat); const h = 0.08 + Math.min(0.9, Math.sqrt(power) * 0.5); m.position.set(x, h / 2, z); m.scale.set(0.065, h, 0.065); m.updateMatrix(); buildings.setMatrixAt(i, m.matrix); buildings.setColorAt(i, new THREE.Color(i % 11 === 0 ? 0xb6ffd5 : 0x477e72)); });
  world.add(buildings);
  const segs = (list: number[][][], y: number) => { const p: number[] = []; list.forEach(r => r.slice(1).forEach((q, i) => { const a = project(r[i][0], r[i][1]), b = project(q[0], q[1]); p.push(a[0], y, a[1], b[0], y, b[1]); })); const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); return g; };
  world.add(new THREE.LineSegments(segs(geo.roads || [], 0.055), new THREE.LineBasicMaterial({ color: 0x8db9aa, transparent: true, opacity: 0.52 })));
  world.add(new THREE.LineSegments(segs(geo.routes, 0.04), new THREE.LineBasicMaterial({ color: 0x69deb3, transparent: true, opacity: 0.62 })));
  const beacons: THREE.Mesh[] = [];
  geo.stations.forEach((s: any) => { const [x, z] = project(s.lon, s.lat); const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.2, 6), new THREE.MeshBasicMaterial({ color: 0xe7ffc9 })); stem.position.set(x, 0.6, z); world.add(stem); const ring = new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.025, 6, 32), new THREE.MeshBasicMaterial({ color: 0xbefb83 })); ring.rotation.x = -Math.PI / 2; ring.position.set(x, 0.16, z); world.add(ring); beacons.push(ring); });
  const paths = (geo.carPaths || []).map(buildRoadPath).filter((p: any) => p.length > 0.1);
  // each car: whole laps per loop; every third car stops for a 3 s charge inside the loop
  const cars = paths.map((path: any, i: number) => {
    const car = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.19, 0.08, 0.36), new THREE.MeshStandardMaterial({ color: 0xffef91, emissive: 0xffd85c, emissiveIntensity: 1.3, metalness: 0.3, roughness: 0.35 })); body.position.y = 0.09; car.add(body);
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(0.145, 0.07, 0.17), new THREE.MeshStandardMaterial({ color: 0x102c3f })); cabin.position.set(0, 0.16, -0.025); car.add(cabin); car.scale.setScalar(1.15);
    const halo = new THREE.Mesh(new THREE.RingGeometry(.22, .31, 32), new THREE.MeshBasicMaterial({ color: 0xffdf76, transparent: true, opacity: .7, side: THREE.DoubleSide })); halo.rotation.x = -Math.PI / 2; halo.position.y = .015; car.add(halo);
    const plug = new THREE.Mesh(new THREE.CylinderGeometry(.04, .04, .8, 8), new THREE.MeshBasicMaterial({ color: 0x72fff0, transparent: true, opacity: .9 })); plug.position.set(.24, .4, 0); plug.visible = false; car.add(plug);
    world.add(car);
    const v = .18 + (i % 5) * .018, charge = i % 3 === 0 ? 3 : 0, start = ((i * 0.618) % 1) * (T - charge);
    const laps = Math.max(1, Math.round(v * (T - charge) / path.length));
    return { car, body, halo, plug, path, charge, start, speed: laps * path.length / (T - charge), off: path.length * ((i * .618) % 1) };
  });
  const dist = (c: any, t: number) => { const moving = c.charge ? (t < c.start ? t : t < c.start + c.charge ? c.start : t - c.charge) : t; return c.off + c.speed * moving; };
  for (let f = 0; f < N; f++) {
    const t = f / FPS, u = t / T;
    world.rotation.y = 0.12;
    camera.position.set(7.4, 6.6, 9.8); camera.lookAt(0.6, 0, 0.9);
    beacons.forEach((r, i) => r.scale.setScalar(1 + Math.sin(2 * Math.PI * 3 * u + i) * 0.16));
    cars.forEach((c: any) => {
      const p = sampleRoadPath(c.path, dist(c, t)); c.car.position.set(p.x, .07, p.z); c.car.rotation.y = p.heading;
      const charging = c.charge > 0 && t >= c.start && t < c.start + c.charge;
      c.plug.visible = charging; c.halo.material.color.set(charging ? 0x72fff0 : 0xffdf76);
      c.halo.scale.setScalar(charging ? 1.25 + Math.sin(2 * Math.PI * 8 * u) * .3 : 1); c.body.material.emissive.set(charging ? 0x39ffe0 : 0xffd85c);
    });
    renderer.render(world, camera);
    const blob: Blob = await new Promise(r => renderer.domElement.toBlob(b => r(b!), 'image/png'));
    await fetch(POST + `g${String(f).padStart(4, '0')}.png`, { method: 'POST', body: blob, mode: 'no-cors' });
    if (location.search.includes('one')) break;
  }
  document.title = 'DONE';
})();
