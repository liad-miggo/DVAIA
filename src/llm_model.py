from langchain_google_vertexai import ChatVertexAI
from google.oauth2 import service_account
from typing import Optional
from base64 import b64decode
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default model and API key from environment
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")
GOOGLE_VERTEX_API_KEY = os.getenv("GOOGLE_VERTEX_API_KEY")


class LLMModel(ChatVertexAI):
    def __init__(
        self,
        model_name: Optional[str] = None,
        credentials=None,
        **kwargs,
    ):
        if model_name is None:
            model_name = LLM_MODEL
        if credentials is None and GOOGLE_VERTEX_API_KEY:
            try:
                credentials = json.loads(b64decode(GOOGLE_VERTEX_API_KEY.encode()))
            except Exception as e:
                raise ValueError(f"Invalid GOOGLE_VERTEX_API_KEY format: {e}")

        if credentials:
            credentials = service_account.Credentials.from_service_account_info(credentials)
        
        super().__init__(model_name=model_name, credentials=credentials, **kwargs) 