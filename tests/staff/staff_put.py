"""
Staff API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class StaffPutTest(BaseResourceTest):
    """Load tests for Staff API PUT endpoints"""
    
    # PUT Operations
    @task(3)
    @tag('put', 'staff')
    def update_staff(self):
        """Update Staff"""
        # TODO: Implement update_staff
        pass
    
    @task(2)
    @tag('put', 'staff')
    def update_staff_position(self):
        """Update Staff Position"""
        # TODO: Implement update_staff_position
        pass
    
