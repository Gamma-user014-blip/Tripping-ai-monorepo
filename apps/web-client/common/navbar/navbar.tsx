import React from "react";
import Image from "next/image";
import { useRouter } from "next/router";
import styles from "./navbar.module.css";
import { resetSession } from "../../lib/session";

const Navbar: React.FC = (): JSX.Element => {
  const router = useRouter();

  const handleBrandClick = (): void => {
    // If already on homepage, do nothing
    if (router.pathname === "/") return;

    // Reset session and navigate to homepage
    resetSession();
    window.location.href = "/";
  };

  return (
    <nav className={styles.container}>
      <div
        className={styles.brand}
        onClick={handleBrandClick}
        role="button"
        tabIndex={0}
      >
        <Image
          src={require("../../assets/logo.png")}
          alt="Tripping.ai"
          height={140}
          width={165}
          style={{ objectFit: "contain" }}
          priority
        />
      </div>
    </nav>
  );
};

export default Navbar;
