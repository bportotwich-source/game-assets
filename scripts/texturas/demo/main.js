import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { ASSETS, UV } from './assets.js';

const KITS = {
  'predio-tijolos': { label: 'Prédio de tijolos', map: { brick: 'brick', stone: 'stone', plaster: 'plaster' } },
  'padaria': { label: 'Padaria', map: { render: 'render_padaria', roof_tiles: 'roof_padaria', brick: 'brick', plaster: 'plaster' } },
  'casa-enxaimel': { label: 'Casa enxaimel', map: { stone2: 'stone2', render: 'render_enx', roof_tiles: 'roof_enx', plaster: 'plaster' } },
  'bangalo': { label: 'Bangalô', map: { siding: 'siding', brick: 'brick', shingles: 'shingles', plaster: 'plaster' } },
};
const STYLES = {
  atual: 'As texturas lisas de hoje: só cor, sem relevo.',
  detalhado: 'Realista e limpo: cada peça com seu tom, juntas fundas, bordas chanfradas e granulado com relevo.',
  pintado: 'Pintado à mão: tons em faixas e luz pintada no topo das peças. Combina com o contorno preto dos kits.',
  envelhecido: 'Realista com desgaste: lascas, rachaduras, musgo, manchas e sujeira subindo do chão.',
};

const b64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
const canvas = document.getElementById('view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xb9c6d2);
scene.fog = new THREE.Fog(0xb9c6d2, 60, 140);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.45;
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 400);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.maxPolarAngle = Math.PI * 0.495;
const hemi = new THREE.HemisphereLight(0xdfe8f2, 0x8a7a66, 0.6); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff1dc, 2.6); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03;
Object.assign(sun.shadow.camera, { left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 120 });
scene.add(sun, sun.target);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: 0x8e9478, roughness: 1 }));
ground.rotation.x = -Math.PI / 2; ground.position.y = -0.01; ground.receiveShadow = true; scene.add(ground);

// ---------- textures ----------
const texCache = {};
async function tex(style, key, kind) {
  const id = `${style}/${key}_${kind}`;
  if (texCache[id]) return texCache[id];
  const bmp = await createImageBitmap(new Blob([b64(ASSETS.tex[id])], { type: 'image/jpeg' }));
  const t = new THREE.Texture(bmp);
  t.flipY = false; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = kind === 'albedo' ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  const r = UV[key]; t.repeat.set(r[0], r[1]); t.needsUpdate = true;
  return (texCache[id] = t);
}

