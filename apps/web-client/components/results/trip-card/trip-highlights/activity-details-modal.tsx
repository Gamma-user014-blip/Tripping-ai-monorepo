import React, { useEffect } from "react";
import { ActivityOption, Money } from "../../types";
import styles from "./activity-details-modal.module.css";
import { Icon } from "../../icon";

interface ActivityDetailsModalProps {
  activity: ActivityOption | null;
  isOpen: boolean;
  onClose: () => void;
}

const ActivityDetailsModal: React.FC<ActivityDetailsModalProps> = ({
  activity,
  isOpen,
  onClose,
}) => {
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent): void => {
      if (event.key === "Escape" && isOpen) onClose();
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen || !activity) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>): void => {
    if (e.target === e.currentTarget) onClose();
  };

  const formatPrice = (money: Money): string => {
    return `${Math.ceil(money.amount).toLocaleString()} ${money.currency === "USD" ? "$" : money.currency}`;
  };

  const firstSlot = activity.available_times && activity.available_times.length > 0 ? `${activity.available_times[0].date} ${activity.available_times[0].time}` : "Flexible";

  return (
    <div className={styles.backdrop} onClick={handleBackdropClick}>
      <div className={styles.modal} role="dialog" aria-modal="true">
        <button className={styles.closeButton} onClick={onClose}>✕</button>

        <div className={styles.hero}>
        <div className={styles.heroInner}>
            <div className={styles.heroLeft}>
            <div className={styles.heroMetaRow}>
                <div className={styles.heroLocation}>
                <Icon icon="location" height={18} color="white" />
                <span>{activity.location.city}</span>
                </div>

                <div className={styles.ratingPill} aria-label={`Rating ${activity.rating}`}>
                <strong>{activity.rating?.toFixed?.(1) ?? "—"}</strong>
                <span>{activity.review_count ? `(${activity.review_count})` : ""}</span>
                </div>

                <div className={styles.heroSubtitle}>{activity.provider}</div>
            </div>

            <div className={styles.heroTitle}>{activity.name}</div>
            </div>

            <div className={styles.heroRight} aria-hidden />
        </div>
        </div>

        <div className={styles.contentContainer}>
          {/* Top detail cards in a boxed row */}
          <div className={styles.box}>
            <div className={styles.detailsRow}>
            <div className={styles.detailCard}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div>
                  <div className={styles.cardLabel}>Duration</div>
                  <div className={styles.cardValue}>{activity.duration_minutes ? `${activity.duration_minutes} minutes` : 'Varies'}</div>
                </div>
              </div>
            </div>

            <div className={styles.detailCard}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div>
                  <div className={styles.cardLabel}>Location</div>
                  <div className={styles.cardValue}>{activity.location.city}, {activity.location.country}</div>
                </div>
              </div>
            </div>

            <div className={styles.detailCard}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div>
                  <div className={styles.cardLabel}>Group Size</div>
                  <div className={styles.cardValue}>{activity.max_participants <= 12 ? `Private (Up to ${activity.max_participants})` : `${activity.min_participants} - ${activity.max_participants} people`}</div>
                </div>
              </div>
            </div>
            </div>
          </div>

          {/* Key details grid in a box */}
          <div className={styles.box}>
            <div className={styles.detailsGrid}>
            <div>
              <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 700 }}>Difficulty</div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>{activity.difficulty_level || '—'}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 700 }}>Provider</div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>{activity.provider || '—'}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 700 }}>Distance</div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>{activity.distance_from_query_km ? `${activity.distance_from_query_km.toFixed(1)} km` : '—'}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 700 }}>Starts</div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>{firstSlot}</div>
            </div>
            </div>
          </div>

          {/* Highlights, Included, Excluded, Amenities each in small boxes */}
          {activity.highlights && activity.highlights.length > 0 && (
            <div className={styles.box}>
              <div className={styles.section}>
                <div className={styles.sectionTitle}>Highlights</div>
                <ul className={styles.list}>
                  {activity.highlights.map((highlight, index) => (
                    <li key={index} className={styles.listItem}>{highlight}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {activity.included && activity.included.length > 0 && (
            <div className={styles.box}>
              <div className={styles.section}>
                <div className={styles.sectionTitle}>Included</div>
                <ul className={styles.list}>
                  {activity.included.map((item, index) => (
                    <li key={index} className={styles.listItem}>✓ {item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {activity.excluded && activity.excluded.length > 0 && (
            <div className={styles.box}>
              <div className={styles.section}>
                <div className={styles.sectionTitle}>Not Included</div>
                <ul className={styles.list}>
                  {activity.excluded.map((item, index) => (
                    <li key={index} className={styles.listItem}>✗ {item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

        </div>

        {/* Footer preserved and visible at bottom of modal */}
        <div className={styles.modalFooter}>
          {activity.price_per_person && (
            <div className={styles.priceBlock}>
              <div className={styles.priceLabel}>Price</div>
              <div className={styles.priceAmount}>{formatPrice(activity.price_per_person)}</div>
              <div className={styles.priceSub}>per person</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ActivityDetailsModal;
