"""
Groups API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class GroupsDeleteTest(BaseResourceTest):
    """Load tests for Groups API DELETE endpoints"""
    
    # DELETE Operations
    @task(3)
    @tag('delete', 'groups')
    def delete_group(self):
        """Delete Group"""
        # TODO: Implement delete_group
        pass
    
    @task(2)
    @tag('delete', 'groups')
    def remove_group_member(self):
        """Remove Group Member"""
        # TODO: Implement remove_group_member
        pass
    
