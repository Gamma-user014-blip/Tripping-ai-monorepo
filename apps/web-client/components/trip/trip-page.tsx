import React from "react";
import { useRouter } from "next/router";
import styles from "./trip-page.module.css";
import Navbar from "../../common/navbar";
import TripHeader from "./trip-header";
import TripItinerary from "./trip-itinerary";
import TripSidebar from "./trip-sidebar";
import { MOCK_RESULTS } from "../results/mock-data";

const TripPage: React.FC = (): JSX.Element => {
  const router = useRouter();
  const { tripId } = router.query;

  // Find trip by tripId or fallback to first mock result
  const trip = MOCK_RESULTS.find((t) => t.tripId === tripId) || MOCK_RESULTS[0];

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
