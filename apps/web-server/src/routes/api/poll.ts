import type { Request, Response } from "express";
import { Router } from "express";
import type { SearchPollRequest, SearchPollResponse } from "@monorepo/shared";
import { SearchStatus } from "@monorepo/shared";
import { getSearchEntry } from "../../search/search-service";

const router: Router = Router();

router.post("/poll", (req: Request, res: Response): void => {
  const { searchId } = req.body as Partial<SearchPollRequest>;

  if (!searchId || typeof searchId !== "string") {
    res.status(400).json({ error: "searchId is required" });
    return;
  }

  const entry = getSearchEntry(searchId);

  if (!entry) {
    const response: SearchPollResponse = {
      status: SearchStatus.ERROR,
      error: "Search not found or expired",
    };
    res.status(404).json(response);
    return;
  }

  const response: SearchPollResponse = {
    status: entry.status,
    results: entry.results,
    error: entry.error,
  };

  res.json(response);
});

export default router;