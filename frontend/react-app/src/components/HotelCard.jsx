import React from 'react';
import { simulateBooking } from '../utils/api';

const HotelCard = ({ hotel }) => {
  const handleBook = async () => {
    alert(`Redirecting to book hotel ${hotel.name}...`);
    try {
      await simulateBooking("user@example.com", {
        type: "hotel",
        name: hotel.name,
        price: hotel.price_per_night
      });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mt-2">
      <div className="flex-1">
        <h3 className="font-bold text-gray-800 text-lg">{hotel.name}</h3>
        <div className="flex items-center gap-1 my-1">
          {/* Star rating */}
          <div className="flex text-yellow-400 text-sm">
            {"★".repeat(Math.floor(hotel.star_rating))}
            {"☆".repeat(5 - Math.floor(hotel.star_rating))}
          </div>
          <span className="text-xs text-gray-500 ml-2">{hotel.star_rating} Stars</span>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {hotel.amenities && hotel.amenities.map((amenity, i) => (
            <span key={i} className="text-xs text-brand-peach bg-brand-light px-2 py-1 rounded-md border border-brand-peach/30">
              {amenity}
            </span>
          ))}
        </div>
      </div>
      <div className="flex flex-col items-end gap-2 w-full md:w-auto mt-4 md:mt-0 border-t md:border-t-0 border-gray-100 pt-4 md:pt-0">
        <div className="text-right">
          <span className="text-xl font-bold text-brand-orange">${hotel.price_per_night}</span>
          <span className="text-xs text-gray-500 block">/ night</span>
        </div>
        <button 
          onClick={handleBook}
          className="w-full md:w-auto px-6 py-2 bg-brand-orange text-white text-sm font-semibold rounded-lg hover:bg-orange-600 transition-colors shadow-sm"
        >
          Book Hotel
        </button>
      </div>
    </div>
  );
};

export default HotelCard;
