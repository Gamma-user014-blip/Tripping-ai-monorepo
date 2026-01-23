import type { Trip } from '../../../../shared/types'

interface SearchTripIndex {
  tripIds: string[]
  createdAt: number
}

const tripStore: Map<string, Trip> = new Map()
const searchTripIndexStore: Map<string, SearchTripIndex> = new Map()

const SEARCH_EXPIRY_MS = 5 * 60 * 1000

const registerSearchTrips = (searchId: string, trips: Trip[]): string[] => {
  const tripIds: string[] = []

  for (const trip of trips) {
    const tripId = crypto.randomUUID()
    tripStore.set(tripId, trip)
    tripIds.push(tripId)
  }

  searchTripIndexStore.set(searchId, {
    tripIds,
    createdAt: Date.now(),
  })

  return tripIds
}

const getTripIdsForSearch = (searchId: string): string[] | null => {
  const entry = searchTripIndexStore.get(searchId)
  if (!entry) return null

  if (Date.now() - entry.createdAt > SEARCH_EXPIRY_MS) {
    searchTripIndexStore.delete(searchId)
    return null
  }

  return entry.tripIds
}

const getTripById = (tripId: string): Trip | null => {
  const trip = tripStore.get(tripId)
  return trip ?? null
}

const cleanupExpiredTrips = (): void => {
  const now = Date.now()
  for (const [searchId, entry] of searchTripIndexStore.entries()) {
    if (now - entry.createdAt > SEARCH_EXPIRY_MS) {
      searchTripIndexStore.delete(searchId)
    }
  }
}

setInterval(cleanupExpiredTrips, 60000)

export { registerSearchTrips, getTripIdsForSearch, getTripById }
