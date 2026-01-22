import React from "react";
import styles from "./trip-sidebar.module.css";
import {
  TripResponse,
  SectionType,
  FlightResponse,
  StayResponse,
  TransferResponse,
  Location,
  Money,
} from "../results/types";
import TripMap from "../results/trip-card/trip-map";

interface TripSidebarProps {
  trip: TripResponse;
}

const isFlightResponse = (data: unknown): data is FlightResponse => {
  return (
    typeof data === "object" &&
    data !== null &&
    "options" in data &&
    Array.isArray((data as FlightResponse).options) &&
    (data as FlightResponse).options.length > 0 &&
    "outbound" in (data as FlightResponse).options[0]
  );
};

const isStayResponse = (data: unknown): data is StayResponse => {
  return typeof data === "object" && data !== null && "hotel_options" in data;
};

const isTransferResponse = (data: unknown): data is TransferResponse => {
  return (
    typeof data === "object" &&
    data !== null &&
    "options" in data &&
    Array.isArray((data as TransferResponse).options) &&
    (data as TransferResponse).options.length > 0 &&
    "mode" in (data as TransferResponse).options[0]
  );
};

interface ExtractedSidebarData {
  totalPrice: Money;
  tripId: string;
  waypoints: Array<{ lat: number; lng: number; label: string }>;
  mapCenter: { lat: number; lng: number };
}

const extractSidebarData = (trip: TripResponse): ExtractedSidebarData => {
  let totalAmount = 0;
  let tripId = "trip-unknown";
  const orderedPath: Array<{ lat: number; lng: number; label: string }> = [];
  let hasStart = false;

  for (const section of trip.sections) {
    if (section.type === SectionType.FLIGHT && isFlightResponse(section.data)) {
      const flight = section.data.options[0];
      if (!flight) continue;

      totalAmount += flight.total_price.amount;
      tripId = flight.id;

      if (!hasStart) {
        orderedPath.push({
          lat: flight.outbound.origin.latitude,
          lng: flight.outbound.origin.longitude,
          label: flight.outbound.origin.city,
        });
        hasStart = true;
      }

      orderedPath.push({
        lat: flight.outbound.destination.latitude,
        lng: flight.outbound.destination.longitude,
        label: flight.outbound.destination.city,
      });
    } else if (section.type === SectionType.STAY && isStayResponse(section.data)) {
      const selectedHotel = section.data.hotel_options[0];
      if (!selectedHotel) continue;

      totalAmount += selectedHotel.total_price.amount;
      orderedPath.push({
        lat: selectedHotel.location.latitude,
        lng: selectedHotel.location.longitude,
        label: selectedHotel.location.city,
      });
    } else if (section.type === SectionType.TRANSFER && isTransferResponse(section.data)) {
      const transfer = section.data.options[0];
      if (!transfer) continue;

      totalAmount += transfer.total_price.amount;
      orderedPath.push({
        lat: transfer.destination.latitude,
        lng: transfer.destination.longitude,
        label: transfer.destination.city,
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
          lat: closedPath.reduce((sum, wp) => sum + wp.lat, 0) / closedPath.length,
          lng: closedPath.reduce((sum, wp) => sum + wp.lng, 0) / closedPath.length,
        }
      : { lat: 51.5, lng: -0.1 };

  return {
    totalPrice: { currency: "USD", amount: totalAmount },
    tripId,
    waypoints: closedPath,
    mapCenter,
  };
};

const TripSidebar = ({ trip }: TripSidebarProps): JSX.Element => {
  const { totalPrice, tripId, waypoints, mapCenter } = extractSidebarData(trip);

  const formatPrice = (amount: number, currency: string): string => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <aside className={styles.sidebarContainer}>
      <div className={styles.detailsCard}>
        <h3 className={styles.cardTitle}>
          <span
            className="material-symbols-outlined"
            style={{ color: "var(--color-primary)" }}
          >
            description
          </span>
          Trip Details
        </h3>
        <div className={styles.detailsList}>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Travelers</span>
            <span className={styles.detailValue}>2 Adults</span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Booking Ref</span>
            <span className={`${styles.detailValue} ${styles.detailValueMono}`}>
              {tripId}
            </span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Flights</span>
            <span className={styles.confirmedText}>
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "16px" }}
              >
                check_circle
              </span>
              Confirmed
            </span>
          </div>
          <div className={`${styles.detailRow} ${styles.priceRow}`}>
            <span className={styles.priceLabel}>Total Cost</span>
            <span className={styles.priceValue}>
              {formatPrice(totalPrice.amount, totalPrice.currency)}
            </span>
          </div>
        </div>
      </div>

      <div className={styles.buttonStack}>
        <button className={styles.actionButton}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            download
          </span>
          Download PDF
        </button>
        <button className={styles.actionButton}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            calendar_add_on
          </span>
          Add to Calendar
        </button>
      </div>

      <div className={styles.mapCard}>
        <TripMap
          center={mapCenter}
          zoom={5}
          waypoints={waypoints}
          interactive={true}
          variant="fill"
        />
      </div>
    </aside>
  );
};

export default TripSidebar;
