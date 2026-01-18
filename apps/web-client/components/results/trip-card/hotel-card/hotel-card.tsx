import React from "react";
import { Hotel } from "../../types";
import { Icon } from "../../icon";
import styles from "./hotel-card.module.css";

interface HotelCardProps {
  hotels: Hotel[];
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

const HotelItem: React.FC<{ hotel: Hotel }> = ({ hotel }) => {
  const address = `${hotel.location.city}, ${hotel.location.country}`;

  return (
    <div className={styles.hotelItemWrapper}>
      <div className={styles.hotelDate}>{hotel.dateRange}</div>
      <div className={styles.hotelItem}>
        <h4 className={styles.name}>{hotel.name}</h4>
        <div className={styles.addressRow}>
          <Icon icon="location" height={16} color="var(--color-text-subtle)" />
          <p className={styles.address}>{address}</p>
        </div>
        <div className={styles.stars}>
          {[...Array(hotel.stars)].map((_, i) => (
            <span key={i} className={styles.star}>
              ★
            </span>
          ))}
        </div>

        <div className={styles.imageContainer}>
          <img src={hotel.image} alt={hotel.name} className={styles.image} />
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
