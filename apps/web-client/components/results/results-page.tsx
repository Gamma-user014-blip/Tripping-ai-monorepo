import React from "react";
import { useRouter } from "next/router";
import styles from "./results-page.module.css";
import Widget from "common/search-widget/widget";
import AiChatSidebar from "./ai-chat-sidebar";
import TripCard from "./trip-card";
import { MOCK_RESULTS } from "./mock-data";

const ResultsPage: React.FC = (): JSX.Element => {
  const router = useRouter();
  const query = router.query;

  const from = Array.isArray(query.from) ? query.from[0] : (query.from as string | undefined);
  const to = Array.isArray(query.to) ? query.to[0] : (query.to as string | undefined);
  const dates = Array.isArray(query.dates) ? query.dates[0] : (query.dates as string | undefined);
  const adults = query.adults ? Number(Array.isArray(query.adults) ? query.adults[0] : query.adults) : undefined;
  const children = query.children ? Number(Array.isArray(query.children) ? query.children[0] : query.children) : undefined;

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
            <AiChatSidebar />
          </div>
          <div className={styles.resultsContainer}>
            <div className={styles.cardsList}>
              {MOCK_RESULTS.map((result) => (
                <TripCard key={result.id} result={result} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
