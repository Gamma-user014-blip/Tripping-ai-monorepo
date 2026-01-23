type CountryEntry = {
  name: string;
  code: string;
};

type AirportEntry = {
  iata: string;
  name: string;
};

type TripLocationLike = {
  city?: string | null;
  country?: string | null;
  airport_code?: string | null;
};

import countries from "../common/countries.json";
import airports from "../common/airports.json";

const COUNTRY_CODE_TO_NAME: Record<string, string> = (() => {
  const mapping: Record<string, string> = {};
  for (const entry of countries as CountryEntry[]) {
    mapping[entry.code.toUpperCase()] = entry.name;
  }
  mapping["UK"] = "United Kingdom";
  mapping["EL"] = "Greece";
  mapping["USA"] = "United States";
  return mapping;
})();

const AIRPORT_CODE_TO_CITY: Record<string, string> = {
  // Israel
  TLV: "Tel Aviv",
  SDV: "Tel Aviv",
  ETH: "Eilat",
  VDA: "Eilat",
  HFA: "Haifa",
  // Italy
  FCO: "Rome",
  CIA: "Rome",
  MXP: "Milan",
  LIN: "Milan",
  BGY: "Bergamo",
  VCE: "Venice",
  TSF: "Venice",
  NAP: "Naples",
  FLR: "Florence",
  PSA: "Pisa",
  BLQ: "Bologna",
  TRN: "Turin",
  CTA: "Catania",
  PMO: "Palermo",
  OLB: "Olbia",
  CAG: "Cagliari",
  BRI: "Bari",
  // France
  CDG: "Paris",
  ORY: "Paris",
  BVA: "Paris",
  NCE: "Nice",
  MRS: "Marseille",
  LYS: "Lyon",
  TLS: "Toulouse",
  BOD: "Bordeaux",
  NTE: "Nantes",
  SXB: "Strasbourg",
  // United Kingdom
  LHR: "London",
  LGW: "London",
  STN: "London",
  LTN: "London",
  LCY: "London",
  SEN: "London",
  MAN: "Manchester",
  BHX: "Birmingham",
  EDI: "Edinburgh",
  GLA: "Glasgow",
  BRS: "Bristol",
  LPL: "Liverpool",
  NCL: "Newcastle",
  BFS: "Belfast",
  CWL: "Cardiff",
  // Spain
  BCN: "Barcelona",
  MAD: "Madrid",
  PMI: "Palma de Mallorca",
  AGP: "Malaga",
  ALC: "Alicante",
  VLC: "Valencia",
  SVQ: "Seville",
  BIO: "Bilbao",
  IBZ: "Ibiza",
  TFS: "Tenerife",
  TFN: "Tenerife",
  LPA: "Gran Canaria",
  FUE: "Fuerteventura",
  ACE: "Lanzarote",
  // Portugal
  LIS: "Lisbon",
  OPO: "Porto",
  FAO: "Faro",
  FNC: "Funchal",
  PDL: "Ponta Delgada",
  // Netherlands
  AMS: "Amsterdam",
  EIN: "Eindhoven",
  RTM: "Rotterdam",
  // Belgium
  BRU: "Brussels",
  CRL: "Brussels",
  ANR: "Antwerp",
  // Germany
  FRA: "Frankfurt",
  HHN: "Frankfurt",
  MUC: "Munich",
  BER: "Berlin",
  SXF: "Berlin",
  TXL: "Berlin",
  DUS: "Dusseldorf",
  HAM: "Hamburg",
  CGN: "Cologne",
  STR: "Stuttgart",
  HAJ: "Hanover",
  NUE: "Nuremberg",
  LEJ: "Leipzig",
  DRS: "Dresden",
  // Austria
  VIE: "Vienna",
  SZG: "Salzburg",
  INN: "Innsbruck",
  GRZ: "Graz",
  // Switzerland
  ZRH: "Zurich",
  GVA: "Geneva",
  BSL: "Basel",
  BRN: "Bern",
  // Czech Republic
  PRG: "Prague",
  BRQ: "Brno",
  // Poland
  WAW: "Warsaw",
  WMI: "Warsaw",
  KRK: "Krakow",
  GDN: "Gdansk",
  WRO: "Wroclaw",
  POZ: "Poznan",
  KTW: "Katowice",
  // Hungary
  BUD: "Budapest",
  // Greece
  ATH: "Athens",
  JTR: "Santorini",
  JMK: "Mykonos",
  HER: "Heraklion",
  CHQ: "Chania",
  RHO: "Rhodes",
  CFU: "Corfu",
  KGS: "Kos",
  ZTH: "Zakynthos",
  SKG: "Thessaloniki",
  // Turkey
  IST: "Istanbul",
  SAW: "Istanbul",
  AYT: "Antalya",
  ADB: "Izmir",
  ESB: "Ankara",
  DLM: "Dalaman",
  BJV: "Bodrum",
  // Scandinavia
  CPH: "Copenhagen",
  ARN: "Stockholm",
  BMA: "Stockholm",
  NYO: "Stockholm",
  GOT: "Gothenburg",
  OSL: "Oslo",
  TRD: "Trondheim",
  BGO: "Bergen",
  HEL: "Helsinki",
  TMP: "Tampere",
  // Baltic
  RIX: "Riga",
  VNO: "Vilnius",
  TLL: "Tallinn",
  // Croatia
  ZAG: "Zagreb",
  SPU: "Split",
  DBV: "Dubrovnik",
  PUY: "Pula",
  ZAD: "Zadar",
  // Slovenia
  LJU: "Ljubljana",
  // Romania
  OTP: "Bucharest",
  CLJ: "Cluj-Napoca",
  TSR: "Timisoara",
  // Bulgaria
  SOF: "Sofia",
  VAR: "Varna",
  BOJ: "Burgas",
  // Serbia
  BEG: "Belgrade",
  // Ireland
  DUB: "Dublin",
  SNN: "Shannon",
  ORK: "Cork",
  // Iceland
  KEF: "Reykjavik",
  // Cyprus
  LCA: "Larnaca",
  PFO: "Paphos",
  // Malta
  MLA: "Malta",
  // Morocco
  CMN: "Casablanca",
  RAK: "Marrakech",
  AGA: "Agadir",
  FEZ: "Fez",
  TNG: "Tangier",
  // Egypt
  CAI: "Cairo",
  HRG: "Hurghada",
  SSH: "Sharm El Sheikh",
  LXR: "Luxor",
  // UAE
  DXB: "Dubai",
  DWC: "Dubai",
  AUH: "Abu Dhabi",
  SHJ: "Sharjah",
  // Qatar
  DOH: "Doha",
  // Saudi Arabia
  RUH: "Riyadh",
  JED: "Jeddah",
  DMM: "Dammam",
  // Jordan
  AMM: "Amman",
  AQJ: "Aqaba",
  // Lebanon
  BEY: "Beirut",
  // USA - East Coast
  JFK: "New York",
  LGA: "New York",
  EWR: "Newark",
  BOS: "Boston",
  PHL: "Philadelphia",
  DCA: "Washington D.C.",
  IAD: "Washington D.C.",
  BWI: "Baltimore",
  MIA: "Miami",
  FLL: "Fort Lauderdale",
  MCO: "Orlando",
  TPA: "Tampa",
  ATL: "Atlanta",
  CLT: "Charlotte",
  RDU: "Raleigh",
  // USA - Midwest
  ORD: "Chicago",
  MDW: "Chicago",
  DTW: "Detroit",
  MSP: "Minneapolis",
  STL: "St. Louis",
  CLE: "Cleveland",
  CVG: "Cincinnati",
  IND: "Indianapolis",
  MKE: "Milwaukee",
  // USA - West Coast
  LAX: "Los Angeles",
  SFO: "San Francisco",
  OAK: "Oakland",
  SJC: "San Jose",
  SAN: "San Diego",
  SEA: "Seattle",
  PDX: "Portland",
  LAS: "Las Vegas",
  PHX: "Phoenix",
  DEN: "Denver",
  SLC: "Salt Lake City",
  // USA - Texas
  DFW: "Dallas",
  IAH: "Houston",
  HOU: "Houston",
  AUS: "Austin",
  SAT: "San Antonio",
  // USA - Other
  MSY: "New Orleans",
  BNA: "Nashville",
  HNL: "Honolulu",
  // Canada
  YYZ: "Toronto",
  YUL: "Montreal",
  YVR: "Vancouver",
  YYC: "Calgary",
  YEG: "Edmonton",
  YOW: "Ottawa",
  YHZ: "Halifax",
  YWG: "Winnipeg",
  // Mexico
  MEX: "Mexico City",
  CUN: "Cancun",
  GDL: "Guadalajara",
  SJD: "Los Cabos",
  PVR: "Puerto Vallarta",
  // Caribbean
  SJU: "San Juan",
  NAS: "Nassau",
  MBJ: "Montego Bay",
  PUJ: "Punta Cana",
  AUA: "Aruba",
  CUR: "Curacao",
  SXM: "St. Maarten",
  // South America
  GRU: "Sao Paulo",
  GIG: "Rio de Janeiro",
  EZE: "Buenos Aires",
  AEP: "Buenos Aires",
  SCL: "Santiago",
  BOG: "Bogota",
  LIM: "Lima",
  CCS: "Caracas",
  UIO: "Quito",
  MVD: "Montevideo",
  // Asia - East
  NRT: "Tokyo",
  HND: "Tokyo",
  KIX: "Osaka",
  NGO: "Nagoya",
  FUK: "Fukuoka",
  CTS: "Sapporo",
  ICN: "Seoul",
  GMP: "Seoul",
  PUS: "Busan",
  PEK: "Beijing",
  PKX: "Beijing",
  PVG: "Shanghai",
  SHA: "Shanghai",
  CAN: "Guangzhou",
  SZX: "Shenzhen",
  HKG: "Hong Kong",
  TPE: "Taipei",
  // Asia - Southeast
  SIN: "Singapore",
  KUL: "Kuala Lumpur",
  BKK: "Bangkok",
  DMK: "Bangkok",
  SGN: "Ho Chi Minh City",
  HAN: "Hanoi",
  CGK: "Jakarta",
  DPS: "Bali",
  MNL: "Manila",
  CEB: "Cebu",
  RGN: "Yangon",
  PNH: "Phnom Penh",
  REP: "Siem Reap",
  // Asia - South
  DEL: "New Delhi",
  BOM: "Mumbai",
  BLR: "Bangalore",
  MAA: "Chennai",
  CCU: "Kolkata",
  HYD: "Hyderabad",
  GOI: "Goa",
  CMB: "Colombo",
  MLE: "Male",
  KTM: "Kathmandu",
  DAC: "Dhaka",
  // Australia & New Zealand
  SYD: "Sydney",
  MEL: "Melbourne",
  BNE: "Brisbane",
  PER: "Perth",
  ADL: "Adelaide",
  CNS: "Cairns",
  OOL: "Gold Coast",
  AKL: "Auckland",
  WLG: "Wellington",
  CHC: "Christchurch",
  ZQN: "Queenstown",
  // South Africa
  JNB: "Johannesburg",
  CPT: "Cape Town",
  DUR: "Durban",
  // East Africa
  NBO: "Nairobi",
  ADD: "Addis Ababa",
  DAR: "Dar es Salaam",
  ZNZ: "Zanzibar",
  EBB: "Entebbe",
  KGL: "Kigali",
  // West Africa
  LOS: "Lagos",
  ACC: "Accra",
  ABJ: "Abidjan",
  DKR: "Dakar",
  // Russia
  SVO: "Moscow",
  DME: "Moscow",
  VKO: "Moscow",
  LED: "St. Petersburg",
};

