import google.generativeai as genai
from config import settings
import asyncio

genai.configure(api_key=settings.GEMINI_API_KEY)

# Free tier models - use exact names from API
DEFAULT_MODEL = "gemini-flash-latest"


def clean_model_name(model: str) -> str:
    """Remove models/ prefix if present."""
    if model.startswith("models/"):
        return model[7:]
    return model


async def chat(messages: list, model: str = None) -> str:
    """Send chat to Gemini with retry on quota errors."""
    if model is None:
        model = DEFAULT_MODEL
    
    model = clean_model_name(model)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            system_instruction = ""
            history = []

            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                else:
                    history.append(
                        {
                            "role": "model" if msg["role"] == "assistant" else "user",
                            "parts": [msg["content"]],
                        }
                    )

            generative_model = genai.GenerativeModel(
                model,
                system_instruction=system_instruction or None,
            )

            chat_session = generative_model.start_chat(
                history=history[:-1] if history else [],
            )

            last_message = history[-1] if history else None
            if not last_message:
                raise Exception("No messages to process")

            result = chat_session.send_message(last_message["parts"][0])
            return result.text
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    await asyncio.sleep(wait_time)
                    continue
            raise Exception(f"Gemini chat error: {error_str}")
    
    raise Exception("Gemini API quota exceeded. Please try again later.")


async def generate_title(message: str, model: str = None) -> str:
    """Generate title with fallback to default response."""
    if model is None:
        model = DEFAULT_MODEL
    
    model = clean_model_name(model)
    
    try:
        generative_model = genai.GenerativeModel(model)
        result = generative_model.generate_content(
            f'Generate a short title (max 50 chars) for this conversation start. Return ONLY the title, nothing else:\n\n"{message}"'
        )
        return result.text.strip().strip("\"'")
    except Exception:
        return "New Chat"
