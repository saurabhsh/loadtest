"""
Staff API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import random


class StaffGetTest(BaseResourceTest):
    """Load tests for Staff API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._staff_ids = []  # Will be populated dynamically
        self._staff_ids_cached = False
        # Valid staff IDs range: 590-638 (IDs before 590 are soft-deleted)
        self._valid_staff_id_range = list(range(590, 639))
    
    def _cache_staff_ids_from_response(self):
        """Cache staff IDs from the staff list response"""
        if not self._staff_ids_cached:
            try:
                response = self.client.get("/staff")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'staff' in data and isinstance(data['staff'], list):
                        staff = data['staff']
                        cached_ids = []
                        for member in staff:
                            if isinstance(member, dict) and 'staff_id' in member:
                                staff_id = member['staff_id']
                                # Only cache IDs in valid range (590-638)
                                if staff_id in self._valid_staff_id_range:
                                    cached_ids.append(staff_id)
                            elif isinstance(member, dict) and 'id' in member:
                                staff_id = member['id']
                                # Only cache IDs in valid range (590-638)
                                if staff_id in self._valid_staff_id_range:
                                    cached_ids.append(staff_id)
                        
                        if cached_ids:
                            self._staff_ids = cached_ids
                        else:
                            self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]
                    elif isinstance(data, list):
                        cached_ids = []
                        for member in data:
                            if isinstance(member, dict) and 'staff_id' in member:
                                staff_id = member['staff_id']
                                if staff_id in self._valid_staff_id_range:
                                    cached_ids.append(staff_id)
                            elif isinstance(member, dict) and 'id' in member:
                                staff_id = member['id']
                                if staff_id in self._valid_staff_id_range:
                                    cached_ids.append(staff_id)
                        
                        if cached_ids:
                            self._staff_ids = cached_ids
                        else:
                            self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]
                    else:
                        self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]
                else:
                    self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]
            except Exception:
                self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]
            
            self._staff_ids_cached = True
    
    # GET Operations
    @task(4)
    @tag('get', 'staff', 'list')
    def get_staff_list(self):
        """Get Staff List - Primary endpoint for fetching all staff (employees and supervisors)"""
        response = self.get_resource("/staff", "Staff")
        
        if response.status_code == 200:
            self._cache_staff_ids_from_response()
    
    @task(3)
    @tag('get', 'staff', 'individual')
    def get_staff_by_id(self):
        """Get Staff By Id - Fetch a specific staff member by its ID"""
        if not self._staff_ids_cached:
            self._cache_staff_ids_from_response()
        
        if not self._staff_ids:
            return
        
        staff_id = random.choice(self._staff_ids)
        self.get_resource(f"/staff/{staff_id}", f"Staff {staff_id}")
    
    @task(2)
    @tag('get', 'staff', 'employees')
    def get_staff_employees(self):
        """Get Staff Employees - Fetch employees only"""
        self.get_resource("/staff/employees", "Employees")
    
    @task(1)
    @tag('get', 'staff', 'supervisors')
    def get_staff_supervisors(self):
        """Get Staff Supervisors - Fetch supervisors only"""
        self.get_resource("/staff/supervisors", "Supervisors")
    
    @task(1)
    @tag('get', 'staff', 'query_params')
    def get_staff_with_query_params(self):
        """Get Staff with query parameters - Test API flexibility"""
        query_params = [
            {},
            {"limit": 10},
            {"offset": 0},
            {"sort": "staff_id"},
            {"role": "employee"},
            {"email_address": "test@example.com"},
        ]
        
        for params in query_params:
            self.get_resource_with_params("/staff", params, f"Staff with params {params}")
