import { TripRequest, FinalTripLayout } from "@monorepo/shared";

const TRIP_BUILDER_URL =
  process.env.TRIP_BUILDER_URL || "http://trip_builder:8000";

/**
 * Calls the trip_builder service to create a final trip layout.
 */
export async function createTrip(
  request: TripRequest,
): Promise<FinalTripLayout> {
  const response = await fetch(`${TRIP_BUILDER_URL}/api/create_trip`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Failed to create trip: ${response.statusText} - ${errorText}`,
    );
  }

  return (await response.json()) as FinalTripLayout;
}
