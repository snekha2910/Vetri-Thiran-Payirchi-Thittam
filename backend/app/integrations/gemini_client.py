import logging
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger("pocketsmart.gemini")

class GeminiManager:
    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        if settings.gemini_api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.gemini_api_key)
                logger.info(f"Gemini client initialized with model {settings.gemini_model} using google.genai SDK")
            except Exception as e:
                logger.warning(f"Could not configure Gemini client: {e}")
                self._client = None
        else:
            self._client = None

    @property
    def client(self) -> Optional[Any]:
        if self._client is None and settings.gemini_api_key:
            self._init_client()
        return self._client

    @property
    def model_name(self) -> str:
        return settings.gemini_model

    @property
    def model(self) -> Optional[Any]:
        return self.client

    @property
    def is_configured(self) -> bool:
        return bool(settings.gemini_api_key) and self.client is not None

    @property
    def is_available(self) -> bool:
        return self.is_configured and not getattr(settings, "gemini_mock_mode", False)

    def check_reachability(self) -> bool:
        """
        Check connectivity to Google GenAI without spending generation quota.
        """
        if not self.is_configured or self.client is None:
            return False
        try:
            for _ in self.client.models.list(config={"page_size": 1}):
                return True
            return True
        except Exception as e:
            logger.warning(f"Gemini reachability check notice: {e}")
            err_str = str(e).lower()
            if any(k in err_str for k in ["429", "quota", "resource_exhausted"]):
                return True
            return False

gemini_manager = GeminiManager()
