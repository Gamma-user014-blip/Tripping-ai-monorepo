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
} from "../lib/session";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: number;
}

interface UseChatOptions {
  onTripsLoaded?: (trips: Trip[]) => void;
  onSearchStart?: () => void;
}

interface UseChatReturn {
  messages: Message[];
  isTyping: boolean;
  isSearching: boolean;
  sendMessage: (text: string) => Promise<void>;
  isSending: boolean;
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

  const startPolling = useCallback(
    (searchId: string): void => {
      stopPollingRef.current?.();

      setIsSearching(true);
      onSearchStart?.();

      const sessionId = getOrCreateSessionId(sessionIdRef);

      stopPollingRef.current = pollForSearchResults(searchId, {
        onComplete: (trips) => {
          void (async (): Promise<void> => {
            try {
              const response = await apiClient.get<{ tripIds: string[] }>(
                `/api/search/${searchId}/trip-ids`,
              );
              sessionStorage.setItem(
                `${TRIP_IDS_KEY_PREFIX}${sessionId}`,
                JSON.stringify(response.tripIds),
              );
            } catch {
              // ignore
            } finally {
              setIsSearching(false);
              onTripsLoaded?.(trips);
            }
          })();
        },
        onError: (error) => {
          setIsSearching(false);
          console.error("Search error:", error);
        },
      });
    },
    [onTripsLoaded, onSearchStart],
  );

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
          startPolling(response.searchId);
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
    [isTyping, isSending, startPolling],
  );

  return {
    messages,
    isTyping,
    isSearching,
    sendMessage,
    isSending,
  };
};

export default useChat;
export type { Message, UseChatOptions, UseChatReturn };
