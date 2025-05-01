"use client"
import { Badge } from "@/components/ui/badge"

export interface ConceptNode {
  term: string
  relevance: number
  category: string
}

export function ConceptMap({ concepts, onSelect }: { concepts: ConceptNode[]; onSelect?: (t: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {concepts.map((c) => (
        <Badge
          key={c.term}
          variant={c.relevance > 80 ? "default" : "secondary"}
          className="cursor-pointer hover:scale-105 transition-transform"
          onClick={() => onSelect?.(c.term)}
        >
          {c.term} · {c.relevance}%
        </Badge>
      ))}
    </div>
  )
}
