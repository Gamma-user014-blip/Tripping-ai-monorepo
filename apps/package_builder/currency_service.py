import json
import time
import os
import requests

CACHE_FILE = os.path.join(os.path.dirname(__file__), "currency_cache.json")
CACHE_TTL = 86400  # 24 hours in seconds
API_URL = "https://open.er-api.com/v6/latest/USD"

# Fallback rates if API fails
FALLBACK_RATES = {
    "USD": 1.0,
    "EUR": 1.1746,
    "GBP": 1.3477,
    "AUD": 0.6673,
    "NZD": 0.5767,
    "CAD": 0.7288,
    "CHF": 1.2626,
    "JPY": 0.00638,
    "CNY": 0.1429,
    "INR": 0.01111,
    "SGD": 0.7780,
    "HKD": 0.1284,
    "SEK": 0.1086,
    "ILS": 0.3139,
    "MXN": 0.0559,
    "ZAR": 0.0607
}

class CurrencyService:
    _instance = None
    _rates = {}
    _last_updated = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurrencyService, cls).__new__(cls)
            cls._instance._load_rates()
        return cls._instance

    def _load_rates(self):
        # Try loading from cache first
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    self._rates = data.get('rates', {})
                    self._last_updated = data.get('timestamp', 0)
                    print("Loaded currency rates from cache.")
                    
                    if time.time() - self._last_updated < CACHE_TTL:
                        print("Cache is fresh.")
                        return
                    else:
                        print("Cache is stale. Attempting update from API...")
            except Exception as e:
                print(f"Failed to load cache: {e}")

        # Fetch from API if cache is invalid/missing/stale
        self._fetch_rates()

    def _fetch_rates(self):
        print("Fetching currency rates from API...")
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            # Open Exchange Rates API returns rates relative to base (USD).
            # e.g. "EUR": 0.92 means 1 USD = 0.92 EUR.
            # We need equivalent USD value for 1 unit of currency.
            # So if 1 USD = 0.92 EUR, then 1 EUR = 1/0.92 USD.
            api_rates = data.get('rates', {})
            
            # Convert to our format (Multiplier to get USD)
            # API: USD -> Currency
            # Ours: Currency -> USD
            new_rates = {}
            for curr, rate in api_rates.items():
                if rate > 0:
                    new_rates[curr] = 1.0 / rate
            
            self._rates = new_rates
            self._last_updated = time.time()
            self._save_cache()
            print("Successfully fetched and cached rates.")
            
        except Exception as e:
            print(f"Error fetching rates: {e}.")
            if self._rates:
                print("Using stale cache.")
            else:
                print("Cache empty. Using fallback.")
                self._rates = FALLBACK_RATES

    def _save_cache(self):
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump({
                    'timestamp': self._last_updated,
                    'rates': self._rates
                }, f)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def get_rate(self, currency_code):
        return self._rates.get(currency_code, FALLBACK_RATES.get(currency_code, 1.0))

# Global function helper
def get_currency_rate(currency_code):
    return CurrencyService().get_rate(currency_code)
