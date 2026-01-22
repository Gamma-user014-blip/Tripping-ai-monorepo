import { ComponentScores, Location, Money, SearchMetadata } from "./common";

export interface AmenityInfo {
  wifi: boolean;
  meal: boolean;
  entertainment: boolean;
  power_outlet: boolean;
  legroom_inches: number;
}

export interface Layover {
  airport: Location;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  arrival_terminal?: string | null;
  departure_terminal?: string | null;
  airline_before: string;
  airline_after: string;
  is_airline_change: boolean;
  is_terminal_change: boolean;
  overnight: boolean;
}

export interface LuggageInfo {
  checked_bags: number;
  checked_bag_weight_kg: number;
  carry_on_bags: number;
  carry_on_weight_kg: number;
  carry_on_dimensions_cm: string;
}

export interface FlightSegment {
  origin: Location;
  destination: Location;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops: number;
  layovers: Layover[];
  airline: string;
  flight_number: string;
  aircraft: string;
  cabin_class: string;
  amenities: AmenityInfo;
  luggage: LuggageInfo;
}

export interface FlightOption {
  id: string;
  outbound: FlightSegment;
  total_price: Money;
  price_per_person: Money;
  scores: ComponentScores;
  booking_url: string;
  provider: string;
  available: boolean;
}

export interface FlightSearchRequest {
  origin: Location;
  destination: Location;
  departure_date: string;
  return_date?: string;
  passengers: number;
  cabin_class: string;
  preferences?: number[];
  max_results?: number;
  max_price?: number;
  max_stops?: number;
}

export interface FlightSearchResponse {
  options: FlightOption[];
  metadata: SearchMetadata;
}
