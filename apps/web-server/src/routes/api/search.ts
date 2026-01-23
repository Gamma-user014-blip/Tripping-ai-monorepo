import type { Request, Response } from "express";
import { Router } from "express";
import { getTripIdsForSearch } from "../../search/trip-registry";
import type {
  SearchPollRequest,
  SearchPollResponse,
} from "../../../../../shared/types";
import { SearchStatus } from "../../../../../shared/types";
import { getSearchStatus } from "../../search/search-store";

const router: Router = Router();

router.post("/poll", (req: Request, res: Response): void => {
  const body = req.body as Partial<SearchPollRequest>;
  const searchId = body.searchId;

  if (!searchId || typeof searchId !== "string") {
    res.status(400).json({ error: "searchId is required" });
    return;
  }

  const searchEntry = getSearchStatus(searchId);

  if (!searchEntry) {
    const response: SearchPollResponse = {
      status: SearchStatus.ERROR,
      error: "Search not found or expired",
    };
    res.status(404).json(response);
    return;
  }

  const response: SearchPollResponse = {
    status: searchEntry.status,
    results: searchEntry.results,
    error: searchEntry.error,
  };

  res.json(response);
});

router.get("/:searchId/trip-ids", (req: Request, res: Response): void => {
  const { searchId } = req.params;

  if (!searchId || typeof searchId !== "string") {
    res.status(400).json({ error: "searchId is required" });
    return;
  }

  const tripIds = getTripIdsForSearch(searchId);

  if (!tripIds) {
    res.status(404).json({ error: "Search not found or expired" });
    return;
  }

  res.json({ tripIds });
});

export default router;
