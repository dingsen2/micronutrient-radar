from typing import Generator
import openai
from app.core.config import settings

def get_openai_client() -> Generator:
    """
    Get OpenAI client instance.
    """
    client = openai.AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE
    )
    try:
        yield client
    finally:
        # Cleanup if needed
        pass 