import React from "react";
import styles from "./navbar.module.css";

const Navbar: React.FC = (): JSX.Element => {
  return (
    <nav className={styles.container}>
      <div className={styles.brand}>Tripping.ai</div>
      <div className={styles.actions}>
        <button className={styles.btn}>Explore</button>
        <button className={styles.btn}>Bookings</button>
        <button className={styles.btn}>Support</button>
        <button className={`${styles.btn} ${styles.btnPrimary}`}>
          Get started
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
