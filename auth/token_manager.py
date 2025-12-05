import time
import threading
from config.settings import settings

class TokenManager:
    """Thread-safe token manager for OAuth2 authentication"""
    
    def __init__(self):
        self._shared_token = None
        self._token_expires_at = None
        self._auth_lock = threading.Lock()
        # Track credentials to detect changes
        self._last_client_id = None
        self._last_client_secret = None
        self._last_api_host = None
    
    def get_shared_token(self, client):
        """Get a shared token for all users, authenticate only once"""
        
        # Check if credentials have changed - if so, clear cached token
        current_client_id = settings.CLIENT_ID
        current_client_secret = settings.CLIENT_SECRET
        current_api_host = settings.API_HOST
        
        if (self._last_client_id != current_client_id or 
            self._last_client_secret != current_client_secret or
            self._last_api_host != current_api_host):
            # Credentials changed, clear cached token
            self._shared_token = None
            self._token_expires_at = None
            self._last_client_id = current_client_id
            self._last_client_secret = current_client_secret
            self._last_api_host = current_api_host
        
        # Check if we have a valid token (without lock for performance)
        if self._shared_token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._shared_token
        
        # Use lock to ensure only one authentication happens at a time
        with self._auth_lock:
            # Double-check after acquiring lock (another thread might have authenticated)
            if self._shared_token and self._token_expires_at and time.time() < self._token_expires_at:
                return self._shared_token
            
            # Need to authenticate
            auth_url = f"{settings.API_HOST}{settings.AUTH_ENDPOINT}"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "scope": settings.SCOPE
            }
            auth_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            auth_response = client.post(auth_url, json=auth_data, headers=auth_headers)
            
            if auth_response.status_code == 200:
                token_data = auth_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    self._shared_token = access_token
                    expires_in = token_data.get("expires_in", settings.DEFAULT_TOKEN_EXPIRY)
                    self._token_expires_at = time.time() + expires_in - settings.TOKEN_REFRESH_BUFFER
                    self._last_client_id = settings.CLIENT_ID
                    self._last_client_secret = settings.CLIENT_SECRET
                    self._last_api_host = settings.API_HOST
                    return access_token
                else:
                    print(f"Access token not found in response")
            else:
                print(f"Authentication failed: {auth_response.status_code} - {auth_response.text}")
            
            return None
    
    def clear_token(self):
        """Clear the cached token (useful for testing)"""
        self._shared_token = None
        self._token_expires_at = None

# Global token manager instance
token_manager = TokenManager()
