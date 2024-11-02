/**
 * Bookmark persistence utilities
 * Stores bookmarked resource IDs in localStorage
 * Added Nov 2024 - reconstructed history
 */

export const BOOKMARKS_KEY = "learning-aid:bookmarks"

export function getBookmarks(): string[] {
  if (typeof window === "undefined") return []
  try {
    const raw = localStorage.getItem(BOOKMARKS_KEY)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

export function setBookmarks(ids: string[]): void {
  if (typeof window === "undefined") return
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(ids))
}

export function toggleBookmark(id: string): string[] {
  const current = getBookmarks()
  const next = current.includes(id) ? current.filter((x) => x !== id) : [...current, id]
  setBookmarks(next)
  return next
}

export function isBookmarked(id: string): boolean {
  return getBookmarks().includes(id)
}
