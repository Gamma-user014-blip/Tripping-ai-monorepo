import React from 'react';
import styles from './trip-sidebar.module.css';
import { TripResult } from '../results/types';
import TripMap from '../results/trip-card/trip-map';
import { exportTripToPDF } from './trip-pdf-export';

interface TripSidebarProps {
  trip: TripResult;
}

export default function TripSidebar({ trip }: TripSidebarProps) {
  const formatPrice = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const allWaypoints = [
    {
      lat: trip.origin.latitude,
      lng: trip.origin.longitude,
      label: trip.origin.city,
    },
    ...(trip.waypoints || []),
    {
      lat: trip.destination.latitude,
      lng: trip.destination.longitude,
      label: trip.destination.city,
    },
  ];

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
      {/* Trip Details Card */}
      <div className={styles.detailsCard}>
        <h3 className={styles.cardTitle}>
          <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)' }}>description</span>
          Trip Details
        </h3>
        <div className={styles.detailsList}>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Travelers</span>
            <span className={styles.detailValue}>2 Adults</span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Booking Ref</span>
            <span className={`${styles.detailValue} ${styles.detailValueMono}`}>{trip.tripId}</span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Flights</span>
            <span className={styles.confirmedText}>
              <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>check_circle</span>
              Confirmed
            </span>
          </div>
          <div className={`${styles.detailRow} ${styles.priceRow}`}>
            <span className={styles.priceLabel}>Total Cost</span>
            <span className={styles.priceValue}>
              {formatPrice(trip.price.amount, trip.price.currency)}
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className={styles.buttonStack}>
        <button className={styles.actionButton} onClick={() => handleExportPDF(trip)}>
          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>download</span>
          Download PDF

        </button>
        <button className={styles.actionButton} onClick={() => handleAddToCalendar(trip)}>
          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>calendar_add_on</span>
          Add to Calendar
        </button>
      </div>

      {/* Map Card */}
      <div className={styles.mapCard}>
        <TripMap
          center={trip.mapCenter}
          zoom={trip.mapZoom - 1} // Zoom out slightly for small view
          waypoints={allWaypoints}
          interactive={true} // Allow interaction since it replaces the main map
          variant="fill"
        />
      </div>
    </aside>
  );
}
