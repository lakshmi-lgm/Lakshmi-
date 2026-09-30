from google import genai
from app.config import settings

class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing in environment variables.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-3.8-flash"

    def ask_tutor(self, question: str, context: str = "") -> str:
        prompt = f"""
You are EduGenie, an expert, encouraging, and clear AI Learning Assistant.
Answer the user's question accurately based on the provided context (if any).

Context:
{context if context else 'No document context provided. Answer using general domain knowledge.'}

Question:
{question}
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def generate_study_material(self, material_type: str, text_content: str) -> str:
        prompts = {
            "notes": "Summarize the following educational content into clear, structured study notes with key bullet points, concepts, and definitions:",
            "flashcards": "Generate 5-8 flashcards from the text below. Format each as:\nQ: [Question]\nA: [Answer]\n---",
            "quiz": "Generate a 5-question Multiple Choice Quiz (MCQ) based on the text. For each question, provide options A, B, C, D, and clearly state the correct answer with brief explanations.",
            "summary": "Provide a concise 3-paragraph executive summary of the following document:"
        }
        
        prompt_prefix = prompts.get(material_type, "Analyze and summarize the following study material:")
        full_prompt = f"{prompt_prefix}\n\nStudy Material:\n{text_content[:8000]}"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt
        )
        return response.text