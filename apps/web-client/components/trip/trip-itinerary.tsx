import React from "react";
import styles from "./trip-itinerary.module.css";
import {
  SectionType,
  FlightOption,
  HotelOption,
  ActivityOption,
  Trip,
} from "../results/types";
import { Icon } from "../results/icon";
import {
  SectionData,
  isFlightOption,
  isFinalStayOption,
  isTransportOption,
} from "../../lib/trip-type-guards";

interface TripItineraryProps {
  trip: Trip;
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
};

const formatTime = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
};

const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const TripItinerary = ({ trip }: TripItineraryProps): JSX.Element => {
  const rendered: JSX.Element[] = [];
  let flightCount = 0;
  let stayCount = 0;

  for (const section of trip.layout.sections) {
    const data = section.data as SectionData;

    if (section.type === SectionType.FLIGHT && isFlightOption(data)) {
      flightCount += 1;
      rendered.push(
        <FlightCard
          key={`flight-${data.id}`}
          type={flightCount === 1 ? "outbound" : "return"}
          flight={data}
        />,
      );
      continue;
    }

    if (section.type === SectionType.STAY && isFinalStayOption(data)) {
      stayCount += 1;
      rendered.push(
        <StayCard
          key={`stay-${data.hotel.id}`}
          hotel={data.hotel}
          activities={data.activities}
          isPrimary={stayCount === 1}
        />,
      );
      continue;
    }

    if (section.type === SectionType.TRANSFER && isTransportOption(data)) {
      rendered.push(
        <TransferDivider
          key={`transfer-${data.id}`}
          label={`${data.provider} to ${data.destination.city}`}
        />,
      );
    }
  }

  return <main className={styles.timelineContainer}>{rendered}</main>;
};

const FlightCard = ({
  type,
  flight,
}: {
  type: "outbound" | "return";
  flight: FlightOption;
}): JSX.Element => {
  const isDeparture = type === "outbound";
  const segment = flight.outbound;
  const departureTime = formatTime(segment.departure_time);
  const arrivalTime = formatTime(segment.arrival_time);
  const duration = formatDuration(segment.duration_minutes);
  const date = segment.departure_time.split("T")[0];

  return (
    <div className={styles.flightCard}>
      <div className={styles.flightContent}>
        <div className={styles.flightIconBox}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "24px" }}
          >
            {isDeparture ? "flight_takeoff" : "flight_land"}
          </span>
        </div>
        <div className={styles.flightDetails}>
          <div className={styles.dateTime}>
            {formatDate(date)} • {departureTime}
          </div>
          <h4 className={styles.flightTitle}>
            {isDeparture ? "Flight to" : "Return flight to"}{" "}
            {segment.destination.airport_code || segment.destination.city}
          </h4>
          <p className={styles.flightSub}>
            {segment.airline} • {duration} •{" "}
            {segment.stops === 0 ? "Direct" : `${segment.stops} Stop(s)`}
          </p>

          <div className={styles.flightRouteRow}>
            <div className={styles.flightTimeSection}>
              <span className={styles.flightTime}>{departureTime}</span>
            </div>

            <div className={styles.flightIconSection}>
              <Icon icon="plane" height={18} color="var(--color-text-subtle)" />
              <span className={styles.flightCode}>
                {segment.origin.airport_code || segment.origin.city}
              </span>
            </div>

            <div className={styles.flightPath}>
              <span className={styles.flightDuration}>{duration}</span>
              <div className={styles.flightLineWrapper}>
                <div className={styles.flightLine} />
                {segment.stops > 0 && (
                  <div className={styles.flightStopMarker}>
                    <div className={styles.flightStopDot} />
                    {segment.layovers.length > 0 && (
                      <span className={styles.flightStopText}>
                        {segment.layovers[0].airport.city}
                      </span>
                    )}
                  </div>
                )}
                <div className={styles.flightDiamond} />
              </div>
            </div>

            <div className={styles.flightIconSection}>
              <Icon
                icon="planeLanding"
                height={18}
                color="var(--color-text-subtle)"
              />
              <span className={styles.flightCode}>
                {segment.destination.airport_code || segment.destination.city}
              </span>
            </div>

            <div className={styles.flightTimeSection}>
              <span className={styles.flightTime}>{arrivalTime}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const STAY_GRADIENTS: Array<[string, string]> = [
  ["hsl(210 70% 55%)", "hsl(232 70% 32%)"],
  ["hsl(195 70% 52%)", "hsl(214 70% 30%)"],
  ["hsl(255 65% 58%)", "hsl(275 70% 34%)"],
  ["hsl(220 24% 62%)", "hsl(232 26% 30%)"],
  ["hsl(205 65% 54%)", "hsl(255 55% 34%)"],
];

