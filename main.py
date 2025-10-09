from locust import HttpUser, task
from config.settings import settings
from auth.token_manager import token_manager

class LoadTestUser(HttpUser):
    """Main Locust user class for load testing"""
    
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
    
    @task(3)  # Weight 3 - most frequent
    def get_scorecard_categories(self):
        """Get scorecard categories - most common operation"""
        response = self.client.get("/scorecards/categories")
        if response.status_code != 200:
            print(f"Categories API failed: {response.status_code}")
    
    @task(2)  # Weight 2 - frequent
    def get_users(self):
        """Get users list"""
        response = self.client.get("/users")
        if response.status_code != 200:
            print(f"Users API failed: {response.status_code}")
    
    @task(2)  # Weight 2 - frequent
    def get_teams(self):
        """Get teams list"""
        response = self.client.get("/teams")
        if response.status_code != 200:
            print(f"Teams API failed: {response.status_code}")
    
    @task(1)  # Weight 1 - less frequent
    def get_staff(self):
        """Get staff list"""
        response = self.client.get("/staff")
        if response.status_code != 200:
            print(f"Staff API failed: {response.status_code}")
    
    @task(1)  # Weight 1 - less frequent
    def get_groups(self):
        """Get groups list"""
        response = self.client.get("/groups")
        if response.status_code != 200:
            print(f"Groups API failed: {response.status_code}")
    
    @task(1)  # Weight 1 - less frequent
    def get_scores(self):
        """Get scores data"""
        response = self.client.get("/scores")
        if response.status_code != 200:
            print(f"Scores API failed: {response.status_code}")
    
    @task(1)  # Weight 1 - less frequent
    def get_scorecards(self):
        """Get scorecards list"""
        response = self.client.get("/scorecards")
        if response.status_code != 200:
            print(f"Scorecards API failed: {response.status_code}")
