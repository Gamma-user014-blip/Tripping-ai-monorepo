import React from "react";
import { Money, Location, ActivityOption, ActivityCategory } from "../../types";
import { Icon } from "../../icon";
import styles from "./trip-highlights.module.css";

interface TripHighlight {
  date: string;
  endDate?: string;
  nights?: number;
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
  activities?: ActivityOption[];
  tripStartDate?: string;
  tripEndDate?: string;
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

// Map ActivityCategory enum to display strings
const categoryDisplayMap: Record<ActivityCategory, string> = {
  [ActivityCategory.CATEGORY_UNKNOWN]: "✨ Experience",
  [ActivityCategory.TOUR]: "🚶 Tour",
  [ActivityCategory.MUSEUM]: "🎨 Museum",
  [ActivityCategory.RESTAURANT]: "🍴 Dining",
  [ActivityCategory.SHOW]: "🎭 Show",
  [ActivityCategory.OUTDOOR]: "🏔️ Outdoor",
  [ActivityCategory.WATER_SPORTS]: "🚤 Water",
  [ActivityCategory.NIGHTLIFE]: "🌙 Nightlife",
  [ActivityCategory.SHOPPING]: "🛍️ Shopping",
  [ActivityCategory.SPA]: "💆 Wellness",
  [ActivityCategory.ADVENTURE]: "🧗 Adventure",
  [ActivityCategory.CULTURAL]: "🏛️ Culture",
  [ActivityCategory.FOOD_TOUR]: "🍕 Food Tour",
};

// Fallback: guess category from name if category is UNKNOWN
const guessCategoryFromName = (name: string): string => {
  const lowerName = name.toLowerCase();
  if (lowerName.includes("food") || lowerName.includes("tasting") || lowerName.includes("culinary") || lowerName.includes("cooking") || lowerName.includes("wine") || lowerName.includes("pizza")) return "🍕 Food Tour";
  if (lowerName.includes("museum") || lowerName.includes("gallery")) return "🎨 Museum";
  if (lowerName.includes("boat") || lowerName.includes("cruise") || lowerName.includes("sailing") || lowerName.includes("kayak") || lowerName.includes("snorkel") || lowerName.includes("dive")) return "🚤 Water";
  if (lowerName.includes("hike") || lowerName.includes("trek") || lowerName.includes("mountain") || lowerName.includes("nature")) return "🏔️ Outdoor";
  if (lowerName.includes("show") || lowerName.includes("performance") || lowerName.includes("concert") || lowerName.includes("theater")) return "🎭 Show";
  if (lowerName.includes("spa") || lowerName.includes("wellness") || lowerName.includes("massage")) return "💆 Wellness";
  if (lowerName.includes("market") || lowerName.includes("shopping")) return "🛍️ Shopping";
  if (lowerName.includes("bar") || lowerName.includes("club") || lowerName.includes("nightlife")) return "🌙 Nightlife";
  if (lowerName.includes("tour") || lowerName.includes("walking") || lowerName.includes("guided")) return "🚶 Tour";
  return "✨ Experience";
};

const getActivityCategoryDisplay = (activity: ActivityOption): string => {
  const cat = activity.category as number;
  // Use actual category if it's set and not UNKNOWN (0)
  if (cat > 0) {
    return categoryDisplayMap[activity.category] || "✨ Experience";
  }
  // Fallback to name-based guessing
  return guessCategoryFromName(activity.name);
};

const TripHighlights: React.FC<TripHighlightsProps> = ({
  highlights,
  origin,
  destination,
  price,
  vibe = "Adventure",
  activities = [],
  tripStartDate,
  tripEndDate,
}) => {
  const [originCity, originCountry] = origin ? origin.split(", ") : ["", ""];
  const [destCity, destCountry] = destination ? destination.split(", ") : ["", ""];
  
  // Count category occurrences and prioritize distinct (less common) categories
  const categoryCounts = new Map<string, number>();
  for (const activity of activities) {
    const category = getActivityCategoryDisplay(activity);
    categoryCounts.set(category, (categoryCounts.get(category) || 0) + 1);
  }
  // Generic categories to deprioritize
  const genericCategories = ["🚶 Tour", "✨ Experience"];
  const topCategories = [...categoryCounts.entries()]
    .sort((a, b) => {
      const aIsGeneric = genericCategories.includes(a[0]) ? 1 : 0;
      const bIsGeneric = genericCategories.includes(b[0]) ? 1 : 0;
      // Put generic categories last, then sort by count descending
      if (aIsGeneric !== bIsGeneric) return aIsGeneric - bIsGeneric;
      return b[1] - a[1];
    })
    .slice(0, 3)
    .map(([category]) => category);

  const hasOrigin = originCity && originCity.trim() !== "";
  const hasDestination = destCity && destCity.trim() !== "";
  // Always show route if we have both origin and destination
  const showRoute = hasOrigin && hasDestination;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.route}>
          {showRoute && (
            <>
              <span className={styles.city}>{originCity}</span>
              {originCountry && originCountry !== "MockCountry" ? `, ${originCountry}` : ""}
              <span className={styles.arrow}>→</span>
              <span className={styles.city}>{destCity}</span>
              {destCountry && destCountry !== "MockCountry" ? `, ${destCountry}` : ""}
            </>
          )}
          {!showRoute && hasOrigin && (
            <>
              <span className={styles.city}>{originCity}</span>
              {originCountry && originCountry !== "MockCountry" ? `, ${originCountry}` : ""}
            </>
          )}
          {!showRoute && !hasOrigin && hasDestination && (
            <>
              <span className={styles.city}>{destCity}</span>
              {destCountry && destCountry !== "MockCountry" ? `, ${destCountry}` : ""}
            </>
          )}
          {!hasOrigin && !hasDestination && (
            <span className={styles.city}>Trip Details</span>
          )}
        </div>

        <button className={styles.selectButton}>{vibe}</button>
      </div>

      <div className={styles.highlightsSection}>
        <div className={styles.sectionTitle}>Trip Highlights • {formatDateRange(tripStartDate as string, tripEndDate)} </div>
        <div className={styles.timelineWrapper}>
          <div className={styles.timelineContainer}>
            <div className={styles.timeline}>
              {highlights.map((item, index) => (
                <div key={index} className={styles.timelineItemGroup}>
                  <div className={styles.timelineItem}>
                    <div className={styles.itemCard}>
                      <div className={styles.itemHeader}>
                        <span className={styles.itemDate}>
                          {item.type === "stay"
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
          <div className={styles.footer}>
            {activities.length > 0 && (
              <div className={styles.activitiesRow}>
                <div className={styles.activityChips}>
                  {topCategories.map((category, idx) => (
                    <span key={idx} className={styles.activityChip}>
                      {category}
                    </span>
                  ))}
                  <span className={styles.activityCount}>{activities.length} activities</span>
                </div>
              </div>
            )}
            <div className={styles.priceTag}>
              {price.currency === "USD"
                ? `$${Math.ceil(price.amount).toLocaleString()}`
                : `${price.currency} ${Math.ceil(price.amount).toLocaleString()}`}
            </div>
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
