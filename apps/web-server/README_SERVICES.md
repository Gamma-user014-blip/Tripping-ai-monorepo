# Tripping.ai Services & JSON Documentation

This document explains the core services and the JSON communication protocols used in the Tripping.ai backend, specifically focusing on the **Json Agent** and the **Trip Builder**.

---

## 🏗️ Architecture Overview

The backend follows a pipelined approach to transform a user's natural language request into a fully bookable trip:

1.  **User Input** (Natural Language/YAML)
2.  **Json Agent**: Translates input into a compact **Action Sequence**.
3.  **Trip Request Builder**: Converts Action Sequences into a structured **TripRequest**.
4.  **Trip Builder**: Takes the **TripRequest**, fetches real-world data (flights, hotels, activities) in parallel, and returns a **FinalTripLayout**.

---

## 🤖 Json Agent (`apps/json_agent`)

The Json Agent acts as the "brain" that interprets intent and projects it onto a timeline.

### 1. Action Sequences

The agent uses a compact, array-based format called "Actions" to represent trip components. This format is designed for LLM efficiency and token savings.

#### **FLIGHT Action**

Used for all air travel segments.

```json
[
  "FLIGHT",
  "origin_city",
  "origin_country",
  "origin_code",
  "dest_city",
  "dest_country",
  "dest_code",
  "date",
  "return_date",
  "passengers",
  "cabin"
]
```

- **Indices**:
  - `0`: "FLIGHT" (Constant)
  - `1..3`: Origin (City, Country, IATA code)
  - `4..6`: Destination (City, Country, IATA code)
  - `7`: Departure Date (YYYY-MM-DD)
  - `8`: Return Date (Optional, YYYY-MM-DD)
  - `9`: Passengers (Integer)
  - `10`: Cabin Class (economy, business, first, etc.)

#### **STAY Action**

Represents a period of time spent in a specific city, including hotel and activity preferences.

```json
[
  "STAY",
  "city",
  "country",
  "start_date",
  "end_date",
  "guests",
  "rooms",
  "description"
]
```

- **Indices**:
  - `0`: "STAY" (Constant)
  - `1..2`: Location (City, Country)
  - `3`: Check-in Date (YYYY-MM-DD)
  - `4`: Check-out Date (YYYY-MM-DD)
  - `5`: Guests (Integer)
  - `6`: Rooms (Integer)
  - `7`: Description (String - used to search for relevant activities/vibes)

### 2. Core Endpoints

- **`POST /api/generate-plans`**:
  - Input: `{ "trip_yml": "string" }`
  - Returns: 3 distinct trip "vibes", each with its own action sequence.
- **`POST /api/build-trip-request`**:
  - Input: `{ "vibe": "string", "actions": [[...], [...]] }`
  - Returns: A structured `TripRequest` object ready for the Trip Builder.
- **`POST /api/edit-plans`**:
  - Input: `{ "plans": [...], "user_text": "shorten London stay" }`
  - Returns: Updated action sequences and indicates which plans were modified.

---

## 🛠️ Trip Builder (`apps/trip_builder`)

The Trip Builder is the "orchestrator" that talks to external data providers (or their wrappers).

### 1. The Workflow

When `POST /api/create_trip` is called with a `TripRequest`:

1.  **Parallel Search**: For every section in the `TripRequest` (FLIGHT or STAY), it triggers parallel asynchronous calls to:
    - `flight_retriever` (for FLIGHT)
    - `hotel_retriever` (for STAY)
    - `activity_retriever` (for STAY)
2.  **Aggregation**: It waits for all results and bundles them into a `TripResponse`.
3.  **Package Building**: It sends the `TripResponse` to the `package_builder` service, which selects the _optimal_ options based on the user's vibe and budget.
4.  **Final Injection**: It returns the `FinalTripLayout`.

---

## 📄 JSON Data Structures Deep Dive

These types are defined in `shared/data_types/models.py`.

### `TripRequest`

The primary structure passed between the AI layer and the Data layer.

```json
{
  "sections": [
    {
      "type": "flight",
      "data": {
        "origin": { "city": "NYC", "airport_code": "JFK" },
        "destination": { "city": "London", "airport_code": "LHR" },
        "departure_date": "2024-05-01",
        "passengers": 1,
        "cabin_class": "economy"
      }
    },
    {
      "type": "stay",
      "data": {
        "hotel_request": {
          "location": { "city": "London" },
          "dates": { "start_date": "2024-05-01", "end_date": "2024-05-05" },
          "guests": 1
        },
        "activity_request": {
          "location": { "city": "London" },
          "description": "Museums and history"
        }
      }
    }
  ]
}
```

### `FinalTripLayout`

The final format returned to the frontend, containing specific selected items.

```json
{
  "sections": [
    {
      "type": "flight",
      "data": {
        "outbound": {
          "airline": "British Airways",
          "flight_number": "BA178",
          "departure_time": "2024-05-01T08:00:00"
        },
        "total_price": { "amount": 450.0, "currency": "USD" }
      }
    },
    {
      "type": "stay",
      "data": {
        "hotel": {
          "name": "The Savoy",
          "rating": 5.0,
          "price_per_night": { "amount": 600.0 }
        },
        "activities": [{ "name": "British Museum Tour", "rating": 4.8 }]
      }
    }
  ]
}
```

---

## 🔑 Key Enums

- **`SectionType`**: `flight`, `stay`, `transfer`.
- **`PreferenceType`**: LUXURY (1), BUDGET (2), ADVENTURE (5), etc.
- **`TransportMode`**: RENTAL_CAR (1), TAXI (2), TRAIN (4), etc.
