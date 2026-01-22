import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./results-page.module.css";
import Widget from "common/search-widget/widget";
import AiChatSidebar from "./ai-chat-sidebar";
import TripCard from "./trip-card";
import type { TripResponse } from "./types";

type LoadingState = 'idle' | 'loading' | 'loaded'

const ResultsPage: React.FC = (): JSX.Element => {
  const router = useRouter();
  const query = router.query;

  const [results, setResults] = useState<TripResponse[] | null>(null)
  const [loadingState, setLoadingState] = useState<LoadingState>('idle')

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const from = Array.isArray(query.from) ? query.from[0] : (query.from as string | undefined);
  const to = Array.isArray(query.to) ? query.to[0] : (query.to as string | undefined);
  const dates = Array.isArray(query.dates) ? query.dates[0] : (query.dates as string | undefined);
  const adults = query.adults ? Number(Array.isArray(query.adults) ? query.adults[0] : query.adults) : undefined;
  const children = query.children ? Number(Array.isArray(query.children) ? query.children[0] : query.children) : undefined;

  const loadResults = async (): Promise<void> => {
    setLoadingState('loading')
    try {
      const res = await fetch('/api/results')
      if (!res.ok) throw new Error('Network response was not ok')
      const data = await res.json()

      setResults(Array.isArray(data) ? data : data.results ?? [])
      setLoadingState('loaded')
    } catch (err) {
      console.error('Failed to load results:', err)
      setResults([])
      setLoadingState('loaded')
    }
  }

  const handleChatMessage = (): void => {
    loadResults()
  }

  return (
    <div className={styles.resultsPage}>
      <div className={styles.mainContainer}>
        <div className={styles.widgetContainer}>
          <Widget
            type="secondary"
            initialFrom={from}
            initialTo={to}
            initialDates={dates}
            initialAdults={adults}
            initialChildren={children}
          />
        </div>
        <div className={styles.resultsAndFilters}>
          <div className={styles.filterContainer}>
            <AiChatSidebar onMessageSent={handleChatMessage} />
          </div>
          <div className={styles.resultsContainer}>
            <div>
              {loadingState === 'idle' ? (
                <div className={styles.idleState}>
                  <div className={styles.idleIcon}>💬</div>
                  <h3 className={styles.idleTitle}>Start Planning Your Trip</h3>
                  <p className={styles.idleText}>
                    Chat with our AI assistant to get personalized trip recommendations.
                    Share your preferences, and we'll find the perfect options for you!
                  </p>
                </div>
              ) : loadingState === 'loading' ? (
                <div className={styles.skeletonsContainer}>
                  {[1, 2, 3].map((i) => (
                    <div className={styles.skeletonCard} key={i} role="article" aria-label="Loading trip option">
                      {/* Hotel column */}
                      <div className={styles.skeletonHotel}>
                        <div className={styles.skeletonHotelHeader} />
                        <div className={styles.skeletonDashedLine} />
                        <div className={styles.skeletonHotelItem}>
                          <div className={styles.skeletonHotelDate} />
                          <div className={styles.skeletonHotelName} />
                          <div className={styles.skeletonHotelAddress} />
                          <div className={styles.skeletonHotelStars} />
                          <div className={styles.skeletonHotelImage} />
                          <div className={styles.skeletonHotelAmenity} />
                          <div className={styles.skeletonHotelIcons}>
                            <div className={styles.skeletonIconBox} />
                            <div className={styles.skeletonIconBox} />
                            <div className={styles.skeletonIconBox} />
                          </div>
                        </div>
                      </div>

                      {/* Middle section */}
                      <div className={styles.skeletonMiddle}>
                        {/* Trip Highlights section */}
                        <div className={styles.skeletonHighlights}>
                          <div className={styles.skeletonRouteHeader}>
                            <div className={styles.skeletonRouteText} />
                            <div className={styles.skeletonChipButton} />
                          </div>
                          <div className={styles.skeletonTimelineLabel} />
                          <div className={styles.skeletonTimeline}>
                            {[1, 2, 3, 4].map((j) => (
                              <div className={styles.skeletonTimelineCard} key={j} />
                            ))}
                          </div>
                          <div className={styles.skeletonPrice} />
                        </div>

                        {/* Flight Details section */}
                        <div className={styles.skeletonFlights}>
                          <div className={styles.skeletonFlightRow}>
                            <div className={styles.skeletonAirlineLogo} />
                            <div className={styles.skeletonFlightTime} />
                            <div className={styles.skeletonFlightCode} />
                            <div className={styles.skeletonFlightPath} />
                            <div className={styles.skeletonFlightCode} />
                            <div className={styles.skeletonFlightTime} />
                            <div className={styles.skeletonBaggage} />
                          </div>
                          <div className={styles.skeletonFlightRow}>
                            <div className={styles.skeletonAirlineLogo} />
                            <div className={styles.skeletonFlightTime} />
                            <div className={styles.skeletonFlightCode} />
                            <div className={styles.skeletonFlightPath} />
                            <div className={styles.skeletonFlightCode} />
                            <div className={styles.skeletonFlightTime} />
                            <div className={styles.skeletonBaggage} />
                          </div>
                        </div>
                      </div>

                      {/* Map column */}
                      <div className={styles.skeletonMap} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className={styles.cardsList}>
                  {results && results.map((result, index) => (
                    <TripCard key={index} trip={result} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
