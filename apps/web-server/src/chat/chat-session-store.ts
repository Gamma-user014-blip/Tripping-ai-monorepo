export type ChatSessionState = {
  count: number
  lastSeenMs: number
}

const chatSessions: Map<string, ChatSessionState> = new Map()
const CHAT_SESSION_TTL_MS = 60 * 60 * 1000

const pruneExpiredChatSessions = (nowMs: number): void => {
  for (const [key, value] of chatSessions.entries()) {
    if (nowMs - value.lastSeenMs > CHAT_SESSION_TTL_MS) {
      chatSessions.delete(key)
    }
  }
}

export const getNextChatMessageCount = (sessionId: string): number => {
  const nowMs = Date.now()
  pruneExpiredChatSessions(nowMs)

  const current = chatSessions.get(sessionId) || { count: 0, lastSeenMs: nowMs }
  const nextCount = current.count + 1
  chatSessions.set(sessionId, { count: nextCount, lastSeenMs: nowMs })
  return nextCount
}
