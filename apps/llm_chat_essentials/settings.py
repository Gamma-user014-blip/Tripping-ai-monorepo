YAML_TRIP_INTAKE_SCHEMA_V11 = """\
meta:
  schema: trip_intake
  timezone: Asia/Jerusalem

conversation:
  rawPrompt: ""
  history:
    lastUserPrompts: []
    summary: ""
  messages: []

trip:
  essentials:
    travelers:
      adults: null
      children: 0
      infants: 0
      childrenAges: []
      rooms: 1

    origin:
      kind: airport_or_city
      iata: null
      city: null
      countryCode: null

    # Multi-destination support (1+ stops)
    destinations:
      - kind: airport_or_city_or_region
        iata: null
        city: null
        countryCode: null
        region: null

    dates:
      mode: fixed_or_flexible
      departureDate: null
      returnDate: null
      nights: null
      flex:
        plusMinusDays: 0
        departDOW: []
        returnDOW: []

    packageScope:
      includeFlight: true
      includeHotel: true
      includeTransfers: null
      includeCarRental: null
      includeActivities: null

    currency: USD

  preferences:
    budget:
      mode: total_or_perPerson_or_perNight
      amount: null
      currency: null
      hardCap: false

    hotel:
      starMin: null
      starMax: null
      board: null
      propertyTypes: []
      amenities:
        wifi: null
        pool: null
        gym: null
        spa: null
      locationPrefs:
        near: []
        areas: []
        avoid: []
        maxDistanceKm: null

  classification:
    summary:
      primaryArchetype: null
      secondaryArchetypes: []
      confidence: 0.0
      userConfirmNeeded: false

    labels:
      archetypes: []
      themes: []
      geoIntents: []
      activityIntents: []
      landmarkIntents: []

    derivedConstraints:
      geoConstraints:
        preferCoastal: null
        maxDistanceToCoastKm: null
        preferCityCenter: null
        maxDistanceToCenterKm: null
      activityConstraints:
        foodTourismPriority: null
        museumPriority: null
        hikingPriority: null
        nightlifePriority: null
      routingHints:
        suggestDestinationsAllowed: true
        mustIncludeLandmark: false
        mustBeInSpecificCity: false

    specialNotes: []

  extraction:
    status:
      state: collecting_or_ready_or_error
      readyForNextModule: false
    blockingMissing: []
"""
YAML_UPDATE_SYSTEM_INSTRUCTIONS = """\
You update a trip-intake state stored as YAML.

OUTPUT
- Return ONE valid YAML document only. No prose, no markdown fences, no comments.
- Start the YAML with: meta:

HOW TO UPDATE
- You will receive:
  1) CURRENT STATE YAML
  2) NEW USER MESSAGE
- Update the YAML to reflect the NEW USER MESSAGE.
- If the user changes/corrects something, overwrite it (latest wins).
- If the user doesn’t mention something, keep the existing value if present.
- Don’t delete filled values unless the user clearly removes them.

DESTINATIONS (MULTI)
- Store destinations in: trip.essentials.destinations (a YAML list).
- If user gives one destination -> list with 1 item.
- If user gives multiple -> one list item per destination, in order.
- “also/add X” means append, “instead/change to …” means replace the list.
- If the YAML currently has trip.essentials.destination (single object), you may convert it once into destinations:[...] and then continue using destinations.

CREATIVE DESTINATIONS (ONLY WHEN USER ASKS YOU TO PICK)
- If the user says “pick/surprise me/two cities in Germany/two countries”, you may choose destinations.
- Choose realistic popular places that fit the constraints.
- Default to 2 destinations if the user didn’t specify a number.
- Add a short note in trip.classification.specialNotes saying the destinations were auto-selected and can be changed.

INFERENCE (LIGHT)
- When a place is mentioned, fill obvious sub-fields if you’re confident:
  city, countryCode, region, iata (only if explicitly given or very confident).
- Dates: if user gives specific dates, use YYYY-MM-DD. If flexible, don’t invent exact dates.
- Travelers: “couple” -> adults=2, etc.

HISTORY (LIGHT)
- Set conversation.rawPrompt to the new user message.
- Append the new message to conversation.history.lastUserPrompts (keep last 5).
- Append a message object to conversation.messages:
  - role: user
    content: "<new user message>"
    ts: null

Remember: output YAML only.
"""
