<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const container = ref(null)
let scene, camera, renderer
let mouseX = 0, mouseY = 0
let animationId = null
let toys = []
let raycaster, mouse

// Colors - modern playful palette
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
  const mat = new THREE.MeshLambertMaterial({ color })
  const block = new THREE.Mesh(geo, mat)
  return block
}

function createToyBall(color, radius = 0.4) {
  const geo = new THREE.SphereGeometry(radius, 16, 16)
  const mat = new THREE.MeshLambertMaterial({ color })
  const ball = new THREE.Mesh(geo, mat)
  return ball
}

function createToyCar() {
  const car = new THREE.Group()

  const bodyGeo = new THREE.BoxGeometry(1.2, 0.4, 0.6)
  const bodyMat = new THREE.MeshLambertMaterial({ color: COLORS.red })
  const body = new THREE.Mesh(bodyGeo, bodyMat)
  body.position.y = 0.1
  car.add(body)

  const cabinGeo = new THREE.BoxGeometry(0.6, 0.35, 0.5)
  const cabinMat = new THREE.MeshLambertMaterial({ color: 0x87CEEB })
  const cabin = new THREE.Mesh(cabinGeo, cabinMat)
  cabin.position.set(-0.1, 0.35, 0)
  car.add(cabin)

  const wheelGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.1, 16)
  const wheelMat = new THREE.MeshLambertMaterial({ color: 0x333333 })

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
  const mat = new THREE.MeshLambertMaterial({ color: COLORS.brown })

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
  const snoutMat = new THREE.MeshLambertMaterial({ color: 0xF5DEB3 })
  const snout = new THREE.Mesh(snoutGeo, snoutMat)
  snout.position.set(0, 0.75, 0.35)
  teddy.add(snout)

  const noseGeo = new THREE.SphereGeometry(0.05, 8, 8)
  const noseMat = new THREE.MeshLambertMaterial({ color: 0x333333 })
  const nose = new THREE.Mesh(noseGeo, noseMat)
  nose.position.set(0, 0.78, 0.48)
  teddy.add(nose)

  const eyeGeo = new THREE.SphereGeometry(0.05, 8, 8)
  const eyeMat = new THREE.MeshLambertMaterial({ color: 0x111111 })

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
  const poleMat = new THREE.MeshLambertMaterial({ color: 0x6D4C41 })
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
    const ringMat = new THREE.MeshLambertMaterial({ color })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = Math.PI / 2
    ring.position.y = 0.15 + i * 0.15
    stacker.add(ring)
  })

  return stacker
}

function createStar() {
  const star = new THREE.Group()
  const mat = new THREE.MeshLambertMaterial({ color: COLORS.yellow })

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
  const mat = new THREE.MeshLambertMaterial({ color: COLORS.cyan })
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
  scene = new THREE.Scene()
  scene.background = null

  // Perspective camera for depth
  const aspect = container.value.clientWidth / container.value.clientHeight
  camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000)
  camera.position.set(0, 0, 20)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(container.value.clientWidth, container.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.value.appendChild(renderer.domElement)

  // Raycaster for mouse interaction
  raycaster = new THREE.Raycaster()
  raycaster.params.Line = { threshold: 1 }
  mouse = new THREE.Vector2()

  // Create toys spread across the viewport
  const toyCount = 60
  const spreadX = 35
  const spreadY = 25
  const spreadZ = 20

  for (let i = 0; i < toyCount; i++) {
    const toy = createRandomToy()

    // Distribute across the full background
    toy.position.set(
      (Math.random() - 0.5) * spreadX,
      (Math.random() - 0.5) * spreadY,
      (Math.random() - 0.5) * spreadZ - 5
    )

    // Random rotation
    toy.rotation.set(
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2
    )

    // Random scale variation
    const scale = 0.6 + Math.random() * 0.8
    toy.scale.set(scale, scale, scale)

    // Store original properties for animation
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

  // Lighting
  const ambient = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambient)

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8)
  dirLight.position.set(5, 10, 10)
  scene.add(dirLight)

  const fillLight = new THREE.DirectionalLight(0x88ccff, 0.3)
  fillLight.position.set(-5, -5, 5)
  scene.add(fillLight)

  // Accent lights for depth
  const pinkLight = new THREE.PointLight(0xff69b4, 0.5, 30)
  pinkLight.position.set(-10, 5, 5)
  scene.add(pinkLight)

  const cyanLight = new THREE.PointLight(0x00ffff, 0.5, 30)
  cyanLight.position.set(10, -5, 5)
  scene.add(cyanLight)
}

function onMouseMove(event) {
  const rect = container.value.getBoundingClientRect()
  mouseX = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouseY = -((event.clientY - rect.top) / rect.height) * 2 + 1

  mouse.x = mouseX
  mouse.y = mouseY
}

function onWindowResize() {
  if (!container.value || !camera || !renderer) return

  const aspect = container.value.clientWidth / container.value.clientHeight
  camera.aspect = aspect
  camera.updateProjectionMatrix()

  renderer.setSize(container.value.clientWidth, container.value.clientHeight)
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
    const toyWorldPos = new THREE.Vector3()
    toy.getWorldPosition(toyWorldPos)

    // Calculate distance from mouse ray to toy
    const rayPoint = new THREE.Vector3()
    raycaster.ray.closestPointToPoint(toyWorldPos, rayPoint)
    const distance = toyWorldPos.distanceTo(rayPoint)

    // Proximity threshold
    const threshold = 3
    const isNear = distance < threshold

    // Smooth highlight transition
    const targetIntensity = isNear ? 1 : 0
    toy.userData.highlightIntensity += (targetIntensity - toy.userData.highlightIntensity) * 0.1

    // Apply highlight effect
    const intensity = toy.userData.highlightIntensity
    const targetScale = toy.userData.originalScale * (1 + intensity * 0.3)
    toy.scale.setScalar(toy.scale.x + (targetScale - toy.scale.x) * 0.1)

    // Glow effect
    setEmissive(toy, intensity * 0.5, 0x00ffff)
  })

  // Subtle camera movement based on mouse
  camera.position.x += (mouseX * 2 - camera.position.x) * 0.02
  camera.position.y += (mouseY * 2 - camera.position.y) * 0.02
  camera.lookAt(0, 0, 0)

  renderer.render(scene, camera)
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
