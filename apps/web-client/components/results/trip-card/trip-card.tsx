import React from "react";
import { useRouter } from "next/router";
import {
  Trip,
  SectionType,
  FlightOption,
  HotelOption,
  Money,
  Location,
  ActivityOption,
  TransportOption,
} from "../types";
import HotelCard from "./hotel-card";
import TripHighlights from "./trip-highlights";
import FlightDetails from "./flight-details";
import TripMap from "./trip-map";
import styles from "./trip-card.module.css";
import {
  SectionData,
  isFlightOption,
  isFinalStayOption,
  isTransportOption,
} from "../../../lib/trip-type-guards";
import { convertToUSD } from "../../../lib/currency";
import { apiClient } from "../../../lib/api-client";
import { formatLocationLabel } from "../../../lib/location-format";
import {
  getOrCreateSessionId,
  SEARCH_ID_KEY_PREFIX,
  TRIP_IDS_KEY_PREFIX,
} from "../../../lib/session";

interface TripCardProps {
  trip: Trip;
  tripId?: string;
  tripIndex: number;
}

interface TripHighlight {
  date: string;
  endDate?: string;
  nights?: number;
  title: string;
  type: "flight" | "stay" | "activity" | "transport";
  location: Location;
}

interface ExtractedTripData {
  hotels: HotelOption[];
  flights: FlightOption[];
  activities: ActivityOption[];
  transfers: TransportOption[];
  highlights: TripHighlight[];
  waypoints: Array<{ lat: number; lng: number; label: string }>;
  totalPrice: Money;
  origin: Location;
  destination: Location;
  tripStartDate: string;
  tripEndDate: string;
  mapCenter: { lat: number; lng: number };
  vibe: string;
}

