import React, { useState, useRef, useEffect } from "react";
import styles from "./ai-chat-sidebar.module.css";
import { apiClient } from "../../../lib/api-client";
import { ChatRequest, ChatResponse, ChatResponseStatus } from "../../../../../shared/types";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: number;
}

interface AiChatSidebarProps {
  loadTrips?: (searchId?: string) => void;
}

const AiChatSidebar: React.FC<AiChatSidebarProps> = ({ loadTrips }) => {
  const CHAT_SESSION_ID_KEY = "chat_session_id";
  const CHAT_MESSAGES_KEY_PREFIX = "chat_messages_";

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      text: "Hello! I'm your AI travel assistant. How can I help you customize your trip today?",
      sender: "ai",
      timestamp: Date.now(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageListRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const sessionIdRef = useRef<string>("");
  const isSendingRef = useRef<boolean>(false);

  const getOrCreateSessionId = (): string => {
    if (sessionIdRef.current) return sessionIdRef.current;

    let storedSessionId = sessionStorage.getItem(CHAT_SESSION_ID_KEY);
    if (!storedSessionId) {
      storedSessionId = crypto.randomUUID();
      sessionStorage.setItem(CHAT_SESSION_ID_KEY, storedSessionId);
    }

    sessionIdRef.current = storedSessionId;
    return storedSessionId;
  };

  useEffect(() => {
    const sessionId = getOrCreateSessionId();

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

  const scrollToBottom = () => {
    const messageList = messageListRef.current;
    if (!messageList) return;
    messageList.scrollTo({ top: messageList.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (): Promise<void> => {
    if (isTyping || isSendingRef.current) return;

    const trimmedMessage = inputValue.trim();
    if (!trimmedMessage) return;

    isSendingRef.current = true;
    const sessionId = getOrCreateSessionId();

    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: trimmedMessage,
      sender: "user",
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    const userMessageText: string = trimmedMessage;
    setInputValue("");
    setIsTyping(true);

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = '32px';
    }

    try {
      const response: ChatResponse = await apiClient.post<ChatResponse>('/api/chat', { 
        message: userMessageText,
        sessionId
      } satisfies ChatRequest);

      if (response.status === ChatResponseStatus.ERROR) {
        throw new Error('AI response error');
      }

      const newAiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.message,
        sender: "ai",
        timestamp: Date.now(),
      };
      
      setMessages((prev) => [...prev, newAiMessage]);

      if (response.status === ChatResponseStatus.COMPLETE) {
        loadTrips?.(response.searchId);
      }

      setTimeout(() => {
        try {
          inputRef.current?.focus({ preventScroll: true });
        } catch (e) {
          // ignore
        }
      }, 0);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting. Please try again.",
        sender: "ai",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      isSendingRef.current = false;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (isTyping || isSendingRef.current) return;
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 100)}px`;
  };

  const handleBlur = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    // If empty, reset to default compact height; otherwise clamp to content height
    if (!e.target.value || !e.target.value.trim()) {
      e.target.style.height = '32px';
    } else {
      e.target.style.height = `${Math.min(e.target.scrollHeight, 100)}px`;
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={`material-symbols-outlined ${styles.headerIcon}`}>
          smart_toy
        </span>
        <h3 className={styles.title}>AI Planner</h3>
      </div>

      <div className={styles.messageList} ref={messageListRef}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${
              msg.sender === "user" ? styles.userMessage : styles.aiMessage
            }`}
          >
            {msg.text}
          </div>
        ))}
        {isTyping && (
          <div className={styles.typingIndicator}>
            <div className={styles.dot} />
            <div className={styles.dot} />
            <div className={styles.dot} />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputArea}>
        <textarea
          ref={inputRef}
          className={styles.input}
          placeholder="Ask anything..."
          value={inputValue}
          onChange={handleInput}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isTyping}
        />
        <button
          className={styles.sendButton}
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isTyping}
        >
          <span className={`material-symbols-outlined ${styles.sendIcon}`}>
            send
          </span>
        </button>
      </div>
    </div>
  );
};

export default AiChatSidebar;
