"""
Staff API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class StaffDeleteTest(BaseResourceTest):
    """Load tests for Staff API DELETE endpoints"""
    
    # DELETE Operations
    @task(3)
    @tag('delete', 'staff')
    def delete_staff(self):
        """Delete Staff"""
        # TODO: Implement delete_staff
        pass
    
    @task(2)
    @tag('delete', 'staff')
    def delete_staff_by_email(self):
        """Delete Staff By Email"""
        # TODO: Implement delete_staff_by_email
        pass
    
