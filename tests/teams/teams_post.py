"""
Teams API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class TeamsPostTest(BaseResourceTest):
    """Load tests for Teams API POST endpoints"""
    
    # POST Operations
    @task(2)
    @tag('create', 'teams')
    def create_team(self):
        """Create a new team"""
        team_data = self.get_sample_data("teams")
        team_data["name"] = f"Test Team {self.environment.runner.user_count}"
        self.post_resource("/teams", team_data, "Create Team")
    
    @task(1)
    @tag('create', 'teams')
    def create_team_with_members(self):
        """Create team with initial members"""
        team_data = {
            "name": f"Team with Members {self.environment.runner.user_count}",
            "description": "Team created with initial members",
            "member_ids": [1, 2, 3]
        }
        self.post_resource("/teams", team_data, "Create Team with Members")
