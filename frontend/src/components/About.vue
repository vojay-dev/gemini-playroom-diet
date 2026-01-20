<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-[calc(100vh-68px-40px)] pb-16">
    <!-- Hero section -->
    <div class="hero py-16 bg-base-300/30">
      <div class="hero-content text-center">
        <div class="max-w-2xl">
          <div class="text-6xl mb-4">🧒🧸🎯</div>
          <h1 class="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent" style="font-family: 'Fredoka', sans-serif;">
            Playroom Diet
          </h1>
          <p class="py-6 text-xl opacity-80">
            AI-powered child development analysis that turns your chaotic toy pile into a science-backed growth plan - plus a Play Quest to start improving today.
          </p>
          <RouterLink to="/" class="btn btn-primary gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Try It Now
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Problem section -->
    <div class="py-16 px-4">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-8" style="font-family: 'Fredoka', sans-serif;">
          The Problem
        </h2>
        <div class="grid md:grid-cols-2 gap-8">
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body">
              <div class="text-4xl mb-2">🤯</div>
              <h3 class="card-title">Toy Overload</h3>
              <p class="opacity-70">
                Parents often accumulate toys without knowing which developmental skills they actually support. The result? Gaps in crucial areas like fine motor skills, cognitive development, or social-emotional growth.
              </p>
            </div>
          </div>
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body">
              <div class="text-4xl mb-2">🎲</div>
              <h3 class="card-title">Guesswork Shopping</h3>
              <p class="opacity-70">
                Without expert guidance, toy purchases become random. Marketing claims don't tell you what skills a toy actually develops or whether your child already has similar toys.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Solution section -->
    <div class="py-16 px-4 bg-base-300/20">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-8" style="font-family: 'Fredoka', sans-serif;">
          Our Solution
        </h2>
        <div class="flex flex-col md:flex-row gap-8 items-center">
          <div class="flex-1">
            <p class="text-lg mb-4">
              Playroom Diet uses a <span class="text-primary font-semibold">multi-agent AI pipeline</span> powered by Google's Gemini 3 to analyze your playroom and provide personalized toy recommendations.
            </p>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <span class="text-2xl">📸</span>
                <span><strong>Upload a photo</strong> of your playroom or toy collection</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl">🔍</span>
                <span><strong>AI analyzes</strong> each toy and maps it to developmental skills</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl">📊</span>
                <span><strong>Get a skill radar</strong> showing your child's coverage across 6 key areas</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl">🗺️</span>
                <span><strong>Receive a roadmap</strong> with 3 targeted toy recommendations</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl">🎮</span>
                <span><strong>Get a Play Quest</strong> - an activity using toys you already own</span>
              </li>
            </ul>
          </div>
          <div class="flex-1">
            <RouterLink to="/system" class="card bg-base-300/50 backdrop-blur-sm hover:bg-base-300/70 transition-all cursor-pointer">
              <div class="card-body items-center text-center">
                <div class="text-5xl mb-2">🏗️</div>
                <h3 class="card-title">View System Architecture</h3>
                <p class="opacity-70">See how our multi-agent AI pipeline works</p>
                <div class="badge badge-primary">Interactive Diagram</div>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Skills section -->
    <div class="py-16 px-4">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-8" style="font-family: 'Fredoka', sans-serif;">
          6 Developmental Areas We Track
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body items-center text-center p-4">
              <div class="text-3xl">🧠</div>
              <h3 class="font-semibold">Cognitive</h3>
              <p class="text-xs opacity-70">Problem-solving, memory, logical thinking</p>
            </div>
          </div>
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body items-center text-center p-4">
              <div class="text-3xl">✋</div>
              <h3 class="font-semibold">Fine Motor</h3>
              <p class="text-xs opacity-70">Hand-eye coordination, dexterity</p>
            </div>
          </div>
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body items-center text-center p-4">
              <div class="text-3xl">🏃</div>
              <h3 class="font-semibold">Gross Motor</h3>
              <p class="text-xs opacity-70">Balance, strength, coordination</p>
            </div>
          </div>
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body items-center text-center p-4">
              <div class="text-3xl">❤️</div>
              <h3 class="font-semibold">Social-Emotional</h3>
              <p class="text-xs opacity-70">Empathy, sharing, emotional regulation</p>
            </div>
          </div>
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body items-center text-center p-4">
              <div class="text-3xl">🎨</div>
              <h3 class="font-semibold">Creative</h3>
              <p class="text-xs opacity-70">Imagination, artistic expression</p>
            </div>
          </div>
          <div class="card bg-base-300/50 backdrop-blur-sm">
            <div class="card-body items-center text-center p-4">
              <div class="text-3xl">💬</div>
              <h3 class="font-semibold">Language</h3>
              <p class="text-xs opacity-70">Vocabulary, communication, reading</p>
            </div>
          </div>
        </div>
        <p class="text-center mt-6 opacity-70">
          Based on the <span class="font-semibold text-primary">O*NET Content Model</span> - the same framework used by the U.S. Department of Labor to classify workplace abilities.
        </p>
      </div>
    </div>

    <!-- Tech stack section -->
    <div class="py-16 px-4 bg-base-300/20">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-8" style="font-family: 'Fredoka', sans-serif;">
          Built With
        </h2>
        <div class="flex flex-wrap justify-center gap-3">
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>🤖</span> Gemini 3 Flash
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>🌀</span> Apache Airflow
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>⚡</span> FastAPI
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>💚</span> Vue.js 3
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>🎨</span> Tailwind CSS
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>🗄️</span> Postgres
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>🐍</span> Python
          </div>
          <div class="badge badge-lg badge-soft badge-primary gap-2 p-4">
            <span>📊</span> O*NET Data
          </div>
        </div>
        <div class="text-center mt-8">
          <RouterLink to="/system" class="btn btn-ghost btn-sm gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            View System Architecture
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Features section -->
    <div class="py-16 px-4">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-8" style="font-family: 'Fredoka', sans-serif;">
          Key Features
        </h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="flex gap-4">
            <div class="text-3xl">🔒</div>
            <div>
              <h3 class="font-semibold">Privacy First</h3>
              <p class="opacity-70 text-sm">Images are analyzed and never stored permanently. Your family's privacy matters.</p>
            </div>
          </div>
          <div class="flex gap-4">
            <div class="text-3xl">⚡</div>
            <div>
              <h3 class="font-semibold">Fast Analysis</h3>
              <p class="opacity-70 text-sm">Get results in under a minute thanks to our optimized multi-agent pipeline.</p>
            </div>
          </div>
          <div class="flex gap-4">
            <div class="text-3xl">🛡️</div>
            <div>
              <h3 class="font-semibold">Safety Checked</h3>
              <p class="opacity-70 text-sm">Every recommendation is verified for age-appropriateness and safety.</p>
            </div>
          </div>
          <div class="flex gap-4">
            <div class="text-3xl">🛒</div>
            <div>
              <h3 class="font-semibold">Easy Shopping</h3>
              <p class="opacity-70 text-sm">Direct links to Amazon, Target, and Walmart for each recommendation.</p>
            </div>
          </div>
          <div class="flex gap-4">
            <div class="text-3xl">🎮</div>
            <div>
              <h3 class="font-semibold">Play Quest</h3>
              <p class="opacity-70 text-sm">Get an immediate activity using toys you already own - no waiting for new purchases.</p>
            </div>
          </div>
          <div class="flex gap-4">
            <div class="text-3xl">📈</div>
            <div>
              <h3 class="font-semibold">Visual Insights</h3>
              <p class="opacity-70 text-sm">Skill radar chart shows coverage at a glance across all developmental areas.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA section -->
    <div class="py-16 px-4 bg-base-300/20">
      <div class="max-w-2xl mx-auto text-center">
        <h2 class="text-3xl font-bold mb-4" style="font-family: 'Fredoka', sans-serif;">
          Ready to Optimize Your Playroom?
        </h2>
        <p class="opacity-70 mb-8">
          Take a photo of your playroom and let our AI find the developmental gaps in your toy collection.
        </p>
        <RouterLink to="/" class="btn btn-primary gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Start Your Analysis
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
