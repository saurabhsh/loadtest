"""
Users API load tests - PUT operations only
"""
from locust import HttpUser, task, tag
from config.settings import settings
from auth.token_manager import token_manager


class UsersPutTest(HttpUser):
    """Load tests for Users API PUT endpoints"""
    
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
    
    def put_resource(self, endpoint, data, resource_name="resource"):
        """Generic PUT request handler"""
        response = self.client.put(endpoint, json=data)
        if response.status_code not in [200, 204]:
            print(f"{resource_name} PUT failed: {response.status_code} - {response.text}")
        return response
    
    # PUT Operations
    @task(2)
    @tag('update', 'users')
    def update_user(self):
        """Update user information"""
        user_data = {
            "first_name": f"Updated{self.environment.runner.user_count}",
            "last_name": f"User{self.environment.runner.user_count}",
            "email_address": f"updated{self.environment.runner.user_count}@example.com",
            "role": "employee"  # Adding valid role for PUT operation
        }
        self.put_resource("/users", user_data, "Update User")
    
    @task(1)
    @tag('update', 'users')
    def update_user_password(self):
        """Update user password"""
        import time
        import random
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        random_num = random.randint(1000, 9999)  # Random 4-digit number
        password_data = {
            "password": f"NewPass{self.environment.runner.user_count}{timestamp}{random_num}"
        }
        self.put_resource("/users/100/password", password_data, "Update User Password")
