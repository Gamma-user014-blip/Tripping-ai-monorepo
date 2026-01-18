import React, { useState, useRef, useEffect } from "react";
import styles from "./ai-chat-sidebar.module.css";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: number;
}

const AiChatSidebar: React.FC = () => {
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
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: inputValue.trim(),
      sender: "user",
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue("");
    setIsTyping(true);

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = '32px';
    }

    // Simulate AI response
    setTimeout(() => {
      const newAiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Hello! That sounds clearer. Let me see what I can find for you.",
        sender: "ai",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, newAiMessage]);
      setIsTyping(false);

      setTimeout(() => {
        try {
          inputRef.current?.focus();
        } catch (e) {
          // ignore
        }
      }, 0);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
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

      <div className={styles.messageList}>
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
