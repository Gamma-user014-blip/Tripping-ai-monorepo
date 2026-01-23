import { useState, useRef, useCallback, useEffect } from "react";
import { apiClient } from "../lib/api-client";
import { pollForSearchResults, StopPolling } from "../lib/search-polling";
import {
  ChatRequest,
  ChatResponse,
  ChatResponseStatus,
  Trip,
} from "../../../shared/types";
import {
  getOrCreateSessionId as getBaseSessionId,
  CHAT_MESSAGES_KEY_PREFIX,
  TRIP_IDS_KEY_PREFIX,
  SEARCH_ID_KEY_PREFIX,
  TRIP_RESULTS_KEY_PREFIX,
} from "../lib/session";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: number;
}

type ChatMode = "inline" | "redirect";

interface UseChatOptions {
  onTripsLoaded?: (trips: Trip[]) => void;
  onSearchStart?: () => void;
  onSearchClear?: () => void;
  onSearchComplete?: () => void;
  onRedirect?: (searchId: string) => void;
  mode?: ChatMode;
}

interface UseChatReturn {
  messages: Message[];
  isTyping: boolean;
  isSearching: boolean;
  sendMessage: (text: string) => Promise<void>;
  isSending: boolean;
  startPollingFromSession: () => void;
}

const getOrCreateSessionId = (
  sessionIdRef: React.MutableRefObject<string>,
): string => {
  if (sessionIdRef.current) return sessionIdRef.current;
  const sessionId = getBaseSessionId();
  sessionIdRef.current = sessionId;
  return sessionId;
};

const useChat = ({
  onTripsLoaded,
  onSearchStart,
  onSearchClear,
  onSearchComplete,
  onRedirect,
  mode = "inline",
}: UseChatOptions = {}): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      text: "Hello! I'm your AI travel assistant. How can I help you customize your trip today?",
      sender: "ai",
      timestamp: Date.now(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const sessionIdRef = useRef<string>("");
  const stopPollingRef = useRef<StopPolling | null>(null);

  useEffect(() => {
    const sessionId = getOrCreateSessionId(sessionIdRef);

    const storedMessages = sessionStorage.getItem(
      `${CHAT_MESSAGES_KEY_PREFIX}${sessionId}`,
    );
    if (!storedMessages) return;

    try {
      const parsed = JSON.parse(storedMessages) as unknown;
      if (!Array.isArray(parsed) || parsed.length === 0) return;
      setMessages(parsed as Message[]);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    const sessionId = sessionIdRef.current;
    if (!sessionId) return;

    sessionStorage.setItem(
      `${CHAT_MESSAGES_KEY_PREFIX}${sessionId}`,
      JSON.stringify(messages),
    );
  }, [messages]);

  useEffect(() => {
    return () => {
      stopPollingRef.current?.();
    };
  }, []);

  const clearSearchData = useCallback((): void => {
    const sessionId = getOrCreateSessionId(sessionIdRef);
    sessionStorage.removeItem(`${TRIP_RESULTS_KEY_PREFIX}${sessionId}`);
    sessionStorage.removeItem(`${TRIP_IDS_KEY_PREFIX}${sessionId}`);
    sessionStorage.removeItem(`${SEARCH_ID_KEY_PREFIX}${sessionId}`);
    onSearchClear?.();
  }, [onSearchClear]);

  const startPolling = useCallback(
    (searchId: string): void => {
      stopPollingRef.current?.();

      // Clear old search data when starting a new search
      clearSearchData();

      setIsSearching(true);
      onSearchStart?.();

      const sessionId = getOrCreateSessionId(sessionIdRef);

      // Store the new search ID
      sessionStorage.setItem(`${SEARCH_ID_KEY_PREFIX}${sessionId}`, searchId);

      stopPollingRef.current = pollForSearchResults(searchId, {
        onProgress: (trips, tripIds) => {
          sessionStorage.setItem(
            `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
            JSON.stringify(tripIds),
          );
          onTripsLoaded?.(trips);
        },
        onComplete: (trips, tripIds) => {
          sessionStorage.setItem(
            `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
            JSON.stringify(tripIds),
          );
          setIsSearching(false);
          onTripsLoaded?.(trips);
          onSearchComplete?.();
        },
        onError: (error) => {
          setIsSearching(false);
          console.error("Search error:", error);
          onSearchComplete?.();
        },
      });
    },
    [onTripsLoaded, onSearchStart, onSearchComplete, clearSearchData],
  );

  const startPollingFromSession = useCallback((): void => {
    const sessionId = getOrCreateSessionId(sessionIdRef);
    const storedSearchId = sessionStorage.getItem(
      `${SEARCH_ID_KEY_PREFIX}${sessionId}`,
    );
    if (storedSearchId) {
      startPolling(storedSearchId);
    }
  }, [startPolling]);

  const sendMessage = useCallback(
    async (text: string): Promise<void> => {
      const trimmedMessage = text.trim();
      if (!trimmedMessage || isTyping || isSending) return;

      setIsSending(true);
      const sessionId = getOrCreateSessionId(sessionIdRef);

      const newUserMessage: Message = {
        id: Date.now().toString(),
        text: trimmedMessage,
        sender: "user",
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, newUserMessage]);
      setIsTyping(true);

      try {
        const response: ChatResponse = await apiClient.post<ChatResponse>(
          "/api/chat",
          {
            message: trimmedMessage,
            sessionId,
          } satisfies ChatRequest,
        );

        if (response.status === ChatResponseStatus.ERROR) {
          throw new Error("AI response error");
        }

        const newAiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.message,
          sender: "ai",
          timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, newAiMessage]);

        if (
          response.status === ChatResponseStatus.COMPLETE &&
          response.searchId
        ) {
          if (mode === "redirect") {
            // Store searchId in session and redirect
            sessionStorage.setItem(
              `${SEARCH_ID_KEY_PREFIX}${sessionId}`,
              response.searchId,
            );
            setIsSearching(true);
            onRedirect?.(response.searchId);
          } else {
            // Inline mode: start polling directly
            startPolling(response.searchId);
          }
        }
      } catch (error) {
        console.error("Failed to send message:", error);
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: "Sorry, I'm having trouble connecting. Please try again.",
          sender: "ai",
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsTyping(false);
        setIsSending(false);
      }
    },
    [isTyping, isSending, startPolling, mode, onRedirect],
  );

  return {
    messages,
    isTyping,
    isSearching,
    sendMessage,
    isSending,
    startPollingFromSession,
  };
};

export default useChat;
export type { Message, UseChatOptions, UseChatReturn };
