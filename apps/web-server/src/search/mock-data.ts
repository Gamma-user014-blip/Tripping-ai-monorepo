import { SectionType, Trip } from "../../../../shared/types";

const mockData: Trip[] = [
  {
    vibe: "TEST VIBE",
    layout: {
      sections: [
        {
          type: "stay" as SectionType,
          data: {
            hotel: {
              id: "ca399b48-ca7c-5b55-b58e-6e057dae1d2f",
              name: "Hotel Lord Byron",
              description:
                "Experience the elegance of Hotel Lord Byron, an Art Deco gem nestled in the heart of Rome, where sophistication meets comfort.Luxurious AccommodationsRelax in one of our 28 stylish guestrooms, featuring memory foam beds, premium bedding, and modern amenities such as LCD televisions and minibars. Each room is designed for your utmost comfort, with complimentary toiletries and high-speed wireless internet access.Gastronomic DelightsIndulge in culinary excellence at our on-site restaurant, Sapori d",
              location: {
                city: "Rome",
                country: "IT",
                airport_code: "",
                latitude: 41.919861,
                longitude: 12.481478,
              },
              distance_to_center_km: 2.5,
              image: "https://static.cupid.travel/hotels/ex_73af06d5_z.jpg",
              rating: 9.0,
              review_count: 132,
              rating_category: "Exceptional",
              price_per_night: {
                currency: "USD",
                amount: 513.4866666666667,
              },
              total_price: {
                currency: "USD",
                amount: 1540.46,
              },
              additional_fees: [],
              room: {
                type: "Superior Room",
                beds: 1,
                bed_type: "standard",
                max_occupancy: 2,
                size_sqm: 0.0,
                features: [],
              },
              amenities: [
                "Facility_1054",
                "Facility_1091",
                "Facility_2020",
                "Facility_2050",
                "Facility_2247",
                "Facility_2253",
                "Facility_2259",
                "Facility_2261",
                "Facility_2411",
                "Facility_107",
              ],
              category: "luxury",
              star_rating: 5,
              scores: {
                price_score: 0.0,
                quality_score: 0.9,
                convenience_score: 0.75,
                preference_score: 0.5,
              },
              booking_url: "https://booking.liteapi.travel/hotels/lp19be2",
              provider: "nuitee",
              available: true,
            },
            activities: [
              {
                id: "vatican-001",
                name: "Private Sistine Chapel, Vatican Museums & St. Peter’s Basilica Tour",
                description:
                  "Expert-guided private tour exploring Vatican Museums, Michelangelo’s Sistine Chapel masterpieces, Raphael Rooms, and St. Peter’s Basilica with skip-the-line access.",
                category: 1,
                location: {
                  city: "Vatican City",
                  country: "IT",
                  airport_code: "FCO",
                  latitude: 41.9028,
                  longitude: 12.4534,
                },
                distance_from_query_km: 0.5,
                rating: 4.9,
                review_count: 1250,
                price_per_person: {
                  currency: "EUR",
                  amount: 250.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 250.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 200.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 225.0,
                  },
                },
                duration_minutes: 180,
                available_times: [
                  {
                    date: "2026-05-05",
                    time: "08:00",
                    available_spots: 6,
                  },
                  {
                    date: "2026-05-06",
                    time: "08:00",
                    available_spots: 6,
                  },
                  {
                    date: "2026-05-07",
                    time: "08:00",
                    available_spots: 6,
                  },
                ],
                highlights: [
                  "Exclusive early access",
                  "Michelangelo’s frescoes",
                  "St. Peter’s Dome views",
                ],
                included: ["Skip-the-line tickets", "Expert guide", "Headsets"],
                excluded: ["Meals", "Hotel pickup", "Dome climb"],
                min_participants: 1,
                max_participants: 6,
                difficulty_level: "easy",
                hotel_pickup: false,
                meal_included: false,
                cancellation_policy:
                  "Free cancellation up to 24 hours in advance",
                scores: {
                  price_score: 0.7,
                  quality_score: 1.0,
                  convenience_score: 0.9,
                  preference_score: 1.0,
                },
                booking_url: "https://www.througheternity.com/vatican",
                provider: "Through Eternity Tours",
                available: true,
                image_urls: [
                  "https://example.com/vatican-private.jpg",
                  "https://example.com/sistine-private.jpg",
                ],
              },
              {
                id: "vatican-002",
                name: "Early Morning Sistine Chapel Small Group Tour",
                description:
                  "Beat the crowds with early entry to Vatican Museums, serene Sistine Chapel visit, and St. Peter’s Basilica guided exploration.",
                category: 1,
                location: {
                  city: "Vatican City",
                  country: "IT",
                  airport_code: "FCO",
                  latitude: 41.9028,
                  longitude: 12.4534,
                },
                distance_from_query_km: 0.5,
                rating: 4.8,
                review_count: 2100,
                price_per_person: {
                  currency: "EUR",
                  amount: 89.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 89.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 69.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 79.0,
                  },
                },
                duration_minutes: 150,
                available_times: [
                  {
                    date: "2026-05-05",
                    time: "07:30",
                    available_spots: 12,
                  },
                  {
                    date: "2026-05-06",
                    time: "07:30",
                    available_spots: 12,
                  },
                  {
                    date: "2026-05-08",
                    time: "07:30",
                    available_spots: 12,
                  },
                ],
                highlights: [
                  "First entry to museums",
                  "Small group max 15",
                  "Direct Basilica access",
                ],
                included: ["Skip-the-line", "Guide", "Headsets"],
                excluded: ["Food", "Transfers"],
                min_participants: 1,
                max_participants: 15,
                difficulty_level: "easy",
                hotel_pickup: false,
                meal_included: false,
                cancellation_policy: "Free up to 48 hours",
                scores: {
                  price_score: 0.9,
                  quality_score: 0.95,
                  convenience_score: 0.95,
                  preference_score: 0.95,
                },
                booking_url: "https://www.takewalks.com/rome-tours",
                provider: "Walks of Italy",
                available: true,
                image_urls: [
                  "https://example.com/early-sistine.jpg",
                  "https://example.com/vatican-morning.jpg",
                ],
              },
              {
                id: "vatican-003",
                name: "Vatican Museums, Sistine Chapel & St. Peter’s Guided Tour",
                description:
                  "Comprehensive skip-the-line tour of Vatican highlights including Gallery of Maps, Tapestry Gallery, Sistine Chapel, and St. Peter’s Basilica.",
                category: 1,
                location: {
                  city: "Vatican City",
                  country: "IT",
                  airport_code: "FCO",
                  latitude: 41.9028,
                  longitude: 12.4534,
                },
                distance_from_query_km: 0.5,
                rating: 4.7,
                review_count: 4500,
                price_per_person: {
                  currency: "EUR",
                  amount: 65.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 65.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 50.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 60.0,
                  },
                },
                duration_minutes: 180,
                available_times: [
                  {
                    date: "2026-05-05",
                    time: "09:00",
                    available_spots: 20,
                  },
                  {
                    date: "2026-05-07",
                    time: "09:00",
                    available_spots: 20,
                  },
                  {
                    date: "2026-05-08",
                    time: "14:00",
                    available_spots: 20,
                  },
                ],
                highlights: [
                  "All major sites",
                  "Passionate guide",
                  "Bernini Staircase",
                ],
                included: ["Entry tickets", "Guided tour"],
                excluded: ["Meals", "Gratuities"],
                min_participants: 1,
                max_participants: 20,
                difficulty_level: "easy",
                hotel_pickup: false,
                meal_included: false,
                cancellation_policy: "Free up to 24 hours",
                scores: {
                  price_score: 0.95,
                  quality_score: 0.9,
                  convenience_score: 0.85,
                  preference_score: 0.9,
                },
                booking_url: "https://www.getyourguide.com",
                provider: "GetYourGuide",
                available: true,
                image_urls: [
                  "https://example.com/vatican-full.jpg",
                  "https://example.com/sistine-chapel.jpg",
                ],
              },
              {
                id: "vatican-004",
                name: "St. Peter’s Basilica & Dome Climb Guided Tour",
                description:
                  "Guided visit to St. Peter’s Basilica, papal tombs, Michelangelo’s Pietà, and optional dome climb for panoramic views.",
                category: 3,
                location: {
                  city: "Vatican City",
                  country: "IT",
                  airport_code: "FCO",
                  latitude: 41.9028,
                  longitude: 12.4534,
                },
                distance_from_query_km: 0.5,
                rating: 4.6,
                review_count: 3200,
                price_per_person: {
                  currency: "EUR",
                  amount: 45.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 45.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 35.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 40.0,
                  },
                },
                duration_minutes: 120,
                available_times: [
                  {
                    date: "2026-05-05",
                    time: "10:00",
                    available_spots: 15,
                  },
                  {
                    date: "2026-05-06",
                    time: "10:00",
                    available_spots: 15,
                  },
                  {
                    date: "2026-05-08",
                    time: "15:00",
                    available_spots: 15,
                  },
                ],
                highlights: [
                  "Dome ascent option",
                  "Papal tombs",
                  "Bernini Baldachin",
                ],
                included: ["Guide", "Dome tickets optional"],
                excluded: ["Museums", "Food"],
                min_participants: 1,
                max_participants: 15,
                difficulty_level: "moderate",
                hotel_pickup: false,
                meal_included: false,
                cancellation_policy: "Free up to 24 hours",
                scores: {
                  price_score: 0.95,
                  quality_score: 0.9,
                  convenience_score: 0.8,
                  preference_score: 0.85,
                },
                booking_url: "https://www.getyourguide.com",
                provider: "GetYourGuide",
                available: true,
                image_urls: [
                  "https://example.com/stpeters-dome.jpg",
                  "https://example.com/pieta.jpg",
                ],
              },
              {
                id: "vatican-005",
                name: "Skip-the-Line Vatican & Sistine Chapel Express",
                description:
                  "Fast-paced tour hitting Vatican Museums highlights, Sistine Chapel, without Basilica for time-conscious visitors.",
                category: 1,
                location: {
                  city: "Vatican City",
                  country: "IT",
                  airport_code: "FCO",
                  latitude: 41.9028,
                  longitude: 12.4534,
                },
                distance_from_query_km: 0.5,
                rating: 4.5,
                review_count: 1800,
                price_per_person: {
                  currency: "EUR",
                  amount: 49.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 49.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 39.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 44.0,
                  },
                },
                duration_minutes: 120,
                available_times: [
                  {
                    date: "2026-05-06",
                    time: "16:00",
                    available_spots: 18,
                  },
                  {
                    date: "2026-05-07",
                    time: "16:00",
                    available_spots: 18,
                  },
                  {
                    date: "2026-05-08",
                    time: "11:00",
                    available_spots: 18,
                  },
                ],
                highlights: [
                  "Quick highlights",
                  "After-hours option",
                  "No lines",
                ],
                included: ["Priority access", "Guide"],
                excluded: ["Basilica", "Meals"],
                min_participants: 1,
                max_participants: 20,
                difficulty_level: "easy",
                hotel_pickup: false,
                meal_included: false,
                cancellation_policy: "Free up to 12 hours",
                scores: {
                  price_score: 1.0,
                  quality_score: 0.85,
                  convenience_score: 0.9,
                  preference_score: 0.8,
                },
                booking_url: "https://www.viator.com",
                provider: "Viator",
                available: true,
                image_urls: ["https://example.com/express-vatican.jpg"],
              },
            ],
          },
        },
        {
          type: "stay" as any,
          data: {
            hotel: {
              id: "266965fe-5bad-5eaf-8c9b-03931535e586",
              name: "Grand Hotel Santa Lucia",
              description:
                "Luxurious Accommodation with Stunning ViewsArt-Nouveau Design and Modern AmenitiesStep into a world of elegance with the impressive Art-Nouveau design of Grand Hotel Santa Lucia. Enjoy modern amenities such as a well-equipped gym to cater to your fitness needs during your stay.Gourmet Dining Experience with Spectacular ViewsIndulge in a culinary journey at the stylish hotel restaurant offering creative, contemporary dishes alongside Neapolitan favorites. Pair your meal with a fine wine from the ",
              location: {
                city: "Naples",
                country: "it",
                airport_code: "",
                latitude: 40.829966,
                longitude: 14.249104,
              },
              distance_to_center_km: 2.5,
              image: "https://static.cupid.travel/hotels/20444083.jpg",
              rating: 9.0,
              review_count: 529,
              rating_category: "Exceptional",
              price_per_night: {
                currency: "USD",
                amount: 426.2875,
              },
              total_price: {
                currency: "USD",
                amount: 1705.15,
              },
              additional_fees: [
                {
                  name: "Mandatory Tax",
                  amount: {
                    currency: "USD",
                    amount: 46.64,
                  },
                  mandatory: true,
                },
              ],
              room: {
                type: "Double Classic",
                beds: 1,
                bed_type: "standard",
                max_occupancy: 2,
                size_sqm: 0.0,
                features: [],
              },
              amenities: [
                "Facility_6848",
                "Facility_16",
                "Facility_109",
                "Facility_3",
                "Facility_5",
                "Facility_28",
                "Facility_4",
                "Facility_48",
                "Facility_91",
                "Facility_51",
              ],
              category: "luxury",
              star_rating: 4,
              scores: {
                price_score: 0.16380555555555554,
                quality_score: 0.9,
                convenience_score: 0.75,
                preference_score: 0.5,
              },
              booking_url: "https://booking.liteapi.travel/hotels/lp1b0dc",
              provider: "nuitee",
              available: true,
            },
            activities: [
              {
                id: "1",
                name: "Pompeii Ruins Guided Tour from Naples",
                description:
                  "Expert-led tour of the ancient ruins of Pompeii, exploring preserved streets, villas, and frescoes frozen in time by Vesuvius eruption.",
                category: 1,
                location: {
                  city: "Naples",
                  country: "IT",
                  airport_code: "NAP",
                  latitude: 40.8518,
                  longitude: 14.2681,
                },
                distance_from_query_km: 0.0,
                rating: 4.8,
                review_count: 1250,
                price_per_person: {
                  currency: "EUR",
                  amount: 65.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 65.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 45.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 60.0,
                  },
                },
                duration_minutes: 240,
                available_times: [
                  {
                    date: "2026-05-08",
                    time: "09:00",
                    available_spots: 20,
                  },
                  {
                    date: "2026-05-09",
                    time: "09:00",
                    available_spots: 18,
                  },
                  {
                    date: "2026-05-10",
                    time: "14:00",
                    available_spots: 22,
                  },
                ],
                highlights: [
                  "Skip-the-line entry",
                  "Archaeologist guide",
                  "Vesuvius viewpoints",
                ],
                included: [
                  "Guided tour",
                  "Entry ticket",
                  "Transport from Naples",
                ],
                excluded: ["Meals", "Personal expenses"],
                min_participants: 1,
                max_participants: 15,
                difficulty_level: "moderate",
                hotel_pickup: true,
                meal_included: false,
                cancellation_policy:
                  "Free cancellation up to 24 hours in advance",
                scores: {
                  price_score: 0.85,
                  quality_score: 0.95,
                  convenience_score: 0.9,
                  preference_score: 1.0,
                },
                booking_url: "https://www.getyourguide.com/naples-l162/",
                provider: "GetYourGuide",
                available: true,
                image_urls: [
                  "https://example.com/pompeii1.jpg",
                  "https://example.com/pompeii2.jpg",
                ],
              },
              {
                id: "2",
                name: "Amalfi Coast Small Group Day Trip",
                description:
                  "Scenic drive along the stunning Amalfi Coast visiting Positano, Amalfi, and Ravello with stops for photos and local exploration.",
                category: 2,
                location: {
                  city: "Naples",
                  country: "IT",
                  airport_code: "NAP",
                  latitude: 40.8518,
                  longitude: 14.2681,
                },
                distance_from_query_km: 0.0,
                rating: 4.9,
                review_count: 890,
                price_per_person: {
                  currency: "EUR",
                  amount: 95.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 95.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 70.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 90.0,
                  },
                },
                duration_minutes: 480,
                available_times: [
                  {
                    date: "2026-05-09",
                    time: "08:00",
                    available_spots: 12,
                  },
                  {
                    date: "2026-05-10",
                    time: "08:00",
                    available_spots: 14,
                  },
                  {
                    date: "2026-05-11",
                    time: "08:00",
                    available_spots: 10,
                  },
                ],
                highlights: [
                  "Small group max 15",
                  "Professional driver",
                  "Coastal viewpoints",
                ],
                included: ["Transport", "Guide", "Hotel pickup"],
                excluded: ["Lunch", "Boat optional"],
                min_participants: 2,
                max_participants: 15,
                difficulty_level: "easy",
                hotel_pickup: true,
                meal_included: false,
                cancellation_policy:
                  "Free cancellation up to 24 hours in advance",
                scores: {
                  price_score: 0.8,
                  quality_score: 0.97,
                  convenience_score: 0.88,
                  preference_score: 1.0,
                },
                booking_url: "https://www.getyourguide.com/naples-l162/",
                provider: "GetYourGuide",
                available: true,
                image_urls: [
                  "https://example.com/amalfi1.jpg",
                  "https://example.com/amalfi2.jpg",
                ],
              },
              {
                id: "3",
                name: "Naples Pizza Making and Tasting Tour",
                description:
                  "Hands-on pizza workshop in a traditional Neapolitan pizzeria followed by tasting session and street food walk.",
                category: 10,
                location: {
                  city: "Naples",
                  country: "IT",
                  airport_code: "NAP",
                  latitude: 40.8518,
                  longitude: 14.2681,
                },
                distance_from_query_km: 0.0,
                rating: 4.7,
                review_count: 650,
                price_per_person: {
                  currency: "EUR",
                  amount: 45.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 45.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 35.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 45.0,
                  },
                },
                duration_minutes: 180,
                available_times: [
                  {
                    date: "2026-05-08",
                    time: "18:00",
                    available_spots: 8,
                  },
                  {
                    date: "2026-05-10",
                    time: "18:00",
                    available_spots: 10,
                  },
                  {
                    date: "2026-05-12",
                    time: "12:00",
                    available_spots: 12,
                  },
                ],
                highlights: [
                  "Make authentic Margherita",
                  "Expert pizzaiolo",
                  "Unlimited tasting",
                ],
                included: ["Ingredients", "Aprons", "Beverages"],
                excluded: ["Transport"],
                min_participants: 2,
                max_participants: 12,
                difficulty_level: "easy",
                hotel_pickup: false,
                meal_included: true,
                cancellation_policy:
                  "Free cancellation up to 24 hours in advance",
                scores: {
                  price_score: 0.92,
                  quality_score: 0.9,
                  convenience_score: 0.85,
                  preference_score: 0.95,
                },
                booking_url: "https://www.tripadvisor.com/",
                provider: "TripAdvisor",
                available: true,
                image_urls: [
                  "https://example.com/pizza1.jpg",
                  "https://example.com/pizza2.jpg",
                ],
              },
              {
                id: "4",
                name: "Pompeii and Vesuvius Day Trip with Lunch",
                description:
                  "Full-day excursion to Pompeii ruins and hike up Mount Vesuvius crater, including lunch and round-trip transport.",
                category: 2,
                location: {
                  city: "Naples",
                  country: "IT",
                  airport_code: "NAP",
                  latitude: 40.8518,
                  longitude: 14.2681,
                },
                distance_from_query_km: 25.0,
                rating: 4.6,
                review_count: 2100,
                price_per_person: {
                  currency: "EUR",
                  amount: 110.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 110.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 80.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 100.0,
                  },
                },
                duration_minutes: 420,
                available_times: [
                  {
                    date: "2026-05-08",
                    time: "07:30",
                    available_spots: 25,
                  },
                  {
                    date: "2026-05-11",
                    time: "07:30",
                    available_spots: 20,
                  },
                  {
                    date: "2026-05-12",
                    time: "07:30",
                    available_spots: 22,
                  },
                ],
                highlights: [
                  "Hike to crater",
                  "Skip-the-line Pompeii",
                  "Italian lunch",
                ],
                included: ["Transport", "Guide", "Lunch", "Tickets"],
                excluded: ["Drinks", "Tips"],
                min_participants: 1,
                max_participants: 25,
                difficulty_level: "challenging",
                hotel_pickup: true,
                meal_included: true,
                cancellation_policy:
                  "Free cancellation up to 24 hours in advance",
                scores: {
                  price_score: 0.78,
                  quality_score: 0.94,
                  convenience_score: 0.92,
                  preference_score: 0.98,
                },
                booking_url: "https://www.getyourguide.com/naples-l162/",
                provider: "GetYourGuide",
                available: true,
                image_urls: [
                  "https://example.com/vesuvius1.jpg",
                  "https://example.com/pompeii3.jpg",
                ],
              },
              {
                id: "5",
                name: "Sorrento, Positano & Amalfi Coast Tour",
                description:
                  "Comfortable bus tour from Naples to Sorrento, Positano, and Amalfi with free time in each picturesque town.",
                category: 2,
                location: {
                  city: "Naples",
                  country: "IT",
                  airport_code: "NAP",
                  latitude: 40.8518,
                  longitude: 14.2681,
                },
                distance_from_query_km: 0.0,
                rating: 4.7,
                review_count: 340,
                price_per_person: {
                  currency: "EUR",
                  amount: 85.0,
                },
                price_details: {
                  adult_price: {
                    currency: "EUR",
                    amount: 85.0,
                  },
                  child_price: {
                    currency: "EUR",
                    amount: 60.0,
                  },
                  senior_price: {
                    currency: "EUR",
                    amount: 80.0,
                  },
                },
                duration_minutes: 450,
                available_times: [
                  {
                    date: "2026-05-09",
                    time: "08:30",
                    available_spots: 30,
                  },
                  {
                    date: "2026-05-10",
                    time: "08:30",
                    available_spots: 28,
                  },
                ],
                highlights: ["Lemon grove visit", "Photo stops", "Local guide"],
                included: ["Transport", "Guide"],
                excluded: ["Meals"],
                min_participants: 1,
                max_participants: 40,
                difficulty_level: "easy",
                hotel_pickup: true,
                meal_included: false,
                cancellation_policy:
                  "Free cancellation up to 24 hours in advance",
                scores: {
                  price_score: 0.82,
                  quality_score: 0.91,
                  convenience_score: 0.89,
                  preference_score: 0.97,
                },
                booking_url: "https://www.tourradar.com/d/naples",
                provider: "TourRadar",
                available: true,
                image_urls: [
                  "https://example.com/sorrento1.jpg",
                  "https://example.com/positano1.jpg",
                ],
              },
            ],
          },
        },
      ],
    },
  },
];

export default mockData;
