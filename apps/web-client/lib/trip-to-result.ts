import { Trip, FlightOption, HotelOption } from "@shared/types";
import { TripResult } from "../components/trip/trip-pdf-export";
import extractTripData from "./trip-extract";
import {
    SectionData,
    isFlightOption,
    isFinalStayOption,
} from "./trip-type-guards";
import { SectionType } from "@shared/types";

/**
 * Converts a Trip object to a TripResult object for use with PDF export and sidebar
 */
export const tripToResult = (trip: Trip, tripId: string): TripResult => {
    const extracted = extractTripData(trip);

    // Get outbound and return flights
    let outboundFlight: FlightOption | null = null;
    let returnFlight: FlightOption | null = null;

    for (const section of trip.layout.sections) {
        const data = section.data as SectionData;
        if (section.type === SectionType.FLIGHT && isFlightOption(data)) {
            if (!outboundFlight) {
                outboundFlight = data;
            } else {
                returnFlight = data;
            }
        }
    }

    // Build hotels with date ranges
    const hotelsWithDates: (HotelOption & { dateRange: string })[] = [];
    for (const section of trip.layout.sections) {
        const data = section.data as SectionData;
        if (section.type === SectionType.STAY && isFinalStayOption(data)) {
            const hotel = data.hotel;
            const nights = Math.round(
                hotel.total_price.amount / hotel.price_per_night.amount
            );
            hotelsWithDates.push({
                ...hotel,
                dateRange: `${nights} night${nights > 1 ? "s" : ""}`,
            });
        }
    }

    // Build highlights from flights, activities, and stays
    const highlights: any[] = [];

    // Add outbound flight as highlight
    if (outboundFlight) {
        highlights.push({
            date: outboundFlight.outbound.departure_time.split("T")[0],
            title: `Flight to ${outboundFlight.outbound.destination.city}`,
            type: "flight",
            location: outboundFlight.outbound.destination,
        });
    }

    // Add stay highlights with nights
    for (const section of trip.layout.sections) {
        const data = section.data as SectionData;
        if (section.type === SectionType.STAY && isFinalStayOption(data)) {
            const hotel = data.hotel;
            const nights = hotel.price_per_night.amount > 0
                ? Math.max(1, Math.round(hotel.total_price.amount / hotel.price_per_night.amount))
                : 1;
            
            highlights.push({
                date: outboundFlight?.outbound.departure_time.split("T")[0] || extracted.startDate.split("T")[0],
                title: `Stay in ${hotel.location.city}`,
                type: "stay",
                location: hotel.location,
                nights: nights,
            });
        }
    }

    // Add activities as highlights
    for (const activity of extracted.activities) {
        if (activity.available_times && activity.available_times.length > 0) {
            highlights.push({
                date: activity.available_times[0].date,
                title: activity.name,
                type: "activity",
                location: activity.location,
            });
        }
    }

    // Add return flight as highlight
    if (returnFlight) {
        highlights.push({
            date: returnFlight.outbound.departure_time.split("T")[0],
            title: `Return flight to ${returnFlight.outbound.destination.city}`,
            type: "flight",
            location: returnFlight.outbound.destination,
        });
    }

    // Default flight segment if no flights exist
    const defaultFlightSegment = {
        airline: "Unknown",
        flight_number: "",
        origin: extracted.origin,
        destination: extracted.destination,
        departure_time: extracted.startDate || new Date().toISOString(),
        arrival_time: extracted.endDate || new Date().toISOString(),
        duration_minutes: 0,
        stops: 0,
        layovers: [],
        aircraft: "",
        cabin_class: "Economy",
        amenities: {
            wifi: false,
            meal: false,
            entertainment: false,
            power_outlet: false,
            legroom_inches: 0,
        },
        luggage: {
            checked_bags: 0,
            checked_bag_weight_kg: 0,
            carry_on_bags: 0,
            carry_on_weight_kg: 0,
            carry_on_dimensions_cm: "",
        },
    };

    return {
        id: tripId,
        tripId: tripId,
        origin: extracted.origin,
        destination: extracted.destination,
        startDate: extracted.startDate || new Date().toISOString(),
        endDate: extracted.endDate || new Date().toISOString(),
        price: extracted.totalPrice,
        hotels: hotelsWithDates,
        highlights: highlights,
        outboundFlight: outboundFlight?.outbound || defaultFlightSegment,
        returnFlight: returnFlight?.outbound || defaultFlightSegment,
        mapCenter: extracted.mapCenter,
        mapZoom: 5,
        waypoints: extracted.waypoints,
    };
};
