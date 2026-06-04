# app/services/llm.py
import os
from groq import Groq

class DigestLLMEngine:
    def __init__(self):
        # Grab the API key from your environment variables
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate_summary(self, article_text: str) -> tuple[str, str]:
        """Returns a tuple of (summary, category)"""
        prompt = f"""
        Analyze the following article text. Provide two things:
        1. A concise, 2-sentence summary of the article.
        2. A single-word category label (e.g., Tech, Finance, Health, Politics).

        Format your output EXACTLY like this:
        SUMMARY: <your summary here>
        CATEGORY: <your category here>

        Article Text:
        {article_text[:2000]}  # Truncate text to fit context cleanly
        """

        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.3 # Low temperature for factual summarization
        )

        response_text = chat_completion.choices[0].message.content
        
        # Simple string parsing to separate Summary and Category
        try:
            lines = response_text.strip().split("\n")
            summary = lines[0].replace("SUMMARY:", "").strip()
            category = lines[1].replace("CATEGORY:", "").strip()
            return summary, category
        except Exception:
            # Fallback if Llama changes the formatting slightly
            return response_text, "General"