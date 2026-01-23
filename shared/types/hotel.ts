import {
  ComponentScores,
  DateRange,
  Location,
  Money,
  SearchMetadata,
} from "./common";
import { PreferenceType } from "./enums";

export interface RoomInfo {
  type: string;
  beds: number;
  bed_type: string;
  max_occupancy: number;
  size_sqm: number;
  features: string[];
}

export interface Fee {
  name: string;
  amount: Money;
  mandatory: boolean;
}

export interface HotelOption {
  id: string;
  name: string;
  description: string;
  location: Location;
  distance_to_center_km: number;
  image: string;
  rating: number;
  review_count: number;
  rating_category: string;
  price_per_night: Money;
  total_price: Money;
  additional_fees: Fee[];
  room: RoomInfo;
  amenities: string[];
  category: string;
  star_rating: number;
  scores: ComponentScores;
  booking_url: string;
  provider: string;
  available: boolean;
}

export interface HotelSearchRequest {
  location: Location;
  dates: DateRange;
  guests: number;
  rooms: number;
  preferences: PreferenceType[];
  max_results: number;
  max_price_per_night: number;
  min_rating: number;
  amenities: number[];
}

export interface HotelSearchResponse {
  options: HotelOption[];
  metadata: SearchMetadata;
}
