"""
Groups API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class GroupsPostTest(BaseResourceTest):
    """Load tests for Groups API POST endpoints"""
    
    # POST Operations
    @task(3)
    @tag('post', 'groups')
    def create_group(self):
        """Create Group"""
        # TODO: Implement create_group
        pass
    
    @task(2)
    @tag('post', 'groups')
    def create_group_with_members(self):
        """Create Group With Members"""
        # TODO: Implement create_group_with_members
        pass
    
