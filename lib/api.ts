/**
 * API client for /api/analyze with fallback
 * Added Jan 2025 - improves resilience when backend unavailable
 */

export interface AnalyzeResponse {
  transcript: { text: string }
  segments: { text: string; timestamp: number; confidence: number }[]
  concepts: { term: string; category: string; relevance: number; confidence: number }[]
  recommendations: unknown[]
}

export async function analyzeAudio(file: File): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append("audio", file)
  const res = await fetch("/api/analyze", { method: "POST", body: form })
  if (!res.ok) throw new Error(`Backend error ${res.status}`)
  return (await res.json()) as AnalyzeResponse
}

export function isAnalyzeAvailable(): boolean {
  return typeof fetch !== "undefined"
}
