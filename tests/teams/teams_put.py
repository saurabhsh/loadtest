"""
Teams API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class TeamsPutTest(BaseResourceTest):
    """Load tests for Teams API PUT endpoints"""
    
    # PUT Operations
    @task(1)
    @tag('update', 'teams')
    def update_team(self):
        """Update team information (bulk operation)"""
        team_data = {
            "name": f"Updated Team {self.environment.runner.user_count}",
            "description": "Updated team description"
        }
        self.put_resource("/teams", team_data, "Update Team")
