'use client';

import html2pdf from 'html2pdf.js';
import { Location, Money, FlightSegment, HotelOption as Hotel } from '@shared/types';

interface TripHighlight {
  date: string;
  endDate?: string;
  nights?: number;
  title: string;
  type: "flight" | "activity" | "transport";
  location?: Location;
}

export interface TripResult {
  id: string;
  tripId: string;
  origin: Location;
  destination: Location;
  startDate: string;
  endDate: string;
  price: Money;
  hotels: (Hotel & { dateRange: string })[];
  highlights: TripHighlight[];
  outboundFlight: FlightSegment;
  returnFlight: FlightSegment;
  mapCenter: { lat: number; lng: number };
  mapZoom: number;
  waypoints: { lat: number; lng: number; label?: string }[];
}
interface TripPDFOptions {
  filename?: string;
  logoUrl?: string;
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const formatTime = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
};

const generateFlightHTML = (flight: FlightSegment, type: 'outbound' | 'return') => {
  const stops = flight.stops === 0 ? 'Non-stop' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`;

  return `
    <div style="margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: #fafafa;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
  <div>
    <h4 style="margin: 0; color: #1a1a1a; font-size: 14px; font-weight: 600;">${type === 'outbound' ? 'OUTBOUND FLIGHT' : 'RETURN FLIGHT'}</h4>
  </div>
  <div style="background-color: #007AFF; color: white; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
    ${flight.airline}
  </div>
</div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
          <p style="margin: 0; color: #666; font-size: 11px; font-weight: 500;">FROM</p>
          <p style="margin: 4px 0 0 0; color: #1a1a1a; font-size: 16px; font-weight: 600;">
            ${flight.origin.city}
            ${flight.origin.airport_code ? `<span style="color: #666; font-size: 12px;"> (${flight.origin.airport_code})</span>` : ''}
          </p>
          <p style="margin: 2px 0 0 0; color: #666; font-size: 13px; font-weight: 500;">${formatTime(flight.departure_time)}</p>
        </div>

        <div style="flex: 1; margin: 0 20px; text-align: center;">
          <p style="margin: 0; color: #666; font-size: 11px; font-weight: 500;">${formatDuration(flight.duration_minutes)}</p>
          <div style="margin: 8px 0; border-bottom: 2px solid #007AFF; position: relative;">
            <div style="position: absolute; left: -6px; top: -7px; width: 12px; height: 12px; background-color: #007AFF; border-radius: 50%; border: 2px solid white;"></div>
            <div style="position: absolute; right: -6px; top: -7px; width: 12px; height: 12px; background-color: #007AFF; border-radius: 50%; border: 2px solid white;"></div>
          </div>
          <p style="margin: 8px 0 0 0; color: #666; font-size: 11px;">${stops}</p>
        </div>

        <div style="text-align: right;">
          <p style="margin: 0; color: #666; font-size: 11px; font-weight: 500;">TO</p>
          <p style="margin: 4px 0 0 0; color: #1a1a1a; font-size: 16px; font-weight: 600;">
            ${flight.destination.city}
            ${flight.destination.airport_code ? `<span style="color: #666; font-size: 12px;"> (${flight.destination.airport_code})</span>` : ''}
          </p>
          <p style="margin: 2px 0 0 0; color: #666; font-size: 13px; font-weight: 500;">${formatTime(flight.arrival_time)}</p>
        </div>
      </div>
    </div>
  `;
};

const generateHotelHTML = (hotel: Hotel & { dateRange: string }, index: number) => {
  const amenitiesList = hotel.amenities.slice(0, 4).join(' • ');

  return `
    <div style="margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; background-color: white;">
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 12px 15px; color: white;">
        <h4 style="margin: 0; font-size: 14px; font-weight: 600;">${hotel.name}</h4>
        <p style="margin: 2px 0 0 0; font-size: 11px; opacity: 0.9;">${hotel.location.city}, ${hotel.location.country}</p>
      </div>
      
      <div style="padding: 15px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
          <div>
            <p style="margin: 0; color: #666; font-size: 11px; font-weight: 500;">RATING</p>
            <p style="margin: 4px 0 0 0; color: #1a1a1a; font-size: 14px; font-weight: 600;">
              ⭐ ${hotel.rating}/5 (${hotel.star_rating} stars)
            </p>
          </div>
          <div style="text-align: right;">
            <p style="margin: 0; color: #666; font-size: 11px; font-weight: 500;">STAY</p>
            <p style="margin: 4px 0 0 0; color: #1a1a1a; font-size: 12px; font-weight: 600;">${hotel.dateRange}</p>
          </div>
        </div>

        ${amenitiesList
      ? `
          <div style="background-color: #f5f5f5; padding: 10px; border-radius: 6px; margin-top: 12px;">
            <p style="margin: 0; color: #666; font-size: 10px; font-weight: 500; margin-bottom: 4px;">AMENITIES</p>
            <p style="margin: 0; color: #1a1a1a; font-size: 12px;">${amenitiesList}</p>
          </div>
        `
      : ''
    }
      </div>
    </div>
  `;
};

const generateHighlightsHTML = (highlights: any[]) => {
  if (!highlights || highlights.length === 0) return '';
  const getHighlightIcon = (highlight: TripHighlight) => {
    if (highlight.type === 'flight') return '✈️';
    if (highlight.type === 'activity') return '🎯';

    // type === 'transport'
    const titleLower = highlight.title.toLowerCase();
    if (titleLower.includes('train')) return '🚆';
    if (titleLower.includes('bus')) return '🚌';
    if (titleLower.includes('ferry') || titleLower.includes('boat')) return '⛴️';
    return '🚗';
  };

  return `
    <div style="margin-top: 25px; page-break-inside: avoid;">
      <h3 style="margin: 0 0 15px 0; color: #1a1a1a; font-size: 16px; font-weight: 700; border-bottom: 3px solid #007AFF; padding-bottom: 8px;">Trip Highlights</h3>
${highlights
      .map(
        (highlight) => `
      <div style="display: flex; margin-bottom: 12px; padding: 10px; background-color: #f9f9f9; border-radius: 6px;">
        <div style="min-width: 40px; text-align: center; margin-right: 12px;">
          <div style="width: 36px; height: 36px; background-color: #007AFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">
            ${getHighlightIcon(highlight)}
          </div>
        </div>
        <div style="flex: 1;">
          <p style="margin: 0; color: #1a1a1a; font-size: 12px; font-weight: 600;">${highlight.title}</p>
          <p style="margin: 2px 0 0 0; color: #666; font-size: 11px;">${formatDate(highlight.date)}</p>
        </div>
      </div>
    `
      )
      .join('')}

    </div>
  `;
};

const getTripDays = (start: string, end: string) => {
  const startDate = new Date(start.split('T')[0]);
  const endDate = new Date(end.split('T')[0]);
  const diffMs = endDate.getTime() - startDate.getTime();
  const days = Math.round(diffMs / (1000 * 60 * 60 * 24));
  return Math.max(1, days);
};


export const exportTripToPDF = async (
  trip: TripResult,
  options: TripPDFOptions = {}
) => {
  const { filename = `trip-${trip.tripId}.pdf`, logoUrl } = options;

  if (typeof window === 'undefined') return;

  const html2pdf = (await import('html2pdf.js')).default;

  let logoSrc: string | null = null;
  if (logoUrl) {
    try {
      const response = await fetch(logoUrl);
      if (response.ok) {
        const blob = await response.blob();
        logoSrc = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as string);
          reader.readAsDataURL(blob);
        });
      }
    } catch (e) {
      console.error('Failed to load logo:', e);
    }
  }

  const htmlContent = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${trip.origin.city} to ${trip.destination.city}</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
          color: #1a1a1a;
          line-height: 1.6;
          background-color: #fff;
        }

  .container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    padding: 30px 20px;
  }

        .header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 30px;
          border-radius: 12px;
          margin-bottom: 30px;
          box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        }

        .header h1 {
          font-size: 32px;
          margin-bottom: 8px;
          font-weight: 700;
        }

        .trip-route {
          font-size: 16px;
          opacity: 0.95;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .trip-route .separator {
          font-size: 20px;
        }

        .header-meta {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 15px;
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .meta-item {
          text-align: center;
        }

        .meta-label {
          font-size: 11px;
          font-weight: 600;
          opacity: 0.8;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .meta-value {
          font-size: 18px;
          font-weight: 700;
          margin-top: 4px;
        }

        .booking-ref {
          background-color: rgba(255, 255, 255, 0.15);
          padding: 8px 12px;
          border-radius: 6px;
          font-family: 'Courier New', monospace;
          font-size: 13px;
          word-break: break-all;
        }

        .section {
          margin-bottom: 30px;
        }

        .section h2 {
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 15px;
          color: #1a1a1a;
          border-bottom: 3px solid #007AFF;
          padding-bottom: 8px;
        }

        .price-card {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          color: white;
          padding: 20px;
          border-radius: 12px;
          text-align: center;
          margin: 20px 0;
          font-size: 28px;
          font-weight: 700;
        }

        .hotels-container {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .flights-container {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .footer {
          margin-top: 40px;
          padding-top: 20px;
          border-top: 1px solid #e0e0e0;
          text-align: center;
          color: #999;
          font-size: 11px;
        }

        @media print {
          body {
            background-color: white;
          }
          .container {
            max-width: 100%;
            padding: 0;
          }
        }
      </style>
    </head>
    <body>
    <div class="container">
     
        <div class="header">
          <h1>${trip.origin.city} → ${trip.destination.city}</h1>
          <div class="trip-route">
            <span>${trip.origin.country}</span>
            <span class="separator">→</span>
            <span>${trip.destination.country}</span>
          </div>
          
          <div class="header-meta">
            <div class="meta-item">
              <div class="meta-label">Departure</div>
              <div class="meta-value">${formatDate(trip.startDate)}</div>
            </div>
            <div class="meta-item">
              <div class="meta-label">Duration</div>
              <div class="meta-value">
                ${trip.highlights.reduce((total, h) => total + (h.nights || 0), 0)} nights
              </div>
            </div>
            
            <div class="meta-item">
              <div class="meta-label">Return</div>
              <div class="meta-value">${formatDate(trip.endDate)}</div>
            </div>
          </div>

          <div style="margin-top: 15px;">
            <div class="meta-label">Booking Reference</div>
            <div class="booking-ref">${trip.tripId}</div>
          </div>
        </div>

        <!-- Total Price -->
        <div class="price-card">
          ${trip.price.currency} ${trip.price.amount.toLocaleString()}
        </div>

        <!-- Flights Section -->
        <div class="section flights-container">
          <h2>✈️ Flights</h2>
          ${generateFlightHTML(trip.outboundFlight, 'outbound')}
          ${generateFlightHTML(trip.returnFlight, 'return')}
        </div>

        <!-- Hotels Section -->
        ${trip.hotels && trip.hotels.length > 0
      ? `
          <div class="section">
            <h2>🏨 Accommodations</h2>
            <div class="hotels-container">
              ${trip.hotels.map((hotel, idx) => generateHotelHTML(hotel, idx)).join('')}
            </div>
          </div>
        `
      : ''
    }

        <!-- Highlights Section -->
        ${generateHighlightsHTML(trip.highlights)}

        <!-- Footer -->
        <div class="footer">
          <p>Trip itinerary generated on ${new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })}</p>
          <p>By Tripping.ai</p>
        </div>
      </div>
    </body>
    </html>
  `;




  const element = document.createElement('div');
  element.innerHTML = htmlContent;

  const config = {
    margin: [10, 10, 10, 10] as [number, number, number, number],
    filename,
    image: { type: 'jpeg' as const, quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true } as any,
    jsPDF: {
      orientation: 'portrait' as const,
      unit: 'mm' as const,
      format: 'a4' as const,
      compress: true as const,
    },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] as const },
  } as const;

  (html2pdf() as any).set(config).from(element).save();
};
