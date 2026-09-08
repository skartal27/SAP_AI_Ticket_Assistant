import os
from dotenv import load_dotenv

load_dotenv()

class MultiLLMClient:
    def __init__(self, provider: str = "Gemini", api_key: str = None):
        self.provider = provider
        
        if self.provider == "Gemini":
            import google.generativeai as genai
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("Gemini API Key bulunamadı! Lütfen arayüzden girin veya .env dosyasına ekleyin.")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

        elif self.provider == "OpenAI":
            from openai import OpenAI
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API Key bulunamadı! Lütfen arayüzden girin veya .env dosyasına ekleyin.")
            self.client = OpenAI(api_key=self.api_key)
            self.model_name = "gpt-4o-mini"

    def analyze_ticket(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "Gemini":
            combined = f"{system_prompt}\n\n{user_prompt}"
            response = self.model.generate_content(combined)
            return response.text
        elif self.provider == "OpenAI":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content