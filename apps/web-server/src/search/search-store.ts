/**
 * @deprecated This file contains legacy mock-based search.
 * Use search-service.ts for the real trip-builder integration.
 * Keeping for reference/testing purposes.
 */

import type { Trip } from "@monorepo/shared";
import { SearchStatus } from "@monorepo/shared";
import mockData from "./mock-data";
import { registerSearchTrips } from "./trip-registry";

interface MockSearchEntry {
  status: SearchStatus;
  results?: Trip[];
  error?: string;
  createdAt: number;
}

const mockSearchStore: Map<string, MockSearchEntry> = new Map();

const MOCK_SEARCH_DELAY_MS = 10_000;
const MOCK_SEARCH_EXPIRY_MS = 5 * 60 * 1000;

const generateMockSearchId = (): string =>
  `mock_search_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

export const startMockSearch = (_tripYaml: string): string => {
  const searchId = generateMockSearchId();

  mockSearchStore.set(searchId, {
    status: SearchStatus.PENDING,
    createdAt: Date.now(),
  });

  setTimeout(() => {
    const entry = mockSearchStore.get(searchId);
    if (!entry) return;

    registerSearchTrips(searchId, mockData);

    mockSearchStore.set(searchId, {
      ...entry,
      status: SearchStatus.COMPLETED,
      results: mockData,
    });
  }, MOCK_SEARCH_DELAY_MS);

  return searchId;
};

export const getMockSearchStatus = (searchId: string): MockSearchEntry | null => {
  const entry = mockSearchStore.get(searchId);
  if (!entry) return null;

  if (Date.now() - entry.createdAt > MOCK_SEARCH_EXPIRY_MS) {
    mockSearchStore.delete(searchId);
    return null;
  }

  return entry;
};
