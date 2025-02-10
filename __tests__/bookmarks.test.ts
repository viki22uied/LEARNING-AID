import { describe, it, expect, beforeEach } from "vitest"
import { getBookmarks, toggleBookmark, BOOKMARKS_KEY } from "@/lib/bookmarks"

beforeEach(() => localStorage.clear())

describe("bookmarks", () => {
  it("toggles bookmark", () => {
    toggleBookmark("1")
    expect(getBookmarks()).toContain("1")
    toggleBookmark("1")
    expect(getBookmarks()).not.toContain("1")
  })
  it("persists to localStorage", () => {
    toggleBookmark("a")
    expect(JSON.parse(localStorage.getItem(BOOKMARKS_KEY) || "[]")).toContain("a")
  })
})
