import { ActivityOption, ActivitySearchRequest } from "./activity";
import { SectionType } from "./enums";
import { FlightOption, FlightSearchRequest } from "./flight";
import { HotelOption, HotelSearchRequest } from "./hotel";
import { TransportOption } from "./transport";

export interface TransferResponse {
  options: TransportOption[];
}

export interface FlightResponse {
  options: FlightOption[];
}

export interface StayResponse {
  hotel_options: HotelOption[];
  activity_options: ActivityOption[];
}

export interface TripSectionResponse {
  type: SectionType;
  data: TransferResponse | FlightResponse | StayResponse;
}

export interface TripResponse {
  sections: TripSectionResponse[];
}

export interface FinalStayOption {
  hotel: HotelOption;
  activities: ActivityOption[];
}

export interface FinalTripSection {
  type: SectionType;
  data: TransportOption | FlightOption | FinalStayOption;
}

export interface FinalTripLayout {
  sections: FinalTripSection[];
}

export interface StayRequest {
  hotel_request: HotelSearchRequest;
  activity_request: ActivitySearchRequest;
}

export interface TripSection {
  type: SectionType;
  data: FlightSearchRequest | StayRequest;
}

export interface TripRequest {
  sections: TripSection[];
}
