import React from 'react';
import { simulateBooking } from '../utils/api';

const FlightCard = ({ flight }) => {
  const handleBook = async () => {
    // If we have a booking_token, SerpApi provides a link. We will just simulate it.
    alert(`Redirecting to book flight ${flight.flight_number} with ${flight.airline}...`);
    
    // Simulate hitting the backend to send confirmation email
    try {
      await simulateBooking("user@example.com", {
        type: "flight",
        airline: flight.airline,
        flight_number: flight.flight_number,
        price: flight.price
      });
      console.log("Confirmation email triggered!");
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mt-2">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-bold text-gray-800">{flight.airline}</span>
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{flight.flight_number}</span>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
          <div className="flex flex-col">
            <span className="font-semibold text-gray-800">{flight.depart_time}</span>
            <span>Departure</span>
          </div>
          <div className="flex-1 border-b-2 border-dashed border-gray-300 relative mx-4">
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-xs bg-white px-2 text-gray-400">
              {Math.floor(flight.duration / 60)}h {flight.duration % 60}m
            </span>
            <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-xs text-gray-400">
              {flight.stops === 0 ? 'Direct' : `${flight.stops} stop(s)`}
            </span>
          </div>
          <div className="flex flex-col text-right">
            <span className="font-semibold text-gray-800">{flight.arrive_time}</span>
            <span>Arrival</span>
          </div>
        </div>
      </div>
      <div className="flex flex-col items-end gap-2 w-full md:w-auto mt-4 md:mt-0 border-t md:border-t-0 border-gray-100 pt-4 md:pt-0">
        <div className="text-xl font-bold text-brand-orange">${flight.price}</div>
        <button 
          onClick={handleBook}
          className="w-full md:w-auto px-6 py-2 bg-brand-orange text-white text-sm font-semibold rounded-lg hover:bg-orange-600 transition-colors shadow-sm"
        >
          Book Now
        </button>
      </div>
    </div>
  );
};

export default FlightCard;
