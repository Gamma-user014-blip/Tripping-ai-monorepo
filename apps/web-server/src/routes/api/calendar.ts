import { Router, Request, Response } from "express";
import { google } from "googleapis";
import { getUserTokensMemory, saveUserTokensMemory } from "../../db/tokenStore"; // adjust path
import { TripResult } from "../../types";
import { Credentials } from "google-auth-library";

const router: Router = Router();

// Remove requireAuth entirely

router.post(
  "/remove-trip-from-calendar",
  async (req: Request, res: Response) => {
    const { eventIds, state } = req.body as {
      eventIds: string[];
      state?: string;
    };

    if (!eventIds || !eventIds.length) {
      return res.status(400).json({ error: "No event IDs provided" });
    }

    if (!state) {
      return res.status(401).json({ error: "Missing auth state" });
    }

    try {
const userTokens = getUserTokensMemory(state);
      console.log("[Calendar] Retrieved userTokens for state:", userTokens);

if (!userTokens) {
  return res.status(401).json({ error: "Google authentication required" });
}

      const oauth2Client = new google.auth.OAuth2(
        process.env.GOOGLE_CLIENT_ID,
        process.env.GOOGLE_CLIENT_SECRET,
        `${process.env.BASE_URL || "http://localhost:3001"}/api/auth/callback`
      );
oauth2Client.setCredentials(userTokens);

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
      res
        .status(500)
        .json({ error: "Failed to remove events from calendar" });
    }
  }
);


router.post(
  "/add-trip-to-calendar",
  async (req: Request, res: Response) => {
    console.log("[Calendar] Received request");
    const { trip, state } = req.body as { trip: TripResult; state?: string };

    if (!trip) {
      console.log("[Calendar] No trip data provided.");
      return res.status(400).json({ error: "Trip data required" });
    }

    if (!state) {
      // No auth state yet → signal frontend to start OAuth
      return res.status(401).json({ error: "Google authentication required" });
    }

    try {
const userTokens = await getUserTokensMemory(state);
      console.log("[Calendar] Retrieved userTokens for state:", userTokens);

if (!userTokens) {
  console.log("Calendar: No tokens for this state");
  return res.status(401).json({ error: "Google authentication required" });
}

      console.log("[Calendar] Creating OAuth2 client...");
const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  `${process.env.BASE_URL}/api/auth/callback`,
);
      console.log(
        "[Calendar] OAuth2 Client created with ID:",
        process.env.GOOGLE_CLIENT_ID
      );

oauth2Client.setCredentials(userTokens);
      console.log(
        "[Calendar] Set credentials:",
        userTokens
      );

if (userTokens.expiry_date && userTokens.expiry_date < Date.now()) {
  if (!userTokens.refresh_token) {
    console.log(
      "[Calendar] Cannot refresh token, no refresh token available."
    );
    return res.status(401).json({
      error: "Google token expired, please re-authenticate.",
    });
  } else {
    const { credentials } = await oauth2Client.refreshAccessToken();
    oauth2Client.setCredentials(credentials);
    // save updated tokens back in memory, not Mongo
    saveUserTokensMemory(state, credentials as Credentials);
    console.log(
      "[Calendar] Token refreshed and saved in memory for state:",
      state
    );
  }
}

      const calendar = google.calendar({ version: "v3", auth: oauth2Client });
      const createdEventIds: string[] = [];

      // Create main trip event
      const formatDate = (isoString: string) => isoString.split("T")[0];

      const tripEvent = {
        summary: `Trip to ${trip.destination.city}`,
        description: `Trip ID: ${trip.tripId}`,
        start: { date: formatDate(trip.startDate) },
        end: {
          date: formatDate(
            new Date(
              new Date(trip.endDate).getTime() + 24 * 60 * 60 * 1000
            ).toISOString()
          ),
        },
        location: `${trip.origin.city}, ${trip.origin.country} to ${trip.destination.city}, ${trip.destination.country}`,
      };
      console.log("[Calendar] Creating main trip event:", tripEvent);

      const tripResponse = await calendar.events.insert({
        calendarId: "primary",
        requestBody: tripEvent,
      });
      console.log(
        "[Calendar] Trip event created, ID:",
        tripResponse.data.id
      );
      createdEventIds.push(tripResponse.data.id!);

      // Create events for each hotel
      let currentHotelStart = new Date(trip.startDate);

      for (const hotel of trip.hotels) {
        const nightsMatch = hotel.dateRange.match(/\d+/);
        const nights = nightsMatch ? parseInt(nightsMatch[0], 10) : 1;

        const hotelStart = new Date(currentHotelStart);
        const hotelEnd = new Date(hotelStart);
        hotelEnd.setDate(hotelEnd.getDate() + nights);

        const hotelEvent = {
          summary: `Stay at ${hotel.name}`,
          description: `Hotel in ${hotel.location.city}, ${hotel.location.country}`,
          start: { date: hotelStart.toISOString().split("T")[0] },
          end: { date: hotelEnd.toISOString().split("T")[0] },
          location: `${hotel.location.city}, ${hotel.location.country}`,
        };

        console.log("[Calendar] Creating hotel event:", hotelEvent);

        const hotelResponse = await calendar.events.insert({
          calendarId: "primary",
          requestBody: hotelEvent,
        });
        console.log(
          "[Calendar] Hotel event created, ID:",
          hotelResponse.data.id
        );
        createdEventIds.push(hotelResponse.data.id!);

        currentHotelStart = hotelEnd;
      }

      console.log("[Calendar] All events created:", createdEventIds);
      res.json({ createdEventIds });
    } catch (error) {
      console.error("[Calendar] Error creating calendar events:", error);
      res.status(500).json({ error: "Failed to add trip to calendar" });
    }
  }
);

export default router;
