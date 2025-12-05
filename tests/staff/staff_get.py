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
                            print(f"Cached {len(cached_ids)} valid staff IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No valid staff IDs found in API response, using fallback IDs")
                            self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]  # Fallback IDs in valid range
                    elif isinstance(data, list):
                        # Handle if response is directly a list
                        cached_ids = []
                        for member in data:
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
                            print(f"Cached {len(cached_ids)} valid staff IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No valid staff IDs found in API response, using fallback IDs")
                            self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]  # Fallback IDs in valid range
                    else:
                        print("Unexpected response format, using fallback IDs")
                        self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]  # Fallback IDs in valid range
                else:
                    print(f"Failed to fetch staff list for caching: {response.status_code}")
                    self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]  # Fallback IDs in valid range
            except Exception as e:
                print(f"Error caching staff IDs: {e}")
                self._staff_ids = [590, 595, 600, 605, 610, 615, 620, 625, 630, 635]  # Fallback IDs in valid range
            
            self._staff_ids_cached = True
    
    # GET Operations
    @task(4)
    @tag('get', 'staff', 'list')
    def get_staff_list(self):
        """Get Staff List - Primary endpoint for fetching all staff (employees and supervisors)"""
        print("Attempting to get staff list...")
        response = self.get_resource("/staff", "Staff")
        print(f"Staff list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                staff_data = response.json()
                # Handle different response structures
                if isinstance(staff_data, dict) and 'staff' in staff_data:
                    staff_count = len(staff_data['staff']) if isinstance(staff_data['staff'], list) else 'unknown'
                    print(f"Retrieved {staff_count} staff members")
                elif isinstance(staff_data, list):
                    print(f"Retrieved {len(staff_data)} staff members")
                else:
                    print(f"Retrieved staff data")
                
                # Cache staff IDs for subsequent individual staff requests
                self._cache_staff_ids_from_response()
            except Exception as e:
                print(f"Error parsing staff response: {e}")
        else:
            print(f"Staff list failed: {response.text}")
    
    @task(3)
    @tag('get', 'staff', 'individual')
    def get_staff_by_id(self):
        """Get Staff By Id - Fetch a specific staff member by its ID"""
        # Ensure we have cached staff IDs
        if not self._staff_ids_cached:
            self._cache_staff_ids_from_response()
        
        if not self._staff_ids:
            print("No staff IDs available for testing, skipping individual staff request")
            return
        
        staff_id = random.choice(self._staff_ids)
        print(f"Testing with staff ID: {staff_id}")
        response = self.get_resource(f"/staff/{staff_id}", f"Staff {staff_id}")
        print(f"Staff by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                staff_data = response.json()
                print(f"Successfully retrieved staff {staff_id}")
            except Exception as e:
                print(f"Error parsing staff {staff_id} response: {e}")
        else:
            print(f"Staff by ID failed: {response.text}")
    
    @task(2)
    @tag('get', 'staff', 'employees')
    def get_staff_employees(self):
        """Get Staff Employees - Fetch employees only"""
        print("Attempting to get employees list...")
        response = self.get_resource("/staff/employees", "Employees")
        print(f"Employees list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                employees_data = response.json()
                # Handle different response structures
                if isinstance(employees_data, dict) and 'staff' in employees_data:
                    employee_count = len(employees_data['staff']) if isinstance(employees_data['staff'], list) else 'unknown'
                    print(f"Retrieved {employee_count} employees")
                elif isinstance(employees_data, list):
                    print(f"Retrieved {len(employees_data)} employees")
                else:
                    print(f"Retrieved employees data")
            except Exception as e:
                print(f"Error parsing employees response: {e}")
        else:
            print(f"Employees list failed: {response.text}")
    
    @task(1)
    @tag('get', 'staff', 'supervisors')
    def get_staff_supervisors(self):
        """Get Staff Supervisors - Fetch supervisors only"""
        print("Attempting to get supervisors list...")
        response = self.get_resource("/staff/supervisors", "Supervisors")
        print(f"Supervisors list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                supervisors_data = response.json()
                # Handle different response structures
                if isinstance(supervisors_data, dict) and 'staff' in supervisors_data:
                    supervisor_count = len(supervisors_data['staff']) if isinstance(supervisors_data['staff'], list) else 'unknown'
                    print(f"Retrieved {supervisor_count} supervisors")
                elif isinstance(supervisors_data, list):
                    print(f"Retrieved {len(supervisors_data)} supervisors")
                else:
                    print(f"Retrieved supervisors data")
            except Exception as e:
                print(f"Error parsing supervisors response: {e}")
        else:
            print(f"Supervisors list failed: {response.text}")
    
    @task(1)
    @tag('get', 'staff', 'query_params')
    def get_staff_with_query_params(self):
        """Get Staff with query parameters - Test API flexibility"""
        print("Testing staff list with query parameters...")
        
        # Test with common query parameters that might be supported
        query_params = [
            {},  # No params
            {"limit": 10},  # Limit results
            {"offset": 0},  # Pagination
            {"sort": "staff_id"},  # Sorting
            {"role": "employee"},  # Filter by role
            {"email_address": "test@example.com"},  # Filter by email
        ]
        
        for params in query_params:
            try:
                response = self.client.get("/staff", params=params)
                print(f"Staff with params {params}: {response.status_code}")
                
                if response.status_code not in [200, 400, 422]:  # 400/422 might be expected for invalid params
                    print(f"Unexpected status for params {params}: {response.text}")
            except Exception as e:
                print(f"Error testing staff with params {params}: {e}")
