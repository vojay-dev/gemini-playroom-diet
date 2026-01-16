<script setup>
import { computed } from 'vue'

const props = defineProps({
  scores: {
    type: Object,
    required: true
  },
  // Optional: show projected improvement from roadmap
  projectedScores: {
    type: Object,
    default: null
  }
})

const skills = [
  { key: 'cognitive', label: 'Cognitive', icon: '🧠' },
  { key: 'motor_fine', label: 'Fine Motor', icon: '✋' },
  { key: 'motor_gross', label: 'Gross Motor', icon: '🏃' },
  { key: 'social_emotional', label: 'Social', icon: '❤️' },
  { key: 'creative', label: 'Creative', icon: '🎨' },
  { key: 'language', label: 'Language', icon: '💬' }
]

const centerX = 150
const centerY = 150
const maxRadius = 100

// Calculate point position on the hexagon
const getPoint = (index, value, total = 6) => {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2
  const radius = (value / 100) * maxRadius
  return {
    x: centerX + radius * Math.cos(angle),
    y: centerY + radius * Math.sin(angle)
  }
}

// Generate polygon points string
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

// Grid lines (20%, 40%, 60%, 80%, 100%)
const gridLevels = [20, 40, 60, 80, 100]

const getGridPoints = (level) => {
  return skills
    .map((_, i) => {
      const point = getPoint(i, level)
      return `${point.x},${point.y}`
    })
    .join(' ')
}

// Axis lines from center to each vertex
const axisLines = computed(() => {
  return skills.map((_, i) => {
    const point = getPoint(i, 100)
    return { x1: centerX, y1: centerY, x2: point.x, y2: point.y }
  })
})

// Label positions (slightly outside the chart)
const labelPositions = computed(() => {
  return skills.map((skill, i) => {
    const point = getPoint(i, 120)
    return { ...skill, x: point.x, y: point.y, score: props.scores[skill.key] || 0 }
  })
})
</script>

<template>
  <div class="skill-radar">
    <svg viewBox="0 0 300 300" class="w-full h-auto">
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

      <!-- Projected improvement area (if provided) -->
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

      <!-- Data points -->
      <circle
        v-for="(skill, i) in skills"
        :key="skill.key"
        :cx="getPoint(i, scores[skill.key] || 0).x"
        :cy="getPoint(i, scores[skill.key] || 0).y"
        r="4"
        class="fill-primary"
      />

      <!-- Labels -->
      <g class="labels">
        <g v-for="label in labelPositions" :key="label.key">
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
            class="fill-current text-[10px] font-medium opacity-70"
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
        </g>
      </g>
    </svg>

    <!-- Legend -->
    <div class="flex justify-center gap-4 mt-2 text-xs">
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
</style>
