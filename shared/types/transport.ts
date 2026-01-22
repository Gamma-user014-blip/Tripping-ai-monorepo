import { TransportMode } from "./enums";
import { ComponentScores, Location, Money, SearchMetadata } from "./common";

export interface RentalCarDetails {
  vehicle_class: string;
  vehicle_model: string;
  seats: number;
  luggage: number;
  transmission: string;
  air_conditioning: boolean;
  unlimited_mileage: boolean;
  included_features: string[];
  daily_rate: Money;
  insurance_cost: Money;
}

export interface RideDetails {
  vehicle_type: string;
  seats: number;
  shared: boolean;
  estimated_wait_minutes: number;
}

export interface PublicTransitDetails {
  line: string;
  stops: number;
  transfer_points: string[];
  service_class: string;
  wifi: boolean;
  food_service: boolean;
}

export interface TransportDetails {
  rental_car?: RentalCarDetails | null;
  ride?: RideDetails | null;
  transit?: PublicTransitDetails | null;
}

export interface TransportOption {
  id: string;
  mode: TransportMode;
  provider: string;
  origin: Location;
  destination: Location;
  distance_km: number;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  total_price: Money;
  price_per_person: Money;
  details: TransportDetails;
  scores: ComponentScores;
  booking_url: string;
  available: boolean;
}

export interface TransportSearchResponse {
  options: TransportOption[];
  metadata: SearchMetadata;
}
