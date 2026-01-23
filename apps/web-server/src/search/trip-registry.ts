import type { Trip } from "@monorepo/shared";

interface SearchTripIndex {
  tripIds: string[];
  createdAt: number;
}

const tripStore: Map<string, Trip> = new Map();
const searchTripIndexStore: Map<string, SearchTripIndex> = new Map();

const SEARCH_EXPIRY_MS = 5 * 60 * 1000;

const registerSearchTrips = (searchId: string, trips: Trip[]): string[] => {
  const existingEntry = searchTripIndexStore.get(searchId);
  const existingTripIds = existingEntry?.tripIds ?? [];
  const tripIds: string[] = [...existingTripIds];

  // Only register new trips (trips beyond what we've already registered)
  for (let i = existingTripIds.length; i < trips.length; i++) {
    const tripId = crypto.randomUUID();
    tripStore.set(tripId, trips[i]);
    tripIds.push(tripId);
  }

  searchTripIndexStore.set(searchId, {
    tripIds,
    createdAt: existingEntry?.createdAt ?? Date.now(),
  });

  return tripIds;
};

const getTripIdsForSearch = (searchId: string): string[] | null => {
  const entry = searchTripIndexStore.get(searchId);
  if (!entry) return null;

  if (Date.now() - entry.createdAt > SEARCH_EXPIRY_MS) {
    searchTripIndexStore.delete(searchId);
    return null;
  }

  return entry.tripIds;
};

const getTripById = (tripId: string): Trip | null => {
  const trip = tripStore.get(tripId);
  return trip ?? null;
};

const cleanupExpiredTrips = (): void => {
  const now = Date.now();
  for (const [searchId, entry] of searchTripIndexStore.entries()) {
    if (now - entry.createdAt > SEARCH_EXPIRY_MS) {
      searchTripIndexStore.delete(searchId);
    }
  }
};

setInterval(cleanupExpiredTrips, 60000);

export { registerSearchTrips, getTripIdsForSearch, getTripById };
