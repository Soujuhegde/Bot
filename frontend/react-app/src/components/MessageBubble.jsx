import React from 'react';
import { Plane, Hotel, CheckCircle, ChevronRight } from 'lucide-react';

const FlightCard = ({ option }) => {
  return (
    <div className="bg-white border border-slate-100 rounded-3xl p-5 my-2 shadow-sm mb-4">
      <div className="font-bold text-slate-800 text-lg mb-4 flex items-center gap-3">
        {option.airline_logo && <img src={option.airline_logo} alt={option.airline_name} className="w-6 h-6 object-contain" />}
        {option.airline_name} - {option.flight_numbers}
      </div>
      
      <div className="flex justify-between text-sm text-slate-500 font-medium mb-1">
        <span>{option.departure_date}</span>
        <span>{option.arrival_date}</span>
      </div>
      
      <div className="flex justify-between items-center mb-1">
        <div className="text-3xl font-bold text-[#004e92]">{option.departure_time}</div>
        <div className="flex-1 flex flex-col items-center mx-4">
          <div className="flex items-center w-full text-slate-400 font-medium text-xs">
            <div className="flex-1 border-t border-dashed border-slate-400"></div>
            <span className="bg-[#f0f4f8] px-2 py-1 rounded-md mx-2 text-slate-700">{option.duration}</span>
            <div className="flex-1 border-t border-dashed border-slate-400"></div>
          </div>
        </div>
        <div className="text-3xl font-bold text-[#004e92]">{option.arrival_time}</div>
      </div>
      
      <div className="flex justify-between text-sm font-semibold text-slate-800 mb-6">
        <div className="w-24 leading-tight">{option.origin_airport}</div>
        <div className="text-slate-600 font-bold">{option.stops}</div>
        <div className="w-24 text-right leading-tight">{option.destination_airport}</div>
      </div>
      
      <div className="space-y-3">
        {option.pricing?.map((p, idx) => (
          <div 
            key={idx} 
            onClick={() => option.onOptionSelect && option.onOptionSelect(option, p.class, p.price)}
            className="flex justify-between items-center bg-orange-50 p-4 rounded-xl cursor-pointer hover:bg-orange-100 transition-colors"
          >
            <span className="font-bold text-slate-900 text-base">{p.class}</span>
            <span className="font-bold text-brand flex items-center gap-1 text-base">
              From {p.price} <ChevronRight className="w-4 h-4" />
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

const renderTextWithLinks = (text) => {
  if (!text) return null;
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = text.split(urlRegex);
  return parts.map((part, i) => {
    if (part.match(urlRegex)) {
      return (
        <a 
          key={i} 
          href={part} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="text-blue-600 underline hover:text-blue-800 break-all"
        >
          {part}
        </a>
      );
    }
    return part;
  });
};

const MessageBubble = ({ message, onQuickReply, onOptionSelect }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      {/* Bot Avatar */}
      {!isUser && (
        <div className="w-10 h-10 rounded-full overflow-hidden mr-3 flex-shrink-0 mt-1 shadow-sm border border-slate-200">
          <img src="https://i.pravatar.cc/150?img=47" alt="AI Agent" className="w-full h-full object-cover" />
        </div>
      )}
      
      <div className={`w-full max-w-[95%] lg:max-w-[85%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div 
          className={`p-5 shadow-sm text-base ${
            isUser 
              ? 'bg-brand text-white rounded-3xl rounded-tr-sm' 
              : 'bg-white text-slate-700 rounded-3xl rounded-tl-sm border border-slate-100'
          }`}
        >
          <p className="whitespace-pre-wrap leading-relaxed">{renderTextWithLinks(message.text)}</p>
        </div>
        
        {/* Quick Replies */}
        {!isUser && message.quick_replies && message.quick_replies.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4 ml-1">
            {message.quick_replies.map((reply, i) => (
              <button 
                key={i} 
                onClick={() => onQuickReply && onQuickReply(reply)}
                className="px-5 py-2.5 bg-white border border-slate-200 text-slate-500 hover:text-slate-700 hover:border-slate-300 rounded-full text-sm font-medium transition-colors shadow-sm"
              >
                {reply}
              </button>
            ))}
          </div>
        )}
        
        {/* Flight Cards and Action Buttons */}
        {message.options && message.options.length > 0 && (
          <div className="mt-4 grid grid-cols-1 gap-4">
            {message.options.map((opt, i) => {
              if (opt.type === 'action_button') {
                return (
                  <a 
                    key={i} 
                    href={opt.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="block w-full text-center bg-brand text-white font-bold py-3 px-4 rounded-xl shadow hover:opacity-90 transition-opacity"
                  >
                    {opt.label}
                  </a>
                );
              }
              return <FlightCard key={i} option={{...opt, onOptionSelect}} />;
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
