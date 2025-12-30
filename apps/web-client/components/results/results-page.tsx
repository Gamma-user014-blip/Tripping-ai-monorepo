import React from "react";
import { useRouter } from "next/router";
import styles from "./results-page.module.css";

const ResultsPage: React.FC = (): JSX.Element => {
  const router = useRouter();
  const { from, to, dates, adults, children } = router.query;

  return (
    <div className={styles.mainContainer}>
      <div>
        <h2>Search Parameters:</h2>
        <p>From: {from}</p>
        <p>To: {to}</p>
        <p>Dates: {dates}</p>
        <p>Adults: {adults}</p>
        <p>Children: {children}</p>
      </div>
    </div>
  );
};

export default ResultsPage;
