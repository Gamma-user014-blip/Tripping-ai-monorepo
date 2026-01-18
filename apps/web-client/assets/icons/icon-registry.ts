import ac from "./ac.svg";
import activity from "./activity.svg";
import arrowConnector from "./arrow-connector.svg";
import baggage from "./baggage.svg";
import flight from "./flight.svg";
import location from "./location.svg";
import plane from "./plane.svg";
import planeLanding from "./plane-landing.svg";
import shuttle from "./shuttle.svg";
import transport from "./transport.svg";
import wifi from "./wifi.svg";

export const ICON_SVGS = {
  ac,
  activity,
  arrow: arrowConnector,
  baggage,
  flight,
  location,
  plane,
  planeLanding,
  shuttle,
  transport,
  wifi,
} as const;

export type IconName = keyof typeof ICON_SVGS;
