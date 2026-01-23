import React from "react";
import styles from "./navbar.module.css";

const Navbar: React.FC = (): JSX.Element => {
  const navigateToHome = () => {
    window.location.href = "/";
  };
  return (
    <nav className={styles.container}>
      <div
        className={styles.brand}
        onClick={navigateToHome}
        role="button"
        tabIndex={0}
      >
        Tripping.ai
      </div>
    </nav>
  );
};

export default Navbar;
