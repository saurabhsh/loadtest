"""
Teams API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class TeamsDeleteTest(BaseResourceTest):
    """Load tests for Teams API DELETE endpoints"""
    
    # DELETE Operations (commented out as requested)
    # @task(1)
    # @tag('delete', 'teams')
    # def delete_team(self):
    #     """Delete a team"""
    #     self.delete_resource("/teams/1", "Delete Team")
    
    # @task(1)
    # @tag('delete', 'teams')
    # def remove_team_member(self):
    #     """Remove member from team"""
    #     self.delete_resource("/teams/1/members/1", "Remove Team Member")
