import React from "react";
import { HotelOption } from "../../types";
import { Icon } from "../../icon";
import styles from "./hotel-card.module.css";

interface HotelCardProps {
  hotels: HotelOption[];
}

const HotelCard: React.FC<HotelCardProps> = ({ hotels }) => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.label}>Hotel selection</span>
      </div>
      <div className={styles.dashedLine} />

      <div className={styles.hotelsList}>
        {hotels.map((hotel) => (
          <HotelItem key={hotel.id} hotel={hotel} />
        ))}
      </div>

      <div className={styles.dashedLine} />
    </div>
  );
};

const getHueFromId = (id: string): number => {
  let hash = 0;
  for (const char of id) {
    hash = (hash * 31 + char.charCodeAt(0)) % 360;
  }
  return hash;
};

const HOTEL_GRADIENTS: Array<[string, string]> = [
  ["hsl(210 70% 55%)", "hsl(232 70% 32%)"],
  ["hsl(195 70% 52%)", "hsl(214 70% 30%)"],
  ["hsl(255 65% 58%)", "hsl(275 70% 34%)"],
  ["hsl(220 24% 62%)", "hsl(232 26% 30%)"],
  ["hsl(205 65% 54%)", "hsl(255 55% 34%)"],
];

const getHotelImageStyle = (hotel: HotelOption): React.CSSProperties => {
  const index = getHueFromId(hotel.id) % HOTEL_GRADIENTS.length;
  const [from, to] = HOTEL_GRADIENTS[index];
  return {
    backgroundImage: `linear-gradient(135deg, ${from}, ${to})`,
  };
};

const HotelItem: React.FC<{ hotel: HotelOption }> = ({ hotel }) => {
  const address = `${hotel.location.city}, ${hotel.location.country}`;
  const priceText = `$${hotel.total_price.amount}/night`;

  return (
    <div className={styles.hotelItemWrapper}>
      <div className={styles.hotelDate}>{priceText}</div>
      <div className={styles.hotelItem}>
        <h4 className={styles.name}>{hotel.name}</h4>
        <div className={styles.addressRow}>
          <Icon icon="location" height={16} color="var(--color-text-subtle)" />
          <p className={styles.address}>{address}</p>
        </div>
        <div className={styles.stars}>
          {[...Array(hotel.star_rating)].map((_, i) => (
            <span key={i} className={styles.star}>
              ★
            </span>
          ))}
        </div>

        <div className={styles.imageContainer}>
          <div
            className={styles.image}
            style={getHotelImageStyle(hotel)}
            role="img"
            aria-label={hotel.name}
          >
            <div className={styles.imageOverlay}>
              <div className={styles.imageTitle}>{hotel.location.city}</div>
              <div className={styles.imageSubtitle}>{hotel.rating_category}</div>
            </div>
          </div>
        </div>

        <div className={styles.amenitiesSection}>
          <span className={styles.amenityHighlight}>{hotel.amenities[0]}</span>
        </div>

        <div className={styles.icons}>
          <div className={styles.iconItem}>
            <Icon icon="wifi" height={16} color="var(--color-text-subtle)" />
            <span>Free Wi-Fi</span>
          </div>
          <div className={styles.iconItem}>
            <Icon icon="shuttle" height={16} color="var(--color-text-subtle)" />
            <span>Shuttle</span>
          </div>
          <div className={styles.iconItem}>
            <Icon icon="ac" height={16} color="var(--color-text-subtle)" />
            <span>AC</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HotelCard;
