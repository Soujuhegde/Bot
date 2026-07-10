const API_BASE = "http://localhost:8000/api";

export const chatWithBot = async (message, sessionId = null) => {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Chat API error:", error);
    throw error;
  }
};

export const simulateBooking = async (email, bookingDetails) => {
  try {
    const response = await fetch(`${API_BASE}/book`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        booking_details: bookingDetails,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Booking API error:", error);
    throw error;
  }
};
