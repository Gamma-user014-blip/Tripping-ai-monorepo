import React from "react";
import { FlightOption, FlightSegment } from "../../types";
import { Icon } from "../../icon";
import styles from "./flight-details.module.css";

interface FlightDetailsProps {
  outbound: FlightOption;
  inbound: FlightOption;
}

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

const FlightDetails: React.FC<FlightDetailsProps> = ({ outbound, inbound }) => {
  return (
    <div className={styles.container}>
      <FlightRow segment={outbound.outbound} airline={outbound.provider} />
      <FlightRow segment={inbound.outbound} airline={inbound.provider} />
    </div>
  );
};

interface FlightRowProps {
  segment: FlightSegment;
  airline: string;
}

const FlightRow: React.FC<FlightRowProps> = ({ segment, airline }) => {
  const departureTime = formatTime(segment.departure_time);
  const arrivalTime = formatTime(segment.arrival_time);
  const duration = formatDuration(segment.duration_minutes);

  return (
    <div className={styles.row}>
      <div className={styles.airlineSection}>
        <div className={styles.logo} aria-hidden="true">
          <Icon icon="plane" height={18} color="var(--color-teal-primary)" />
        </div>
        <span className={styles.airlineName}>{segment.airline}</span>
      </div>

      <div className={styles.timeSection}>
        <span className={styles.time}>{departureTime}</span>
      </div>

      <div className={styles.iconSection}>
        <Icon icon="plane" height={18} color="var(--color-text-subtle)" />
        <span className={styles.code}>
          {segment.origin.airport_code || segment.origin.city}
        </span>
      </div>

      <div className={styles.flightPath}>
        <span className={styles.duration}>{duration}</span>
        <div className={styles.lineWrapper}>
          <div className={styles.line} />
          {segment.stops > 0 && (
            <div className={styles.stopMarker}>
              <div className={styles.stopDot} />
              {segment.layovers.length > 0 && (
                <span className={styles.stopText}>
                  {segment.layovers[0].airport.city}
                </span>
              )}
            </div>
          )}
          <div className={styles.diamond} />
        </div>
      </div>

      <div className={styles.iconSection}>
        <Icon
          icon="planeLanding"
          height={18}
          color="var(--color-text-subtle)"
        />
        <span className={styles.code}>
          {segment.destination.airport_code || segment.destination.city}
        </span>
      </div>

      <div className={styles.timeSection}>
        <span className={styles.time}>{arrivalTime}</span>
      </div>

      <div className={styles.baggage}>
        <Icon icon="baggage" height={16} color="var(--color-teal-primary)" />
      </div>
    </div>
  );
};

export default FlightDetails;
