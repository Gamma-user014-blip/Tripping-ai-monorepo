import type {
  FlightOption,
  FinalStayOption,
  TransportOption,
} from "@shared/types";

type SectionData = TransportOption | FlightOption | FinalStayOption;

const isFlightOption = (data: SectionData): data is FlightOption => {
  return "outbound" in data;
};

const isFinalStayOption = (data: SectionData): data is FinalStayOption => {
  return "hotel" in data && "activities" in data;
};

const isTransportOption = (data: SectionData): data is TransportOption => {
  return "mode" in data && "departure_time" in data;
};

export type { SectionData };
export { isFlightOption, isFinalStayOption, isTransportOption };