const getStayGradient = (id: string): string => {
  let hash = 0;
  for (const char of id) {
    hash = (hash * 31 + char.charCodeAt(0)) % 360;
  }
  const index = hash % STAY_GRADIENTS.length;
  const [from, to] = STAY_GRADIENTS[index];
  return `linear-gradient(135deg, ${from}, ${to})`;
};

const StayCard = ({
  hotel,
  activities,
  isPrimary,
}: {
  hotel: HotelOption;
  activities: ActivityOption[];
  isPrimary: boolean;
}): JSX.Element => {
  const gradientBg = getStayGradient(hotel.id);
  const bgStyle = hotel.image
    ? {
        backgroundImage: `linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url("${hotel.image}")`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }
    : { background: gradientBg };

  const hotelActivities = activities.filter(
    (act) =>
      act.location.city.toLowerCase() === hotel.location.city.toLowerCase()
  );

  const nights = Math.round(
    hotel.total_price.amount / hotel.price_per_night.amount
  );

  return (
    <div className={styles.stayCard}>
      <div
        className={styles.stayImageContainer}
        style={bgStyle}
      >
        <div className={styles.ratingBadge}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "14px", color: "#eab308" }}
          >
            star
          </span>
          {hotel.rating}
        </div>
      </div>

      <div className={styles.stayContent}>
        <div className={styles.stayHeader}>
          <div>
            <div className={styles.stayTags}>
              <span className={styles.stayBadge}>
                {isPrimary ? "Primary Stay" : "Secondary Stay"}
              </span>
              <span className={styles.stayNights}>
                {nights} night{nights > 1 ? "s" : ""} · ${hotel.total_price.amount}
              </span>
            </div>
            <h3 className={styles.stayTitle}>{hotel.name}</h3>
          </div>
        </div>

        <div className={styles.locationRow}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "16px" }}
          >
            location_on
          </span>
          {hotel.location.city}, {hotel.location.country}
        </div>

        <div className={styles.amenities}>
          {hotel.amenities.slice(0, 5).map((tag, i) => (
            <span key={i} className={styles.amenityTag}>
              {tag}
            </span>
          ))}
        </div>

        {hotelActivities.length > 0 && (
          <div className={styles.activitiesSection}>
            <h4 className={styles.activitiesTitle}>
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "18px", color: "#0d9488" }}
              >
                attractions
              </span>
              Planned Activities
            </h4>
            <div className={styles.activitiesGrid}>
              {hotelActivities.map((act) => (
                <div key={act.id} className={styles.activityCard}>
                  <div className={styles.activityIcon}>
                    <span className="material-symbols-outlined">
                      attractions
                    </span>
                  </div>
                  <div className={styles.activityInfo}>
                    <h5 className={styles.activityName}>{act.name}</h5>
                    <span className={styles.activityMeta}>
                      {act.available_times[0]?.date
                        ? formatDate(act.available_times[0].date)
                        : "TBD"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const TransferDivider = ({ label }: { label: string }): JSX.Element => {
  return (
    <div className={styles.transferDivider}>
      <div className={styles.dividerLine}></div>
      <div className={styles.transferLabel}>
        <span
          className="material-symbols-outlined"
          style={{ fontSize: "16px" }}
        >
          directions_car
        </span>
        {label}
      </div>
      <div className={styles.dividerLine}></div>
    </div>
  );
};

export default TripItinerary;
