# Playroom Diet - Frontend

Vue.js 3 single-page application for the Playroom Diet analysis tool.

## Features

- **Photo Upload**: Upload or capture playroom photos, with example images
- **Smart Image Compression**: Client-side optimization keeps uploads under 1.5MB
- **Age Slider**: Select child's age (1-12 years)
- **Results Dashboard**: Displays skill radar, 6-month roadmap, and Play Quest
- **Toy Heatmap**: AI detection overlay showing identified toys with bounding boxes
- **Share Card**: Generate shareable result images
- **System Overview**: Visual pipeline diagram using Vue Flow
- **Toast Notifications**: Non-intrusive feedback system
- **Confetti Celebration**: Fun animation on successful analysis

## Tech Stack

- Vue.js 3 (Composition API)
- Vite 7
- Tailwind CSS 4 + daisyUI 5
- Vue Router 4
- Vue Flow (pipeline visualization)
- Three.js (3D background)
- canvas-confetti

## Project Structure

```
src/
├── components/
│   ├── Home.vue          # Upload form
│   ├── ScanResult.vue    # Results dashboard
│   ├── SkillRadar.vue    # Radar chart component
│   ├── ShareCard.vue     # Shareable image generator
│   ├── SystemOverview.vue # Pipeline diagram
│   ├── About.vue         # About page
│   └── PlayroomScene.vue # 3D background
├── composables/
│   ├── useToast.js       # Toast notification system
│   └── useImageCompressor.js # Client-side image compression
├── router.js             # Route definitions
├── main.js               # App entry point
└── App.vue               # Root component
```

## Image Compression

The frontend automatically compresses large images before upload to avoid Supabase storage limits:

- **Target size**: <= 1.5 MB
- **Max dimensions**: 2048px (maintains aspect ratio)
- **Quality**: Starts at 90%, reduces iteratively if needed
- **Format**: Converts to JPEG for consistent compression

Users see a toast notification when compression saves significant space.

## Setup

```sh
npm install
```

## Development

```sh
npm run dev
```

Runs at `http://localhost:5173`

## Environment Variables

Create `.env` file:

```
GPD_API_URL=http://localhost:8000
```

For production, set this to your Cloud Run backend URL.

## Build

```sh
npm run build
```

Output goes to `dist/` directory.

## Deployment

Deployed to Firebase Hosting. See `DEPLOYMENT.md` in root directory for instructions.
