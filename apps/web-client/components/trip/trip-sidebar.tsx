import React from 'react';
import styles from './trip-sidebar.module.css';
import { TripResult } from '../results/types';
import TripMap from '../results/trip-card/trip-map';

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
        <button className={styles.actionButton}>
          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>download</span>
          Download PDF
        </button>
        <button className={styles.actionButton}>
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
