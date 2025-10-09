"""
Staff API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class StaffPostTest(BaseResourceTest):
    """Load tests for Staff API POST endpoints"""
    
    # POST Operations
    @task(3)
    @tag('post', 'staff')
    def create_staff(self):
        """Create Staff"""
        # TODO: Implement create_staff
        pass
    
    @task(2)
    @tag('post', 'staff')
    def create_staff_with_position(self):
        """Create Staff With Position"""
        # TODO: Implement create_staff_with_position
        pass
    
