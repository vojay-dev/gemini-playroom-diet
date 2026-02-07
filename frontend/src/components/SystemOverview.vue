<script setup>
import { ref } from 'vue'
import { VueFlow, useVueFlow, Handle, Position } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/minimap/dist/style.css'
import '@vue-flow/controls/dist/style.css'

const { fitView } = useVueFlow()

const nodes = ref([
  {
    id: 'user',
    type: 'custom',
    position: { x: 350, y: 0 },
    data: { label: 'User', icon: '👤', category: 'user' }
  },
  {
    id: 'frontend',
    type: 'custom',
    position: { x: 350, y: 100 },
    data: { label: 'Vue.js Frontend', icon: '🖥️', category: 'frontend', tech: 'Vue 3 + Tailwind' }
  },
  {
    id: 'backend',
    type: 'custom',
    position: { x: 350, y: 200 },
    data: { label: 'FastAPI Backend', icon: '⚡', category: 'backend', tech: 'Python + FastAPI' }
  },
  {
    id: 'airflow',
    type: 'custom',
    position: { x: 150, y: 320 },
    data: { label: 'Airflow', icon: '🌀', category: 'orchestration', tech: 'Apache Airflow' }
  },
  {
    id: 'supabase-storage',
    type: 'custom',
    position: { x: 550, y: 320 },
    data: { label: 'Image Storage', icon: '🖼️', category: 'storage', tech: 'Supabase Storage' }
  },
  {
    id: 'supabase-db',
    type: 'custom',
    position: { x: 550, y: 480 },
    data: { label: 'Database', icon: '🗄️', category: 'storage', tech: 'Supabase PostgreSQL' }
  },
  {
    id: 'agent-vision',
    type: 'custom',
    position: { x: 50, y: 420 },
    data: { label: 'Vision Analyzer', icon: '👁️', category: 'ai', tech: 'Gemini 3 Pro' }
  },
  {
    id: 'agent-recommend',
    type: 'custom',
    position: { x: 0, y: 530 },
    data: { label: 'Toy Recommender', icon: '🧸', category: 'ai', tech: 'Gemini 3 Flash' }
  },
  {
    id: 'agent-playquest',
    type: 'custom',
    position: { x: 200, y: 530 },
    data: { label: 'Play Quest', icon: '🎮', category: 'ai', tech: 'Gemini 3 Flash' }
  },
  {
    id: 'agent-safety',
    type: 'custom',
    position: { x: 0, y: 640 },
    data: { label: 'Safety Checker', icon: '🛡️', category: 'ai', tech: 'Gemini 3 Flash' }
  }
])

const edges = ref([
  {
    id: 'e-user-frontend',
    source: 'user',
    target: 'frontend',
    type: 'default',
    animated: true,
    style: { stroke: '#6366f1', strokeWidth: 2 }
  },
  {
    id: 'e-frontend-backend',
    source: 'frontend',
    target: 'backend',
    type: 'default',
    animated: true,
    style: { stroke: '#6366f1', strokeWidth: 2 }
  },
  {
    id: 'e-backend-airflow',
    source: 'backend',
    target: 'airflow',
    type: 'default',
    animated: true,
    style: { stroke: '#f59e0b', strokeWidth: 2 }
  },
  {
    id: 'e-backend-storage',
    source: 'backend',
    target: 'supabase-storage',
    type: 'default',
    animated: true,
    style: { stroke: '#22c55e', strokeWidth: 2 }
  },
  {
    id: 'e-storage-db',
    source: 'supabase-storage',
    target: 'supabase-db',
    type: 'default',
    animated: true,
    style: { stroke: '#22c55e', strokeWidth: 2 }
  },
  {
    id: 'e-airflow-vision',
    source: 'airflow',
    target: 'agent-vision',
    type: 'default',
    animated: true,
    style: { stroke: '#ec4899', strokeWidth: 2 }
  },
  {
    id: 'e-vision-recommend',
    source: 'agent-vision',
    target: 'agent-recommend',
    type: 'default',
    animated: true,
    style: { stroke: '#ec4899', strokeWidth: 2 }
  },
  {
    id: 'e-vision-playquest',
    source: 'agent-vision',
    target: 'agent-playquest',
    type: 'default',
    animated: true,
    style: { stroke: '#ec4899', strokeWidth: 2 }
  },
  {
    id: 'e-recommend-safety',
    source: 'agent-recommend',
    target: 'agent-safety',
    type: 'default',
    animated: true,
    style: { stroke: '#ec4899', strokeWidth: 2 }
  },
  {
    id: 'e-safety-db',
    source: 'agent-safety',
    target: 'supabase-db',
    sourceHandle: 'right-source',
    targetHandle: 'bottom-target',
    type: 'default',
    animated: true,
    style: { stroke: '#22c55e', strokeWidth: 2 }
  },
  {
    id: 'e-playquest-db',
    source: 'agent-playquest',
    target: 'supabase-db',
    sourceHandle: 'right-source',
    targetHandle: 'bottom-target',
    type: 'default',
    animated: true,
    style: { stroke: '#22c55e', strokeWidth: 2 }
  }
])

