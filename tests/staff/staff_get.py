"""
Staff API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class StaffGetTest(BaseResourceTest):
    """Load tests for Staff API GET endpoints"""
    
    # GET Operations
    @task(3)
    @tag('get', 'staff')
    def get_staff_list(self):
        """Get Staff List"""
        # TODO: Implement get_staff_list
        pass
    
    @task(2)
    @tag('get', 'staff')
    def get_staff_by_id(self):
        """Get Staff By Id"""
        # TODO: Implement get_staff_by_id
        pass
    
    @task(1)
    @tag('get', 'staff')
    def get_staff_employees(self):
        """Get Staff Employees"""
        # TODO: Implement get_staff_employees
        pass
    
