import type { Request, Response } from "express";
import { Router } from "express";
import { getTripById } from "../../search/trip-registry";

const router: Router = Router();

router.get("/trips/:tripId", (req: Request, res: Response): void => {
  const { tripId } = req.params;

  if (!tripId || typeof tripId !== "string") {
    res.status(400).json({ error: "tripId is required" });
    return;
  }

  const trip = getTripById(tripId);

  if (!trip) {
    res.status(404).json({ error: "Trip not found" });
    return;
  }

  res.json(trip);
});

export default router;
