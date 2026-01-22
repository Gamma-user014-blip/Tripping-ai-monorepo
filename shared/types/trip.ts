import { SectionType } from "./enums";
import { FlightOption } from "./flight";
import { HotelOption } from "./hotel";
import { ActivityOption } from "./activity";
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
