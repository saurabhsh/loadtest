"""
Groups API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class GroupsGetTest(BaseResourceTest):
    """Load tests for Groups API GET endpoints"""
    
    # GET Operations
    @task(3)
    @tag('get', 'groups')
    def get_groups_list(self):
        """Get Groups List"""
        # TODO: Implement get_groups_list
        pass
    
    @task(2)
    @tag('get', 'groups')
    def get_group_by_id(self):
        """Get Group By Id"""
        # TODO: Implement get_group_by_id
        pass
    
