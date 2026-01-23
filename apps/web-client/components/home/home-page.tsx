import React, { useRef, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./home-page.module.css";
import Navbar from "../../common/navbar";
import useChat from "../../hooks/use-chat";
import { clearPendingSearch } from "../../lib/session";

const HomePage: React.FC = (): JSX.Element => {
  const router = useRouter();

  useEffect(() => {
    clearPendingSearch();
  }, []);

  const { messages, isTyping, sendMessage, isSending, isSearching } = useChat({
    mode: "redirect",
    onRedirect: (searchId: string) => {
      router.push(`/results?searchId=${searchId}`);
    },
  });

  const [inputValue, setInputValue] = React.useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageListRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = (): void => {
    const messageList = messageListRef.current;
    if (!messageList) return;
    messageList.scrollTo({ top: messageList.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async (): Promise<void> => {
    if (isTyping || isSending || !inputValue.trim()) return;

    const text = inputValue;
    setInputValue("");

    if (inputRef.current) {
      inputRef.current.style.height = "48px";
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
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const handleBlur = (e: React.FocusEvent<HTMLTextAreaElement>): void => {
    if (!e.target.value || !e.target.value.trim()) {
      e.target.style.height = "48px";
    } else {
      e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
    }
  };

  return (
    <div className={styles.homePage}>
      <div className={styles.navContainer}>
        <Navbar />
      </div>

      <div className={styles.chatContainer}>
        <div className={styles.chatContent}>
          {messages.length <= 1 && !isTyping ? (
            <div className={styles.welcomeState}>
              <div className={styles.welcomeIcon}>
                <span className="material-symbols-outlined">flight_takeoff</span>
              </div>
              <h1 className={styles.welcomeTitle}>Where do you want to go?</h1>
              <p className={styles.welcomeSubtitle}>
                Tell me about your dream trip and I'll find the perfect options for you
              </p>
            </div>
          ) : (
            <div className={styles.messageList} ref={messageListRef}>
              {messages.slice(1).map((msg) => (
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
              {isSearching && (
                <div className={styles.searchingIndicator}>
                  <span className={`material-symbols-outlined ${styles.searchingIcon}`}>
                    travel_explore
                  </span>
                  <span>Finding the best trips for you...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className={styles.inputContainer}>
          <div className={styles.inputWrapper}>
            <textarea
              ref={inputRef}
              className={styles.chatInput}
              placeholder="I want to go to Italy for a week..."
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
      </div>

      {/* Features Section - always visible */}
      <div className={styles.featuresSection}>
        <div className={styles.featuresSectionHeader}>
          <h2 className={styles.featuresSectionTitle}>How Tripping.ai Works</h2>
          <p className={styles.featuresSectionSubtitle}>
            Your AI-powered travel planning assistant
          </p>
        </div>

        <div className={styles.featuresContainer}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <span className="material-symbols-outlined">chat</span>
            </div>
            <h3 className={styles.featureTitle}>Tell Us Your Dreams</h3>
            <p className={styles.featureText}>
              Describe your ideal trip — destinations, dates, budget, vibes. Our AI understands natural language.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <span className="material-symbols-outlined">search</span>
            </div>
            <h3 className={styles.featureTitle}>We Find Options</h3>
            <p className={styles.featureText}>
              Our AI searches thousands of flights, hotels, and activities to build complete trip packages.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <span className="material-symbols-outlined">compare</span>
            </div>
            <h3 className={styles.featureTitle}>Compare & Choose</h3>
            <p className={styles.featureText}>
              Review curated options side-by-side with pricing, itineraries, and highlights all in one place.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <span className="material-symbols-outlined">hotel</span>
            </div>
            <h3 className={styles.featureTitle}>Handpicked Hotels</h3>
            <p className={styles.featureText}>
              We match you with accommodations that fit your style, from boutique stays to luxury resorts.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <span className="material-symbols-outlined">flight</span>
            </div>
            <h3 className={styles.featureTitle}>Smart Flight Combos</h3>
            <p className={styles.featureText}>
              Find the best flight combinations with optimal layovers, pricing, and travel times.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <span className="material-symbols-outlined">local_activity</span>
            </div>
            <h3 className={styles.featureTitle}>Curated Activities</h3>
            <p className={styles.featureText}>
              Discover tours, experiences, and hidden gems tailored to your interests at each destination.
            </p>
          </div>
        </div>

        <div className={styles.howItWorksSection}>
          <div className={styles.stepCard}>
            <div className={styles.stepNumber}>1</div>
            <h4 className={styles.stepTitle}>Start a Conversation</h4>
            <p className={styles.stepText}>Type your travel request in natural language above</p>
          </div>
          <div className={styles.stepArrow}>
            <span className="material-symbols-outlined">arrow_forward</span>
          </div>
          <div className={styles.stepCard}>
            <div className={styles.stepNumber}>2</div>
            <h4 className={styles.stepTitle}>AI Plans Your Trip</h4>
            <p className={styles.stepText}>Our AI searches and builds complete packages</p>
          </div>
          <div className={styles.stepArrow}>
            <span className="material-symbols-outlined">arrow_forward</span>
          </div>
          <div className={styles.stepCard}>
            <div className={styles.stepNumber}>3</div>
            <h4 className={styles.stepTitle}>Explore Options</h4>
            <p className={styles.stepText}>Browse detailed itineraries and pick your favorite</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
