"""
Base test class for all ScoreBuddy API load tests
"""
from locust import HttpUser, task, tag
from config.settings import settings
from auth.token_manager import token_manager


class BaseResourceTest(HttpUser):
    """Base class for all resource tests with common functionality"""
    abstract = True
    host = settings.API_HOST
    
    def on_start(self):
        """Called when a user starts. Set up authentication."""
        # Set timeout for all requests to prevent hanging
        self.client.timeout = 10  # 10 second timeout
        
        token = token_manager.get_shared_token(self.client)
        if token:
            self.client.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"  # Explicitly request JSON responses
            })
        else:
            print("Failed to get authentication token")
    
    def get_resource(self, endpoint, resource_name="resource"):
        """Generic GET request handler"""
        response = self.client.get(endpoint)
        if response.status_code != 200:
            print(f"{resource_name} GET failed: {response.status_code} - {response.text}")
        return response
    
    def post_resource(self, endpoint, data, resource_name="resource"):
        """Generic POST request handler"""
        response = self.client.post(endpoint, json=data)
        if response.status_code not in [200, 201]:
            print(f"{resource_name} POST failed: {response.status_code} - {response.text}")
        return response
    
    def put_resource(self, endpoint, data, resource_name="resource"):
        """Generic PUT request handler"""
        response = self.client.put(endpoint, json=data)
        if response.status_code not in [200, 201, 204]:
            print(f"{resource_name} PUT failed: {response.status_code} - {response.text}")
        return response
    
    def delete_resource(self, endpoint, resource_name="resource"):
        """Generic DELETE request handler"""
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
