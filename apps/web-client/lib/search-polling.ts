import { apiClient } from "../lib/api-client";
import {
  SearchPollRequest,
  SearchPollResponse,
  SearchStatus,
  Trip,
} from "../../../shared/types";

const POLL_INTERVAL_MS = 3000;

interface PollOptions {
  onComplete: (trips: Trip[]) => void;
  onError?: (error: string) => void;
}

type StopPolling = () => void;

const pollForSearchResults = (
  searchId: string,
  options: PollOptions,
): StopPolling => {
  let intervalId: NodeJS.Timeout | null = null;
  let isStopped = false;

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

      if (response.status === SearchStatus.COMPLETED && response.results) {
        stop();
        options.onComplete(response.results);
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
