import json
import httpx
from typing import Any, Dict
from app.config import settings
from app.schemas.schemas import ExtractedIntent
from langchain_groq import ChatGroq

class LLMClient:
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.sarvam_api_key = settings.SARVAM_API_KEY
        self.model = settings.LLM_MODEL
        
        # Primary: Groq for fast structured output
        if self.groq_api_key:
            self.llm = ChatGroq(
                api_key=self.groq_api_key,
                model=self.model,
                temperature=0,
            )
        else:
            self.llm = None

    async def parse_intent_sarvam(self, prompt: str) -> ExtractedIntent:
        """Fallback or primary call to Sarvam AI (sarvam-105b) if Groq fails or user prefers it."""
        url = "https://api.sarvam.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.sarvam_api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "You are a travel assistant. Extract the intent and travel details from the user's message. "
            "Output valid JSON matching this schema: "
            "{'intent': 'book_flight' | 'book_hotel' | 'book_both' | 'general_qa', "
            "'origin': string, 'destination': string, 'departure_date': 'YYYY-MM-DD', "
            "'return_date': 'YYYY-MM-DD', 'passengers': int, 'cabin_class': string, "
            "'check_in_date': 'YYYY-MM-DD', 'check_out_date': 'YYYY-MM-DD'}. "
            "Only output the JSON object, nothing else."
        )

        payload = {
            "model": "sarvam-105b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            try:
                # Basic cleanup in case it returns markdown JSON
                content = content.strip().strip("```json").strip("```").strip()
                parsed = json.loads(content)
                return ExtractedIntent(**parsed)
            except Exception as e:
                print(f"Error parsing Sarvam response: {e}, Content: {content}")
                return ExtractedIntent(intent="general_qa")

    async def parse_intent(self, prompt: str) -> ExtractedIntent:
        """Parse user intent using Groq (primary) with structured output."""
        if not self.llm:
            if self.sarvam_api_key:
                return await self.parse_intent_sarvam(prompt)
            raise ValueError("No LLM API keys provided.")

        try:
            structured_llm = self.llm.with_structured_output(ExtractedIntent)
            
            messages = [
                ("system", "You are a travel assistant. Extract the intent and travel details from the user's message."),
                ("user", prompt)
            ]
            
            result = structured_llm.invoke(messages)
            return result
        except Exception as e:
            print(f"Groq failed: {e}. Falling back to Sarvam AI.")
            if self.sarvam_api_key:
                return await self.parse_intent_sarvam(prompt)
            raise e

    async def generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate natural language response."""
        if self.llm:
            try:
                messages = [
                    ("system", system_prompt),
                    ("user", user_message)
                ]
                response = self.llm.invoke(messages)
                return response.content
            except Exception as e:
                print(f"Groq failed: {e}")
        
        # Fallback to Sarvam AI
        if self.sarvam_api_key:
            url = "https://api.sarvam.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.sarvam_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "sarvam-105b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.5
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
        
        return "I'm having trouble connecting to my brain right now. Please try again."

llm_client = LLMClient()
