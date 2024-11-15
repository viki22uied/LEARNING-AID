/**
 * Search filtering & sorting utilities
 * Extracted from page.tsx for testability
 * Added Nov 2024
 */

export interface SearchFilters {
  query: string
  difficulty: string
  type: string
  sortBy: string
}

export interface ResourceLike {
  title: string
  description: string
  difficulty: string
  type: string
  relevanceScore: number
  credibilityScore: number
  duration?: number
  readingTime?: number
}

export function filterResources<T extends ResourceLike>(resources: T[], filters: SearchFilters): T[] {
  const q = filters.query.toLowerCase()
  return resources
    .filter((r) => {
      const matchesSearch = !q || r.title.toLowerCase().includes(q) || r.description.toLowerCase().includes(q)
      const matchesDifficulty = filters.difficulty === "all" || r.difficulty === filters.difficulty
      const matchesType = filters.type === "all" || r.type === filters.type
      return matchesSearch && matchesDifficulty && matchesType
    })
    .sort((a, b) => {
      switch (filters.sortBy) {
        case "relevance":
          return b.relevanceScore - a.relevanceScore
        case "credibility":
          return b.credibilityScore - a.credibilityScore
        case "duration":
          return (a.duration || a.readingTime || 0) - (b.duration || b.readingTime || 0)
        case "difficulty": {
          const order = { beginner: 1, intermediate: 2, advanced: 3 } as const
          return (order[a.difficulty as keyof typeof order] || 99) - (order[b.difficulty as keyof typeof order] || 99)
        }
        default:
          return 0
      }
    })
}

export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, "0")}`
}
