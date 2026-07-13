import React, { useState, useRef, useEffect } from 'react';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  return (
    <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-white via-white to-transparent pt-6 pb-6 px-4 md:px-0">
      <div className="max-w-3xl mx-auto relative">
        <div className="relative flex items-end w-full p-2 bg-white border border-gray-300 rounded-2xl shadow-sm focus-within:ring-1 focus-within:ring-brand-peach focus-within:border-brand-peach transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            placeholder="Book a flight to Paris next week..."
            className="w-full max-h-48 py-2 pl-3 pr-12 bg-transparent border-0 resize-none focus:ring-0 text-gray-800 text-lg"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            className={`absolute right-3 bottom-3 p-1.5 rounded-lg flex items-center justify-center transition-colors ${
              message.trim() && !isLoading
                ? 'bg-brand-orange text-white hover:bg-orange-600'
                : 'bg-gray-200 text-gray-400'
            }`}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5" xmlns="http://www.w3.org/2000/svg"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            )}
          </button>
        </div>
        <div className="text-center text-xs text-gray-400 mt-2">
          Travel Chatbot can make mistakes. Consider verifying important information.
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
