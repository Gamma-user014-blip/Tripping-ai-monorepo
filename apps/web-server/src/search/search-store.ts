import type { Trip } from '../../../../shared/types'
import { SearchStatus } from '../../../../shared/types'
import mockData from './mock-data'
import { registerSearchTrips } from './trip-registry'

interface SearchEntry {
  status: SearchStatus
  results?: Trip[]
  error?: string
  createdAt: number
}

const searchStore: Map<string, SearchEntry> = new Map()

const SEARCH_DELAY_MS = 10000
const SEARCH_EXPIRY_MS = 5 * 60 * 1000

const generateSearchId = (): string => {
  return `search_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

const startSearch = (): string => {
  const searchId = generateSearchId()

  searchStore.set(searchId, {
    status: SearchStatus.PENDING,
    createdAt: Date.now(),
  })

  setTimeout(() => {
    const entry = searchStore.get(searchId)
    if (!entry) return

    registerSearchTrips(searchId, mockData)

    searchStore.set(searchId, {
      ...entry,
      status: SearchStatus.COMPLETED,
      results: mockData,
    })
  }, SEARCH_DELAY_MS)

  return searchId
}

const getSearchStatus = (searchId: string): SearchEntry | null => {
  const entry = searchStore.get(searchId)
  if (!entry) return null

  if (Date.now() - entry.createdAt > SEARCH_EXPIRY_MS) {
    searchStore.delete(searchId)
    return null
  }

  return entry
}

const cleanupExpiredSearches = (): void => {
  const now = Date.now()
  for (const [searchId, entry] of searchStore.entries()) {
    if (now - entry.createdAt > SEARCH_EXPIRY_MS) {
      searchStore.delete(searchId)
    }
  }
}

setInterval(cleanupExpiredSearches, 60000)

export { startSearch, getSearchStatus }
