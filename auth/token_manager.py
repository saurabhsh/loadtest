import time
import threading
from config.settings import settings

class TokenManager:
    """Thread-safe token manager for OAuth2 authentication"""
    
    def __init__(self):
        self._shared_token = None
        self._token_expires_at = None
        self._auth_lock = threading.Lock()
    
    def get_shared_token(self, client):
        """Get a shared token for all users, authenticate only once"""
        
        # Check if we have a valid token (without lock for performance)
        if self._shared_token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._shared_token
        
        # Use lock to ensure only one authentication happens at a time
        with self._auth_lock:
            # Double-check after acquiring lock (another thread might have authenticated)
            if self._shared_token and self._token_expires_at and time.time() < self._token_expires_at:
                return self._shared_token
            
            # Need to authenticate
            print("Authenticating to get shared token...")
            auth_response = client.post(settings.AUTH_ENDPOINT, json={
                "grant_type": "client_credentials",
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "scope": settings.SCOPE
            })
            
            if auth_response.status_code == 200:
                token_data = auth_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    self._shared_token = access_token
                    # Set expiration (default to 1 hour if not provided)
                    expires_in = token_data.get("expires_in", settings.DEFAULT_TOKEN_EXPIRY)
                    self._token_expires_at = time.time() + expires_in - settings.TOKEN_REFRESH_BUFFER
                    
                    print(f"Shared token obtained: {access_token[:20]}... (expires in {expires_in}s)")
                    return access_token
                else:
                    print(f"Access token not found in response: {token_data}")
            else:
                print(f"Authentication failed: {auth_response.status_code} - {auth_response.text}")
            
            return None
    
    def clear_token(self):
        """Clear the cached token (useful for testing)"""
        self._shared_token = None
        self._token_expires_at = None

# Global token manager instance
token_manager = TokenManager()
