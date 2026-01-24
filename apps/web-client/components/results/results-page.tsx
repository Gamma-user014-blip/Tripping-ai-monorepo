import React, { useState, useEffect, useCallback, useRef } from "react";
import styles from "./results-page.module.css";
import confetti from "canvas-confetti";
import Navbar from "../../common/navbar";
import AiChatSidebar from "./ai-chat-sidebar";
import TripCard from "./trip-card";
import type { Trip } from "./types";
import {
  getOrCreateSessionId,
  TRIP_RESULTS_KEY_PREFIX,
  TRIP_IDS_KEY_PREFIX,
} from "../../lib/session";

type LoadingState = "idle" | "loading" | "loaded";

const ResultsPage: React.FC = (): JSX.Element => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [tripIds, setTripIds] = useState<string[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [isEditing, setIsEditing] = useState(false);
  const TOTAL_SLOTS = 3;
  const loadedCount = trips.length;
  const remainingCount = Math.max(0, TOTAL_SLOTS - loadedCount);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const prevTripsCountRef = useRef(0);
  const cardsContainerRef = useRef<HTMLDivElement>(null);

  const playSuccessSound = useCallback(() => {
    try {
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const playNote = (freq: number, start: number, duration: number) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.2, start);
        gain.gain.exponentialRampToValueAtTime(0.01, start + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(start);
        osc.stop(start + duration);
      };
      const now = audioCtx.currentTime;
      playNote(523.25, now, 0.1); // C5
      playNote(659.25, now + 0.1, 0.1); // E5
      playNote(783.99, now + 0.2, 0.3); // G5
    } catch (err) {
      console.warn("AudioContext failed:", err);
    }
  }, []);

  useEffect(() => {
    if (trips.length > prevTripsCountRef.current && cardsContainerRef.current) {
      // Find the last trip card added (using the data attribute)
      const cards = cardsContainerRef.current.querySelectorAll('[data-trip-card="true"]');
      const lastCard = Array.from(cards).pop() as HTMLElement;

      if (lastCard) {
        const rect = lastCard.getBoundingClientRect();
        const x = (rect.left + rect.width / 2) / window.innerWidth;
        const y = (rect.top + rect.height / 2) / window.innerHeight;

        // Trigger confetti at the card's position
        confetti({
          particleCount: 80,
          spread: 80,
          origin: { x, y },
          colors: ["#26ccff", "#a259ff", "#ff2121", "#25ff56", "#ffa502", "#ff0068"],
          zIndex: 10001,
        });
      } else {
        // Fallback to center if card not found
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
        });
      }

      playSuccessSound();
    }
    prevTripsCountRef.current = trips.length;
  }, [trips.length, playSuccessSound]);

  useEffect(() => {
    const sessionId = getOrCreateSessionId();
    const storedTripsJson = sessionStorage.getItem(
      `${TRIP_RESULTS_KEY_PREFIX}${sessionId}`,
    );
    const storedTripIdsJson = sessionStorage.getItem(
      `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
    );
    if (!storedTripsJson) return;

    try {
      const parsed = JSON.parse(storedTripsJson) as unknown;
      if (!Array.isArray(parsed)) return;
      const loadedTrips = parsed as Trip[];
      setTrips(loadedTrips);
      prevTripsCountRef.current = loadedTrips.length; // Don't fire on initial load from session

      if (storedTripIdsJson) {
        const parsedTripIds = JSON.parse(storedTripIdsJson) as unknown;
        if (Array.isArray(parsedTripIds)) {
          setTripIds(parsedTripIds as string[]);
        }
      }

      setLoadingState("loaded");
    } catch {
      // ignore
    }
  }, []);

  const handleTripsLoaded = useCallback((loadedTrips: Trip[]): void => {
    const sessionId = getOrCreateSessionId();
    sessionStorage.setItem(
      `${TRIP_RESULTS_KEY_PREFIX}${sessionId}`,
      JSON.stringify(loadedTrips),
    );

    const storedTripIdsJson = sessionStorage.getItem(
      `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
    );
    if (storedTripIdsJson) {
      try {
        const parsedTripIds = JSON.parse(storedTripIdsJson) as unknown;
        if (Array.isArray(parsedTripIds)) {
          setTripIds(parsedTripIds as string[]);
        }
      } catch {
        // ignore
      }
    }

    setTrips(loadedTrips);
    // Keep loading state as-is. We switch to "loaded" only when polling completes.
  }, []);

  const handleSearchStart = useCallback((): void => {
    setLoadingState("loading");
  }, []);

  const handleEditStart = useCallback((): void => {
    setIsEditing(true);
  }, []);

  const handleSearchComplete = useCallback((): void => {
    setLoadingState("loaded");
    setIsEditing(false);
  }, []);

  const handleSearchClear = useCallback((): void => {
    // Clear old results and show loading state when starting a new search
    setTrips([]);
    setTripIds([]);
    setLoadingState("loading");
    setIsEditing(false);
  }, []);

  return (
    <div className={`${styles.resultsPage} ${isEditing ? styles.isEditing : ""}`}>
      {isEditing && (
        <div className={styles.editOverlay}>
          <div className={styles.editOverlayContent}>
            <div className={styles.editStars}>
              <span className={styles.editStarLarge} />
              <span className={styles.editStarLarge} />
              <span className={styles.editStarLarge} />
            </div>
            <h2 className={styles.editTitle}>Editing your trip</h2>
            <div className={styles.editPulseBadge}>
              <span className={styles.pulseDot} />
              Refining details...
            </div>
          </div>
        </div>
      )}
      <div className={styles.navContainer}>
        <Navbar />
      </div>

      <div className={styles.heroSection} />

      <div className={styles.mainContainer}>
        <div className={styles.resultsAndFilters}>
          <div className={styles.filterContainer}>
            <AiChatSidebar
              onTripsLoaded={handleTripsLoaded}
              onSearchStart={handleSearchStart}
              onSearchClear={handleSearchClear}
              onSearchComplete={handleSearchComplete}
              onEditStart={handleEditStart}
            />
          </div>
          <div className={styles.resultsContainer}>
            <div>
              {loadingState === "idle" ? (
                <div className={styles.idleState}>
                  <div className={styles.idleIcon}>💬</div>
                  <h3 className={styles.idleTitle}>Start Planning Your Trip</h3>
                  <p className={styles.idleText}>
                    Chat with our AI assistant to get personalized trip
                    recommendations. Share your preferences, and we'll find the
                    perfect options for you!
                  </p>
                </div>
              ) : (
                <div>
                  <div className={styles.loadingBanner} role="region">
                    {loadingState === "loading" && remainingCount > 0 ? (
                      <>
                        <div className={styles.loadingEmoji} aria-hidden>🧭</div>
                        <div className={styles.loadingText}>
                          <div className={styles.loadingTitle}>Finding the perfect trips for you</div>
                          <div className={styles.loadingSubtitle}>Assembling personalized options — {loadedCount}/{TOTAL_SLOTS} ready</div>
                        </div>
                        <div className={styles.loadingStars} aria-hidden>
                          <span className={styles.star} />
                          <span className={styles.star} />
                          <span className={styles.star} />
                        </div>
                      </>
                    ) : (
                      <div className={styles.bannerHeader}>
                        <div className={styles.bannerHeaderLeft}>
                          <div className={styles.bannerEmoji} aria-hidden>✨</div>
                          <div>
                            <div className={styles.bannerHeaderTitle}>Trip ideas</div>
                            <div className={styles.bannerHeaderSubtitle}>
                              {loadedCount > 0
                                ? `${loadedCount} suggestion${loadedCount > 1 ? "s" : ""} — tailored from your chat`
                                : "Personalized options will appear here as the AI finalizes them"}
                            </div>
                          </div>
                        </div>
                        {loadingState === "loading" && remainingCount === 0 && (
                          <div className={styles.loadingStarsSmall} aria-hidden>
                            <span className={styles.star} />
                            <span className={styles.star} />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className={styles.cardsList} ref={cardsContainerRef}>
                    {trips.map((trip, index) => (
                      <TripCard
                        key={index}
                        trip={trip}
                        tripId={tripIds[index]}
                        tripIndex={index}
                      />
                    ))}
                    {Array.from({ length: Math.max(0, 3 - trips.length) }).map(
                      (_, i) => (
                        <div
                          className={styles.skeletonCard}
                          key={`skeleton-${i}`}
                          role="article"
                          aria-label="Loading trip option"
                        >
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
                                  <div
                                    className={styles.skeletonTimelineCard}
                                    key={j}
                                  />
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
                      ),
                    )}
                  </div>
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
