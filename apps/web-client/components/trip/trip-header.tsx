import React from "react";
import {
  TripResponse,
  SectionType,
  FlightResponse,
  StayResponse,
  Location,
  HotelOption,
} from "../results/types";
import styles from "./trip-header.module.css";

interface TripHeaderProps {
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

interface ExtractedHeaderData {
  origin: Location;
  destination: Location;
  startDate: string;
  endDate: string;
  firstHotel: HotelOption | null;
  highlightCount: number;
}

const extractHeaderData = (trip: TripResponse): ExtractedHeaderData => {
  let origin: Location | null = null;
  let destination: Location | null = null;
  let startDate = "";
  let endDate = "";
  let firstHotel: HotelOption | null = null;
  let highlightCount = 0;

  for (const section of trip.sections) {
    if (section.type === SectionType.FLIGHT && isFlightResponse(section.data)) {
      const flight = section.data.options[0];
      if (!origin) {
        origin = flight.outbound.origin;
        startDate = flight.outbound.departure_time.split("T")[0];
      }
      destination = flight.outbound.destination;
      endDate = flight.outbound.arrival_time.split("T")[0];
      highlightCount++;
    } else if (section.type === SectionType.STAY && isStayResponse(section.data)) {
      if (!firstHotel && section.data.hotel_options.length > 0) {
        firstHotel = section.data.hotel_options[0];
      }
      highlightCount += section.data.activity_options.length;
    } else if (section.type === SectionType.TRANSFER) {
      highlightCount++;
    }
  }

  const defaultLocation: Location = {
    city: "",
    country: "",
    airport_code: "",
    latitude: 0,
    longitude: 0,
  };

  return {
    origin: origin || defaultLocation,
    destination: destination || defaultLocation,
    startDate,
    endDate,
    firstHotel,
    highlightCount,
  };
};

const TripHeader: React.FC<TripHeaderProps> = ({ trip }) => {
  const { origin, destination, startDate, endDate, firstHotel, highlightCount } =
    extractHeaderData(trip);

  const getDurationDays = (): number => {
    return highlightCount || 5;
  };

  const title =
    origin.city === destination.city
      ? `Trip to ${destination.city}, ${destination.country}`
      : `${origin.city} to ${destination.city}`;

  const bgImage =
    firstHotel
      ? `https://source.unsplash.com/800x600/?hotel,${firstHotel.location.city}`
      : "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80&w=2073";

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
