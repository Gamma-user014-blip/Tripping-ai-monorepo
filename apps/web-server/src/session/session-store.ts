export type ChatMessageRole = "user" | "assistant";

export type ChatMessage = {
  role: ChatMessageRole;
  content: string;
  createdAtMs: number;
};

export type SessionChatState = {
  messageCount: number;
  messages: ChatMessage[];
};

export type SessionData = {
  sessionId: string;
  createdAtMs: number;
  updatedAtMs: number;
  tripYaml: string;
  chat: SessionChatState;
  lastSearchYaml?: string;
  hasCompletedSearch?: boolean;
};

export const DEFAULT_TRIP_YAML: string = `
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
`;

const SESSION_TTL_MS: number = 2 * 60 * 60 * 1000;
const MAX_CHAT_MESSAGES: number = 50;

const sessionsById: Map<string, SessionData> = new Map();

const pruneExpiredSessions = (nowMs: number): void => {
  for (const [sessionId, session] of sessionsById) {
    if (nowMs - session.updatedAtMs > SESSION_TTL_MS) {
      sessionsById.delete(sessionId);
    }
  }
};

const touchSession = (session: SessionData, nowMs: number): void => {
  session.updatedAtMs = nowMs;
};

const trimChatMessages = (messages: ChatMessage[]): ChatMessage[] => {
  if (messages.length <= MAX_CHAT_MESSAGES) {
    return messages;
  }

  return messages.slice(messages.length - MAX_CHAT_MESSAGES);
};

export const getOrCreateSession = (
  sessionId: string,
  defaultTripYaml: string,
): SessionData => {
  const nowMs = Date.now();
  pruneExpiredSessions(nowMs);

  const existing = sessionsById.get(sessionId);
  if (existing) {
    touchSession(existing, nowMs);
    return existing;
  }

  const created: SessionData = {
    sessionId,
    createdAtMs: nowMs,
    updatedAtMs: nowMs,
    tripYaml: defaultTripYaml,
    chat: {
      messageCount: 0,
      messages: [],
    },
  };

  sessionsById.set(sessionId, created);
  return created;
};

export const appendChatMessage = (
  sessionId: string,
  defaultTripYaml: string,
  role: ChatMessageRole,
  content: string,
): SessionData => {
  const nowMs = Date.now();
  const session = getOrCreateSession(sessionId, defaultTripYaml);

  if (role === "user") {
    session.chat.messageCount += 1;
  }

  session.chat.messages = trimChatMessages([
    ...session.chat.messages,
    { role, content, createdAtMs: nowMs },
  ]);

  touchSession(session, nowMs);
  return session;
};

export const setTripYaml = (
  sessionId: string,
  defaultTripYaml: string,
  yaml: string,
): SessionData => {
  const nowMs = Date.now();
  const session = getOrCreateSession(sessionId, defaultTripYaml);
  session.tripYaml = yaml;
  touchSession(session, nowMs);
  return session;
};

export const markSearchCompleted = (
  sessionId: string,
  defaultTripYaml: string,
  searchYaml: string,
): void => {
  const session = getOrCreateSession(sessionId, defaultTripYaml);
  session.lastSearchYaml = searchYaml;
  session.hasCompletedSearch = true;
};

export const resetSessionForNewSearch = (
  sessionId: string,
  defaultTripYaml: string,
): void => {
  const session = getOrCreateSession(sessionId, defaultTripYaml);
  session.tripYaml = defaultTripYaml;
  session.hasCompletedSearch = false;
};
