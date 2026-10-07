import logging
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger("pocketsmart.supabase")


class SupabaseManager:
    _instance = None
    _client = None
    _admin_client = None

    def __init__(self):
        self._init_client()

    def _init_client(self):
        url = settings.supabase_url
        key = settings.supabase_service_role_key or settings.supabase_key
        anon_key = settings.supabase_anon_key or settings.supabase_key
        if url and key:
            try:
                from supabase import create_client, Client

                # Primary client uses service role key (bypasses RLS for backend writes)
                self._client: Client = create_client(url, key)

                # Admin client uses service role key explicitly for admin operations
                if settings.supabase_service_role_key:
                    self._admin_client: Client = create_client(url, settings.supabase_service_role_key)
                else:
                    self._admin_client = self._client

                logger.info("Supabase PostgreSQL client connected successfully to %s", url)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self._client = None
                self._admin_client = None
        else:
            logger.warning("Supabase URL or Key not configured.")
            self._client = None
            self._admin_client = None

    @property
    def client(self) -> Optional[Any]:
        if self._client is None and (settings.supabase_url and (settings.supabase_service_role_key or settings.supabase_key)):
            self._init_client()
        return self._client

    @property
    def admin_client(self) -> Optional[Any]:
        """Returns a client initialized with the service-role key for admin operations."""
        if self._admin_client is None and settings.supabase_service_role_key:
            self._init_client()
        return self._admin_client

    @property
    def is_connected(self) -> bool:
        return self.client is not None


supabase_manager = SupabaseManager()
