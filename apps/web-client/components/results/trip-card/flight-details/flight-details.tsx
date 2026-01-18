import React from "react";
import { FlightSegment } from "../../types";
import { Icon } from "../../icon";
import styles from "./flight-details.module.css";

interface FlightDetailsProps {
  outbound: FlightSegment;
  inbound: FlightSegment;
}

const FlightDetails: React.FC<FlightDetailsProps> = ({ outbound, inbound }) => {
  return (
    <div className={styles.container}>
      <FlightRow segment={outbound} />
      <FlightRow segment={inbound} />
    </div>
  );
};

const FlightRow: React.FC<{ segment: FlightSegment }> = ({ segment }) => {
  return (
    <div className={styles.row}>
      <div className={styles.airlineSection}>
        <img
          src={segment.airlineLogo}
          alt={segment.airline}
          className={styles.logo}
        />
        <span className={styles.airlineName}>{segment.airline}</span>
      </div>

      <div className={styles.timeSection}>
        <span className={styles.time}>{segment.departureTime}</span>
      </div>

      <div className={styles.iconSection}>
        <Icon icon="plane" height={18} color="var(--color-text-subtle)" />
        <span className={styles.code}>
          {segment.origin.airportCode || segment.origin.city}
        </span>
      </div>

      <div className={styles.flightPath}>
        <span className={styles.duration}>{segment.duration}</span>
        <div className={styles.lineWrapper}>
          <div className={styles.line} />
          {segment.stops > 0 && (
            <div className={styles.stopMarker}>
              <div className={styles.stopDot} />
              {segment.stopInfo && (
                <span className={styles.stopText}>{segment.stopInfo}</span>
              )}
            </div>
          )}
          <div className={styles.diamond} />
        </div>
      </div>

      <div className={styles.iconSection}>
        <Icon icon="planeLanding" height={18} color="var(--color-text-subtle)" />
        <span className={styles.code}>
          {segment.destination.airportCode || segment.destination.city}
        </span>
      </div>

      <div className={styles.timeSection}>
        <span className={styles.time}>{segment.arrivalTime}</span>
      </div>

      <div className={styles.baggage}>
        <Icon icon="baggage" height={16} color="var(--color-teal-primary)" />
      </div>
    </div>
  );
};

export default FlightDetails;
