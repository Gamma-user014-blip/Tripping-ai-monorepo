const CHAT_SESSION_ID_KEY =
  process.env.NEXT_PUBLIC_CHAT_SESSION_ID_KEY || "chat_session_id";
const TRIP_RESULTS_KEY_PREFIX =
  process.env.NEXT_PUBLIC_TRIP_RESULTS_KEY_PREFIX || "trip_results_";
const TRIP_IDS_KEY_PREFIX =
  process.env.NEXT_PUBLIC_TRIP_IDS_KEY_PREFIX || "trip_ids_";
const CHAT_MESSAGES_KEY_PREFIX =
  process.env.NEXT_PUBLIC_CHAT_MESSAGES_KEY_PREFIX || "chat_messages_";

const getOrCreateSessionId = (): string => {
  let storedSessionId = sessionStorage.getItem(CHAT_SESSION_ID_KEY);
  if (!storedSessionId) {
    storedSessionId = crypto.randomUUID();
    sessionStorage.setItem(CHAT_SESSION_ID_KEY, storedSessionId);
  }
  return storedSessionId;
};

const resetSession = (): string => {
  const currentSessionId = sessionStorage.getItem(CHAT_SESSION_ID_KEY);

  if (currentSessionId) {
    sessionStorage.removeItem(`${TRIP_RESULTS_KEY_PREFIX}${currentSessionId}`);
    sessionStorage.removeItem(`${TRIP_IDS_KEY_PREFIX}${currentSessionId}`);
    sessionStorage.removeItem(`${CHAT_MESSAGES_KEY_PREFIX}${currentSessionId}`);
    sessionStorage.removeItem(CHAT_SESSION_ID_KEY);
  }

  const newSessionId = crypto.randomUUID();
  sessionStorage.setItem(CHAT_SESSION_ID_KEY, newSessionId);
  return newSessionId;
};

export {
  getOrCreateSessionId,
  resetSession,
  CHAT_SESSION_ID_KEY,
  TRIP_RESULTS_KEY_PREFIX,
  TRIP_IDS_KEY_PREFIX,
  CHAT_MESSAGES_KEY_PREFIX,
};
