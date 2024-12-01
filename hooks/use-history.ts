"use client"
import { useEffect, useState } from "react"

export interface SessionRecord {
  id: string
  timestamp: string
  transcript: string
  concepts: string[]
  resourceCount: number
}

const KEY = "learning-aid:sessions"

export function useHistory() {
  const [sessions, setSessions] = useState<SessionRecord[]>([])

  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY)
      if (raw) setSessions(JSON.parse(raw))
    } catch {}
  }, [])

  const addSession = (s: Omit<SessionRecord, "id" | "timestamp">) => {
    const record: SessionRecord = { ...s, id: crypto.randomUUID(), timestamp: new Date().toISOString() }
    const next = [record, ...sessions].slice(0, 20)
    setSessions(next)
    localStorage.setItem(KEY, JSON.stringify(next))
  }

  const clearHistory = () => {
    setSessions([])
    localStorage.removeItem(KEY)
  }

  return { sessions, addSession, clearHistory }
}
