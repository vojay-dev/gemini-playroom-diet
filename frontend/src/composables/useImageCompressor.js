/**
 * Image compression utility for client-side image optimization.
 * Compresses images to stay under a target file size while preserving quality.
 */

const MAX_FILE_SIZE = 2.5 * 1024 * 1024 // 2.5 MB
const MAX_DIMENSION = 2048 // Max width or height
const INITIAL_QUALITY = 0.9
const MIN_QUALITY = 0.7
const QUALITY_STEP = 0.1

/**
 * Compress an image file to stay under the maximum file size.
 * Uses canvas-based resizing and JPEG compression.
 *
 * @param {File} file - The image file to compress
 * @returns {Promise<File>} - The compressed file (or original if already small enough)
 */
export async function compressImage(file) {
  // Skip compression if already under limit
  if (file.size <= MAX_FILE_SIZE) {
    return file
  }

  // Load image
  const img = await loadImage(file)

  // Calculate new dimensions (maintain aspect ratio)
  const { width, height } = calculateDimensions(img.width, img.height)

  // Create canvas and draw resized image
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height

  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0, width, height)

  // Compress with decreasing quality until under limit
  let quality = INITIAL_QUALITY
  let blob = await canvasToBlob(canvas, quality)

  while (blob.size > MAX_FILE_SIZE && quality > MIN_QUALITY) {
    quality -= QUALITY_STEP
    blob = await canvasToBlob(canvas, quality)
  }

  // If still too large, reduce dimensions further
  if (blob.size > MAX_FILE_SIZE) {
    const scaleFactor = Math.sqrt(MAX_FILE_SIZE / blob.size) * 0.9
    const newWidth = Math.floor(width * scaleFactor)
    const newHeight = Math.floor(height * scaleFactor)

    canvas.width = newWidth
    canvas.height = newHeight
    ctx.drawImage(img, 0, 0, newWidth, newHeight)

    blob = await canvasToBlob(canvas, MIN_QUALITY)
  }

  // Create new File from blob
  const compressedFile = new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), {
    type: 'image/jpeg',
    lastModified: Date.now()
  })

  console.log(`Image compressed: ${formatSize(file.size)} -> ${formatSize(compressedFile.size)}`)

  return compressedFile
}

/**
 * Load an image file into an HTMLImageElement
 */
function loadImage(file) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(img.src)
      resolve(img)
    }
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}

/**
 * Calculate new dimensions while maintaining aspect ratio
 */
function calculateDimensions(width, height) {
  if (width <= MAX_DIMENSION && height <= MAX_DIMENSION) {
    return { width, height }
  }

  const ratio = Math.min(MAX_DIMENSION / width, MAX_DIMENSION / height)
  return {
    width: Math.floor(width * ratio),
    height: Math.floor(height * ratio)
  }
}

/**
 * Convert canvas to blob with specified quality
 */
function canvasToBlob(canvas, quality) {
  return new Promise((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', quality)
  })
}

/**
 * Format file size for logging
 */
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}
