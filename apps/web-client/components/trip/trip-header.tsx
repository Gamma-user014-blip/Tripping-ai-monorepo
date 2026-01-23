import React from "react";
import toast from "react-hot-toast";
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

const handleShare = async (): Promise<void> => {
  const url = window.location.href;
  try {
    await navigator.clipboard.writeText(url);
    toast.success("Link copied to clipboard!");
  } catch {
    toast.error("Failed to copy link");
  }
};

const TripHeader: React.FC<TripHeaderProps> = ({ trip }) => {
  const { origin, destination, startDate, endDate, totalNights, firstHotel } =
    extractTripData(trip);

  const getTitle = (): string => {
    const destCity = destination.city || firstHotel?.location.city || "Unknown";
    const destCountry =
      destination.country || firstHotel?.location.country || "";
    const origCity = origin.city || "";

    if (!origCity || origCity === destCity) {
      return destCountry
        ? `Trip to ${destCity}, ${destCountry}`
        : `Trip to ${destCity}`;
    }
    return `${origCity} to ${destCity}`;
  };

  const title = getTitle();

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

  const dateRangeText =
    startDate && endDate
      ? `${formatDate(startDate)} - ${formatDate(endDate)}`
      : "";

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
              {((): string => {
                if (!startDate) {
                  return totalNights > 0
                    ? `${totalNights} Night${totalNights !== 1 ? "s" : ""}`
                    : "Flexible dates";
                }
                const todayMidnight = new Date(
                  new Date().getFullYear(),
                  new Date().getMonth(),
                  new Date().getDate(),
                );
                const start = new Date(startDate);
                const diffMs = start.getTime() - todayMidnight.getTime();
                const daysUntil = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
                if (daysUntil <= 0) return "Starts today";
                return `${daysUntil} day${daysUntil !== 1 ? "s" : ""}`;
              })()}
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
            {dateRangeText ? `${dateRangeText} • ` : ""}
            {totalNights > 0
              ? `${totalNights} Night${totalNights !== 1 ? "s" : ""} • `
              : "Dates TBD • "}
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
          <button className={styles.shareButton} onClick={handleShare}>
            <span className="material-symbols-outlined">share</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TripHeader;
