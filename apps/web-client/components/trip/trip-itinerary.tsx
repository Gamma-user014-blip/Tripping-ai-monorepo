import React from 'react';
import styles from './trip-itinerary.module.css';
import { TripResult, FlightSegment, Hotel, TripHighlight } from '../results/types';
import { Icon } from '../results/icon';

interface TripItineraryProps {
  trip: TripResult;
}

// Helper to ensure consistent date formatting on server/client
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
};

export default function TripItinerary({ trip }: TripItineraryProps) {
  const stays = trip.hotels || [];

  return (
    <main className={styles.timelineContainer}>
      {/* 1. Outbound Flight */}
      <FlightCard
        type="outbound"
        segment={trip.outboundFlight}
        date={trip.startDate}
      />

      {stays.map((hotel, index) => {
        const label = index === 0 ? 'Airport Transfer to Hotel' : 'Transfer to Next Stay';
        const isPrimary = index === 0;
        const stayHighlights = filterHighlightsForHotelCity(trip.highlights, hotel);
        const nights = getNightsFromHotelDateRange(hotel);

        return (
          <React.Fragment key={hotel.id}>
            <TransferDivider label={label} />
            <StayCard
              hotel={hotel}
              highlights={stayHighlights}
              nights={nights}
              isPrimary={isPrimary}
            />
          </React.Fragment>
        );
      })}

      <TransferDivider label="Transfer to Airport" />

      {/* 3. Return Flight */}
      <FlightCard
        type="return"
        segment={trip.returnFlight}
        date={trip.endDate}
      />
    </main>
  );
}

// --- Subcomponents ---

function FlightCard({
  type,
  segment,
  date,
}: {
  type: 'outbound' | 'return';
  segment: FlightSegment;
  date: string;
}) {
  const isDeparture = type === 'outbound';

  return (
    <div className={styles.flightCard}>
      {/* <div className={styles.confirmedBadge}>Confirmed</div> */}
      <div className={styles.flightContent}>
        <div className={styles.flightIconBox}>
          <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
            {isDeparture ? 'flight_takeoff' : 'flight_land'}
          </span>
        </div>
        <div className={styles.flightDetails}>
          <div className={styles.dateTime}>
            {formatDate(date)} • {segment.departureTime}
          </div>
          <h4 className={styles.flightTitle}>
            Flight to {segment.destination.airportCode || segment.destination.city}
          </h4>
          <p className={styles.flightSub}>
            {segment.airline} • {segment.duration} •{' '}
            {segment.stops === 0 ? 'Direct' : `${segment.stops} Stop(s)`}
          </p>

          <div className={styles.flightRouteRow}>
            <div className={styles.flightTimeSection}>
              <span className={styles.flightTime}>{segment.departureTime}</span>
            </div>

            <div className={styles.flightIconSection}>
              <Icon icon="plane" height={18} color="var(--color-text-subtle)" />
              <span className={styles.flightCode}>
                {segment.origin.airportCode || segment.origin.city}
              </span>
            </div>

            <div className={styles.flightPath}>
              <span className={styles.flightDuration}>{segment.duration}</span>
              <div className={styles.flightLineWrapper}>
                <div className={styles.flightLine} />
                {segment.stops > 0 && (
                  <div className={styles.flightStopMarker}>
                    <div className={styles.flightStopDot} />
                    {segment.stopInfo && (
                      <span className={styles.flightStopText}>{segment.stopInfo}</span>
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
                {segment.destination.airportCode || segment.destination.city}
              </span>
            </div>

            <div className={styles.flightTimeSection}>
              <span className={styles.flightTime}>{segment.arrivalTime}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StayCard({
  hotel,
  highlights,
  nights,
  isPrimary,
}: {
  hotel: Hotel;
  highlights: TripHighlight[];
  nights: number;
  isPrimary: boolean;
}) {
  const [selectedActivity, setSelectedActivity] =
    React.useState<TripHighlight | null>(null);
  const [isActivityOpen, setIsActivityOpen] = React.useState(false);

  const bgImage =
    hotel.image && hotel.image.startsWith('http')
      ? `url("${hotel.image}")`
      : undefined;

  return (
    <div className={styles.stayCard}>
      <div
        className={styles.stayImageContainer}
        style={{ backgroundImage: bgImage }}
      >
        {!bgImage && (
          <span
            className="material-symbols-outlined"
            style={{ fontSize: '48px', color: '#9ca3af' }}
          >
            hotel
          </span>
        )}
        <div className={styles.ratingBadge}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: '14px', color: '#eab308' }}
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
                {isPrimary ? 'Primary Stay' : 'Secondary Stay'}
              </span>
              <span className={styles.stayNights}>{nights} Nights</span>
            </div>
            <h3 className={styles.stayTitle}>{hotel.name}</h3>
          </div>
        </div>

        <div className={styles.locationRow}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: '16px' }}
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

        <div className={styles.activitiesSection}>
          <h4 className={styles.activitiesTitle}>
            <span
              className="material-symbols-outlined"
              style={{ fontSize: '18px', color: '#0d9488' }}
            >
              attractions
            </span>
            Planned Activities
          </h4>
          <div className={styles.activitiesGrid}>
            {highlights
              .filter((h) => h.type === 'activity')
              .map((act, idx) => (
                <div
                  key={idx}
                  className={styles.activityCard}
                  onClick={() => {
                    setSelectedActivity(act);
                    setIsActivityOpen(true);
                  }}
                >
                  <div className={styles.activityIcon}>
                    <span className="material-symbols-outlined">attractions</span>
                  </div>
                  <div className={styles.activityInfo}>
                    <h5 className={styles.activityName}>{act.title}</h5>
                    <span className={styles.activityMeta}>
                      {formatDate(act.date)}
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>

      {isActivityOpen && selectedActivity && (
        <div
          className={styles.activityModalBackdrop}
          onClick={() => setIsActivityOpen(false)}
        >
          <div
            className={styles.activityModal}
            onClick={(e) => e.stopPropagation()}
          >
            <h4 className={styles.activityModalTitle}>{selectedActivity.title}</h4>
            <p className={styles.activityModalDate}>
              {formatDate(selectedActivity.date)}
            </p>
            <button
              className={styles.activityModalClose}
              onClick={() => setIsActivityOpen(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function TransferDivider({ label }: { label: string }) {
  return (
    <div className={styles.transferDivider}>
      <div className={styles.dividerLine}></div>
      <div className={styles.transferLabel}>
        <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
          directions_car
        </span>
        {label}
      </div>
      <div className={styles.dividerLine}></div>
    </div>
  );
}

const filterHighlightsForHotelCity = (
  highlights: TripHighlight[],
  hotel: Hotel,
) => {
  const hotelCity = hotel.location.city.toLowerCase();
  return highlights.filter((h) => {
    if (h.type !== 'activity') return false;
    const highlightCity = h.location?.city?.toLowerCase();
    return highlightCity ? highlightCity === hotelCity : true;
  });
};

const getNightsFromHotelDateRange = (hotel: Hotel) => {
  // Expected: "YYYY-MM-DD - YYYY-MM-DD"
  const rangeParts = hotel.dateRange.split(' - ').map((p) => p.trim());
  if (rangeParts.length !== 2) return 1;

  const start = new Date(rangeParts[0]);
  const end = new Date(rangeParts[1]);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 1;

  const diff = Math.abs(end.getTime() - start.getTime());
  const nights = Math.max(1, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  return nights;
};