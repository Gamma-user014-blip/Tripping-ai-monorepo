import React, { useRef, useEffect } from "react";
import styles from "./ai-chat-sidebar.module.css";
import useChat from "../../../hooks/use-chat";
import { Trip } from "../../../../../shared/types";

interface AiChatSidebarProps {
  onTripsLoaded?: (trips: Trip[]) => void;
  onSearchStart?: () => void;
  onSearchClear?: () => void;
  onSearchComplete?: () => void;
}

const AiChatSidebar: React.FC<AiChatSidebarProps> = ({
  onTripsLoaded,
  onSearchStart,
  onSearchClear,
  onSearchComplete,
}) => {
  const {
    messages,
    isTyping,
    isSearching,
    sendMessage,
    isSending,
    startPollingFromSession,
  } = useChat({
    onTripsLoaded,
    onSearchStart,
    onSearchClear,
    onSearchComplete,
    mode: "inline",
  });

  const [inputValue, setInputValue] = React.useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageListRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const hasStartedPollingRef = useRef(false);

  // On mount, check if we have a pending searchId from homepage redirect
  useEffect(() => {
    if (hasStartedPollingRef.current) return;
    hasStartedPollingRef.current = true;
    startPollingFromSession();
  }, [startPollingFromSession]);

  const scrollToBottom = (): void => {
    const messageList = messageListRef.current;
    if (!messageList) return;
    messageList.scrollTo({ top: messageList.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (): Promise<void> => {
    if (isTyping || isSending || !inputValue.trim()) return;

    const text = inputValue;
    setInputValue("");

    if (inputRef.current) {
      inputRef.current.style.height = "32px";
    }

    await sendMessage(text);

    setTimeout(() => {
      inputRef.current?.focus({ preventScroll: true });
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (isTyping || isSending) return;
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setInputValue(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 100)}px`;
  };

  const handleBlur = (e: React.FocusEvent<HTMLTextAreaElement>): void => {
    if (!e.target.value || !e.target.value.trim()) {
      e.target.style.height = "32px";
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
          disabled={isTyping || isSearching}
        />
        <button
          className={styles.sendButton}
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isTyping || isSearching}
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
