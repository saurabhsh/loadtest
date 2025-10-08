import time
import threading
from locust import HttpUser, task

# Global token cache - shared across all users
_shared_token = None
_token_expires_at = None
_auth_lock = threading.Lock()  # Lock to prevent concurrent authentication

def get_shared_token(client):
    """Get a shared token for all users, authenticate only once"""
    global _shared_token, _token_expires_at
    
    # Check if we have a valid token (without lock for performance)
    if _shared_token and _token_expires_at and time.time() < _token_expires_at:
        return _shared_token
    
    # Use lock to ensure only one authentication happens at a time
    with _auth_lock:
        # Double-check after acquiring lock (another thread might have authenticated)
        if _shared_token and _token_expires_at and time.time() < _token_expires_at:
            return _shared_token
        
        # Need to authenticate
        print("Authenticating to get shared token...")
        auth_response = client.post("/authorisation/token", json={
            "grant_type": "client_credentials",
            "client_id": "saurabh",
            "client_secret": "356e674dc5f9b4a2f8a535a7d48fae4140bd4a4f79ca6f8afcda29b8d3ece914",
            "scope": "staff:read users:read teams:read groups:read scores:read scorecards:read"
        })
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                _shared_token = access_token
                # Set expiration (default to 1 hour if not provided)
                expires_in = token_data.get("expires_in", 3600)
                _token_expires_at = time.time() + expires_in - 60  # Refresh 1 minute early
                
                print(f"Shared token obtained: {access_token[:20]}... (expires in {expires_in}s)")
                return access_token
            else:
                print(f"Access token not found in response: {token_data}")
        else:
            print(f"Authentication failed: {auth_response.status_code} - {auth_response.text}")
        
        return None

class MyUser(HttpUser):
    host = "https://www.staging.scorebuddy.co.uk/1777161849/api/v1"
    
    def on_start(self):
        """Called when a user starts. Use shared token."""
        token = get_shared_token(self.client)
        if token:
            self.client.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
        else:
            print("Failed to get authentication token")
    
    @task
    def check_api_status(self):
        response = self.client.get("/scorecards/categories")
        if response.status_code != 200:
            print(f"API call failed with status: {response.status_code}")
            print(f"Response: {response.text}")