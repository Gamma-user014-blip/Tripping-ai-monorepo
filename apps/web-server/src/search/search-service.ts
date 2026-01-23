import type { Trip } from "@monorepo/shared";
import { SearchStatus } from "@monorepo/shared";
import { generatePlans, buildTripRequest } from "../chat/json-agent-util";
import { createTrip } from "../chat/trip-builder-util";
import mockData from "./mock-data";

export interface SearchProgress {
  totalPlans: number;
  completedPlans: number;
  currentVibe?: string;
}

export interface SearchEntry {
  status: SearchStatus;
  results: Trip[];
  progress: SearchProgress;
  error?: string;
  createdAtMs: number;
  updatedAtMs: number;
}

const searchStore: Map<string, SearchEntry> = new Map();

const SEARCH_EXPIRY_MS: number = 10 * 60 * 1000;

const generateSearchId = (): string =>
  `search_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

const createInitialEntry = (): SearchEntry => ({
  status: SearchStatus.PENDING,
  results: [],
  progress: { totalPlans: 0, completedPlans: 0 },
  createdAtMs: Date.now(),
  updatedAtMs: Date.now(),
});

const updateEntry = (
  searchId: string,
  update: Partial<SearchEntry>,
): SearchEntry | null => {
  const entry = searchStore.get(searchId);
  if (!entry) return null;

  const updated: SearchEntry = {
    ...entry,
    ...update,
    updatedAtMs: Date.now(),
  };
  searchStore.set(searchId, updated);
  return updated;
};

const processPlans = async (searchId: string, tripYaml: string): Promise<void> => {
  const plans = await generatePlans(tripYaml);

  updateEntry(searchId, {
    progress: { totalPlans: plans.length, completedPlans: 0 },
  });

  for (const plan of plans) {
    const entry = searchStore.get(searchId);
    if (!entry || entry.status === SearchStatus.ERROR) break;

    updateEntry(searchId, {
      progress: {
        ...entry.progress,
        currentVibe: plan.vibe,
      },
    });

    try {
      const { trip_request: tripRequest } = await buildTripRequest(plan.vibe, plan.actions);
      const layout = await createTrip(tripRequest);

      const trip: Trip = { vibe: plan.vibe, layout };

      const current = searchStore.get(searchId);
      if (!current) break;

      const newCompletedCount = current.progress.completedPlans + 1;

      updateEntry(searchId, {
        status: SearchStatus.IN_PROGRESS,
        results: [...current.results, trip],
        progress: {
          totalPlans: plans.length,
          completedPlans: newCompletedCount,
          currentVibe: undefined,
        },
      });
    } catch (tripError) {
      console.error(`Failed to process trip "${plan.vibe}":`, tripError);
      // Continue with next trip instead of failing the entire search
      const current = searchStore.get(searchId);
      if (current) {
        updateEntry(searchId, {
          progress: {
            ...current.progress,
            completedPlans: current.progress.completedPlans + 1,
            currentVibe: undefined,
          },
        });
      }
    }
  }

  const final = searchStore.get(searchId);
  if (final && final.status !== SearchStatus.ERROR) {
    updateEntry(searchId, { status: SearchStatus.COMPLETED });
  }
};

export const startSearch = (tripYaml: string): string => {
  const searchId = generateSearchId();
  searchStore.set(searchId, createInitialEntry());

  processPlans(searchId, tripYaml).catch((error: Error) => {
    console.error(`Search ${searchId} failed:`, error);
    updateEntry(searchId, {
      status: SearchStatus.ERROR,
      error: error.message,
    });
  });

  return searchId;
};

export const getSearchEntry = (searchId: string): SearchEntry | null => {
  const entry = searchStore.get(searchId);
  if (!entry) return null;

  if (Date.now() - entry.createdAtMs > SEARCH_EXPIRY_MS) {
    searchStore.delete(searchId);
    return null;
  }

  return entry;
};

export const cleanupExpiredSearches = (): void => {
  const now = Date.now();
  for (const [searchId, entry] of searchStore) {
    if (now - entry.createdAtMs > SEARCH_EXPIRY_MS) {
      searchStore.delete(searchId);
    }
  }
};

const processMockPlans = async (searchId: string): Promise<void> => {
  const mockTrips = mockData;

  updateEntry(searchId, {
    progress: { totalPlans: mockTrips.length, completedPlans: 0 },
  });

  for (let i = 0; i < mockTrips.length; i++) {
    const entry = searchStore.get(searchId);
    if (!entry || entry.status === SearchStatus.ERROR) break;

    // Simulate some delay to show progressive loading
    await new Promise((resolve) => setTimeout(resolve, 500));

    const current = searchStore.get(searchId);
    if (!current) break;

    updateEntry(searchId, {
      status: SearchStatus.IN_PROGRESS,
      results: [...current.results, mockTrips[i]],
      progress: {
        totalPlans: mockTrips.length,
        completedPlans: i + 1,
        currentVibe: undefined,
      },
    });
  }

  const final = searchStore.get(searchId);
  if (final && final.status !== SearchStatus.ERROR) {
    updateEntry(searchId, { status: SearchStatus.COMPLETED });
  }
};

export const startMockSearch = (): string => {
  const searchId = generateSearchId();
  searchStore.set(searchId, createInitialEntry());

  processMockPlans(searchId).catch((error: Error) => {
    console.error(`Mock search ${searchId} failed:`, error);
    updateEntry(searchId, {
      status: SearchStatus.ERROR,
      error: error.message,
    });
  });

  return searchId;
};

setInterval(cleanupExpiredSearches, 60_000);