const extractTripData = (trip: Trip): ExtractedTripData => {
  const hotels: HotelOption[] = [];
  const flights: FlightOption[] = [];
  const activities: ActivityOption[] = [];
  const transfers: TransportOption[] = [];
  const highlights: TripHighlight[] = [];
  const staySections: Array<{ hotel: HotelOption; activities: ActivityOption[] }> = [];
  const stayHighlightRefs: Array<{ highlightIndex: number; stayIndex: number }> = [];
  const orderedPath: Array<{ lat: number; lng: number; label: string }> = [];
  let totalPrice = 0;
  let origin: Location | null = null;
  let mainDestination: Location | null = null;

  const flightDates: string[] = [];

  const getIsoDate = (dateTime: string): string => dateTime.split("T")[0];

  const addDays = (isoDate: string, days: number): string => {
    const base = new Date(`${isoDate}T00:00:00.000Z`);
    base.setUTCDate(base.getUTCDate() + days);
    return base.toISOString().slice(0, 10);
  };

  const diffNights = (startIso: string, endIso: string): number => {
    const start = new Date(`${startIso}T00:00:00.000Z`);
    const end = new Date(`${endIso}T00:00:00.000Z`);
    const diffMs = end.getTime() - start.getTime();
    return Math.floor(diffMs / (1000 * 60 * 60 * 24));
  };

  // First pass: collect all data and extract dates from flights
  for (const section of trip.layout.sections) {
    const data = section.data as SectionData;

    if (section.type === SectionType.FLIGHT && isFlightOption(data)) {
      flights.push(data);
      totalPrice += convertToUSD(
        data.total_price.amount,
        data.total_price.currency,
      );

      if (!origin) {
        origin = data.outbound.origin;
      }

      const flightDest = data.outbound.destination;
      const isReturnFlight =
        origin &&
        flightDest.latitude === origin.latitude &&
        flightDest.longitude === origin.longitude;

      // Track all flight dates for stay date calculation
      flightDates.push(getIsoDate(data.outbound.departure_time));

      if (!isReturnFlight) {
        mainDestination = flightDest;
        orderedPath.push({
          lat: flightDest.latitude,
          lng: flightDest.longitude,
          label: formatLocationLabel(flightDest),
        });
      }

      const flightLabel = formatLocationLabel(flightDest);
      highlights.push({
        date: getIsoDate(data.outbound.departure_time),
        title: isReturnFlight
          ? `Flight to ${flightLabel}`
          : `Flight to ${flightLabel}`,
        type: "flight",
        location: flightDest,
      });
    } else if (section.type === SectionType.STAY && isFinalStayOption(data)) {
      // Skip empty/invalid hotel stays
      if (!data.hotel?.id || !data.hotel?.name) {
        continue;
      }

      hotels.push(data.hotel);
      const stayIndex = staySections.length;
      staySections.push({ hotel: data.hotel, activities: data.activities });

      totalPrice += convertToUSD(
        data.hotel.total_price.amount,
        data.hotel.total_price.currency,
      );

      orderedPath.push({
        lat: data.hotel.location.latitude,
        lng: data.hotel.location.longitude,
        label: data.hotel.location.city,
      });

      for (const activity of data.activities) {
        activities.push(activity);
      }

      // Preserve highlight order exactly as sections arrive.
      // Dates will be filled in later once we know tripStartDate/tripEndDate.
      const highlightIndex = highlights.length;
      highlights.push({
        date: "",
        endDate: undefined,
        title: `Stay in ${data.hotel.name}, ${data.hotel.location.city}`,
        type: "stay",
        location: data.hotel.location,
      });
      stayHighlightRefs.push({ highlightIndex, stayIndex });
    } else if (
      section.type === SectionType.TRANSFER &&
      isTransportOption(data)
    ) {
      transfers.push(data);
      totalPrice += convertToUSD(
        data.total_price.amount,
        data.total_price.currency,
      );
    }
  }

  // Calculate total nights from all hotels (fallback)
  const totalNightsFromHotels = hotels.reduce((sum, h) => {
    if (h.price_per_night.amount > 0) {
      return sum + Math.round(h.total_price.amount / h.price_per_night.amount);
    }
    return sum + 1;
  }, 0);

  // Trip dates come from flights only
  const tripStartDate = flightDates.length > 0 ? flightDates[0] : "";
  const tripEndDate = flightDates.length > 1 ? flightDates[flightDates.length - 1] :
    (tripStartDate && totalNightsFromHotels > 0 ? addDays(tripStartDate, totalNightsFromHotels) : "");

  // Calculate nights from date range (preferred) or fallback to hotel sum
  const totalNights = (() => {
    if (tripStartDate && tripEndDate) {
      const start = new Date(`${tripStartDate}T00:00:00.000Z`);
      const end = new Date(`${tripEndDate}T00:00:00.000Z`);
      const diffMs = end.getTime() - start.getTime();
      const nights = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      return Math.max(nights, 1);
    }
    return totalNightsFromHotels;
  })();

  // Fill stay highlight dates sequentially between outbound and return flight dates.
  // This supports multi-city trips with ONLY start/end flights (no in-country flights).
  if (stayHighlightRefs.length > 0 && tripStartDate && tripEndDate) {
    let current = tripStartDate;
    const requestedNightsByStay = staySections.map((stay) => {
      if (stay.hotel.price_per_night.amount > 0) {
        return Math.max(
          1,
          Math.round(stay.hotel.total_price.amount / stay.hotel.price_per_night.amount),
        );
      }
      return 1;
    });

    for (let i = 0; i < stayHighlightRefs.length; i++) {
      const { highlightIndex, stayIndex } = stayHighlightRefs[i];
      const remainingStays = stayHighlightRefs.length - i;
      const remainingNights = diffNights(current, tripEndDate);

      // Ensure we can allocate at least 1 night per remaining stay.
      const maxForThis = Math.max(1, remainingNights - (remainingStays - 1));
      const requested = requestedNightsByStay[stayIndex] ?? 1;
      const nightsForThis =
        i === stayHighlightRefs.length - 1
          ? Math.max(1, remainingNights)
          : Math.min(requested, maxForThis);

      const stayStart = current;
      const stayEnd = addDays(stayStart, nightsForThis);
      current = stayEnd;

      const highlight = highlights[highlightIndex];
      if (highlight) {
        highlight.date = stayStart;
        highlight.endDate = stayEnd !== stayStart ? stayEnd : undefined;
        highlight.nights = nightsForThis;
      }
    }
  }

  // If no origin from flights, use first hotel location
  if (!origin && hotels.length > 0) {
    origin = hotels[0].location;
  }

  // If no destination from flights, use first hotel location
  if (!mainDestination && hotels.length > 0) {
    mainDestination = hotels[0].location;
  }

  const uniqueWaypoints = orderedPath.filter(
    (wp, index, arr) =>
      arr.findIndex((w) => w.lat === wp.lat && w.lng === wp.lng) === index,
  );

  const mapCenter =
    uniqueWaypoints.length > 0
      ? {
        lat:
          uniqueWaypoints.reduce((sum, wp) => sum + wp.lat, 0) /
          uniqueWaypoints.length,
        lng:
          uniqueWaypoints.reduce((sum, wp) => sum + wp.lng, 0) /
          uniqueWaypoints.length,
      }
      : { lat: 51.5, lng: -0.1 };

  const defaultLocation: Location = {
    city: "",
    country: "",
    airport_code: "",
    latitude: 0,
    longitude: 0,
  };

  return {
    hotels,
    flights,
    activities,
    transfers,
    highlights,
    waypoints: uniqueWaypoints,
    totalPrice: { currency: "USD", amount: Math.round(totalPrice) },
    origin: origin || defaultLocation,
    destination: mainDestination || defaultLocation,
    tripStartDate,
    tripEndDate,
    mapCenter,
    vibe: trip.vibe,
  };
};

