import React from "react";
import { TripResult } from "../results/types";
import styles from "./trip-header.module.css";

interface TripHeaderProps {
  trip: TripResult;
}

const TripHeader: React.FC<TripHeaderProps> = ({ trip }) => {
  const getDurationDays = (): number => {
    return trip.highlights?.length || 5;
  };

  const title =
    trip.origin.city === trip.destination.city
      ? `Trip to ${trip.destination.city}, ${trip.destination.country}`
      : `${trip.origin.city} to ${trip.destination.city}`;

  const bgImage =
    trip.hotels[0]?.image ||
    "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80&w=2073&ixlib=rb-4.0.3";

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
              {getDurationDays()} Days
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
            {trip.startDate} - {trip.endDate}
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
