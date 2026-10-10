import * as THREE from './vendor/three.module.min.js';

// Decorative only. The inline CSS scene remains visible without JS or WebGL.
const canvas = document.querySelector('#signal-scene');
const container = canvas.parentElement;
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
} catch {
  container.dataset.renderer = 'static';
}

if (renderer) {
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 80);
  camera.position.set(0, 3.1, 12);
  camera.lookAt(0, 0.4, 0);
  const system = new THREE.Group();
  scene.add(system);

  const cyan = new THREE.MeshBasicMaterial({ color: 0x70ffe7, transparent: true, opacity: 0.9 });
  const violet = new THREE.MeshBasicMaterial({ color: 0xae92ff, transparent: true, opacity: 0.8 });
  const softCyan = new THREE.MeshBasicMaterial({ color: 0x70ffe7, transparent: true, opacity: 0.025, depthWrite: false, blending: THREE.AdditiveBlending });
  const softViolet = softCyan.clone();
  softViolet.color.setHex(0xae92ff);
  const rings = [];
  for (let i = 0; i < 3; i++) {
    const radius = [2.25, 2.65, 1.9][i];
    const ring = new THREE.Group();
    const material = i === 1 ? violet : cyan;
    ring.add(new THREE.Mesh(new THREE.TorusGeometry(radius, 0.009, 6, 160), material));
    for (const thickness of [0.035, 0.065, 0.11]) {
      ring.add(new THREE.Mesh(new THREE.TorusGeometry(radius, thickness, 6, 128), i === 1 ? softViolet : softCyan));
    }
    // Small illuminated nodes make the orbit's motion visible.
    for (let n = 0; n < 4; n++) {
      const angle = (n / 4) * Math.PI * 2;
      const node = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.09, 0.09), material);
      node.position.set(Math.cos(angle) * radius, Math.sin(angle) * radius, 0);
      ring.add(node);
    }
    ring.rotation.set([1.2, 0.55, -0.7][i], [0.3, 1.1, 0.6][i], [0.2, -0.4, 0.9][i]);
    system.add(ring);
    rings.push(ring);
  }

  const coreGeometry = new THREE.IcosahedronGeometry(1.02, 0);
  const coreMaterial = new THREE.MeshPhongMaterial({ color: 0x101f35, emissive: 0x071729, shininess: 100, flatShading: true });
  const core = new THREE.Mesh(coreGeometry, coreMaterial);
  core.add(new THREE.LineSegments(new THREE.EdgesGeometry(coreGeometry), new THREE.LineBasicMaterial({ color: 0x70ffe7, transparent: true, opacity: 0.8 })));
  system.add(core);
  scene.add(new THREE.AmbientLight(0xb3cfff, 1.5));
  const light = new THREE.PointLight(0x70ffe7, 35, 30);
  light.position.set(5, 6, 5);
  scene.add(light);

  const glowCanvas = document.createElement('canvas');
  glowCanvas.width = glowCanvas.height = 64;
  const context = glowCanvas.getContext('2d');
  const gradient = context.createRadialGradient(32, 32, 0, 32, 32, 32);
  gradient.addColorStop(0, 'rgba(255,255,255,0.28)');
  gradient.addColorStop(0.35, 'rgba(255,255,255,0.08)');
  gradient.addColorStop(1, 'rgba(255,255,255,0)');
  context.fillStyle = gradient;
  context.fillRect(0, 0, 64, 64);
  const glowMaterial = new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(glowCanvas), color: 0x70ffe7, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
  const glow = new THREE.Sprite(glowMaterial);
  glow.scale.set(8, 8, 1);
  system.add(glow);

  const grid = new THREE.GridHelper(50, 50, 0x70ffe7, 0x324a68);
  grid.position.y = -2.5;
  grid.material.transparent = true;
  grid.material.opacity = 0.22;
  scene.add(grid);
  const stars = new Float32Array(180 * 3);
  // Seeded positions give previews a stable composition.
  let seed = 27;
  const random = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
  for (let i = 0; i < stars.length; i += 3) {
    stars[i] = (random() - 0.5) * 30;
    stars[i + 1] = random() * 13 - 1;
    stars[i + 2] = -random() * 18 - 2;
  }
  const starGeometry = new THREE.BufferGeometry();
  starGeometry.setAttribute('position', new THREE.BufferAttribute(stars, 3));
  const starMaterial = new THREE.PointsMaterial({ color: 0xa9c7e8, size: 0.025, transparent: true, opacity: 0.65 });
  scene.add(new THREE.Points(starGeometry, starMaterial));

  const trails = new THREE.Group();
  for (let i = 0; i < 12; i++) {
    const trail = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.015, 1.3), i % 3 ? cyan : violet);
    trail.position.set((i % 7 - 3) * 1.65, -2.48, -i * 2);
    trails.add(trail);
  }
  scene.add(trails);

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0;
  let visible = true;
  let contextLost = false;
  const pointer = new THREE.Vector2();
  const render = () => renderer.render(scene, camera);
  const resize = () => {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const mobile = window.innerWidth <= 600;
    camera.position.z = mobile ? 11.8 : 12;
    system.position.set(mobile ? 0 : 3.4, mobile ? 0.2 : 0.9, 0);
    system.scale.setScalar(mobile ? 0.9 : 1);
    camera.updateProjectionMatrix();
    render();
  };
  const theme = () => {
    const isLight = document.documentElement.dataset.theme === 'light';
    const accent = isLight ? 0x007d92 : 0x70ffe7;
    const purple = isLight ? 0x6940c5 : 0xae92ff;
    cyan.color.setHex(accent); violet.color.setHex(purple);
    softCyan.color.setHex(accent); softViolet.color.setHex(purple);
    core.children[0].material.color.setHex(accent);
    coreMaterial.color.setHex(isLight ? 0xb5cde3 : 0x101f35);
    coreMaterial.emissive.setHex(isLight ? 0x091423 : 0x071729);
    glowMaterial.color.setHex(accent);
    glowMaterial.opacity = isLight ? 0.35 : 1;
    grid.material.opacity = isLight ? 0.13 : 0.22;
    starMaterial.color.setHex(isLight ? 0x385b85 : 0xa9c7e8);
    light.color.setHex(accent);
    render();
  };
  const animate = (timestamp) => {
    if (motion.matches || !visible || document.hidden || contextLost) { frame = 0; return; }
    const time = timestamp * 0.001;
    rings[0].rotation.z = 0.2 + time * 0.08;
    rings[1].rotation.z = -0.4 - time * 0.06;
    rings[2].rotation.y = 0.6 + time * 0.07;
    core.rotation.set(time * 0.06, time * 0.12, 0.1);
    system.rotation.y += (pointer.x * 0.12 - system.rotation.y) * 0.025;
    system.rotation.x += (pointer.y * 0.07 - system.rotation.x) * 0.025;
    trails.children.forEach((trail, i) => { trail.position.z = ((time * 1.8 + i * 2.7) % 28) - 24; });
    render();
    frame = requestAnimationFrame(animate);
  };
  const resume = () => {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
    if (!motion.matches && visible && !document.hidden && !contextLost) frame = requestAnimationFrame(animate);
    else if (!contextLost) render();
  };
  new ResizeObserver(resize).observe(container);
  new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; resume(); }).observe(container);
  document.querySelector('.hero').addEventListener('pointermove', (event) => {
    const bounds = container.getBoundingClientRect();
    pointer.set((event.clientX - bounds.left) / bounds.width - 0.5, (event.clientY - bounds.top) / bounds.height - 0.5);
  }, { passive: true });
  document.querySelector('.hero').addEventListener('pointerleave', () => pointer.set(0, 0));
  window.addEventListener('themechange', theme);
  document.addEventListener('visibilitychange', resume);
  motion.addEventListener('change', resume);
  canvas.addEventListener('webglcontextlost', (event) => {
    event.preventDefault(); contextLost = true; container.dataset.renderer = 'static'; resume();
  });
  canvas.addEventListener('webglcontextrestored', () => {
    contextLost = false; container.dataset.renderer = 'webgl'; theme(); resize(); resume();
  });
  theme(); resize();
  container.dataset.renderer = 'webgl';
  resume();
}
