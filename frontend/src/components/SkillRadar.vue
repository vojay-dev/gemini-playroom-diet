<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  scores: {
    type: Object,
    required: true
  },
  projectedScores: {
    type: Object,
    default: null
  }
})

const skills = [
  { key: 'cognitive', label: 'Cognitive', icon: '🧠', desc: 'Problem-solving, memory, logical thinking, and understanding cause and effect.' },
  { key: 'motor_fine', label: 'Fine Motor', icon: '✋', desc: 'Small muscle control — drawing, building, buttoning, and using utensils.' },
  { key: 'motor_gross', label: 'Gross Motor', icon: '🏃', desc: 'Large muscle movement — running, jumping, climbing, and balance.' },
  { key: 'social_emotional', label: 'Social', icon: '❤️', desc: 'Sharing, empathy, cooperation, emotional regulation, and role-playing.' },
  { key: 'creative', label: 'Creative', icon: '🎨', desc: 'Imagination, artistic expression, open-ended play, and storytelling.' },
  { key: 'language', label: 'Language', icon: '💬', desc: 'Vocabulary, communication, reading readiness, and verbal expression.' }
]

const hoveredSkill = ref(null)
const svgRef = ref(null)
const isTouch = typeof window !== 'undefined' && matchMedia('(pointer: coarse)').matches

const centerX = 150
const centerY = 150
const maxRadius = 100

const getPoint = (index, value, total = 6) => {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2
  const radius = (value / 100) * maxRadius
  return {
    x: centerX + radius * Math.cos(angle),
    y: centerY + radius * Math.sin(angle)
  }
}

const currentPoints = computed(() => {
  return skills
    .map((skill, i) => {
      const point = getPoint(i, props.scores[skill.key] || 0)
      return `${point.x},${point.y}`
    })
    .join(' ')
})

const projectedPoints = computed(() => {
  if (!props.projectedScores) return null
  return skills
    .map((skill, i) => {
      const point = getPoint(i, props.projectedScores[skill.key] || 0)
      return `${point.x},${point.y}`
    })
    .join(' ')
})

const gridLevels = [20, 40, 60, 80, 100]

const getGridPoints = (level) => {
  return skills
    .map((_, i) => {
      const point = getPoint(i, level)
      return `${point.x},${point.y}`
    })
    .join(' ')
}

const axisLines = computed(() => {
  return skills.map((_, i) => {
    const point = getPoint(i, 100)
    return { x1: centerX, y1: centerY, x2: point.x, y2: point.y }
  })
})

const labelPositions = computed(() => {
  return skills.map((skill, i) => {
    const point = getPoint(i, 120)
    return { ...skill, x: point.x, y: point.y, score: props.scores[skill.key] || 0 }
  })
})

const tooltipData = computed(() => {
  if (hoveredSkill.value === null) return null
  const i = hoveredSkill.value
  const skill = skills[i]
  const current = props.scores[skill.key] || 0
  const projected = props.projectedScores?.[skill.key] || null
  return { ...skill, current, projected }
})

function onSvgMove(event) {
  const svg = svgRef.value
  if (!svg) return
  const rect = svg.getBoundingClientRect()
  const mx = ((event.clientX - rect.left) / rect.width) * 300
  const my = ((event.clientY - rect.top) / rect.height) * 300

  let closest = null
  let closestDist = Infinity
  for (let i = 0; i < labelPositions.value.length; i++) {
    const lp = labelPositions.value[i]
    const dx = mx - lp.x
    const dy = my - lp.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < closestDist) {
      closestDist = dist
      closest = i
    }
  }
  hoveredSkill.value = closestDist < 35 ? closest : null
}

function onSvgLeave() {
  hoveredSkill.value = null
}

function onSkillTap(i) {
  hoveredSkill.value = hoveredSkill.value === i ? null : i
}
</script>

