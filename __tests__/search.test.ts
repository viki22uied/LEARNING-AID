import { describe, it, expect } from "vitest"
import { filterResources, formatTime } from "@/lib/search"

describe("filterResources", () => {
  const data = [
    { title: "ML Intro", description: "basics", difficulty: "beginner", type: "document", relevanceScore: 90, credibilityScore: 95, readingTime: 30 },
    { title: "Advanced NN", description: "deep", difficulty: "advanced", type: "video", relevanceScore: 80, credibilityScore: 98, duration: 20 },
  ]

  it("filters by query", () => {
    expect(filterResources(data, { query: "ml", difficulty: "all", type: "all", sortBy: "relevance" })).toHaveLength(1)
  })
  it("sorts by relevance", () => {
    const sorted = filterResources(data, { query: "", difficulty: "all", type: "all", sortBy: "relevance" })
    expect(sorted[0].title).toBe("ML Intro")
  })
  it("filters by difficulty", () => {
    expect(filterResources(data, { query: "", difficulty: "beginner", type: "all", sortBy: "relevance" })).toHaveLength(1)
  })
})

describe("formatTime", () => {
  it("formats 0 and 65s", () => {
    expect(formatTime(0)).toBe("0:00")
    expect(formatTime(65)).toBe("1:05")
  })
})
