"""
Users API load tests - DELETE operations only
"""
from locust import HttpUser, task, tag
from config.settings import settings
from auth.token_manager import token_manager


class UsersDeleteTest(HttpUser):
    """Load tests for Users API DELETE endpoints"""
    
    def on_start(self):
        """Called when a user starts. Set up authentication."""
        # Set the client's base URL directly from settings
        self.client.base_url = settings.API_HOST
        
        token = token_manager.get_shared_token(self.client)
        if token:
            self.client.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
        else:
            print("Failed to get authentication token")
    
    def delete_resource(self, endpoint, resource_name="resource"):
        """Generic DELETE request handler"""
        response = self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            print(f"{resource_name} DELETE failed: {response.status_code} - {response.text}")
        return response
    
    # DELETE Operations (commented out as requested)
    # @task(1)
    # @tag('delete', 'users')
    # def delete_user(self):
    #     """Delete a user"""
    #     self.delete_resource("/users/100", "Delete User")
    
    # @task(1)
    # @tag('delete', 'users')
    # def delete_user_by_email(self):
    #     """Delete user by email"""
    #     self.delete_resource("/users/email/test@example.com", "Delete User by Email")
