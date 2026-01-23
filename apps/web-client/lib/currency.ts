/**
 * Currency conversion utility.
 * Exchange rates are approximate and should be updated for production use.
 * All conversions target USD as the base currency.
 */

interface ExchangeRates {
  [currency: string]: number;
}

// Exchange rates to USD (1 unit of currency = X USD)
// These are approximate rates - in production, use a live API
const exchangeRatesToUSD: ExchangeRates = {
  USD: 1,
  EUR: 1.08,
  GBP: 1.27,
  JPY: 0.0067,
  CAD: 0.74,
  AUD: 0.66,
  CHF: 1.12,
  CNY: 0.14,
  INR: 0.012,
  MXN: 0.058,
  BRL: 0.20,
  KRW: 0.00074,
  SGD: 0.74,
  HKD: 0.13,
  NOK: 0.094,
  SEK: 0.096,
  DKK: 0.15,
  NZD: 0.62,
  ZAR: 0.055,
  RUB: 0.011,
  THB: 0.029,
  PLN: 0.25,
  TRY: 0.031,
  AED: 0.27,
  SAR: 0.27,
  ILS: 0.28,
  PHP: 0.018,
  MYR: 0.22,
  IDR: 0.000063,
  TWD: 0.031,
  CZK: 0.043,
  HUF: 0.0027,
  CLP: 0.0011,
  COP: 0.00025,
  ARS: 0.0010,
  VND: 0.000041,
  EGP: 0.020,
  PKR: 0.0036,
  NGN: 0.00064,
  UAH: 0.024,
  RON: 0.22,
  BGN: 0.55,
  HRK: 0.14,
  ISK: 0.0073,
};

interface ConversionResult {
  amount: number;
  currency: "USD";
  originalAmount: number;
  originalCurrency: string;
}

/**
 * Convert an amount from a given currency to USD
 * @param amount - The amount to convert
 * @param fromCurrency - The source currency code (e.g., "EUR", "JPY")
 * @returns The converted amount in USD
 */
const convertToUSD = (amount: number, fromCurrency: string): number => {
  const normalizedCurrency = fromCurrency.toUpperCase();
  const rate = exchangeRatesToUSD[normalizedCurrency];

  if (rate === undefined) {
    console.warn(`Unknown currency: ${fromCurrency}, treating as USD`);
    return amount;
  }

  return Math.round(amount * rate * 100) / 100;
};

/**
 * Convert an amount from a given currency to USD with detailed result
 * @param amount - The amount to convert
 * @param fromCurrency - The source currency code
 * @returns Conversion result with original and converted values
 */
const convertToUSDWithDetails = (
  amount: number,
  fromCurrency: string
): ConversionResult => ({
  amount: convertToUSD(amount, fromCurrency),
  currency: "USD",
  originalAmount: amount,
  originalCurrency: fromCurrency.toUpperCase(),
});

/**
 * Check if a currency is supported for conversion
 * @param currency - The currency code to check
 * @returns True if the currency is supported
 */
const isSupportedCurrency = (currency: string): boolean =>
  exchangeRatesToUSD[currency.toUpperCase()] !== undefined;

/**
 * Get the exchange rate for a currency to USD
 * @param currency - The currency code
 * @returns The exchange rate or undefined if not supported
 */
const getExchangeRate = (currency: string): number | undefined =>
  exchangeRatesToUSD[currency.toUpperCase()];

/**
 * Get all supported currency codes
 * @returns Array of supported currency codes
 */
const getSupportedCurrencies = (): string[] => Object.keys(exchangeRatesToUSD);

/**
 * Format a USD amount for display
 * @param amount - The amount in USD
 * @param options - Intl.NumberFormat options
 * @returns Formatted currency string
 */
const formatUSD = (
  amount: number,
  options?: Partial<Intl.NumberFormatOptions>
): string =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    ...options,
  }).format(amount);

export {
  convertToUSD,
  convertToUSDWithDetails,
  isSupportedCurrency,
  getExchangeRate,
  getSupportedCurrencies,
  formatUSD,
  exchangeRatesToUSD,
};