<template>
  <div class="skill-radar relative">
    <svg
      ref="svgRef"
      viewBox="0 0 300 300"
      class="w-full h-auto"
      @mousemove="onSvgMove"
      @mouseleave="onSvgLeave"
      @touchend="hoveredSkill = null"
    >
      <!-- Background grid -->
      <g class="grid-lines">
        <polygon
          v-for="level in gridLevels"
          :key="level"
          :points="getGridPoints(level)"
          fill="none"
          stroke="currentColor"
          :stroke-opacity="level === 100 ? 0.3 : 0.1"
          stroke-width="1"
        />
      </g>

      <!-- Axis lines -->
      <g class="axis-lines">
        <line
          v-for="(line, i) in axisLines"
          :key="i"
          :x1="line.x1"
          :y1="line.y1"
          :x2="line.x2"
          :y2="line.y2"
          stroke="currentColor"
          stroke-opacity="0.2"
          stroke-width="1"
        />
      </g>

      <!-- Projected improvement area -->
      <polygon
        v-if="projectedPoints"
        :points="projectedPoints"
        class="fill-success/20 stroke-success"
        stroke-width="2"
        stroke-dasharray="4 2"
      />

      <!-- Current skills area -->
      <polygon
        :points="currentPoints"
        class="fill-primary/30 stroke-primary"
        stroke-width="2"
      />

      <!-- Data points (current) -->
      <circle
        v-for="(skill, i) in skills"
        :key="skill.key"
        :cx="getPoint(i, scores[skill.key] || 0).x"
        :cy="getPoint(i, scores[skill.key] || 0).y"
        :r="hoveredSkill === i ? 6 : 4"
        class="fill-primary transition-all duration-200"
      />

      <!-- Data points (projected) -->
      <template v-if="projectedScores">
        <circle
          v-for="(skill, i) in skills"
          :key="'proj-' + skill.key"
          :cx="getPoint(i, projectedScores[skill.key] || 0).x"
          :cy="getPoint(i, projectedScores[skill.key] || 0).y"
          :r="hoveredSkill === i ? 6 : 4"
          class="fill-success transition-all duration-200"
          stroke="white"
          stroke-width="1"
          stroke-opacity="0.3"
        />
      </template>

      <!-- Labels -->
      <g class="labels">
        <g v-for="(label, i) in labelPositions" :key="label.key">
          <text
            :x="label.x"
            :y="label.y - 8"
            text-anchor="middle"
            class="text-lg"
          >
            {{ label.icon }}
          </text>
          <text
            :x="label.x"
            :y="label.y + 10"
            text-anchor="middle"
            class="fill-current text-[10px] font-medium"
            :opacity="hoveredSkill === i ? 1 : 0.7"
          >
            {{ label.label }}
          </text>
          <text
            :x="label.x"
            :y="label.y + 22"
            text-anchor="middle"
            class="fill-current text-[10px] font-bold"
            :class="label.score >= 70 ? 'fill-success' : label.score >= 40 ? 'fill-warning' : 'fill-error'"
          >
            {{ label.score }}%
          </text>

          <circle
            :cx="label.x"
            :cy="label.y + 4"
            r="24"
            fill="transparent"
            class="cursor-pointer"
            @click.stop="onSkillTap(i)"
            @touchend.stop.prevent="onSkillTap(i)"
          />
        </g>
      </g>
    </svg>

    <!-- Tooltip -->
    <Transition name="tooltip-fade">
      <div
        v-if="tooltipData"
        class="tooltip-box absolute left-1/2 w-56 p-3 rounded-xl bg-base-100/95 backdrop-blur-md border border-white/15 shadow-lg z-20 text-center pointer-events-none"
      >
        <div class="text-sm font-semibold mb-1">
          {{ tooltipData.icon }} {{ tooltipData.label }}
        </div>
        <p class="text-xs opacity-60 mb-2">{{ tooltipData.desc }}</p>
        <div class="flex justify-center gap-3 text-xs">
          <span class="font-mono">
            <span class="text-primary font-bold">{{ tooltipData.current }}%</span>
            <span class="opacity-50"> now</span>
          </span>
          <span v-if="tooltipData.projected !== null" class="font-mono">
            <span class="text-success font-bold">{{ tooltipData.projected }}%</span>
            <span class="opacity-50"> goal</span>
          </span>
        </div>
      </div>
    </Transition>

    <p class="text-center text-[11px] opacity-40 mt-1">
      {{ isTouch ? 'Tap' : 'Hover' }} a skill to learn more
      <template v-if="projectedScores"> · Dashed line shows projected improvement</template>
    </p>

    <!-- Legend -->
    <div class="flex justify-center gap-4 mt-1 text-xs">
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-full bg-primary/50"></div>
        <span class="opacity-70">Current</span>
      </div>
      <div v-if="projectedScores" class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-full bg-success/50 border border-dashed border-success"></div>
        <span class="opacity-70">After Roadmap</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skill-radar text {
  font-family: system-ui, sans-serif;
}

.tooltip-box {
  bottom: 36px;
  transform: translateX(-50%);
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: all 0.15s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}

.tooltip-fade-enter-to,
.tooltip-fade-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>
