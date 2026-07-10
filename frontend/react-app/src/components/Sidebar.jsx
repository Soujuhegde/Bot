import React from 'react';

const Sidebar = ({ onNewChat }) => {
  return (
    <div className="w-64 bg-sidebar h-full flex flex-col border-r border-gray-200 hidden md:flex">
      <div className="p-4">
        <button 
          onClick={onNewChat}
          className="w-full flex items-center gap-2 p-3 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors shadow-sm text-sm font-medium text-gray-700"
        >
          <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          New chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto sidebar-scroll p-3 pt-0">
        {/* Placeholder for chat history */}
        <div className="text-xs font-semibold text-gray-400 mb-2 mt-4 px-2">Today</div>
        <button className="w-full text-left truncate p-2 rounded-md hover:bg-sidebar-hover text-sm text-gray-700 transition-colors">
          Booking flights to NYC
        </button>
        <button className="w-full text-left truncate p-2 rounded-md hover:bg-sidebar-hover text-sm text-gray-700 transition-colors">
          Hotels in Tokyo
        </button>
      </div>
      <div className="p-4 border-t border-gray-200 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-brand-orange flex items-center justify-center text-white font-bold text-sm">
          U
        </div>
        <div className="text-sm font-medium text-gray-700">User</div>
      </div>
    </div>
  );
};

export default Sidebar;
