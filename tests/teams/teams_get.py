"""
Teams API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class TeamsGetTest(BaseResourceTest):
    """Load tests for Teams API GET endpoints"""
    
    # GET Operations
    @task(3)
    @tag('read', 'teams')
    def get_teams_list(self):
        """Get all teams - most common operation"""
        self.get_resource("/teams", "Teams List")
    
    @task(2)
    @tag('read', 'teams')
    def get_team_by_id(self):
        """Get specific team by ID"""
        self.get_resource("/teams/1", "Team by ID")
