/**
 * Export utilities for transcription + analysis
 * Supports txt / json / pdf (txt fallback)
 * Added Jan 2025
 */

export type ExportFormat = "txt" | "json" | "pdf"

export interface ExportPayload {
  transcription: string
  segments?: { text: string; timestamp: number; confidence: number }[]
  concepts?: { term: string; relevance: number }[]
}

export function buildExportContent(payload: ExportPayload, format: ExportFormat) {
  switch (format) {
    case "txt":
      return { content: payload.transcription, mimeType: "text/plain", ext: "txt" }
    case "json":
      return {
        content: JSON.stringify({ ...payload, exportedAt: new Date().toISOString() }, null, 2),
        mimeType: "application/json",
        ext: "json",
      }
    case "pdf":
      return {
        content: `AI Learning Aid - Report\nDate: ${new Date().toLocaleDateString()}\n\nTranscription:\n${payload.transcription}\n\nConcepts:\n${(payload.concepts || []).map((c) => `- ${c.term} (${c.relevance}%)`).join("\n")}`,
        mimeType: "text/plain",
        ext: "txt",
      }
  }
}

export function downloadBlob(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
