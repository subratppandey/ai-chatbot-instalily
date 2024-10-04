import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";
import { FiCopy } from "react-icons/fi"; 

function ChatWindow() {
  const defaultMessage = [{
    role: "assistant",
    isDefault: true,
    content: "PartSelect's AI-powered chatbot welcomes you. Please ask specific questions related to Dishwashers and Refrigerators, and we would be glad to help! For more details about products, please visit our website: https://www.partselect.com/"
  }];

  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    return savedMessages ? JSON.parse(savedMessages) : defaultMessage;
  });

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false); 
  const [copiedMessageIndex, setCopiedMessageIndex] = useState(null);
  const [showScrollButton, setShowScrollButton] = useState(false); 
  const [scrollDirection, setScrollDirection] = useState('top'); // 'top' or 'bottom'

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToTop = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    }
  };

  const handleScrollButtonClick = () => {
    if (scrollDirection === 'top') {
      scrollToTop();
    } else {
      scrollToBottom();
    }
  };

  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
    scrollToBottom();
  }, [messages]);

  // Show or hide the scroll button based on the scroll position and content height
  useEffect(() => {
    const handleScroll = () => {
      const chatContainer = chatContainerRef.current;

      // Check if the total height exceeds the visible height (scrollable content)
      const isScrollable = chatContainer.scrollHeight > chatContainer.clientHeight;

      if (isScrollable) {
        setShowScrollButton(true);

        // Determine when to show "Scroll to Bottom" or "Scroll to Top"
        if (chatContainer.scrollTop === 0) {
          setScrollDirection('bottom'); // Show "Scroll to Bottom" when at the top
        } else if (chatContainer.scrollTop + chatContainer.clientHeight < chatContainer.scrollHeight - 200) {
          setScrollDirection('top'); // Show "Scroll to Top" when scrolled down
        } else {
          setShowScrollButton(false); // Hide button when at the bottom
        }
      } else {
        setShowScrollButton(false); // Don't show the button if there isn't enough content to scroll
      }
    };

    const chatContainer = chatContainerRef.current;
    chatContainer.addEventListener("scroll", handleScroll);

    return () => {
      chatContainer.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const handleSend = async (input) => {
    if (input.trim() !== "" && !isSending) {
      setIsSending(true); 
      setMessages(prevMessages => [...prevMessages, { role: "user", content: input }]);
      setInput("");

      // Show loading dots
      const loadingMessageId = Date.now();
      setMessages(prevMessages => [...prevMessages, { role: "loading", content: "...", id: loadingMessageId }]);

      // Get response from the API
      const newMessage = await getAIMessage(input);

      // Replace the loading message with the actual response
      setMessages(prevMessages => prevMessages.map(msg =>
        msg.id === loadingMessageId ? { ...newMessage, id: undefined } : msg
      ));

      setIsSending(false); 
    }
  };

  const handleCopy = (content, index) => {
    navigator.clipboard.writeText(content).then(() => {
      setCopiedMessageIndex(index);

      setTimeout(() => setCopiedMessageIndex(null), 2000);
    });
  };

  // Clear chat history and local storage
  const handleClearChat = () => {
    localStorage.removeItem('chatMessages');
    setMessages(defaultMessage);
  };

  return (
    <div className="messages-container" ref={chatContainerRef}>
      {messages.map((message, index) => (
        <div key={index} className={`${message.role}-message-container`}>
          {message.role === 'loading' ? (
            <div className="typing-indicator">
              <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
              <span> PartSelect is typing...</span>
            </div>
          ) : (
            <div className={`message ${message.isDefault ? 'default-message' : `${message.role}-message`}`}>
              <div dangerouslySetInnerHTML={{__html: marked(message.content).replace(/<p>|<\/p>/g, "")}}></div>
              
              {!message.isDefault && message.role === "assistant" && (
                <div className="copy-icon-container">
                  <FiCopy className="copy-button" onClick={() => handleCopy(message.content, index)} />
                  {copiedMessageIndex === index && <span className="copied-notification">Copied!</span>}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
      <div ref={messagesEndRef} />
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me a question..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
        />
        <button className="send-button" onClick={() => handleSend(input)} disabled={isSending}>
          Send
        </button>

        {/* Only show the scroll button when necessary */}
        {showScrollButton && (
          <button className="scroll-to-top" onClick={handleScrollButtonClick}>
            {scrollDirection === 'top' ? '⬆' : '⬇'}
          </button>
        )}

        {/* Clear Chat Button */}
        <button className="clear-chat-button" onClick={handleClearChat}>
          Clear Chat
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;