const AIRPORT_CODE_TO_AIRPORT_NAME: Record<string, string> = (() => {
  const mapping: Record<string, string> = {};
  for (const entry of airports as AirportEntry[]) {
    mapping[entry.iata.toUpperCase()] = entry.name;
  }
  return mapping;
})();

const normalizeAirportCode = (airportCode: string | null | undefined): string => {
  if (!airportCode) return "";
  return airportCode.trim().toUpperCase();
};

const normalizeCountryName = (country: string | null | undefined): string => {
  if (!country) return "";

  const trimmed = country.trim();
  if (!trimmed) return "";

  const upper = trimmed.toUpperCase();
  const mapped = COUNTRY_CODE_TO_NAME[upper];
  if (mapped) return mapped;

  if (upper === "MOCKCOUNTRY") return "";

  return trimmed;
};

const normalizeCityName = (
  city: string | null | undefined,
  airportCode: string,
): string => {
  const trimmed = (city ?? "").trim();
  if (!trimmed) {
    const mapped = AIRPORT_CODE_TO_CITY[airportCode];
    return mapped ?? "";
  }

  const upper = trimmed.toUpperCase();
  const looksLikeIata = /^[A-Z]{3}$/.test(upper);
  if (looksLikeIata) {
    const mapped = AIRPORT_CODE_TO_CITY[airportCode] ?? AIRPORT_CODE_TO_CITY[upper];
    return mapped ?? trimmed;
  }

  return trimmed;
};

export const formatLocationLabel = (location: TripLocationLike | null): string => {
  if (!location) return "";

  const airportCode = normalizeAirportCode(location.airport_code);
  const city = normalizeCityName(location.city, airportCode);
  const country = normalizeCountryName(location.country);

  if (city && country) return `${city}, ${country}`;
  if (city) return city;

  const airportName = AIRPORT_CODE_TO_AIRPORT_NAME[airportCode];
  if (airportName && country) return `${airportName}, ${country}`;
  if (airportName) return airportName;

  if (airportCode && country) return `${airportCode}, ${country}`;
  if (airportCode) return airportCode;

  return country;
};
