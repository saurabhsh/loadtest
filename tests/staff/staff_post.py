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
        # Known-good staff IDs range (IDs before 590 are soft-deleted in this env)
        self._valid_supervisor_id_range = list(range(590, 639))
        self._created_staff = []  # Track staff created by this instance
        self._test_start_time = time.time()
        self._test_duration = None  # Will be set from environment
        self._stop_messages_printed = set()
    
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

    def _get_external_id(self, prefix="UX"):
        """Generate a non-empty external_id (required by Staff POST APIs in this env)."""
        timestamp = int(time.time() * 1000000)  # Microseconds
        instance_id = id(self) % 100000
        random_num = random.randint(10000, 99999)
        return f"{prefix}-{instance_id}-{timestamp}-{random_num}"

    def _get_supervisor_id(self):
        """Return a valid non-empty supervisor_id for employee creation."""
        return random.choice(self._valid_supervisor_id_range)

    def _log_stop_once(self, key: str, message: str):
        """Avoid spamming stop logs when remaining_time <= 5s."""
        if key in self._stop_messages_printed:
            return
        self._stop_messages_printed.add(key)
        print(message)
    
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
    
    def on_stop(self):
        """Called when a user stops. Clean up any remaining created staff."""
        print(f"\n[CLEANUP] on_stop() called. Tracking {len(self._created_staff)} staff IDs: {self._created_staff}")
        
        if not self._created_staff:
            print("[CLEANUP] No staff to clean up.")
            return
        
        print(f"[CLEANUP] Starting cleanup of {len(self._created_staff)} remaining staff...")
        deleted_count = 0
        failed_count = 0
        
        # Create a copy of the list to avoid modification during iteration
        staff_to_delete = list(self._created_staff)
        
        for staff_id in staff_to_delete:
            print(f"[CLEANUP] Attempting to delete staff {staff_id}...")
            if self._delete_staff(staff_id):
                deleted_count += 1
            else:
                failed_count += 1
        
        print(f"[CLEANUP] Cleanup completed: {deleted_count} deleted, {failed_count} failed")
        if self._created_staff:
            print(f"[CLEANUP] WARNING: {len(self._created_staff)} staff IDs still in tracking list: {self._created_staff}")
    
    def _delete_staff(self, staff_id):
        """Delete a staff member by ID"""
        try:
            print(f"[DELETE] Attempting to delete staff {staff_id}...")
            response = self.delete_resource(f"/staff/{staff_id}", f"Delete Staff {staff_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted staff {staff_id} (status: {response.status_code})")
                # Remove from tracking list if deletion succeeds
                if staff_id in self._created_staff:
                    self._created_staff.remove(staff_id)
                    print(f"[TRACK] Removed staff_id {staff_id} from tracking list. Remaining: {len(self._created_staff)}")
                return True
            else:
                print(f"✗ Failed to delete staff {staff_id}: status {response.status_code}, response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"✗ Error deleting staff {staff_id}: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False
    
    def _extract_staff_id_from_response(self, response):
        """Extract staff ID from response"""
        try:
            if response.content:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Try different possible field names and nested structures
                    # The API returns different keys based on endpoint:
                    # - /staff returns {'staff_member': {'staff_id': ...}}
                    # - /staff/supervisors returns {'supervisor': {'staff_id': ...}}
                    # - /staff/employees returns {'employee': {'staff_id': ...}}
                    staff_id = (response_data.get("staff_id") or 
                              response_data.get("id") or
                              (response_data.get("staff", {}).get("staff_id")) or
                              (response_data.get("staff", {}).get("id")) or
                              (response_data.get("staff_member", {}).get("staff_id")) or
                              (response_data.get("staff_member", {}).get("id")) or
                              (response_data.get("supervisor", {}).get("staff_id")) or
                              (response_data.get("supervisor", {}).get("id")) or
                              (response_data.get("employee", {}).get("staff_id")) or
                              (response_data.get("employee", {}).get("id")))
                    if staff_id:
                        print(f"[DEBUG] Extracted staff_id: {staff_id} from response")
                        return staff_id
                    else:
                        # Log the full response structure for debugging
                        print(f"[WARN] Could not extract staff_id. Response keys: {list(response_data.keys())}")
                        print(f"[WARN] Full response data: {response_data}")
                else:
                    print(f"[WARN] Response is not a dict, type: {type(response_data)}, value: {response_data}")
        except Exception as e:
            print(f"[ERROR] Could not extract staff ID from response: {e}")
            print(f"[ERROR] Response status: {response.status_code}, content: {response.text[:500]}")
        return None
    
    # POST Operations
    @task(3)
    @tag('post', 'staff', 'basic')
    def create_staff(self):
        """Create Staff - Basic staff creation with required fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            self._log_stop_once(
                "basic",
                f"[STOP] Stopping basic create requests - {elapsed:.1f}s elapsed, stopping 5s before end",
            )
            return
        
        unique_email = self._get_unique_email("poststaff")
        
        # Basic staff data with required fields.
        # In this environment, the /staff POST schema is effectively the "full staff" schema
        # (external_id, deleted, supervisor_id, employment, etc.).
        staff_data = {
            "external_id": self._get_external_id(),
            "first_name": f"Post{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),  # Optional: 1-3 random group IDs
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),  # Optional: 1-3 random team IDs
            "deleted": False,
            # Fields commonly required by the API (mirrors Postman "basic staff" example)
            "notes": f"Staff created via load test ({unique_email})",
            "role": "employee",
            "dashboard": random.choice([True, False]),
            "supervisor_id": self._get_supervisor_id(),
            "self_score": random.choice([True, False]),
            "can_score_peers": random.choice([True, False]),
            "employment": "full_time",
            "personal_goals": random.choice([True, False]),
            "can_be_scored": random.choice([True, False]),
            "can_audit": random.choice([True, False]),
            "staff_access": random.choice([True, False]),
            "read_only": random.choice([True, False]),
        }
        
        print(f"Creating basic staff with email: {unique_email}")
        try:
            response = self.post_resource("/staff", staff_data, f"Create Staff {unique_email}")
            print(f"POST response received: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] POST request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"[OK] Successfully created staff: {unique_email}")
            
            # Extract staff ID, track it, and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                # Track staff ID for cleanup (even if immediate deletion fails)
                if staff_id not in self._created_staff:
                    self._created_staff.append(staff_id)
                    print(f"[TRACK] Added staff_id {staff_id} to tracking list. Total tracked: {len(self._created_staff)}")
                # Attempt immediate deletion
                self._delete_staff(staff_id)
            else:
                print(f"[WARN] Could not extract staff ID from response for {unique_email}")
                print(f"[WARN] Response status: {response.status_code}, content preview: {response.text[:200]}")
        else:
            print(f"[FAIL] Failed to create staff {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('post', 'staff', 'employees')
    def create_staff_employee(self):
        """Create Employee - Create staff member with employee-specific fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            self._log_stop_once(
                "employee",
                f"[STOP] Stopping employee create requests - {elapsed:.1f}s elapsed, stopping 5s before end",
            )
            return
        
        unique_email = self._get_unique_email("postemployee")
        
        # Employee data with employee-specific fields
        employee_data = {
            "external_id": self._get_external_id(),
            "first_name": f"Employee{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "role": "employee",
            "dashboard": random.choice([True, False]),
            "deleted": False,
            # Employee-specific fields
            "supervisor_id": self._get_supervisor_id(),
            "self_score": random.choice([True, False]),
            "can_score_peers": random.choice([True, False]),
            "employment": "full_time",
            "personal_goals": random.choice([True, False]),
        }
        
        print(f"Creating employee with email: {unique_email}")
        try:
            response = self.post_resource("/staff/employees", employee_data, f"Create Employee {unique_email}")
            print(f"POST employee response received: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] POST employee request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"[OK] Successfully created employee: {unique_email}")
            
            # Extract staff ID, track it, and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                # Track staff ID for cleanup (even if immediate deletion fails)
                if staff_id not in self._created_staff:
                    self._created_staff.append(staff_id)
                    print(f"[TRACK] Added staff_id {staff_id} to tracking list. Total tracked: {len(self._created_staff)}")
                # Attempt immediate deletion
                self._delete_staff(staff_id)
            else:
                print(f"[WARN] Could not extract staff ID from employee response for {unique_email}")
                print(f"[WARN] Response status: {response.status_code}, content preview: {response.text[:200]}")
        else:
            print(f"[FAIL] Failed to create employee {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('post', 'staff', 'supervisors')
    def create_staff_supervisor(self):
        """Create Supervisor - Create staff member with supervisor-specific fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            self._log_stop_once(
                "supervisor",
                f"[STOP] Stopping supervisor create requests - {elapsed:.1f}s elapsed, stopping 5s before end",
            )
            return
        
        unique_email = self._get_unique_email("postsupervisor")
        
        # Supervisor data with supervisor-specific fields
        supervisor_data = {
            "external_id": self._get_external_id(),
            "first_name": f"Supervisor{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "role": "supervisor",
            "dashboard": random.choice([True, False]),
            "deleted": False,
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
            print(f"[FAIL] POST supervisor request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"[OK] Successfully created supervisor: {unique_email}")
            
            # Extract staff ID, track it, and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                # Track staff ID for cleanup (even if immediate deletion fails)
                if staff_id not in self._created_staff:
                    self._created_staff.append(staff_id)
                    print(f"[TRACK] Added staff_id {staff_id} to tracking list. Total tracked: {len(self._created_staff)}")
                # Attempt immediate deletion
                self._delete_staff(staff_id)
            else:
                print(f"[WARN] Could not extract staff ID from supervisor response for {unique_email}")
                print(f"[WARN] Response status: {response.status_code}, content preview: {response.text[:200]}")
        else:
            print(f"[FAIL] Failed to create supervisor {unique_email}: {response.status_code}")
    
    @task(1)
    @tag('post', 'staff', 'all_fields')
    def create_staff_with_all_fields(self):
        """Create Staff with All Fields - Test staff creation with all available fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            self._log_stop_once(
                "all_fields",
                f"[STOP] Stopping all fields create requests - {elapsed:.1f}s elapsed, stopping 5s before end",
            )
            return
        
        unique_email = self._get_unique_email("fullstaff")
        
        # Randomly choose between employee and supervisor for all fields test
        staff_type = random.choice(["employee", "supervisor"])
        
        # Common fields for all staff
        all_fields_data = {
            "first_name": f"FullData{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "external_id": self._get_external_id("EXT"),  # Required in this env
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
                "supervisor_id": self._get_supervisor_id(),
                "self_score": random.choice([True, False]),
                "can_score_peers": random.choice([True, False]),
                "employment": "full_time",
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
            print(f"[FAIL] POST all fields request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"[OK] Successfully created {staff_type} with all fields: {unique_email}")
            
            # Extract staff ID, track it, and delete immediately
            staff_id = self._extract_staff_id_from_response(response)
            if staff_id:
                # Track staff ID for cleanup (even if immediate deletion fails)
                if staff_id not in self._created_staff:
                    self._created_staff.append(staff_id)
                    print(f"[TRACK] Added staff_id {staff_id} to tracking list. Total tracked: {len(self._created_staff)}")
                # Attempt immediate deletion
                self._delete_staff(staff_id)
            else:
                print(f"[WARN] Could not extract staff ID from all fields response for {unique_email}")
                print(f"[WARN] Response status: {response.status_code}, content preview: {response.text[:200]}")
        else:
            print(f"[FAIL] Failed to create {staff_type} with all fields {unique_email}: {response.status_code}")