// world-space shader extras: large-scale tone variation (hides the 2 m repetition) and,
// for the weathered style, dirt rising from the ground.
function addWorldDetail(mat, grime) {
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uGrime = { value: grime };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWP;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWP = (modelMatrix * vec4(transformed,1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vWP; uniform float uGrime;
float h3(vec3 p){ p=fract(p*0.3183099+.1); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
float vn(vec3 x){ vec3 i=floor(x), f=fract(x); f=f*f*(3.0-2.0*f);
  return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z); }`)
      .replace('#include <map_fragment>', `#include <map_fragment>
float mac = vn(vWP*0.35)*0.6 + vn(vWP*1.1)*0.4;
diffuseColor.rgb *= 0.9 + 0.2*mac;
if (uGrime > 0.0) {
  float n = vn(vec3(vWP.x*3.0, vWP.y*0.4, vWP.z*3.0));
  float g = clamp(1.0 - vWP.y/(0.6 + 0.9*n), 0.0, 1.0);
  g = g*g*uGrime;
  diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb*vec3(0.55,0.5,0.42), g);
  float streak = smoothstep(0.62, 0.9, vn(vec3(vWP.x*9.0+vWP.z*9.0, vWP.y*0.25, 0.0))) * uGrime;
  diffuseColor.rgb *= 1.0 - 0.18*streak;
}`);
  };
  mat.customProgramCacheKey = () => 'wd' + grime;
}

// ---------- buildings ----------
const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
const kits = {};
async function loadKit(name) {
  if (kits[name]) return kits[name];
  const buf = b64(ASSETS.glb[name]).buffer;
  const gltf = await new Promise((res, rej) => loader.parse(buf, '', res, rej));
  const root = gltf.scene; const sets = { atual: new Map() };
  const conf = KITS[name].map; const mats = new Map();
  root.traverse((o) => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; mats.set(o.material.uuid, o.material); } });
  for (const st of ['detalhado', 'pintado', 'envelhecido']) sets[st] = new Map();
  for (const m of mats.values()) {
    sets.atual.set(m, m);
    const key = conf[m.name];
    for (const st of ['detalhado', 'pintado', 'envelhecido']) {
      const n = m.clone();
      if (key) {
        n.map = await tex(st, key, 'albedo'); n.normalMap = await tex(st, key, 'normal');
        const orm = await tex(st, key, 'orm'); n.roughnessMap = orm; n.aoMap = orm; n.aoMapIntensity = 1;
        n.roughness = 1; n.metalness = 0; n.color.set(0xffffff);
        n.normalScale.set(st === 'pintado' ? 0.8 : 1.2, st === 'pintado' ? 0.8 : 1.2);
        addWorldDetail(n, st === 'envelhecido' && !/roof|shingle|plaster/.test(m.name) ? 1 : 0);
      } else if (st === 'envelhecido' && !/glass/.test(m.name)) {
        addWorldDetail(n, 0.8);
      }
      sets[st].set(m, n);
    }
  }
  const meshes = []; root.traverse((o) => { if (o.isMesh) meshes.push([o, o.material]); });
  const box = new THREE.Box3().setFromObject(root);
  return (kits[name] = { root, sets, meshes, box });
}
function applyStyle(kit, st) { for (const [o, m] of kit.meshes) o.material = kit.sets[st].get(m); }

// ---------- UI state ----------
const state = { kit: 'predio-tijolos', style: 'detalhado', compare: true, split: 0.5, sunAz: 0.75, view: 'inteiro' };
let current = null;
async function showKit(name) {
  document.getElementById('status').hidden = false;
  const k = await loadKit(name);
  if (current) scene.remove(current.root);
  current = k; scene.add(k.root);
  frame(state.view); placeSun();
  document.getElementById('status').hidden = true;
}
function frame(view) {
  const b = current.box, c = b.getCenter(new THREE.Vector3()), s = b.getSize(new THREE.Vector3());
  const r = Math.max(s.x, s.y, s.z);
  if (view === 'perto') {
    controls.target.set(c.x - s.x * 0.2, 1.6, b.max.z);
    camera.position.set(c.x - s.x * 0.05, 1.8, b.max.z + 3.2);
  } else {
    controls.target.copy(c).setY(s.y * 0.42);
    camera.position.set(c.x + r * 0.75, s.y * 0.55 + 2, b.max.z + r * 1.15);
  }
  controls.update();
}
function placeSun() {
  const c = current ? current.box.getCenter(new THREE.Vector3()) : new THREE.Vector3();
  const a = state.sunAz * Math.PI * 2;
  sun.position.set(c.x + Math.sin(a) * 30, 26, c.z + Math.cos(a) * 30); sun.target.position.copy(c);
}

function chips(id, entries, key, after) {
  const el = document.getElementById(id); el.innerHTML = '';
  for (const [v, label] of entries) {
    const b = document.createElement('button'); b.type = 'button'; b.textContent = label; b.dataset.v = v;
    b.setAttribute('aria-pressed', state[key] === v);
    b.onclick = () => { state[key] = v; for (const x of el.children) x.setAttribute('aria-pressed', x.dataset.v === v); after(v); };
    el.appendChild(b);
  }
}
const STYLE_LABEL = { atual: 'Atual (liso)', detalhado: 'Detalhado', pintado: 'Pintado à mão', envelhecido: 'Envelhecido' };
chips('kits', Object.entries(KITS).map(([k, v]) => [k, v.label]), 'kit', showKit);
chips('styles', Object.entries(STYLE_LABEL), 'style', updateStyleText);
chips('views', [['inteiro', 'Prédio inteiro'], ['perto', 'De perto (3 m)']], 'view', frame);
function updateStyleText() {
  document.getElementById('styleText').textContent = STYLES[state.style];
  document.getElementById('rightLabel').textContent = STYLE_LABEL[state.style];
}
updateStyleText();
const cmp = document.getElementById('compare');
cmp.onchange = () => { state.compare = cmp.checked; document.getElementById('split').hidden = !cmp.checked; };
document.getElementById('sun').oninput = (e) => { state.sunAz = +e.target.value; placeSun(); };

// split handle
const split = document.getElementById('split'); const handle = document.getElementById('handle');
let dragging = false;
const setSplit = (x) => { const r = canvas.getBoundingClientRect(); state.split = Math.min(0.95, Math.max(0.05, (x - r.left) / r.width)); split.style.left = state.split * 100 + '%'; };
handle.addEventListener('pointerdown', (e) => { dragging = true; handle.setPointerCapture(e.pointerId); e.stopPropagation(); });
handle.addEventListener('pointermove', (e) => { if (dragging) setSplit(e.clientX); });
handle.addEventListener('pointerup', () => { dragging = false; });
handle.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { const r = canvas.getBoundingClientRect(); setSplit(r.left + (state.split + (e.key === 'ArrowLeft' ? -0.05 : 0.05)) * r.width); } });

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio()) || canvas.height !== Math.floor(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
}
function loop() {
  requestAnimationFrame(loop); resize(); controls.update();
  if (!current) return;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (state.compare && state.style !== 'atual') {
    const sx = Math.round(w * state.split);
    renderer.setScissorTest(true);
    applyStyle(current, 'atual'); renderer.setScissor(0, 0, sx, h); renderer.setViewport(0, 0, w, h); renderer.render(scene, camera);
    applyStyle(current, state.style); renderer.setScissor(sx, 0, w - sx, h); renderer.render(scene, camera);
    renderer.setScissorTest(false);
  } else {
    applyStyle(current, state.style); renderer.setViewport(0, 0, w, h); renderer.render(scene, camera);
  }
}
showKit(state.kit).then(async () => { loop(); for (const k of Object.keys(KITS)) await loadKit(k); })
  .catch((e) => { document.getElementById('status').textContent = 'Não consegui carregar o modelo: ' + e.message; });
window.__ready = () => !!current;
