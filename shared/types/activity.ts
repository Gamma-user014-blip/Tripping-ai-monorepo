import { ActivityCategory } from "./enums";
import { ComponentScores, Location, Money, SearchMetadata } from "./common";

export interface PriceDetails {
  adult_price: Money;
  child_price: Money;
  senior_price: Money;
}

export interface TimeSlot {
  date: string;
  time: string;
  available_spots: number;
}

export interface ActivityOption {
  id: string;
  name: string;
  description: string;
  category: ActivityCategory;
  location: Location;
  distance_from_query_km: number;
  rating: number;
  review_count: number;
  price_per_person: Money;
  price_details: PriceDetails;
  duration_minutes: number;
  available_times: TimeSlot[];
  highlights: string[];
  included: string[];
  excluded: string[];
  min_participants: number;
  max_participants: number;
  difficulty_level: string;
  hotel_pickup: boolean;
  meal_included: boolean;
  cancellation_policy: string;
  scores: ComponentScores;
  booking_url: string;
  provider: string;
  available: boolean;
  image_urls: string[];
}

export interface ActivitySearchResponse {
  options: ActivityOption[];
  metadata: SearchMetadata;
}
