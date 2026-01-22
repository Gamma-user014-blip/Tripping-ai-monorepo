export interface Money {
  currency: string;
  amount: number;
}

export interface Location {
  city: string;
  country: string;
  airport_code: string;
  latitude: number;
  longitude: number;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface TimeRange {
  start_time: string;
  end_time: string;
}

export interface ComponentScores {
  price_score: number;
  quality_score: number;
  convenience_score: number;
  preference_score: number;
}

export interface SearchMetadata {
  total_results: number;
  search_id: string;
  timestamp: string;
  data_source: string;
}
