import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./trip-page.module.css";
import Navbar from "../../common/navbar";
import TripHeader from "./trip-header";
import TripItinerary from "./trip-itinerary";
import TripSidebar from "./trip-sidebar";
import type { TripResponse } from "../results/types";

const TripPage: React.FC = (): JSX.Element => {
  const router = useRouter();
  const { tripId } = router.query;
  const [trip, setTrip] = useState<TripResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrip = async () => {
      try {
        const response = await fetch("/api/results");
        const data = await response.json();
        const trips: TripResponse[] = Array.isArray(data) ? data : data.results ?? [];
        setTrip(trips[0] || null);
      } catch (error) {
        console.error("Failed to fetch trip:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrip();
  }, [tripId]);

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
          <div className={styles.error}>Trip not found</div>
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
            <TripSidebar trip={trip} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripPage;
