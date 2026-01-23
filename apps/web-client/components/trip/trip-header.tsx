import React from "react";
import type { Trip } from "@shared/types";
import styles from "./trip-header.module.css";
import extractTripData from "../../lib/trip-extract";

interface TripHeaderProps {
  trip: Trip;
}

const getDurationDays = (startDate: string, endDate: string): number => {
  if (!startDate || !endDate) return 0;
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffMs = end.getTime() - start.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  return Math.max(1, diffDays + 1);
};

const TripHeader: React.FC<TripHeaderProps> = ({ trip }) => {
  const { origin, destination, startDate, endDate, firstHotel } =
    extractTripData(trip);

  const title =
    origin.city === destination.city
      ? `Trip to ${destination.city}, ${destination.country}`
      : `${origin.city} to ${destination.city}`;

  const bgImage =
    firstHotel?.image ||
    (firstHotel
      ? `https://source.unsplash.com/800x600/?hotel,${firstHotel.location.city}`
      : "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80&w=2073");

  const formatDate = (dateStr: string): string => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className={styles.heroContainer}>
      <div
        className={styles.heroContent}
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.7) 100%), url("${bgImage}")`,
        }}
      >
        <div className={styles.textContent}>
          <div className={styles.badges}>
            <span className={styles.badgeUpcoming}>UPCOMING</span>
            <span className={styles.badgeDuration}>
              <span
                className="material-symbols-outlined"
                style={{ fontSize: 14 }}
              >
                calendar_month
              </span>{" "}
              {getDurationDays(startDate, endDate) || 5} Days
            </span>
          </div>
          <h1 className={styles.title}>{title}</h1>
          <h2 className={styles.subtitle}>
            <span
              className="material-symbols-outlined"
              style={{ fontSize: 18 }}
            >
              date_range
            </span>{" "}
            {formatDate(startDate)} - {formatDate(endDate)}
            <span style={{ margin: "0 4px" }}>•</span>
            <span
              className="material-symbols-outlined"
              style={{ fontSize: 18 }}
            >
              group
            </span>{" "}
            2 Travelers
          </h2>
        </div>
        <div className={styles.buttonGroup}>
          <button className={styles.shareButton}>
            <span className="material-symbols-outlined">share</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TripHeader;
