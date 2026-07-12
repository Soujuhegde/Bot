import React from 'react';

const HotelTicket = ({ ticket }) => {
  if (!ticket) return null;

  const pricePerNight = ticket.price_per_night || "₹2,250";
  const totalPrice = ticket.total_price || "₹2,250";
  const nights = ticket.nights || 1;
  const occupancy = `${ticket.guests || "01 Adult"}, ${ticket.rooms || "01 Room"}`;

  return (
    <div className="w-full max-w-xl mx-auto my-4 bg-white border border-slate-200 rounded-3xl p-5 shadow-lg relative font-sans flex flex-col gap-4">
      {/* Green Checkmark Circle on left edge */}
      <div className="absolute -left-5 top-1/2 -translate-y-1/2 w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center border-4 border-white shadow-md z-10">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="w-5 h-5 text-white">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>

      <div className="pl-4">
        {/* Room & Price Summary Header */}
        <h3 className="font-bold text-slate-800 text-lg mb-4">Room & Price Summary</h3>

        <div className="flex gap-4 items-start mb-4">
          {/* Room Image */}
          <div className="w-24 h-24 rounded-xl overflow-hidden flex-shrink-0 bg-slate-100 border border-slate-100">
            <img 
              src={ticket.image || "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=200&q=80"} 
              alt={ticket.room_type} 
              className="w-full h-full object-cover"
            />
          </div>

          {/* Room Details */}
          <div className="flex-1 min-w-0">
            <h4 className="font-bold text-slate-800 text-lg truncate">{ticket.room_type || "Executive Rooms"}</h4>
            
            {/* Address */}
            <p className="text-xs text-slate-400 mt-1 mb-2 flex items-start gap-1 font-medium leading-tight">
              <span className="flex-shrink-0 text-slate-400">📍</span>
              <span className="truncate">{ticket.hotel_name}, {ticket.city}, India</span>
            </p>

            {/* Amenities */}
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-slate-500 font-medium text-xs">
              <span className="flex items-center gap-1">📰 Newspaper</span>
              <span className="flex items-center gap-1">🍺 Refrigerator</span>
              <span className="text-[#3b82f6] font-bold hover:underline cursor-pointer">More Amenities</span>
            </div>
          </div>
        </div>

        {/* Shaded Occupancy Table */}
        <div className="bg-[#f0f6ff] rounded-xl p-3 grid grid-cols-2 gap-3 text-left mb-4">
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Check In Date/Time</p>
            <p className="font-bold text-slate-800 text-sm mt-0.5">{ticket.check_in_date || "12 PM"}</p>
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Check Out Date/Time</p>
            <p className="font-bold text-slate-800 text-sm mt-0.5">{ticket.check_out_date || "11 AM"}</p>
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Occupancy</p>
            <p className="font-bold text-slate-800 text-sm mt-0.5 truncate">{occupancy}</p>
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Guest Name</p>
            <p className="font-bold text-slate-800 text-sm mt-0.5 truncate">{ticket.guest_name || "Guest"}</p>
          </div>
        </div>

        {/* Pricing Info */}
        <div className="flex justify-between items-center py-2 px-2 border-b border-dashed border-slate-100 mb-4">
          <div className="text-center flex-1">
            <p className="text-lg font-black text-slate-800">{pricePerNight}</p>
            <p className="text-[10px] text-slate-400 font-bold mt-0.5">Total rooms price</p>
          </div>
          
          <div className="text-xl font-bold text-slate-300 px-4">+</div>

          <div className="text-center flex-1">
            <p className="text-lg font-black text-slate-800">{totalPrice}</p>
            <p className="text-[10px] text-slate-400 font-bold mt-0.5">Total price for {nights} Night(s) stay</p>
          </div>
        </div>

        {/* Booked Button */}
        <div className="flex justify-end mt-2">
          <button 
            disabled 
            className="bg-[#1e88e5] text-white font-bold py-2.5 px-10 rounded-xl text-sm opacity-100 shadow transition-opacity cursor-default w-32 text-center"
          >
            Booked
          </button>
        </div>
      </div>
    </div>
  );
};

export default HotelTicket;
