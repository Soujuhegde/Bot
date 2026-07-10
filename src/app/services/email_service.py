import httpx
from app.config import settings

class EmailService:
    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.url = "https://api.brevo.com/v3/smtp/email"

    async def send_booking_confirmation(self, email_to: str, booking_details: dict):
        if not self.api_key:
            print("Brevo API key not set. Skipping email sending.")
            return True

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
        
        # Simple text template based on booking details
        content = f"Your booking is confirmed! Details:\n\n{booking_details}"

        payload = {
            "sender": {"name": "Travel Chatbot", "email": "noreply@travelchatbot.local"},
            "to": [{"email": email_to}],
            "subject": "Booking Confirmation",
            "textContent": content
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"Error sending email: {e}")
                return False

email_service = EmailService()