const TripCard: React.FC<TripCardProps> = ({ trip, tripId, tripIndex }) => {
  const router = useRouter();
  const {
    hotels,
    flights,
    activities,
    highlights,
    waypoints,
    totalPrice,
    origin,
    destination,
    tripStartDate,
    tripEndDate,
    mapCenter,
    vibe,
  } = extractTripData(trip);

  const outboundFlight = flights[0];
  const returnFlight = flights.length > 1 ? flights[flights.length - 1] : null;

  const originStr = formatLocationLabel(outboundFlight?.outbound.origin ?? origin);
  const destinationStr = formatLocationLabel(
    outboundFlight?.outbound.destination ?? destination,
  );

  const resolveTripId = async (): Promise<string | null> => {
    if (tripId) return tripId;

    const sessionId = getOrCreateSessionId();
    const storedTripIdsJson = sessionStorage.getItem(
      `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
    );
    if (storedTripIdsJson) {
      try {
        const parsed = JSON.parse(storedTripIdsJson) as unknown;
        if (Array.isArray(parsed)) {
          const ids = parsed.filter((v) => typeof v === "string") as string[];
          const idAtIndex = ids[tripIndex];
          if (idAtIndex) return idAtIndex;
        }
      } catch {
        // ignore
      }
    }

    const searchIdFromQuery =
      typeof router.query.searchId === "string" ? router.query.searchId : "";
    const searchIdFromSession = sessionStorage.getItem(
      `${SEARCH_ID_KEY_PREFIX}${sessionId}`,
    );
    const searchId = searchIdFromQuery || searchIdFromSession || "";
    if (!searchId) return null;

    try {
      const response = await apiClient.get<{ tripIds: string[] }>(
        `/api/search/${searchId}/trip-ids`,
      );
      sessionStorage.setItem(
        `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
        JSON.stringify(response.tripIds),
      );
      return response.tripIds[tripIndex] ?? null;
    } catch {
      return null;
    }
  };

  const handleCardClick = (): void => {
    void (async (): Promise<void> => {
      const resolvedTripId = await resolveTripId();
      if (!resolvedTripId) return;
      const url = `/trip?tripId=${encodeURIComponent(resolvedTripId)}`;
      window.open(url, "_blank", "noopener,noreferrer");
    })();
  };

  const handleKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleCardClick();
    }
  };

  return (
    <div
      className={styles.card}
      onClick={handleCardClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      data-trip-card="true"
    >
      <HotelCard hotels={hotels} />
      <div className={styles.middleSection}>
        <TripHighlights
          highlights={highlights}
          origin={originStr}
          destination={destinationStr}
          price={totalPrice}
          vibe={vibe}
          activities={activities}
          tripStartDate={tripStartDate}
          tripEndDate={tripEndDate}
        />
        {outboundFlight && (
          <FlightDetails
            outbound={outboundFlight}
            inbound={returnFlight || outboundFlight}
          />
        )}
      </div>
      <TripMap
        center={mapCenter}
        zoom={6}
        interactive={false}
        waypoints={waypoints}
      />
    </div>
  );
};

export default TripCard;
