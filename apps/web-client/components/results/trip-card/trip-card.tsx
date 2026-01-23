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

interface TripCardProps {
  trip: Trip;
  tripId?: string;
}

interface TripHighlight {
  date: string;
  endDate?: string;
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
  mapCenter: { lat: number; lng: number };
  vibe: string;
}

const extractTripData = (trip: Trip): ExtractedTripData => {
  const hotels: HotelOption[] = [];
  const flights: FlightOption[] = [];
  const activities: ActivityOption[] = [];
  const transfers: TransportOption[] = [];
  const highlights: TripHighlight[] = [];
  const orderedPath: Array<{ lat: number; lng: number; label: string }> = [];
  let totalPrice = 0;
  let origin: Location | null = null;
  let mainDestination: Location | null = null;

  let outboundArrivalDate = "";
  let returnDepartureDate = "";
  let primaryHotel: HotelOption | null = null;

  const getIsoDate = (dateTime: string): string => dateTime.split("T")[0];

  for (const section of trip.layout.sections) {
    const data = section.data as SectionData;

    if (section.type === SectionType.FLIGHT && isFlightOption(data)) {
      flights.push(data);
      totalPrice += convertToUSD(
        data.total_price.amount,
        data.total_price.currency
      );

      if (!origin) {
        origin = data.outbound.origin;
      }

      const flightDest = data.outbound.destination;
      const isReturnFlight =
        origin &&
        flightDest.latitude === origin.latitude &&
        flightDest.longitude === origin.longitude;

      if (!isReturnFlight) {
        mainDestination = flightDest;
        orderedPath.push({
          lat: flightDest.latitude,
          lng: flightDest.longitude,
          label: flightDest.city,
        });

        if (!outboundArrivalDate) {
          outboundArrivalDate = getIsoDate(data.outbound.arrival_time);
        }
      } else {
        returnDepartureDate = getIsoDate(data.outbound.departure_time);
      }

      highlights.push({
        date: getIsoDate(data.outbound.departure_time),
        title: isReturnFlight
          ? `Flight back to ${flightDest.city}`
          : `Flight to ${flightDest.city}`,
        type: "flight",
        location: flightDest,
      });
    } else if (section.type === SectionType.STAY && isFinalStayOption(data)) {
      hotels.push(data.hotel);

      if (!primaryHotel) {
        primaryHotel = data.hotel;
      }

      totalPrice += convertToUSD(
        data.hotel.total_price.amount,
        data.hotel.total_price.currency
      );

      orderedPath.push({
        lat: data.hotel.location.latitude,
        lng: data.hotel.location.longitude,
        label: data.hotel.location.city,
      });

      for (const activity of data.activities) {
        activities.push(activity);
      }
    } else if (section.type === SectionType.TRANSFER && isTransportOption(data)) {
      transfers.push(data);
      totalPrice += convertToUSD(
        data.total_price.amount,
        data.total_price.currency
      );
    }
  }

  if (primaryHotel && outboundArrivalDate) {
    const checkInDate = outboundArrivalDate;
    const checkOutDate = returnDepartureDate || "";

    highlights.push({
      date: checkInDate,
      endDate: checkOutDate || undefined,
      title: `Stay at ${primaryHotel.name}`,
      type: "stay",
      location: primaryHotel.location,
    });
  }

  const typeRank: Record<TripHighlight["type"], number> = {
    stay: 0,
    flight: 1,
    transport: 2,
    activity: 3,
  };

  highlights.sort(
    (a, b) => a.date.localeCompare(b.date) || typeRank[a.type] - typeRank[b.type]
  );

  const uniqueWaypoints = orderedPath.filter(
    (wp, index, arr) =>
      arr.findIndex((w) => w.lat === wp.lat && w.lng === wp.lng) === index
  );

  const mapCenter =
    uniqueWaypoints.length > 0
      ? {
          lat:
            uniqueWaypoints.reduce((sum, wp) => sum + wp.lat, 0) / uniqueWaypoints.length,
          lng:
            uniqueWaypoints.reduce((sum, wp) => sum + wp.lng, 0) / uniqueWaypoints.length,
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
    highlights: highlights.slice(0, 4),
    waypoints: uniqueWaypoints,
    totalPrice: { currency: "USD", amount: Math.round(totalPrice) },
    origin: origin || defaultLocation,
    destination: mainDestination || defaultLocation,
    mapCenter,
    vibe: trip.vibe,
  };
};

const TripCard: React.FC<TripCardProps> = ({ trip, tripId }) => {
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
    vibe,
  } = extractTripData(trip);

  const originStr = origin.city ? `${origin.city}, ${origin.country}` : "";
  const destinationStr = destination.city
    ? `${destination.city}, ${destination.country}`
    : "";

  const outboundFlight = flights[0];
  const returnFlight = flights.length > 1 ? flights[flights.length - 1] : null;

  const handleCardClick = (): void => {
    if (!tripId) return
    router.push(`/trip?tripId=${tripId}`);
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
          vibe={vibe}
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
