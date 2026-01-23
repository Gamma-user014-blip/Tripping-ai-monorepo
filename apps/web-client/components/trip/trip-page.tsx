import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./trip-page.module.css";
import Navbar from "../../common/navbar";
import TripHeader from "./trip-header";
import TripItinerary from "./trip-itinerary";
import TripSidebar from "./trip-sidebar";
import type { Trip } from "@shared/types";
import { apiClient } from "../../lib/api-client";

const TripPage: React.FC = (): JSX.Element => {
  const router = useRouter();
  const { tripId } = router.query;
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const normalizedTripId =
    typeof tripId === "string"
      ? tripId
      : Array.isArray(tripId)
        ? tripId[0]
        : null;

  useEffect(() => {
    if (!router.isReady) return;

    const fetchTrip = async () => {
      try {
        if (!normalizedTripId) {
          setErrorMessage("Missing tripId");
          setTrip(null);
          return;
        }

        setErrorMessage(null);
        const fetchedTrip = await apiClient.get<Trip>(
          `/api/trips/${normalizedTripId}`,
        );
        setTrip(fetchedTrip);
      } catch (error) {
        setTrip(null);
        setErrorMessage(
          error instanceof Error ? error.message : "Failed to fetch trip",
        );
      } finally {
        setLoading(false);
      }
    };

    setLoading(true);
    fetchTrip();
  }, [router.isReady, normalizedTripId]);

  if (loading) {
    return (
      <div className={styles.tripPage}>
        <div className={styles.navContainer}>
          <Navbar />
        </div>
        <div className={styles.mainContainer}>
          <div className={styles.loading}>Loading trip details...</div>
        </div>
      </div>
    );
  }

  if (!trip) {
    return (
      <div className={styles.tripPage}>
        <div className={styles.navContainer}>
          <Navbar />
        </div>
        <div className={styles.mainContainer}>
          <div className={styles.error}>{errorMessage || "Trip not found"}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.tripPage} id="trip-page-content">
      <div className={styles.navContainer}>
        <Navbar />
      </div>

      <div className={styles.mainContainer}>
        <TripHeader trip={trip} />

        <div className={styles.contentGrid}>
          <div className={styles.itinerarySection}>
            <TripItinerary trip={trip} />
          </div>

          <div className={styles.sidebarSection}>
            <TripSidebar trip={trip} bookingRef={normalizedTripId || ""} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripPage;
