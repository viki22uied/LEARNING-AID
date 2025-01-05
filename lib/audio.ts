/**
 * Audio helpers for recording and playback
 * Added Jan 2025
 */

export const SUPPORTED_AUDIO_TYPES = [
  "audio/mp3",
  "audio/mpeg",
  "audio/wav",
  "audio/x-wav",
  "audio/m4a",
  "audio/x-m4a",
  "audio/aac",
  "audio/ogg",
  "audio/webm",
]

export const SUPPORTED_EXTS = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".webm"]

export const MAX_AUDIO_BYTES = 50 * 1024 * 1024

export function isSupportedAudio(file: File): boolean {
  const lower = file.name.toLowerCase()
  const extOk = SUPPORTED_EXTS.some((e) => lower.endsWith(e))
  return SUPPORTED_AUDIO_TYPES.includes(file.type) || extOk
}

export function validateAudioFile(file: File): string | null {
  if (file.size > MAX_AUDIO_BYTES) return `File "${file.name}" exceeds 50MB limit`
  if (!isSupportedAudio(file)) return `Unsupported format: ${file.type || "unknown"}`
  return null
}
