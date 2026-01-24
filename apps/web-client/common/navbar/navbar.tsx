import React from "react";
import Image from "next/image";
import { useRouter } from "next/router";
import styles from "./navbar.module.css";
import { resetSession } from "../../lib/session";

const Navbar: React.FC = (): JSX.Element => {
  const router = useRouter();
  const isHomePage = router.pathname === "/";

  const handleBrandClick = (): void => {
    // Reset session and navigate to homepage
    resetSession();
    window.location.href = "/";
  };

  const handleBrandKeyDown = (e: React.KeyboardEvent<HTMLDivElement>): void => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleBrandClick();
    }
  };

  const smoothScrollTo = (id: string): void => {
    const el = document.getElementById(id);
    if (!el) return;
    const NAVBAR_OFFSET = 24; // accounts for sticky navbar height + spacing
    const top = el.getBoundingClientRect().top + window.scrollY - NAVBAR_OFFSET;
    window.scrollTo({ top, behavior: "smooth" });
  };

  const handleHowItWorksClick = (e: React.MouseEvent<HTMLAnchorElement>): void => {
    e.preventDefault();
    if (router.pathname === "/") {
      smoothScrollTo("how-it-works");
    } else {
      router.push("/").then(() => setTimeout(() => smoothScrollTo("how-it-works"), 120));
    }
  };

  const handleStartPlanningClick = (e: React.MouseEvent<HTMLAnchorElement | HTMLButtonElement>): void => {
    // allow button or anchor
    e.preventDefault();
    const doScroll = () => smoothScrollTo("chat");
    // reset session first so chat input is ready
    resetSession();
    if (router.pathname === "/") {
      doScroll();
    } else {
      router.push("/").then(() => setTimeout(doScroll, 120));
    }
  };

  return (
    <nav className={styles.container}>
      <div
        className={styles.brand}
        onClick={handleBrandClick}
        onKeyDown={handleBrandKeyDown}
        role="button"
        tabIndex={0}
      >
        <Image
          src={require("../../assets/logo.png")}
          alt="Tripping.ai"
          height={90}
          width={165}
          style={{ objectFit: "contain" }}
          priority
        />
        <span className={styles.betaBadge}>beta</span>
      </div>

      <div className={styles.actions}>
        <a className={styles.btn} href="/about-us" target="_blank" rel="noreferrer">
          About us
        </a>

        <a className={styles.btn} href="/#how-it-works" onClick={handleHowItWorksClick}>
          How it works
        </a>

        {isHomePage ? (
          <a className={`${styles.btn} ${styles.btnPrimary}`} href="/" onClick={handleStartPlanningClick}>
            Start planning
          </a>
        ) : (
          <button
            type="button"
            className={`${styles.btn} ${styles.btnPrimary}`}
            onClick={handleStartPlanningClick}
          >
            New trip
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
