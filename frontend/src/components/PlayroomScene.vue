<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js'
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js'

const container = ref(null)
let scene, camera, renderer
let composer, bloomPass, finishPass
let starfield = null
let mouseX = 0, mouseY = 0
let animationId = null
let toys = []
let raycaster, mouse
let lastMouseMoveTime = 0
let usePostprocessing = true
let lowQuality = false

// Reusable vectors to avoid per-frame allocations
const _toyWorldPos = new THREE.Vector3()
const _rayPoint = new THREE.Vector3()

// Combined chromatic aberration + vignette + film grain in one fragment pass.
const FinishShader = {
  uniforms: {
    tDiffuse: { value: null },
    uTime: { value: 0 },
    uAberration: { value: 0.0028 },
    uVignette: { value: 0.55 },
    uGrain: { value: 0.012 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uTime;
    uniform float uAberration;
    uniform float uVignette;
    uniform float uGrain;
    varying vec2 vUv;

    float random(vec2 st) {
      return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
    }

    void main() {
      vec2 uv = vUv;
      vec2 offset = uv - 0.5;
      float dist = length(offset);
      vec2 dir = normalize(offset + 0.0001);

      // Radial chromatic aberration: stronger toward the edges.
      float aberration = uAberration * dist * 2.0;
      vec3 col;
      col.r = texture2D(tDiffuse, uv - dir * aberration).r;
      col.g = texture2D(tDiffuse, uv).g;
      col.b = texture2D(tDiffuse, uv + dir * aberration).b;

      // Vignette: darken corners.
      float vig = smoothstep(uVignette + 0.45, uVignette - 0.15, dist);
      col *= mix(0.55, 1.0, vig);

      // Film grain.
      float grain = (random(uv + fract(uTime)) - 0.5) * uGrain;
      col += grain;

      gl_FragColor = vec4(col, 1.0);
    }
  `,
}

const COLORS = {
  red: 0xE74C3C,
  blue: 0x3498DB,
  yellow: 0xF1C40F,
  green: 0x2ECC71,
  orange: 0xE67E22,
  purple: 0x9B59B6,
  pink: 0xE91E63,
  brown: 0xC9A679,
  cyan: 0x00BCD4,
}

const COLOR_ARRAY = Object.values(COLORS)

function createToyBlock(color, size = 0.6) {
  const geo = new THREE.BoxGeometry(size, size, size)
  const mat = new THREE.MeshStandardMaterial({ color })
  const block = new THREE.Mesh(geo, mat)
  return block
}

function createToyBall(color, radius = 0.4) {
  const geo = new THREE.SphereGeometry(radius, 16, 16)
  const mat = new THREE.MeshStandardMaterial({ color })
  const ball = new THREE.Mesh(geo, mat)
  return ball
}

function createToyCar() {
  const car = new THREE.Group()

  const bodyGeo = new THREE.BoxGeometry(1.2, 0.4, 0.6)
  const bodyMat = new THREE.MeshStandardMaterial({ color: COLORS.red })
  const body = new THREE.Mesh(bodyGeo, bodyMat)
  body.position.y = 0.1
  car.add(body)

  const cabinGeo = new THREE.BoxGeometry(0.6, 0.35, 0.5)
  const cabinMat = new THREE.MeshStandardMaterial({ color: 0x87CEEB })
  const cabin = new THREE.Mesh(cabinGeo, cabinMat)
  cabin.position.set(-0.1, 0.35, 0)
  car.add(cabin)

  const wheelGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.1, 16)
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x333333 })

  const wheelPositions = [
    [-0.4, -0.05, 0.35],
    [-0.4, -0.05, -0.35],
    [0.4, -0.05, 0.35],
    [0.4, -0.05, -0.35]
  ]

  wheelPositions.forEach(pos => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMat)
    wheel.rotation.x = Math.PI / 2
    wheel.position.set(...pos)
    car.add(wheel)
  })

  return car
}

function createTeddyBear() {
  const teddy = new THREE.Group()
  const mat = new THREE.MeshStandardMaterial({ color: COLORS.brown })

  const bodyGeo = new THREE.SphereGeometry(0.5, 16, 16)
  const body = new THREE.Mesh(bodyGeo, mat)
  body.scale.y = 1.2
  body.position.y = 0
  teddy.add(body)

  const headGeo = new THREE.SphereGeometry(0.4, 16, 16)
  const head = new THREE.Mesh(headGeo, mat)
  head.position.y = 0.8
  teddy.add(head)

  const earGeo = new THREE.SphereGeometry(0.15, 12, 12)
  const earL = new THREE.Mesh(earGeo, mat)
  earL.position.set(-0.3, 1.1, 0)
  teddy.add(earL)

  const earR = new THREE.Mesh(earGeo, mat)
  earR.position.set(0.3, 1.1, 0)
  teddy.add(earR)

  const snoutGeo = new THREE.SphereGeometry(0.15, 12, 12)
  const snoutMat = new THREE.MeshStandardMaterial({ color: 0xF5DEB3 })
  const snout = new THREE.Mesh(snoutGeo, snoutMat)
  snout.position.set(0, 0.75, 0.35)
  teddy.add(snout)

  const noseGeo = new THREE.SphereGeometry(0.05, 8, 8)
  const noseMat = new THREE.MeshStandardMaterial({ color: 0x333333 })
  const nose = new THREE.Mesh(noseGeo, noseMat)
  nose.position.set(0, 0.78, 0.48)
  teddy.add(nose)

  const eyeGeo = new THREE.SphereGeometry(0.05, 8, 8)
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111 })

  const eyeL = new THREE.Mesh(eyeGeo, eyeMat)
  eyeL.position.set(-0.15, 0.9, 0.35)
  teddy.add(eyeL)

  const eyeR = new THREE.Mesh(eyeGeo, eyeMat)
  eyeR.position.set(0.15, 0.9, 0.35)
  teddy.add(eyeR)

  return teddy
}

function createRainbowStacker() {
  const stacker = new THREE.Group()
  const colors = [COLORS.red, COLORS.orange, COLORS.yellow, COLORS.green, COLORS.blue, COLORS.purple]

  const poleGeo = new THREE.CylinderGeometry(0.05, 0.05, 1, 8)
  const poleMat = new THREE.MeshStandardMaterial({ color: 0x6D4C41 })
  const pole = new THREE.Mesh(poleGeo, poleMat)
  pole.position.y = 0.5
  stacker.add(pole)

  const baseGeo = new THREE.CylinderGeometry(0.4, 0.4, 0.1, 16)
  const base = new THREE.Mesh(baseGeo, poleMat)
  base.position.y = 0.05
  stacker.add(base)

  colors.forEach((color, i) => {
    const radius = 0.35 - i * 0.05
    const ringGeo = new THREE.TorusGeometry(radius, 0.08, 8, 16)
    const ringMat = new THREE.MeshStandardMaterial({ color })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = Math.PI / 2
    ring.position.y = 0.15 + i * 0.15
    stacker.add(ring)
  })

  return stacker
}

function createStar() {
  const star = new THREE.Group()
  const mat = new THREE.MeshStandardMaterial({ color: COLORS.yellow })

  // Simple star shape using triangles
  const shape = new THREE.Shape()
  const outerRadius = 0.5
  const innerRadius = 0.2
  const spikes = 5

  for (let i = 0; i < spikes * 2; i++) {
    const radius = i % 2 === 0 ? outerRadius : innerRadius
    const angle = (i * Math.PI) / spikes - Math.PI / 2
    const x = Math.cos(angle) * radius
    const y = Math.sin(angle) * radius
    if (i === 0) {
      shape.moveTo(x, y)
    } else {
      shape.lineTo(x, y)
    }
  }
  shape.closePath()

  const extrudeSettings = { depth: 0.15, bevelEnabled: false }
  const geo = new THREE.ExtrudeGeometry(shape, extrudeSettings)
  const mesh = new THREE.Mesh(geo, mat)
  mesh.rotation.x = Math.PI / 2
  star.add(mesh)

  return star
}

function createDiamond() {
  const geo = new THREE.OctahedronGeometry(0.5)
  const mat = new THREE.MeshStandardMaterial({ color: COLORS.cyan })
  const diamond = new THREE.Mesh(geo, mat)
  diamond.scale.y = 1.5
  return diamond
}

function createRandomToy() {
  const toyTypes = [
    () => createToyBlock(COLOR_ARRAY[Math.floor(Math.random() * COLOR_ARRAY.length)], 0.5 + Math.random() * 0.3),
    () => createToyBall(COLOR_ARRAY[Math.floor(Math.random() * COLOR_ARRAY.length)], 0.3 + Math.random() * 0.2),
    createToyCar,
    createTeddyBear,
    createRainbowStacker,
    createStar,
    createDiamond,
  ]

  const createFn = toyTypes[Math.floor(Math.random() * toyTypes.length)]
  return createFn()
}

function init() {
  // Detect device capability up-front.
  lowQuality =
    window.matchMedia('(max-width: 768px)').matches ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  usePostprocessing = !lowQuality

  scene = new THREE.Scene()
  scene.background = null
  // Fog gives depth and lets distant toys fade into the dark backdrop.
  scene.fog = new THREE.Fog(0x0a1a2e, 18, 55)

  // Perspective camera for depth
  const aspect = container.value.clientWidth / container.value.clientHeight
  camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000)
  camera.position.set(0, 0, 20)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(container.value.clientWidth, container.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, lowQuality ? 1.25 : 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.15
  container.value.appendChild(renderer.domElement)

  // Raycaster for mouse interaction
  raycaster = new THREE.Raycaster()
  raycaster.params.Line = { threshold: 1 }
  mouse = new THREE.Vector2()

  // Create toys spread across the viewport. Fewer hero toys, wider Z range
  // so parallax actually reads as depth instead of a flat sticker layer.
  const toyCount = lowQuality ? 14 : 25
  const spreadX = 38
  const spreadY = 26
  const zNear = -25
  const zFar = 5

  for (let i = 0; i < toyCount; i++) {
    const toy = createRandomToy()

    toy.position.set(
      (Math.random() - 0.5) * spreadX,
      (Math.random() - 0.5) * spreadY,
      zNear + Math.random() * (zFar - zNear)
    )

    toy.rotation.set(
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2
    )

    const scale = 0.7 + Math.random() * 0.9
    toy.scale.set(scale, scale, scale)

    // Tune all materials at once: slightly glossy plastic look, with a hint of
    // emissive so bloom picks up the toy's own color rather than only specular.
    toy.traverse((child) => {
      if (child.isMesh && child.material && 'roughness' in child.material) {
        child.material.roughness = 0.45
        child.material.metalness = 0.08
        if (child.material.color) {
          child.material.emissive = child.material.color.clone().multiplyScalar(0.08)
        }
      }
    })

    toy.userData = {
      originalScale: scale,
      originalPosition: toy.position.clone(),
      floatOffset: Math.random() * Math.PI * 2,
      floatSpeed: 0.3 + Math.random() * 0.4,
      rotationSpeed: {
        x: (Math.random() - 0.5) * 0.01,
        y: (Math.random() - 0.5) * 0.01,
        z: (Math.random() - 0.5) * 0.01,
      },
      isHighlighted: false,
      highlightIntensity: 0,
    }

    toys.push(toy)
    scene.add(toy)
  }

  // Starfield on a spherical shell around the origin. Symmetric so the slow
  // rotation in animate() spins them in place rather than sweeping them all
  // to one side of the screen.
  const starCount = lowQuality ? 120 : 260
  const starGeo = new THREE.BufferGeometry()
  const starPositions = new Float32Array(starCount * 3)
  const starInnerR = 32
  const starOuterR = 52
  for (let i = 0; i < starCount; i++) {
    // Uniform direction on a sphere via inverse CDF.
    const u = Math.random()
    const v = Math.random()
    const theta = u * Math.PI * 2
    const phi = Math.acos(2 * v - 1)
    const r = starInnerR + Math.random() * (starOuterR - starInnerR)
    starPositions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta)
    starPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    starPositions[i * 3 + 2] = r * Math.cos(phi)
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3))
  const starMat = new THREE.PointsMaterial({
    color: 0x88ddff,
    size: 0.18,
    sizeAttenuation: true,
    transparent: true,
    opacity: 0.85,
    depthWrite: false,
  })
  starfield = new THREE.Points(starGeo, starMat)
  scene.add(starfield)

  // Lighting tuned for PBR + bloom.
  const ambient = new THREE.AmbientLight(0xffffff, 0.35)
  scene.add(ambient)

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.1)
  dirLight.position.set(5, 10, 10)
  scene.add(dirLight)

  const fillLight = new THREE.DirectionalLight(0x88ccff, 0.5)
  fillLight.position.set(-5, -5, 5)
  scene.add(fillLight)

  // Accent point lights: brighter so they create bloom-worthy highlights.
  const pinkLight = new THREE.PointLight(0xff5dc8, 2.2, 35)
  pinkLight.position.set(-12, 6, 6)
  scene.add(pinkLight)

  const cyanLight = new THREE.PointLight(0x4dd9ff, 2.2, 35)
  cyanLight.position.set(12, -6, 6)
  scene.add(cyanLight)

  // Postprocessing pipeline.
  if (usePostprocessing) {
    const w = container.value.clientWidth
    const h = container.value.clientHeight
    composer = new EffectComposer(renderer)
    composer.setSize(w, h)

    composer.addPass(new RenderPass(scene, camera))

    // UnrealBloomPass(resolution, strength, radius, threshold).
    bloomPass = new UnrealBloomPass(new THREE.Vector2(w, h), 0.4, 0.55, 0.7)
    composer.addPass(bloomPass)

    finishPass = new ShaderPass(FinishShader)
    composer.addPass(finishPass)

    composer.addPass(new OutputPass())
  }
}

function onMouseMove(event) {
  const now = performance.now()
  if (now - lastMouseMoveTime < 32) return // ~30fps throttle
  lastMouseMoveTime = now

  const rect = container.value.getBoundingClientRect()
  mouseX = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouseY = -((event.clientY - rect.top) / rect.height) * 2 + 1

  mouse.x = mouseX
  mouse.y = mouseY
}

function onWindowResize() {
  if (!container.value || !camera || !renderer) return

  const w = container.value.clientWidth
  const h = container.value.clientHeight
  const aspect = w / h
  camera.aspect = aspect
  camera.updateProjectionMatrix()

  renderer.setSize(w, h)
  if (composer) composer.setSize(w, h)
  if (bloomPass) bloomPass.setSize(w, h)
}

function setEmissive(object, intensity, color = 0xffffff) {
  object.traverse((child) => {
    if (child.isMesh && child.material) {
      if (!child.material.emissive) return
      child.material.emissive.setHex(color)
      child.material.emissiveIntensity = intensity
    }
  })
}

function animate() {
  animationId = requestAnimationFrame(animate)

  const time = Date.now() * 0.001

  // Update raycaster
  raycaster.setFromCamera(mouse, camera)

  // Check for intersections and proximity
  toys.forEach((toy) => {
    // Floating animation
    const floatY = Math.sin(time * toy.userData.floatSpeed + toy.userData.floatOffset) * 0.3
    toy.position.y = toy.userData.originalPosition.y + floatY

    // Gentle rotation
    toy.rotation.x += toy.userData.rotationSpeed.x
    toy.rotation.y += toy.userData.rotationSpeed.y
    toy.rotation.z += toy.userData.rotationSpeed.z

    // Check proximity to mouse ray
    toy.getWorldPosition(_toyWorldPos)

    // Calculate distance from mouse ray to toy
    raycaster.ray.closestPointToPoint(_toyWorldPos, _rayPoint)
    const distance = _toyWorldPos.distanceTo(_rayPoint)

    // Proximity threshold
    const threshold = 3
    const isNear = distance < threshold

    // Smooth highlight transition
    const targetIntensity = isNear ? 1 : 0
    toy.userData.highlightIntensity += (targetIntensity - toy.userData.highlightIntensity) * 0.3

    // Apply highlight effect
    const intensity = toy.userData.highlightIntensity
    const targetScale = toy.userData.originalScale * (1 + intensity * 0.3)
    toy.scale.setScalar(toy.scale.x + (targetScale - toy.scale.x) * 0.1)

    // Hover glow: high intensity so cyan reliably crosses the bloom threshold.
    setEmissive(toy, intensity * 1.6, 0x00ffff)
  })

  // Slow camera breathing on top of mouse parallax, so the scene drifts even
  // when the user is still. Mouse parallax still dominates.
  const breatheX = Math.sin(time * 0.18) * 0.6
  const breatheY = Math.cos(time * 0.12) * 0.4
  camera.position.x += ((mouseX * 2 + breatheX) - camera.position.x) * 0.02
  camera.position.y += ((mouseY * 2 + breatheY) - camera.position.y) * 0.02
  camera.lookAt(0, 0, 0)

  // Slow starfield drift for added parallax.
  if (starfield) {
    starfield.rotation.y = time * 0.005
    starfield.rotation.x = Math.sin(time * 0.04) * 0.05
  }

  if (usePostprocessing && composer) {
    if (finishPass) finishPass.uniforms.uTime.value = time
    composer.render()
  } else {
    renderer.render(scene, camera)
  }
}

onMounted(() => {
  init()
  animate()

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', onWindowResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', onWindowResize)

  // Cleanup
  toys.forEach((toy) => {
    toy.traverse((child) => {
      if (child.geometry) child.geometry.dispose()
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose())
        } else {
          child.material.dispose()
        }
      }
    })
  })
  toys = []

  if (starfield) {
    starfield.geometry.dispose()
    starfield.material.dispose()
    starfield = null
  }

  if (composer) {
    composer.passes.forEach((pass) => {
      if (pass.dispose) pass.dispose()
    })
    composer = null
    bloomPass = null
    finishPass = null
  }

  if (renderer) {
    renderer.dispose()
    container.value?.removeChild(renderer.domElement)
  }
})
</script>

<template>
  <div ref="container" class="playroom-canvas"></div>
</template>

<style scoped>
.playroom-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.playroom-canvas :deep(canvas) {
  pointer-events: none;
}
</style>
