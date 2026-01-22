import React from "react";
import { useRouter } from "next/router";
import {
  TripResponse,
  SectionType,
  FlightResponse,
  StayResponse,
  TransferResponse,
  FlightOption,
  HotelOption,
  Money,
  Location,
  ActivityOption,
  TransportOption,
  PreferenceType,
} from "../types";
import HotelCard from "./hotel-card";
import TripHighlights from "./trip-highlights";
import FlightDetails from "./flight-details";
import TripMap from "./trip-map";
import styles from "./trip-card.module.css";

interface TripCardProps {
  trip: TripResponse;
}

interface TripHighlight {
  date: string;
  title: string;
  type: "flight" | "activity" | "transport";
  location: Location;
}

const isFlightResponse = (
  data: FlightResponse | StayResponse | TransferResponse
): data is FlightResponse => {
  return "options" in data && data.options.length > 0 && "outbound" in data.options[0];
};

const isStayResponse = (
  data: FlightResponse | StayResponse | TransferResponse
): data is StayResponse => {
  return "hotel_options" in data;
};

const isTransferResponse = (
  data: FlightResponse | StayResponse | TransferResponse
): data is TransferResponse => {
  return "options" in data && data.options.length > 0 && "mode" in data.options[0];
};

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
  mapCenter: { lat: number; lng: number };
  tripKind: PreferenceType;
}

const extractTripData = (trip: TripResponse): ExtractedTripData => {
  const hotels: HotelOption[] = [];
  const flights: FlightOption[] = [];
  const activities: ActivityOption[] = [];
  const transfers: TransportOption[] = [];
  const highlights: TripHighlight[] = [];
  const orderedPath: Array<{ lat: number; lng: number; label: string }> = [];
  let totalPrice = 0;
  let origin: Location | null = null;
  let destination: Location | null = null;

  for (const section of trip.sections) {
    if (section.type === SectionType.FLIGHT && isFlightResponse(section.data)) {
      const flight = section.data.options[0];
      if (!flight) continue;

      flights.push(flight);
      totalPrice += flight.total_price.amount;

      if (!origin) {
        origin = flight.outbound.origin;
        orderedPath.push({
          lat: origin.latitude,
          lng: origin.longitude,
          label: origin.city,
        });
      }

      destination = flight.outbound.destination;
      orderedPath.push({
        lat: destination.latitude,
        lng: destination.longitude,
        label: destination.city,
      });

      highlights.push({
        date: flight.outbound.departure_time.split("T")[0],
        title: `Flight to ${flight.outbound.destination.city}`,
        type: "flight",
        location: flight.outbound.destination,
      });
    } else if (section.type === SectionType.STAY && isStayResponse(section.data)) {
      const stayData = section.data;

      for (const hotel of stayData.hotel_options) {
        hotels.push(hotel);
      }

      const selectedHotel = stayData.hotel_options[0];
      if (selectedHotel) {
        totalPrice += selectedHotel.total_price.amount;
        orderedPath.push({
          lat: selectedHotel.location.latitude,
          lng: selectedHotel.location.longitude,
          label: selectedHotel.location.city,
        });
      }

      for (const activity of stayData.activity_options) {
        activities.push(activity);
      }

      const selectedActivity = stayData.activity_options[0];
      if (selectedActivity) {
        highlights.push({
          date: selectedActivity.available_times[0]?.date || "",
          title: selectedActivity.name,
          type: "activity",
          location: selectedActivity.location,
        });
      }
    } else if (
      section.type === SectionType.TRANSFER &&
      isTransferResponse(section.data)
    ) {
      const transfer = section.data.options[0];
      if (!transfer) continue;

      transfers.push(transfer);
      totalPrice += transfer.total_price.amount;

      orderedPath.push({
        lat: transfer.destination.latitude,
        lng: transfer.destination.longitude,
        label: transfer.destination.city,
      });

      highlights.push({
        date: transfer.departure_time.split("T")[0],
        title: `${transfer.provider} to ${transfer.destination.city}`,
        type: "transport",
        location: transfer.destination,
      });
    }
  }

  const closedPath =
    orderedPath.length > 1
      ? (() => {
          const first = orderedPath[0];
          const last = orderedPath[orderedPath.length - 1];
          const isClosed = first.lat === last.lat && first.lng === last.lng;
          return isClosed ? orderedPath : [...orderedPath, first];
        })()
      : orderedPath;

  const mapCenter =
    closedPath.length > 0
      ? {
          lat:
            closedPath.reduce((sum, wp) => sum + wp.lat, 0) / closedPath.length,
          lng:
            closedPath.reduce((sum, wp) => sum + wp.lng, 0) / closedPath.length,
        }
      : { lat: 51.5, lng: -0.1 };

  const defaultLocation: Location = {
    city: "",
    country: "",
    airport_code: "",
    latitude: 0,
    longitude: 0,
  };

  const TRIP_KINDS_LIST = [
    PreferenceType.LUXURY,
    PreferenceType.BUDGET,
    PreferenceType.ROMANTIC,
    PreferenceType.FAMILY,
    PreferenceType.ADVENTURE,
    PreferenceType.CULTURE,
    PreferenceType.FOOD,
    PreferenceType.NATURE,
    PreferenceType.BEACH,
    PreferenceType.CITY,
  ];

  const tripId = flights[0]?.id || hotels[0]?.id || "default";
  let tripKindHash = 0;
  for (const char of tripId) {
    tripKindHash = (tripKindHash * 31 + char.charCodeAt(0)) % TRIP_KINDS_LIST.length;
  }
  const tripKind = TRIP_KINDS_LIST[tripKindHash];

  return {
    hotels,
    flights,
    activities,
    transfers,
    highlights: highlights.slice(0, 4),
    waypoints: closedPath,
    totalPrice: { currency: "USD", amount: totalPrice },
    origin: origin || defaultLocation,
    destination: destination || defaultLocation,
    mapCenter,
    tripKind,
  };
};

const TripCard: React.FC<TripCardProps> = ({ trip }) => {
  const router = useRouter();
  const {
    hotels,
    flights,
    highlights,
    waypoints,
    totalPrice,
    origin,
    destination,
    mapCenter,
    tripKind,
  } = extractTripData(trip);

  const originStr = origin.city ? `${origin.city}, ${origin.country}` : "";
  const destinationStr = destination.city
    ? `${destination.city}, ${destination.country}`
    : "";

  const outboundFlight = flights[0];
  const returnFlight = flights.length > 1 ? flights[flights.length - 1] : null;

  const handleCardClick = (): void => {
    router.push(`/trip?tripId=${outboundFlight?.id || "unknown"}`);
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
    >
      <HotelCard hotels={hotels} />
      <div className={styles.middleSection}>
        <TripHighlights
          highlights={highlights}
          origin={originStr}
          destination={destinationStr}
          price={totalPrice}
          tripKind={tripKind}
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
