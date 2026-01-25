import React, { useState, useEffect, useRef } from "react";
import styles from "./trip-sidebar.module.css";
import TripMap from "../results/trip-card/trip-map";
import { exportTripToPDF, TripResult } from "./trip-pdf-export";
import { Snackbar, Alert } from "@mui/material";

interface TripSidebarProps {
  trip: TripResult;
}

const TripSidebar = ({ trip }: TripSidebarProps): JSX.Element => {
  const totalPrice = trip.price;
  const waypoints = trip.waypoints;
  const mapCenter = trip.mapCenter;

  const [calendarEventIds, setCalendarEventIds] = useState<string[]>([]);

  // Snackbar state
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState<"success" | "error">(
    "success"
  );

  const popupRef = useRef<Window | null>(null);

  const handleSnackbar = (
    message: string,
    severity: "success" | "error" = "success"
  ) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const formatPrice = (amount: number, currency: string): string => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(Math.ceil(amount));
  };

const handleRemoveFromCalendar = async () => {
  if (!calendarEventIds.length) return;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

  const res = await fetch(
    `${apiUrl}/api/calendar/remove-trip-from-calendar`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        eventIds: calendarEventIds,
        state: oauthStateRef.current, // same state used for add
      }),
      credentials: "include",
    }
  );

  if (!res.ok) {
    handleSnackbar("Failed to remove trip from calendar", "error");
    return;
  }

  const data = await res.json();
  console.log("Deleted event IDs:", data.deletedEventIds);
  setCalendarEventIds([]); // clear after deletion
  handleSnackbar("Trip removed from calendar successfully!", "success");
};


const oauthStateRef = useRef<string | null>(null);

const handleAddToCalendar = async (trip: TripResult) => {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
    console.log("[Parent] calling add-trip-to-calendar", apiUrl);
const res = await fetch(
  `${apiUrl}/api/calendar/add-trip-to-calendar`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trip,
      state: oauthStateRef.current, // undefined on first call, set on retry
    }),
    credentials: "include",
  }
);


    console.log("[Parent] add-trip-to-calendar response status:", res.status);

    if (res.status === 401) {
      console.warn("[Parent] not authenticated, opening OAuth popup");

      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      const state = crypto.randomUUID(); // or your own random ID
      oauthStateRef.current = state;

      const authPopup = window.open(
        `${apiUrl}/api/auth/google?state=${encodeURIComponent(state)}`,
        "GoogleAuth",
        `width=${width},height=${height},top=${top},left=${left}`
      );

      if (authPopup) {
        popupRef.current = authPopup;
      } else {
        console.warn("[Parent] Popup blocked by browser");
        handleSnackbar(
          "Please allow popups for this site and try again.",
          "error"
        );
      }

      return { ok: false, status: res.status };
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      console.error("Failed to add trip to Google Calendar", err);
      handleSnackbar(
        "Failed to add trip to calendar. Please try again.",
        "error"
      );
      return { ok: false, status: res.status, err };
    }

    const data = await res.json();
    console.log("[Parent] Created Google event IDs:", data.createdEventIds);

    setCalendarEventIds(data.createdEventIds || []);
    handleSnackbar("Trip added to calendar successfully!", "success");

    return { ok: true, data };
  } catch (error) {
    console.error("Error adding to calendar:", error);
    handleSnackbar("An error occurred. Please try again.", "error");
    return { ok: false, error };
  }
};


  const handleExportPDF = async (trip: TripResult) => {
    await exportTripToPDF(trip, {
      filename: `${trip.origin.city}-to-${trip.destination.city}.pdf`,
    });
  };

useEffect(() => {
  const handleMessage = async (event: MessageEvent) => {
    console.log("[Parent] message event:", {
      origin: event.origin,
      data: event.data,
    });

    const allowedOrigins = [
      window.location.origin,
      "http://localhost:3001",
    ];
    if (!allowedOrigins.includes(event.origin)) return;
    if (!event.data || typeof event.data !== "object") return;

    const { status, state, close } = event.data as {
      status?: string;
      state?: string;
      close?: boolean;
    };

    if (status === "success" && state && state === oauthStateRef.current) {
      console.log("[Parent] OAuth completed, retrying add-to-calendar...");
      const result = await handleAddToCalendar(trip);
      console.log("[Parent] handleAddToCalendar result:", result);

      if (close && popupRef.current) {
        popupRef.current.close();
        popupRef.current = null;
      }
    }
  };

  window.addEventListener("message", handleMessage);
  return () => window.removeEventListener("message", handleMessage);
}, [trip]);



  return (
    <aside className={styles.sidebarContainer}>
      <div className={styles.detailsCard}>
        <h3 className={styles.cardTitle}>
          <span
            className="material-symbols-outlined"
            style={{ color: "var(--color-primary)" }}
          >
            description
          </span>
          Trip Details
        </h3>
        <div className={styles.detailsList}>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Travelers</span>
            <span className={styles.detailValue}>2 Adults</span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Trip ID</span>
            <span
              className={`${styles.detailValue} ${styles.detailValueMono}`}
            >
              {trip.tripId}
            </span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Flights</span>
            <span className={styles.confirmedText}>
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "16px" }}
              >
                check_circle
              </span>
              Confirmed
            </span>
          </div>
          <div className={`${styles.detailRow} ${styles.priceRow}`}>
            <span className={styles.priceLabel}>Total Cost</span>
            <span className={styles.priceValue}>
              {typeof totalPrice === "number"
                ? formatPrice(totalPrice, "USD")
                : formatPrice(
                    totalPrice.amount ?? 0,
                    totalPrice.currency ?? "USD"
                  )}
            </span>
          </div>
        </div>
      </div>

      <div className={styles.buttonStack}>
        <button
          className={styles.actionButton}
          onClick={() => handleExportPDF(trip)}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            download
          </span>
          Download PDF
        </button>

        <button
          className={styles.actionButton}
          onClick={() => handleAddToCalendar(trip)}
          disabled={calendarEventIds.length > 0}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            calendar_add_on
          </span>
          {calendarEventIds.length > 0
            ? "Added to Calendar"
            : "Add to Calendar"}
        </button>

        <button
          className={styles.actionButton}
          onClick={handleRemoveFromCalendar}
          disabled={calendarEventIds.length === 0}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            delete
          </span>
          {calendarEventIds.length === 0
            ? "Nothing to Remove"
            : "Remove Trip from Calendar"}
        </button>
      </div>

      <div className={styles.mapCard}>
        <TripMap
          center={mapCenter}
          zoom={5}
          waypoints={waypoints}
          interactive={true}
          variant="fill"
        />
      </div>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: "100%" }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </aside>
  );
};

export default TripSidebar;
