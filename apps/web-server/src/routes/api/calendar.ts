import { Router, Request, Response } from "express";
import { google } from "googleapis";
import { getUserTokens, saveUserTokens, UserTokens } from "../../db/mongo-util";
import { TripResult } from "../../types";

declare global {
  namespace Express {
    interface Request {
      userTokens?: UserTokens;
    }
  }
}

const router: Router = Router();

// Middleware to check auth
const requireAuth = async (req: Request, res: Response, next: any) => {
  console.log("[Auth] Checking authentication...");

  const userId = req.session?.id;
  console.log("[Auth] Session userId:", userId);

  if (!userId) {
    console.log("[Auth] No session userId found.");
    return res.status(401).json({ error: "Not authenticated" });
  }

  const userTokens = await getUserTokens(userId);
  console.log("[Auth] Retrieved userTokens:", userTokens);

  if (!userTokens) {
    console.log("[Auth] No Google tokens found for user.");
    return res.status(401).json({ error: "Google authentication required" });
  }

  req.userTokens = userTokens;
  next();
};



router.post("/remove-trip-from-calendar", requireAuth, async (req: Request, res: Response) => {
  const { eventIds } = req.body as { eventIds: string[] };

  if (!eventIds || !eventIds.length) {
    return res.status(400).json({ error: "No event IDs provided" });
  }

  try {
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      `${process.env.BASE_URL || 'http://localhost:3001'}/api/auth/callback`
    );
    oauth2Client.setCredentials(req.userTokens!.googleTokens);

    const calendar = google.calendar({ version: "v3", auth: oauth2Client });

    for (const id of eventIds) {
      await calendar.events.delete({
        calendarId: "primary",
        eventId: id,
      });
      console.log("[Calendar] Deleted event:", id);
    }

    res.json({ success: true, deletedEventIds: eventIds });
  } catch (error) {
    console.error("[Calendar] Error deleting events:", error);
    res.status(500).json({ error: "Failed to remove events from calendar" });
  }
});



router.post("/add-trip-to-calendar", requireAuth, async (req: Request, res: Response) => {
  console.log("[Calendar] Received request body:", req.body);
  const trip: TripResult = req.body;
  if (!trip) {
    console.log("[Calendar] No trip data provided.");
    return res.status(400).json({ error: "Trip data required" });
  }

  try {
    console.log("[Calendar] Creating OAuth2 client...");
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      `${process.env.BASE_URL || 'http://localhost:3001'}/api/auth/callback`
    );
    console.log("[Calendar] OAuth2 Client created with ID:", process.env.GOOGLE_CLIENT_ID);

    oauth2Client.setCredentials(req.userTokens!.googleTokens);
    console.log("[Calendar] Set credentials:", req.userTokens!.googleTokens);

    // Refresh token if expired
    if (req.userTokens!.googleTokens.expiry_date && req.userTokens!.googleTokens.expiry_date < Date.now()) {
      console.log("[Calendar] Access token expired. Refreshing...");
      const { credentials } = await oauth2Client.refreshAccessToken();
      oauth2Client.setCredentials(credentials);
      console.log("[Calendar] Token refreshed:", credentials);
      // Update in DB
      await saveUserTokens(req.session!.id, credentials);
      console.log("[Calendar] Saved refreshed tokens to DB");
    }

    const calendar = google.calendar({ version: "v3", auth: oauth2Client });
    const createdEventIds: string[] = [];

    // Create main trip event
const formatDate = (isoString: string) => isoString.split('T')[0];

const tripEvent = {
  summary: `Trip from ${trip.origin.city} to ${trip.destination.city}`,
  description: `Trip ID: ${trip.tripId}`,
  start: { date: formatDate(trip.startDate) },
  end: { date: formatDate(new Date(new Date(trip.endDate).getTime() + 24*60*60*1000).toISOString()) },
  location: `${trip.origin.city}, ${trip.origin.country} to ${trip.destination.city}, ${trip.destination.country}`,
};
    console.log("[Calendar] Creating main trip event:", tripEvent);

    const tripResponse = await calendar.events.insert({
      calendarId: "primary",
      requestBody: tripEvent,
    });
    console.log("[Calendar] Trip event created, ID:", tripResponse.data.id);
    createdEventIds.push(tripResponse.data.id!);

    // Create events for each hotel
let currentHotelStart = new Date(trip.startDate); // start from trip start

for (const hotel of trip.hotels) {
  // Extract number of nights from string like "3 nights"
  const nightsMatch = hotel.dateRange.match(/\d+/);
  const nights = nightsMatch ? parseInt(nightsMatch[0], 10) : 1;

  const hotelStart = new Date(currentHotelStart); // clone current start
  const hotelEnd = new Date(hotelStart);
  hotelEnd.setDate(hotelEnd.getDate() + nights); // end is one day after last night

  const hotelEvent = {
    summary: `Stay at ${hotel.name}`,
    description: `Hotel in ${hotel.location.city}, ${hotel.location.country}`,
    start: { date: hotelStart.toISOString().split("T")[0] }, // all-day format
    end: { date: hotelEnd.toISOString().split("T")[0] },
    location: `${hotel.location.city}, ${hotel.location.country}`,
  };

  console.log("[Calendar] Creating hotel event:", hotelEvent);

  const hotelResponse = await calendar.events.insert({
    calendarId: "primary",
    requestBody: hotelEvent,
  });
  console.log("[Calendar] Hotel event created, ID:", hotelResponse.data.id);
  createdEventIds.push(hotelResponse.data.id!);

  // update start date for next hotel
  currentHotelStart = hotelEnd;
}


    console.log("[Calendar] All events created:", createdEventIds);
    res.json({ createdEventIds });
  } catch (error) {
    console.error("[Calendar] Error creating calendar events:", error);
    res.status(500).json({ error: "Failed to add trip to calendar" });
  }
});

export default router;
