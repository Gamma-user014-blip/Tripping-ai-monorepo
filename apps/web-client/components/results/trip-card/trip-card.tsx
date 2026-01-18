import React from "react";
import { useRouter } from "next/router";
import { TripResult } from "../types";
import HotelCard from "./hotel-card";
import TripHighlights from "./trip-highlights";
import FlightDetails from "./flight-details";
import TripMap from "./trip-map";
import styles from "./trip-card.module.css";

interface TripCardProps {
  result: TripResult;
}

const TripCard: React.FC<TripCardProps> = ({ result }) => {
  const router = useRouter();
  const originStr = `${result.origin.city}, ${result.origin.country}`;
  const destinationStr = `${result.destination.city}, ${result.destination.country}`;

  const handleCardClick = (): void => {
    router.push(`/trip?tripId=${result.tripId}`);
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
      <HotelCard hotels={result.hotels} />
      <div className={styles.middleSection}>
        <TripHighlights
          highlights={result.highlights}
          origin={originStr}
          destination={destinationStr}
          price={result.price}
        />
        <FlightDetails
          outbound={result.outboundFlight}
          inbound={result.returnFlight}
        />
      </div>
      <TripMap
        center={result.mapCenter}
        zoom={result.mapZoom}
        interactive={false}
        waypoints={[
          {
            lat: result.origin.latitude,
            lng: result.origin.longitude,
            label: result.origin.city,
          },
          ...(result.waypoints || []),
          {
            lat: result.destination.latitude,
            lng: result.destination.longitude,
            label: result.destination.city,
          },
        ]}
      />
    </div>
  );
};

export default TripCard;
