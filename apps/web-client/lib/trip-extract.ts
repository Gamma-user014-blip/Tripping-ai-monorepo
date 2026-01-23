import {
  ActivityOption,
  FlightOption,
  HotelOption,
  Location,
  Money,
  SectionType,
  TransportOption,
  Trip,
} from "@shared/types";
import {
  SectionData,
  isFlightOption,
  isFinalStayOption,
  isTransportOption,
} from "./trip-type-guards";
import { convertToUSD } from "./currency";

export interface TripWaypoint {
  lat: number;
  lng: number;
  label: string;
}

export interface ExtractedTripData {
  hotels: HotelOption[];
  flights: FlightOption[];
  activities: ActivityOption[];
  transfers: TransportOption[];
  totalPrice: Money;
  origin: Location;
  destination: Location;
  startDate: string;
  endDate: string;
  waypoints: TripWaypoint[];
  mapCenter: { lat: number; lng: number };
  firstHotel: HotelOption | null;
}

const extractTripData = (trip: Trip): ExtractedTripData => {
  const hotels: HotelOption[] = [];
  const flights: FlightOption[] = [];
  const activities: ActivityOption[] = [];
  const transfers: TransportOption[] = [];
  const orderedPath: TripWaypoint[] = [];

  let totalPriceAmount = 0;

  let origin: Location | null = null;
  let mainDestination: Location | null = null;
  let startDate = "";
  let endDate = "";
  let firstHotel: HotelOption | null = null;

  for (const section of trip.layout.sections) {
    const data = section.data as SectionData;

    if (section.type === SectionType.FLIGHT && isFlightOption(data)) {
      flights.push(data);
      totalPriceAmount += convertToUSD(
        data.total_price.amount,
        data.total_price.currency,
      );

      if (!origin) {
        origin = data.outbound.origin;
        startDate = data.outbound.departure_time.split("T")[0] || "";
      }

      const flightDest = data.outbound.destination;
      endDate = data.outbound.arrival_time.split("T")[0] || endDate;

      const isReturnFlight =
        origin &&
        flightDest.latitude === origin.latitude &&
        flightDest.longitude === origin.longitude;

      if (!isReturnFlight) {
        mainDestination = flightDest;
        orderedPath.push({
          lat: flightDest.latitude,
          lng: flightDest.longitude,
          label: flightDest.city,
        });
      }

      continue;
    }

    if (section.type === SectionType.STAY && isFinalStayOption(data)) {
      hotels.push(data.hotel);
      totalPriceAmount += convertToUSD(
        data.hotel.total_price.amount,
        data.hotel.total_price.currency,
      );

      if (!firstHotel) {
        firstHotel = data.hotel;
      }

      orderedPath.push({
        lat: data.hotel.location.latitude,
        lng: data.hotel.location.longitude,
        label: data.hotel.location.city,
      });

      for (const activity of data.activities) {
        activities.push(activity);
      }

      continue;
    }

    if (section.type === SectionType.TRANSFER && isTransportOption(data)) {
      transfers.push(data);
      totalPriceAmount += convertToUSD(
        data.total_price.amount,
        data.total_price.currency,
      );
    }
  }

  const defaultLocation: Location = {
    city: "",
    country: "",
    airport_code: "",
    latitude: 0,
    longitude: 0,
  };

  // Fallback: if no destination from flights, use first hotel location
  if (!mainDestination && firstHotel) {
    mainDestination = firstHotel.location;
  }

  // Fallback: if no origin from flights, use first hotel location as well
  if (!origin && firstHotel) {
    origin = firstHotel.location;
  }

  // Fallback: if no dates from flights, try to get from activities
  if (!startDate && activities.length > 0) {
    const allDates = activities
      .flatMap((a) => a.available_times?.map((t) => t.date) ?? [])
      .filter(Boolean)
      .sort();
    if (allDates.length > 0) {
      startDate = allDates[0];
      endDate = allDates[allDates.length - 1];
    }
  }

  const uniqueWaypoints = orderedPath.filter(
    (wp, index, arr) =>
      arr.findIndex((w) => w.lat === wp.lat && w.lng === wp.lng) === index,
  );

  const mapCenter =
    uniqueWaypoints.length > 0
      ? {
          lat:
            uniqueWaypoints.reduce((sum, wp) => sum + wp.lat, 0) /
            uniqueWaypoints.length,
          lng:
            uniqueWaypoints.reduce((sum, wp) => sum + wp.lng, 0) /
            uniqueWaypoints.length,
        }
      : { lat: 51.5, lng: -0.1 };

  return {
    hotels,
    flights,
    activities,
    transfers,
    totalPrice: { currency: "USD", amount: Math.round(totalPriceAmount) },
    origin: origin || defaultLocation,
    destination: mainDestination || defaultLocation,
    startDate,
    endDate,
    waypoints: uniqueWaypoints,
    mapCenter,
    firstHotel,
  };
};

export default extractTripData;
