import React, { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import styles from "./trip-map.module.css";

interface MapWaypoint {
  lat: number;
  lng: number;
  label?: string;
}

interface TripMapProps {
  center: { lat: number; lng: number };
  zoom: number;
  waypoints?: MapWaypoint[];
  interactive?: boolean;
  variant?: "card" | "fill";
}

const TripMap: React.FC<TripMapProps> = ({
  center,
  zoom,
  waypoints,
  interactive = true,
  variant = "card",
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [hasError, setHasError] = useState(false);
  const API_KEY =
    process.env.NEXT_PUBLIC_MAPTILER_API_KEY || "a";

  useEffect(() => {
    if (map.current) return;
    if (!mapContainer.current) return;

    try {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${API_KEY}`,
        center: [center.lng, center.lat],
        zoom: zoom || 6,
        interactive: interactive,
        attributionControl: false,
      });
      requestAnimationFrame(() => {
        map.current?.resize();
      });

      if (interactive) {
        map.current.addControl(new maplibregl.NavigationControl(), "top-right");
      }

      map.current.on("load", () => {
        if (!map.current) return;

        map.current.resize();

        // Add waypoints logic
        if (waypoints && waypoints.length > 0) {
          const bounds = new maplibregl.LngLatBounds();
          const coordinates: [number, number][] = [];

          waypoints.forEach((waypoint) => {
            const pinEl = document.createElement("div");
            pinEl.style.width = "22px";
            pinEl.style.height = "30px";
            pinEl.style.display = "flex";
            pinEl.style.alignItems = "center";
            pinEl.style.justifyContent = "center";
            pinEl.style.pointerEvents = "auto";

            pinEl.innerHTML = `
              <svg viewBox="0 0 24 24" width="22" height="30" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="#0B3D91"/>
                <circle cx="12" cy="9" r="3.5" fill="#002A5C"/>
              </svg>
            `;

            // Anchor bottom and offset downwards so the tip aligns slightly below the coordinate
            new maplibregl.Marker({ element: pinEl, anchor: "bottom", offset: [0, 4] })
              .setLngLat([waypoint.lng, waypoint.lat])
              .setPopup(new maplibregl.Popup().setText(waypoint.label || ""))
              .addTo(map.current!);

            bounds.extend([waypoint.lng, waypoint.lat]);
            coordinates.push([waypoint.lng, waypoint.lat]);
          });

          // Close loop for trip path
          if (coordinates.length > 1) {
            // Check if loop is already closed or we want to loop it. static map code looked like it loops
            // const pathCoords = [...waypoints, waypoints[0]]...
            coordinates.push(coordinates[0]);

            map.current.addSource("route", {
              type: "geojson",
              data: {
                type: "Feature",
                properties: {},
                geometry: {
                  type: "LineString",
                  coordinates: coordinates,
                },
              },
            });

            map.current.addLayer({
              id: "route",
              type: "line",
              source: "route",
              layout: {
                "line-join": "round",
                "line-cap": "round",
              },
              paint: {
                "line-color": "#009688",
                "line-width": 2,
                "line-opacity": 0.95,
                "line-dasharray": [2, 3],
              },
            });
          }

          requestAnimationFrame(() => {
            map.current?.resize();
            map.current?.fitBounds(bounds, {
              padding: 60,
              maxZoom: 15,
            });
          });
        }
      });

      map.current.on("error", () => {
        // Vector tiles might fail but we don't want to destroy the map immediately on every tile error
        // setHasError(true);
      });
    } catch (e) {
      console.error("Map initialization failed", e);
      setHasError(true);
    }

    // Cleanup
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [
    center.lng,
    center.lat,
    zoom,
    API_KEY /* waypoints - handled in init only for now to safely avoid duplicates */,
  ]);

  return (
    <div
      className={`${styles.container} ${variant === "fill" ? styles.fill : ""} ${!interactive ? styles.nonInteractive : ""}`}
    >
      {!hasError ? (
        <div
          ref={mapContainer}
          className={styles.mapContainer}
          style={{ width: "100%", height: "100%" }}
        />
      ) : (
        <div className={styles.mapFallback}>
          <div className={styles.mapFallbackTitle}>Map unavailable</div>
          <div className={styles.mapFallbackText}>
            Unable to load map. Check API configuration.
          </div>
        </div>
      )}
    </div>
  );
};

export default TripMap;
