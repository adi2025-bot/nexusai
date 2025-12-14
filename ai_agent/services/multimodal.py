import google.generativeai as genai
from ai_agent.config.settings import settings

class VisionService:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_image(self, image_data, prompt: str = "Describe this image in detail.") -> str:
        """
        Uses Gemini Vision to analyze images.
        image_data: PIL Image or path
        """
        try:
            response = self.model.generate_content([prompt, image_data])
            return response.text
        except Exception as e:
            return f"Image analysis failed: {str(e)}"