const nodeColor = (node) => {
  const colors = {
    user: '#6366f1',
    frontend: '#6366f1',
    backend: '#f59e0b',
    storage: '#22c55e',
    orchestration: '#f59e0b',
    ai: '#ec4899'
  }
  return colors[node.data?.category] || '#64748b'
}
</script>

<template>
  <div class="h-[calc(100vh-68px-40px)] w-full relative">
    <!-- Header overlay -->
    <div class="absolute top-4 left-4 z-10 bg-base-300/80 backdrop-blur-sm rounded-xl p-4 max-w-sm">
      <h1 class="text-2xl font-bold mb-2" style="font-family: 'Fredoka', sans-serif;">
        System Architecture
      </h1>
      <p class="text-sm opacity-70">
        Interactive diagram showing how Playroom Diet processes your photos through our multi-agent AI pipeline.
      </p>

      <!-- Legend -->
      <div class="mt-4 flex flex-wrap gap-2">
        <div class="flex items-center gap-1 text-xs">
          <div class="w-3 h-3 rounded-full bg-[#6366f1]"></div>
          <span>Frontend</span>
        </div>
        <div class="flex items-center gap-1 text-xs">
          <div class="w-3 h-3 rounded-full bg-[#f59e0b]"></div>
          <span>Backend</span>
        </div>
        <div class="flex items-center gap-1 text-xs">
          <div class="w-3 h-3 rounded-full bg-[#22c55e]"></div>
          <span>Storage</span>
        </div>
        <div class="flex items-center gap-1 text-xs">
          <div class="w-3 h-3 rounded-full bg-[#ec4899]"></div>
          <span>AI Agents</span>
        </div>
      </div>
    </div>

    <VueFlow
      :nodes="nodes"
      :edges="edges"
      :fit-view-on-init="true"
      :default-viewport="{ zoom: 1 }"
      class="vue-flow-wrapper"
    >
      <!-- Custom node template -->
      <template #node-custom="{ data }">
        <Handle type="target" :position="Position.Top" class="handle-hidden" />
        <Handle type="target" :position="Position.Left" class="handle-hidden" />
        <Handle type="target" :position="Position.Bottom" id="bottom-target" class="handle-hidden" />
        <div
          class="node-card"
          :class="`node-${data.category}`"
        >
          <div class="node-icon">{{ data.icon }}</div>
          <div class="node-content">
            <div class="node-label">{{ data.label }}</div>
            <div v-if="data.tech" class="node-tech">{{ data.tech }}</div>
          </div>
        </div>
        <Handle type="source" :position="Position.Bottom" class="handle-hidden" />
        <Handle type="source" :position="Position.Right" id="right-source" class="handle-hidden" />
        <Handle type="source" :position="Position.Left" class="handle-hidden" />
      </template>

      <Background pattern-color="#374151" :gap="20" />

      <MiniMap
        :node-color="nodeColor"
        class="mini-map"
      />

      <Controls class="controls" />
    </VueFlow>
  </div>
</template>

<style>
.vue-flow-wrapper {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
}

.vue-flow__minimap {
  background-color: rgba(15, 23, 42, 0.8) !important;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.vue-flow__controls {
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  bottom: 20px !important;
  left: 20px !important;
}

.vue-flow__minimap {
  bottom: 20px !important;
  right: 20px !important;
}

.vue-flow__controls-button {
  background-color: rgba(30, 41, 59, 0.9) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

.vue-flow__controls-button:hover {
  background-color: rgba(51, 65, 85, 0.9) !important;
}

.vue-flow__controls-button svg {
  fill: white !important;
}

.node-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  min-width: 140px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.node-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.node-user { border-color: #6366f1; }
.node-frontend { border-color: #6366f1; }
.node-backend { border-color: #f59e0b; }
.node-storage { border-color: #22c55e; }
.node-orchestration { border-color: #f59e0b; }
.node-ai { border-color: #ec4899; }

.node-icon {
  font-size: 24px;
  line-height: 1;
}

.node-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.node-label {
  font-weight: 600;
  font-size: 13px;
  color: white;
}

.node-tech {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.handle-hidden {
  opacity: 0;
  width: 8px;
  height: 8px;
}
</style>
