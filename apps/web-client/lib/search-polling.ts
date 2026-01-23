import { apiClient } from "../lib/api-client";
import {
  SearchPollRequest,
  SearchPollResponse,
  SearchStatus,
  Trip,
} from "../../../shared/types";

const POLL_INTERVAL_MS = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL_MS) || 10000;

interface PollOptions {
  onComplete: (trips: Trip[], tripIds: string[]) => void;
  onProgress?: (trips: Trip[], tripIds: string[]) => void;
  onError?: (error: string) => void;
}

type StopPolling = () => void;

const pollForSearchResults = (
  searchId: string,
  options: PollOptions,
): StopPolling => {
  let intervalId: NodeJS.Timeout | null = null;
  let isStopped = false;
  let lastResultCount = 0;

  const poll = async (): Promise<void> => {
    if (isStopped) return;

    try {
      const response = await apiClient.post<SearchPollResponse>(
        "/api/search/poll",
        {
          searchId,
        } satisfies SearchPollRequest,
      );

      if (isStopped) return;

      const results = response.results ?? [];
      const tripIds = response.tripIds ?? [];

      if (response.status === SearchStatus.COMPLETED) {
        stop();
        options.onComplete(results, tripIds);
      } else if (response.status === SearchStatus.IN_PROGRESS && results.length > lastResultCount) {
        lastResultCount = results.length;
        options.onProgress?.(results, tripIds);
      } else if (response.status === SearchStatus.ERROR) {
        stop();
        options.onError?.(response.error ?? "Unknown search error");
      }
    } catch (error) {
      console.error("Polling error:", error);
    }
  };

  const stop = (): void => {
    isStopped = true;
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };

  poll();
  intervalId = setInterval(poll, POLL_INTERVAL_MS);

  return stop;
};

export { pollForSearchResults };
export type { PollOptions, StopPolling };
