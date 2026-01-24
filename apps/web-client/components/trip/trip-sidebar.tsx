import React from "react";
import styles from "./trip-sidebar.module.css";
import TripMap from "../results/trip-card/trip-map";
import { exportTripToPDF, TripResult } from './trip-pdf-export';
import { useState } from 'react';

interface TripSidebarProps {
  trip: TripResult;
}

const TripSidebar = ({ trip }: TripSidebarProps): JSX.Element => {
  const totalPrice = trip.price;
  const waypoints = trip.waypoints;
  const mapCenter = trip.mapCenter;
  const [calendarEventIds, setCalendarEventIds] = useState<string[]>([]);


  const formatPrice = (amount: number, currency: string): string => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(Math.ceil(amount));
  };


 const handleRemoveFromCalendar = async () => {
  if (!calendarEventIds.length) return;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
  const res = await fetch(`${apiUrl}/api/calendar/remove-trip-from-calendar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ eventIds: calendarEventIds }),
    credentials: 'include',
  });

  if (!res.ok) {
    console.error('Failed to remove trip from calendar');
    return;
  }

  const data = await res.json();
  console.log('Deleted event IDs:', data.deletedEventIds);
  setCalendarEventIds([]); // clear after deletion
  alert('Trip removed from calendar successfully!');
};
  const handleAddToCalendar = async (trip: TripResult) => {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
    const res = await fetch(`${apiUrl}/api/calendar/add-trip-to-calendar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trip),
      credentials: 'include', // important for session
    });

    if (res.status === 401) {
      // Redirect to auth if not logged in
      window.location.href = `${apiUrl}/api/auth/google`;
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      console.error('Failed to add trip to Google Calendar', err);
      alert('Failed to add trip to calendar. Please try again.');
      return;
    }

    const data = await res.json();
    console.log('Created Google event IDs:', data.createdEventIds);

    // Save the IDs in state so you can remove later
    setCalendarEventIds(data.createdEventIds);

    alert('Trip added to calendar successfully!');
  } catch (error) {
    console.error('Error adding to calendar:', error);
    alert('An error occurred. Please try again.');
  }
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
              {typeof totalPrice === "number"
              ? formatPrice(totalPrice, "USD")
              : formatPrice(totalPrice.amount ?? 0, totalPrice.currency ?? "USD")}
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

<button
  className={styles.actionButton}
  onClick={() => handleAddToCalendar(trip)}
  disabled={calendarEventIds.length > 0} // disable if already added
>
  <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
    calendar_add_on
  </span>
  {calendarEventIds.length > 0 ? "Added to Calendar" : "Add to Calendar"}
</button>
        
  <button
    className={styles.actionButton}
    onClick={() => handleRemoveFromCalendar()}
    disabled={calendarEventIds.length === 0} // disabled if nothing to remove
  >
    <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
      delete
    </span>
    {calendarEventIds.length === 0 ? "Nothing to Remove" : "Remove Trip from Calendar"}
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
