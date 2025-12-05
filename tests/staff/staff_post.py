"""
Staff API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class StaffPostTest(BaseResourceTest):
    """Load tests for Staff API POST endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._staff_ids = []  # Will be populated dynamically for supervisor_id references
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Valid group IDs (visible in UI, not soft deleted)
        self._team_ids = [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]  # Valid team IDs (visible in UI, not soft deleted)
        self._created_staff = []  # Track staff created by this instance
        self._test_start_time = time.time()
        self._test_duration = None  # Will be set from environment
    
    def _get_test_duration(self):
        """Get test duration from environment"""
        if self._test_duration is None:
            # Try to get duration from environment
            if hasattr(self.environment, 'parsed_options') and hasattr(self.environment.parsed_options, 'run_time'):
                self._test_duration = self.environment.parsed_options.run_time
            else:
                # Default to 30 seconds if not specified
                self._test_duration = 30
        return self._test_duration
    
    def _should_stop_creating_requests(self):
        """Check if we should stop creating new requests (5 seconds before end)"""
        elapsed_time = time.time() - self._test_start_time
        test_duration = self._get_test_duration()
        remaining_time = test_duration - elapsed_time
        
        # Stop creating new requests 5 seconds before test ends
        return remaining_time <= 5
    
    def _get_unique_email(self, prefix="teststaff"):
        """Generate a unique email address"""
        # Use full timestamp without modulo to avoid collisions
        timestamp = int(time.time() * 1000000)  # Microseconds for better precision
        # Include instance ID for uniqueness across concurrent Locust users
        instance_id = id(self) % 100000  # Unique per instance, modulo for shorter email
        # Larger random number range for better uniqueness
        random_num = random.randint(10000, 99999)
        return f"{prefix}_{instance_id}_{timestamp}_{random_num}@example.com"
    
    def _get_random_group_ids(self, count=1):
        """Get random group IDs from valid groups (32-37)"""
        if count >= len(self._group_ids):
            return self._group_ids.copy()
        return random.sample(self._group_ids, count)
    
    def _get_random_team_ids(self, count=1):
        """Get random team IDs from valid teams (34-45)"""
        if count >= len(self._team_ids):
            return self._team_ids.copy()
        return random.sample(self._team_ids, count)
    
    def _delete_staff(self, staff_id):
        """Delete a staff member by ID"""
        try:
            print(f"Deleting staff {staff_id}...")
            response = self.delete_resource(f"/staff/{staff_id}", f"Delete Staff {staff_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted staff {staff_id}")
                return True
            else:
                print(f"✗ Failed to delete staff {staff_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting staff {staff_id}: {e}")
            return False
    
    def _extract_staff_id_from_response(self, response):
        """Extract staff ID from response"""
        try:
            if response.content:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Try different possible field names
                    staff_id = (response_data.get("staff_id") or 
                              response_data.get("id") or
                              (response_data.get("staff", {}).get("staff_id")) or
                              (response_data.get("staff", {}).get("id")))
                    return staff_id
        except Exception as e:
            print(f"Could not extract staff ID from response: {e}")
        return None
    
    # POST Operations
    @task(3)
    @tag('post', 'staff', 'basic')
    def create_staff(self):
        """Create Staff - Basic staff creation with required fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping basic create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("poststaff")
        
        # Basic staff data with required fields
        staff_data = {
            "first_name": f"Post{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),  # Optional: 1-3 random group IDs
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),  # Optional: 1-3 random team IDs
        }
        
        print(f"Creating basic staff with email: {unique_email}")
        try:
            response = self.post_resource("/staff", staff_data, f"Create Staff {unique_email}")
            print(f"POST response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created staff: {unique_email}")
            
            # Extract staff ID and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                self._delete_staff(staff_id)
            else:
                print(f"⚠ Could not extract staff ID from response for {unique_email}")
        else:
            print(f"✗ Failed to create staff {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('post', 'staff', 'employees')
    def create_staff_employee(self):
        """Create Employee - Create staff member with employee-specific fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping employee create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("postemployee")
        
        # Employee data with employee-specific fields
        employee_data = {
            "first_name": f"Employee{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "role": "employee",
            "dashboard": random.choice([True, False]),
            # Employee-specific fields
            "supervisor_id": None,  # Optional: can be set to valid staff_id if available
            "self_score": random.choice([True, False]),
            "can_score_peers": random.choice([True, False]),
            "employment": random.choice(["full_time", "part_time", "contract", "temporary"]),
            "personal_goals": random.choice([True, False]),
        }
        
        print(f"Creating employee with email: {unique_email}")
        try:
            response = self.post_resource("/staff/employees", employee_data, f"Create Employee {unique_email}")
            print(f"POST employee response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST employee request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created employee: {unique_email}")
            
            # Extract staff ID and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                self._delete_staff(staff_id)
            else:
                print(f"⚠ Could not extract staff ID from employee response for {unique_email}")
        else:
            print(f"✗ Failed to create employee {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('post', 'staff', 'supervisors')
    def create_staff_supervisor(self):
        """Create Supervisor - Create staff member with supervisor-specific fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping supervisor create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("postsupervisor")
        
        # Supervisor data with supervisor-specific fields
        supervisor_data = {
            "first_name": f"Supervisor{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "role": "supervisor",
            "dashboard": random.choice([True, False]),
            # Supervisor-specific fields
            "can_be_scored": random.choice([True, False]),
            "can_audit": random.choice([True, False]),
            "staff_access": random.choice([True, False]),
            "read_only": random.choice([True, False]),
        }
        
        print(f"Creating supervisor with email: {unique_email}")
        try:
            response = self.post_resource("/staff/supervisors", supervisor_data, f"Create Supervisor {unique_email}")
            print(f"POST supervisor response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST supervisor request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created supervisor: {unique_email}")
            
            # Extract staff ID and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                self._delete_staff(staff_id)
            else:
                print(f"⚠ Could not extract staff ID from supervisor response for {unique_email}")
        else:
            print(f"✗ Failed to create supervisor {unique_email}: {response.status_code}")
    
    @task(1)
    @tag('post', 'staff', 'all_fields')
    def create_staff_with_all_fields(self):
        """Create Staff with All Fields - Test staff creation with all available fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping all fields create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("fullstaff")
        
        # Randomly choose between employee and supervisor for all fields test
        staff_type = random.choice(["employee", "supervisor"])
        
        # Common fields for all staff
        all_fields_data = {
            "first_name": f"FullData{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "external_id": f"EXT{random.randint(10000, 99999)}",  # Optional: external ID from HRMS
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "notes": f"Test notes for {unique_email} - created via POST API",
            "role": staff_type,
            "dashboard": random.choice([True, False]),
            "deleted": False,
        }
        
        # Add type-specific fields
        if staff_type == "employee":
            all_fields_data.update({
                "supervisor_id": None,  # Optional: can reference valid staff_id
                "self_score": random.choice([True, False]),
                "can_score_peers": random.choice([True, False]),
                "employment": random.choice(["full_time", "part_time", "contract", "temporary"]),
                "personal_goals": random.choice([True, False]),
            })
            endpoint = "/staff/employees"
        else:  # supervisor
            all_fields_data.update({
                "can_be_scored": random.choice([True, False]),
                "can_audit": random.choice([True, False]),
                "staff_access": random.choice([True, False]),
                "read_only": random.choice([True, False]),
            })
            endpoint = "/staff/supervisors"
        
        print(f"Creating {staff_type} with all fields: {unique_email}")
        try:
            response = self.post_resource(endpoint, all_fields_data, f"Create {staff_type.capitalize()} with All Fields {unique_email}")
            print(f"POST all fields response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST all fields request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created {staff_type} with all fields: {unique_email}")
            
            # Extract staff ID and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                self._delete_staff(staff_id)
            else:
                print(f"⚠ Could not extract staff ID from all fields response for {unique_email}")
        else:
            print(f"✗ Failed to create {staff_type} with all fields {unique_email}: {response.status_code}")
