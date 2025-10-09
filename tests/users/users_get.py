"""
Users API load tests - GET operations only
"""
from locust import HttpUser, task, tag
from config.settings import settings
from auth.token_manager import token_manager


class UsersGetTest(HttpUser):
    """Load tests for Users API GET endpoints"""
    
    host = settings.API_HOST
    
    def on_start(self):
        """Called when a user starts. Set up authentication."""
        token = token_manager.get_shared_token(self.client)
        if token:
            self.client.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
        else:
            print("Failed to get authentication token")
    
    def get_resource(self, endpoint, resource_name="resource"):
        """Generic GET request handler"""
        response = self.client.get(endpoint)
        if response.status_code != 200:
            print(f"{resource_name} GET failed: {response.status_code} - {response.text}")
        return response
    
    # GET Operations
    @task(3)
    @tag('read', 'users')
    def get_users_list(self):
        """Get all users - most common operation"""
        self.get_resource("/users", "Users List")
    
    @task(2)
    @tag('read', 'users')
    def get_user_by_id(self):
        """Get specific user by ID - using a more likely ID"""
        self.get_resource("/users/100", "User by ID")
    
    # Note: GET /users/{user_id}/password returns 405 - method not allowed
    # This endpoint only supports POST/PUT operations
