export interface Location {
  city: string;
  country: string;
  airportCode?: string;
  latitude: number;
  longitude: number;
}

export interface Money {
  currency: string;
  amount: number;
}

export interface Hotel {
  id: string;
  name: string;
  location: Location;
  stars: number;
  image: string;
  amenities: string[];
  rating: number;
  dateRange: string;
}

export interface FlightSegment {
  airline: string;
  airlineLogo: string;
  departureTime: string;
  arrivalTime: string;
  origin: Location;
  destination: Location;
  duration: string;
  stops: number;
  stopInfo?: string;
}

export interface TripHighlight {
  date: string;
  title: string;
  type: "flight" | "activity" | "transport";
  location?: Location;
}

export interface MapWaypoint {
  lat: number;
  lng: number;
  label?: string;
}

export interface TripResult {
  id: string;
  tripId: string;
  origin: Location;
  destination: Location;
  startDate: string;
  endDate: string;
  price: Money;
  hotels: Hotel[];
  highlights: TripHighlight[];
  outboundFlight: FlightSegment;
  returnFlight: FlightSegment;
  mapCenter: { lat: number; lng: number };
  mapZoom: number;
  waypoints: MapWaypoint[];
}
