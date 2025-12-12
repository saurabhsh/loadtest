"""
Base test class for all ScoreBuddy API load tests
"""
from locust import HttpUser, task, tag
from config.settings import settings
from auth.token_manager import token_manager


class BaseResourceTest(HttpUser):
    """Base class for all resource tests with common functionality"""
    abstract = True
    
    def on_start(self):
        """Called when a user starts. Set up authentication."""
        # Respect --host parameter from Locust command line
        # If --host is provided, self.host is set and self.client.base_url should be set by Locust
        # Only use settings.API_HOST as fallback if no --host was provided
        if hasattr(self, 'host') and self.host:
            # --host parameter was provided, ensure base_url is set from it
            if not self.client.base_url:
                self.client.base_url = self.host
        else:
            # No --host parameter provided, use settings as fallback
            self.client.base_url = settings.API_HOST
        
        self.client.timeout = 10
        
        token = token_manager.get_shared_token(self.client)
        if token:
            self.client.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
        else:
            print("Failed to get authentication token - check CLIENT_ID, CLIENT_SECRET, and API_HOST in .env file")
    
    def _ensure_headers_set(self):
        """Ensure authentication headers are set before making requests"""
        if 'Authorization' not in self.client.headers:
            # Try to get token again
            token = token_manager.get_shared_token(self.client)
            if token:
                self.client.headers.update({
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                })
            else:
                print("⚠ Warning: No authentication token available - requests will fail")
                return False
        return True
    
    def get_resource(self, endpoint, resource_name="resource"):
        """Generic GET request handler"""
        self._ensure_headers_set()
        response = self.client.get(endpoint)
        if response.status_code != 200:
            print(f"{resource_name} GET failed: {response.status_code} - {response.text}")
        return response
    
    def get_resource_with_params(self, endpoint, params, resource_name="resource"):
        """Generic GET request handler with query parameters"""
        if not self._ensure_headers_set():
            return None
        response = self.client.get(endpoint, params=params)
        return response
    
    def post_resource(self, endpoint, data, resource_name="resource"):
        """Generic POST request handler"""
        self._ensure_headers_set()
        response = self.client.post(endpoint, json=data)
        if response.status_code not in [200, 201]:
            print(f"{resource_name} POST failed: {response.status_code} - {response.text}")
        return response
    
    def put_resource(self, endpoint, data, resource_name="resource"):
        """Generic PUT request handler"""
        self._ensure_headers_set()
        response = self.client.put(endpoint, json=data)
        if response.status_code not in [200, 201, 204]:
            print(f"{resource_name} PUT failed: {response.status_code} - {response.text}")
        return response
    
    def delete_resource(self, endpoint, resource_name="resource"):
        """Generic DELETE request handler"""
        self._ensure_headers_set()
        response = self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            print(f"{resource_name} DELETE failed: {response.status_code} - {response.text}")
        return response
    
    def get_sample_data(self, resource_type):
        """Return sample data for POST/PUT requests based on resource type"""
        sample_data = {
            "users": {
                "name": "Test User",
                "email": "test@example.com",
                "role": "user"
            },
            "teams": {
                "name": "Test Team",
                "description": "Test team description"
            },
            "staff": {
                "name": "Test Staff",
                "email": "staff@example.com",
                "position": "Developer"
            },
            "groups": {
                "name": "Test Group",
                "description": "Test group description"
            },
            "integrations": {
                "name": "Test Integration",
                "type": "webhook",
                "url": "https://example.com/webhook"
            }
        }
        return sample_data.get(resource_type, {})
