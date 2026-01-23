import React from "react";
import styles from "./trip-sidebar.module.css";
import TripMap from "../results/trip-card/trip-map";
import { exportTripToPDF, TripResult } from './trip-pdf-export';

interface TripSidebarProps {
  trip: TripResult;
}

const TripSidebar = ({ trip }: TripSidebarProps): JSX.Element => {
  const totalPrice = trip.price;
  const waypoints = trip.waypoints;
  const mapCenter = trip.mapCenter;

  const formatPrice = (amount: number, currency: string): string => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(Math.ceil(amount));
  };

  const handleAddToCalendar = async (trip: TripResult) => {
    const res = await fetch('/api/add-trip-to-calendar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trip),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      console.error('Failed to add trip to Google Calendar', err);
      return;
    }

    const data = await res.json();
    console.log('Created Google event IDs:', data.createdEventIds);
  };

  const handleExportPDF = async (trip: TripResult) => {
    await exportTripToPDF(trip, {
      filename: `${trip.origin.city}-to-${trip.destination.city}.pdf`,
    });
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
            <span className={styles.detailLabel}>Trip ID</span>
            <span className={`${styles.detailValue} ${styles.detailValueMono}`}>
              {trip.tripId}
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
            </span>
          </div>
        </div>
      </div>

      <div className={styles.buttonStack}>
        <button className={styles.actionButton} onClick={() => handleExportPDF(trip)}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            download
          </span>
          Download PDF

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
