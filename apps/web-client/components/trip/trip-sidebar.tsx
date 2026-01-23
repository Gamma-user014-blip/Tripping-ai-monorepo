import React from "react";
import styles from "./trip-sidebar.module.css";
import type { Trip } from "@shared/types";
import TripMap from "../results/trip-card/trip-map";
import extractTripData from "../../lib/trip-extract";

interface TripSidebarProps {
  trip: Trip;
  bookingRef: string;
}

const TripSidebar = ({ trip, bookingRef }: TripSidebarProps): JSX.Element => {
  const { totalPrice, waypoints, mapCenter } = extractTripData(trip);

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
              {bookingRef}
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
