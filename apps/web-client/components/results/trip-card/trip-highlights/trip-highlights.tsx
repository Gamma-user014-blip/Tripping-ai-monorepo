import React from "react";
import { Money, Location } from "../../types";
import { Icon } from "../../icon";
import styles from "./trip-highlights.module.css";

interface TripHighlight {
  date: string;
  endDate?: string;
  title: string;
  type: "flight" | "stay" | "activity" | "transport";
  location: Location;
}

interface TripHighlightsProps {
  highlights: TripHighlight[];
  origin: string;
  destination: string;
  price: Money;
  vibe?: string;
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
};

const formatDateRange = (startDate: string, endDate?: string): string => {
  if (!startDate) return "";
  if (!endDate) return formatDate(startDate);
  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
};

const TripHighlights: React.FC<TripHighlightsProps> = ({
  highlights,
  origin,
  destination,
  price,
  vibe = "Adventure",
}) => {
  const [originCity, originCountry] = origin.split(", ");
  const [destCity, destCountry] = destination.split(", ");

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.route}>
          <span className={styles.city}>{originCity}</span>,
          {originCountry || ""}
          <span className={styles.arrow}>⟶</span>
          <span className={styles.city}>{destCity}</span>,{destCountry || ""}
        </div>
        <button className={styles.selectButton}>{vibe}</button>
      </div>

      <div className={styles.highlightsSection}>
        <div className={styles.sectionTitle}>Trip Highlights</div>
        <div className={styles.timelineWrapper}>
          <div className={styles.timelineContainer}>
            <div className={styles.timeline}>
              {highlights.map((item, index) => (
                <div key={index} className={styles.timelineItemGroup}>
                  <div className={styles.timelineItem}>
                    <div className={styles.itemCard}>
                      <div className={styles.itemHeader}>
                        <span className={styles.itemDate}>
                          {item.endDate
                            ? formatDateRange(item.date, item.endDate)
                            : formatDate(item.date)}
                        </span>
                        <HighlightIcon type={item.type} />
                      </div>
                      <div className={styles.itemTitle}>{item.title}</div>
                    </div>
                  </div>
                  {index < highlights.length - 1 && (
                    <div className={styles.connectorWrapper}>
                      <Icon
                        icon="arrow"
                        width="100%"
                        height="100%"
                        color="#CBD5E1"
                        className={styles.connector}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className={styles.priceTag}>
            {price.amount.toLocaleString()}
            {price.currency === "USD" ? "$" : price.currency}
          </div>
        </div>
      </div>
    </div>
  );
};

const HighlightIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case "flight":
      return <Icon icon="flight" height={12} color="var(--color-text-muted)" />;
    case "stay":
      return (
        <Icon icon="location" height={12} color="var(--color-text-muted)" />
      );
    case "activity":
      return (
        <Icon icon="activity" height={12} color="var(--color-text-muted)" />
      );
    case "transport":
      return (
        <Icon icon="transport" height={12} color="var(--color-text-muted)" />
      );
    default:
      return null;
  }
};

export default TripHighlights;
