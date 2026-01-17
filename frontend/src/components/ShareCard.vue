<script setup>
import { ref, computed } from 'vue'
import { domToPng } from 'modern-screenshot'

const props = defineProps({
  roadmap: {
    type: Array,
    required: true
  },
  skillScores: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const cardRef = ref(null)
const isGenerating = ref(false)
const isGenerated = ref(false)
const imageUrl = ref(null)

const skills = [
  { key: 'cognitive', label: 'Cognitive', icon: '🧠' },
  { key: 'motor_fine', label: 'Fine Motor', icon: '✋' },
  { key: 'motor_gross', label: 'Gross Motor', icon: '🏃' },
  { key: 'social_emotional', label: 'Social', icon: '❤️' },
  { key: 'creative', label: 'Creative', icon: '🎨' },
  { key: 'language', label: 'Language', icon: '💬' }
]

const topSkills = computed(() => {
  return skills
    .map(s => ({ ...s, score: props.skillScores[s.key] || 0 }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 3)
})

const timeframeLabels = {
  'now': 'Now',
  '3_months': '3 Months',
  '6_months': '6 Months'
}

const generateImage = async () => {
  if (!cardRef.value) return

  isGenerating.value = true

  try {
    const dataUrl = await domToPng(cardRef.value, {
      scale: 2,
      backgroundColor: '#1a1a2e'
    })

    imageUrl.value = dataUrl
    isGenerated.value = true
  } catch (e) {
    console.error('Failed to generate image:', e)
    alert('Failed to generate image. Please try again.')
  } finally {
    isGenerating.value = false
  }
}

const downloadImage = () => {
  if (!imageUrl.value) return

  const link = document.createElement('a')
  link.download = 'playroom-diet-roadmap.png'
  link.href = imageUrl.value
  link.click()
}

const copyToClipboard = async () => {
  if (!imageUrl.value) return

  try {
    const response = await fetch(imageUrl.value)
    const blob = await response.blob()
    await navigator.clipboard.write([
      new ClipboardItem({ 'image/png': blob })
    ])
    alert('Image copied to clipboard!')
  } catch (e) {
    console.error('Failed to copy:', e)
    alert('Failed to copy to clipboard. Try downloading instead.')
  }
}

const resetAndClose = () => {
  isGenerated.value = false
  imageUrl.value = null
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="bg-base-200 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-auto">

      <!-- Modal Header -->
      <div class="p-4 border-b border-base-300 flex items-center justify-between">
        <h2 class="text-xl font-bold">Share Your Results</h2>
        <button @click="resetAndClose" class="btn btn-ghost btn-sm btn-circle">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Card Preview -->
      <div class="p-4">
        <!-- The actual card that will be captured - using inline styles for html2canvas compatibility -->
        <div
          ref="cardRef"
          class="share-card"
          style="padding: 24px; border-radius: 12px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%); font-family: system-ui, -apple-system, sans-serif;"
        >
          <!-- Header -->
          <div style="text-align: center; margin-bottom: 16px;">
            <div style="font-size: 32px; margin-bottom: 4px;">🧸</div>
            <h1 style="font-size: 20px; font-weight: bold; color: #ffffff; margin: 0; font-family: 'Fredoka', sans-serif;">
              Playroom Diet
            </h1>
            <p style="font-size: 11px; color: rgba(255,255,255,0.6); margin: 4px 0 0 0;">AI-Powered Child Development</p>
          </div>

          <!-- Roadmap Summary -->
          <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <h2 style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.8); margin: 0 0 12px 0;">🗺️ My 6-Month Roadmap</h2>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div
                v-for="item in roadmap"
                :key="item.timeframe"
                style="display: flex; align-items: center; gap: 8px;"
              >
                <span style="font-size: 11px; padding: 2px 8px; border-radius: 9999px; background: rgba(255,255,255,0.2); color: rgba(255,255,255,0.8);">
                  {{ timeframeLabels[item.timeframe] || item.timeframe }}
                </span>
                <span style="font-size: 13px; color: #ffffff; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;">
                  {{ item.final_toy || item.recommended_toy }}
                </span>
              </div>
            </div>
          </div>

          <!-- Skill Highlights -->
          <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <h2 style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.8); margin: 0 0 12px 0;">📈 Top Skills</h2>
            <div style="display: flex; justify-content: space-around;">
              <div
                v-for="skill in topSkills"
                :key="skill.key"
                style="text-align: center;"
              >
                <div style="font-size: 24px; margin-bottom: 4px;">{{ skill.icon }}</div>
                <div style="font-size: 18px; font-weight: bold; color: #ffffff;">{{ skill.score }}%</div>
                <div style="font-size: 10px; color: rgba(255,255,255,0.6);">{{ skill.label }}</div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div style="text-align: center;">
            <p style="font-size: 10px; color: rgba(255,255,255,0.4); margin: 0;">
              Generated with Playroom Diet • playroom-diet.app
            </p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="p-4 border-t border-base-300">
        <div v-if="!isGenerated" class="flex justify-center">
          <button
            @click="generateImage"
            :disabled="isGenerating"
            class="btn btn-primary gap-2"
          >
            <span v-if="isGenerating" class="loading loading-spinner loading-sm"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ isGenerating ? 'Generating...' : 'Generate Image' }}
          </button>
        </div>

        <div v-else class="space-y-3">
          <p class="text-center text-sm text-success">Image generated successfully!</p>
          <div class="flex gap-2 justify-center">
            <button @click="downloadImage" class="btn btn-primary gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
            <button @click="copyToClipboard" class="btn btn-secondary gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </button>
          </div>
          <button @click="isGenerated = false" class="btn btn-ghost btn-sm w-full">
            Regenerate
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.share-card {
  font-family: system-ui, -apple-system, sans-serif;
}
</style>
