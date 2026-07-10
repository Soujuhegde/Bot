import React from 'react';

const TypingIndicator = () => {
  return (
    <div className="flex space-x-1.5 p-4 bg-white rounded-2xl rounded-tl-none shadow-sm w-16 border border-slate-100">
      <div className="w-2 h-2 bg-brand rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-2 h-2 bg-brand rounded-full animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-2 h-2 bg-brand rounded-full animate-bounce"></div>
    </div>
  );
};

export default TypingIndicator;
