import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import FlightCard from './FlightCard';
import HotelCard from './HotelCard';

const ChatArea = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto pb-32">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-center px-4">
          <div className="w-16 h-16 bg-brand-orange rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-orange-200">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-8 w-8 text-white"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">How can I help you travel today?</h2>
          <div className="flex flex-wrap justify-center gap-3 mt-8 max-w-2xl">
            <button className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-100 transition-colors">
              "Find me flights to Tokyo next week"
            </button>
            <button className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-100 transition-colors">
              "I need a hotel in Paris for 2 nights"
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col w-full">
          {messages.map((msg, index) => (
            <React.Fragment key={index}>
              <MessageBubble message={msg} />
              
              {/* Render Flight Options if they exist in the bot's response */}
              {msg.flightOptions && msg.flightOptions.length > 0 && (
                <div className="w-full bg-brand-light/30 border-b border-black/10 pb-6">
                  <div className="max-w-3xl mx-auto px-4 md:px-6 pl-16 md:pl-18">
                    <div className="space-y-4 mt-2">
                      {msg.flightOptions.map((flight, i) => (
                        <FlightCard key={`flight-${i}`} flight={flight} />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Render Hotel Options if they exist in the bot's response */}
              {msg.hotelOptions && msg.hotelOptions.length > 0 && (
                <div className="w-full bg-brand-light/30 border-b border-black/10 pb-6">
                  <div className="max-w-3xl mx-auto px-4 md:px-6 pl-16 md:pl-18">
                    <div className="space-y-4 mt-2">
                      {msg.hotelOptions.map((hotel, i) => (
                        <HotelCard key={`hotel-${i}`} hotel={hotel} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
          
          {isLoading && (
            <div className="w-full bg-brand-light/30 border-b border-black/10 py-6">
              <div className="max-w-3xl mx-auto flex gap-4 px-4 md:px-6">
                <div className="flex-shrink-0 w-8 h-8 rounded-sm bg-brand-orange flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5 text-white"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatArea;
