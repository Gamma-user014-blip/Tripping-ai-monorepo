import React from "react";
import { HotelOption } from "../../types";
import { Icon } from "../../icon";
import styles from "./hotel-card.module.css";

interface HotelCardProps {
  hotels: HotelOption[];
}

const formatAmenity = (amenity: string): string => {
  const amenityMap: Record<string, string> = {
    wifi: "Free Wi-Fi",
    breakfast: "Breakfast",
    concierge: "Concierge",
    pool: "Pool",
    gym: "Gym",
    spa: "Spa",
    parking: "Parking",
    restaurant: "Restaurant",
    bar: "Bar",
    laundry: "Laundry",
    "room service": "Room Service",
    "24h reception": "24h Reception",
    onsen: "Hot Spring",
    dinner: "Dinner",
    shuttle: "Shuttle",
    ac: "AC",
  };

  const key = amenity.toLowerCase();
  return amenityMap[key] || amenity.charAt(0).toUpperCase() + amenity.slice(1);
};

type IconName = React.ComponentProps<typeof Icon>["icon"];

const AmenityIcon: React.FC<{ amenity: string }> = ({ amenity }) => {
  const iconMap: Record<string, IconName> = {
    wifi: "wifi",
    shuttle: "shuttle",
    ac: "ac",
  };

  const iconName = iconMap[amenity.toLowerCase()] || "location";
  return <Icon icon={iconName} height={16} color="var(--color-text-subtle)" />;
};

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

const getFallbackGradient = (hotel: HotelOption): string => {
  const index = getHueFromId(hotel.id) % HOTEL_GRADIENTS.length;
  const [from, to] = HOTEL_GRADIENTS[index];
  return `linear-gradient(135deg, ${from}, ${to})`;
};

const getHotelImageStyle = (hotel: HotelOption): React.CSSProperties => {
  if (hotel.image) {
    return {
      backgroundImage: `url(${hotel.image})`,
      backgroundSize: "cover",
      backgroundPosition: "center",
    };
  }
  return {
    backgroundImage: getFallbackGradient(hotel),
  };
};

const HotelItem: React.FC<{ hotel: HotelOption }> = ({ hotel }) => {
  const address = `${hotel.location.city}, ${hotel.location.country}`;
  const priceText =
    hotel.price_per_night.currency === "USD"
      ? `$${hotel.price_per_night.amount}/night`
      : `${hotel.price_per_night.amount} ${hotel.price_per_night.currency}/night`;

  const uniqueAmenities = Array.from(
    new Map(
      (hotel.amenities || []).map((amenity) => [
        amenity.toLowerCase(),
        amenity,
      ]),
    ).values(),
  );

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
              <div className={styles.imageSubtitle}>
                {hotel.rating_category}
              </div>
            </div>
          </div>
        </div>

        <div className={styles.icons}>
          {uniqueAmenities.slice(0, 3).map((amenity, i) => (
            <div key={i} className={styles.iconItem}>
              <AmenityIcon amenity={amenity} />
              <span>{formatAmenity(amenity)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HotelCard;
