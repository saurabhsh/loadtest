"""
Users API load tests - POST operations only
"""
from locust import HttpUser, task, tag
from config.settings import settings
from auth.token_manager import token_manager


class UsersPostTest(HttpUser):
    """Load tests for Users API POST endpoints"""
    
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
    
    def post_resource(self, endpoint, data, resource_name="resource"):
        """Generic POST request handler"""
        response = self.client.post(endpoint, json=data)
        if response.status_code not in [200, 201]:
            print(f"{resource_name} POST failed: {response.status_code} - {response.text}")
        return response
    
    # POST Operations
    @task(2)
    @tag('create', 'users')
    def create_user(self):
        """Create a new user"""
        user_data = {
            "first_name": f"Test{self.environment.runner.user_count}",
            "last_name": f"User{self.environment.runner.user_count}",
            "email_address": f"test{self.environment.runner.user_count}@example.com"
        }
        self.post_resource("/users", user_data, "Create User")
    
    @task(1)
    @tag('create', 'users')
    def create_user_password(self):
        """Create user password"""
        import time
        import random
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        random_num = random.randint(1000, 9999)  # Random 4-digit number
        password_data = {
            "password": f"TestPass{self.environment.runner.user_count}{timestamp}{random_num}"
        }
        self.post_resource("/users/100/password", password_data, "Create User Password")
