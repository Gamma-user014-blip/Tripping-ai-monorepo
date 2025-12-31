import Image from "next/image";
import styles from "./home-page.module.css";
import React from "react";
import TextLabel from "../../common/text-label";
import Widget from "common/search-widget";
import Navbar from "../../common/navbar";

const HomePage: React.FC = (): JSX.Element => {
  return (
    <div className={styles.homeContainer}>
      <div className={styles.navBar}>
        <Navbar />
      </div>
      <div className={styles.backgroundImage}>
        <Image
          alt="Back to nature"
          src={require("../../assets/background.jpg")}
          fill
          sizes="100vw"
          style={{ objectFit: "cover" }}
          priority
        />
      </div>
      <div className={styles.centerOverlay}>
        <TextLabel type="H300" classname={styles.title}>
          Simply choose your preferences.
        </TextLabel>
        <Widget />
      </div>
    </div>
  );
};

export default HomePage;
