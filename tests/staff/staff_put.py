"""
Staff API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class StaffPutTest(BaseResourceTest):
    """Load tests for Staff API PUT endpoints"""
    
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
        """Generate a non-empty external_id (required by Staff PUT APIs in this env)."""
        timestamp = int(time.time() * 1000000)  # Microseconds
        instance_id = id(self) % 100000
        random_num = random.randint(10000, 99999)
        return f"{prefix}-{instance_id}-{timestamp}-{random_num}"

    def _get_supervisor_id(self):
        """Return a valid non-empty supervisor_id for employee creation."""
        return random.choice(self._valid_supervisor_id_range)
    
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
    
    @task(3)
    @tag('put', 'staff', 'upsert')
    def upsert_staff(self):
        """Upsert Staff - Create or update staff member with common fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping upsert requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("upsertstaff")
        
        # Staff data with common fields
        # The /staff endpoint requires all fields regardless of role
        role = random.choice(["employee", "supervisor"])
        staff_data = {
            "external_id": self._get_external_id(),
            "first_name": f"Upsert{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "deleted": False,
            "role": role,
            "dashboard": random.choice([True, False]),
            # Employee fields (required for /staff endpoint even when role is supervisor)
            "supervisor_id": self._get_supervisor_id(),
            "self_score": random.choice([True, False]),
            "can_score_peers": random.choice([True, False]),
            "employment": "full_time",
            "personal_goals": random.choice([True, False]),
            # Common fields for both roles
            "can_be_scored": random.choice([True, False]),
            "can_audit": random.choice([True, False]),
            "staff_access": random.choice([True, False]),
            "read_only": random.choice([True, False]),
        }
        
        print(f"Upserting staff with email: {unique_email}")
        try:
            response = self.put_resource("/staff", staff_data, f"Upsert Staff {unique_email}")
            print(f"PUT response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT request failed with exception: {e}")
            return
        
        # Handle 206 (Partial Content) - indicates SCIM-managed staff, not an error
        if response.status_code in [200, 201, 204, 206]:
            if response.status_code == 206:
                print(f"⚠ Partial content (206) - staff may be SCIM-managed: {unique_email}")
            else:
                print(f"✓ Successfully upserted staff: {unique_email}")
            
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
            print(f"✗ Failed to upsert staff {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('put', 'staff', 'employees')
    def upsert_employee(self):
        """Upsert Employee - Create or update employee with employee-specific fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping employee upsert requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("upsertemployee")
        
        # Employee data with employee-specific fields
        employee_data = {
            "external_id": self._get_external_id(),
            "first_name": f"UpsertEmp{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "deleted": False,
            "role": "employee",
            "dashboard": random.choice([True, False]),
            # Employee-specific fields
            "supervisor_id": self._get_supervisor_id(),
            "self_score": random.choice([True, False]),
            "can_score_peers": random.choice([True, False]),
            "employment": "full_time",  # API only accepts "full_time"
            "personal_goals": random.choice([True, False]),
            # Common fields
            "can_be_scored": random.choice([True, False]),
            "can_audit": random.choice([True, False]),
            "staff_access": random.choice([True, False]),
            "read_only": random.choice([True, False]),
        }
        
        print(f"Upserting employee with email: {unique_email}")
        try:
            response = self.put_resource("/staff/employees", employee_data, f"Upsert Employee {unique_email}")
            print(f"PUT employee response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT employee request failed with exception: {e}")
            return
        
        # Handle 206 (Partial Content) - indicates SCIM-managed staff, not an error
        if response.status_code in [200, 201, 204, 206]:
            if response.status_code == 206:
                print(f"⚠ Partial content (206) - employee may be SCIM-managed: {unique_email}")
            else:
                print(f"✓ Successfully upserted employee: {unique_email}")
            
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
            print(f"✗ Failed to upsert employee {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('put', 'staff', 'supervisors')
    def upsert_supervisor(self):
        """Upsert Supervisor - Create or update supervisor with supervisor-specific fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping supervisor upsert requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("upsertsupervisor")
        
        # Supervisor data with supervisor-specific fields
        supervisor_data = {
            "external_id": self._get_external_id(),
            "first_name": f"UpsertSup{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),
            "deleted": False,
            "role": "supervisor",
            "dashboard": random.choice([True, False]),
            # Supervisor-specific fields
            "can_be_scored": random.choice([True, False]),
            "can_audit": random.choice([True, False]),
            "staff_access": random.choice([True, False]),
            "read_only": random.choice([True, False]),
        }
        
        print(f"Upserting supervisor with email: {unique_email}")
        try:
            response = self.put_resource("/staff/supervisors", supervisor_data, f"Upsert Supervisor {unique_email}")
            print(f"PUT supervisor response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT supervisor request failed with exception: {e}")
            return
        
        # Handle 206 (Partial Content) - indicates SCIM-managed staff, not an error
        if response.status_code in [200, 201, 204, 206]:
            if response.status_code == 206:
                print(f"⚠ Partial content (206) - supervisor may be SCIM-managed: {unique_email}")
            else:
                print(f"✓ Successfully upserted supervisor: {unique_email}")
            
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
            print(f"✗ Failed to upsert supervisor {unique_email}: {response.status_code}")
    
    @task(1)
    @tag('put', 'staff', 'validation')
    def test_put_validation(self):
        """Test PUT validation with minimal required data"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping validation requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("minimalstaff")
        
        # Test with minimal required data
        # The /staff endpoint requires all fields even for validation test
        minimal_data = {
            "external_id": self._get_external_id(),
            "first_name": f"Minimal{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(1),  # Required field
            "team_ids": self._get_random_team_ids(1),  # Required field
            "deleted": False,
            "role": "employee",  # Required field
            "dashboard": False,  # Required field
            "supervisor_id": self._get_supervisor_id(),  # Required field
            "self_score": False,  # Required field
            "can_score_peers": False,  # Required field
            "employment": "full_time",  # Required field
            "personal_goals": False,  # Required field
            "can_be_scored": False,  # Required field
            "can_audit": False,  # Required field
            "staff_access": False,  # Required field
            "read_only": False,  # Required field
        }
        
        print(f"Testing PUT validation with minimal data: {unique_email}")
        try:
            response = self.put_resource("/staff", minimal_data, f"Validation Test {unique_email}")
            print(f"PUT validation response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT validation request failed with exception: {e}")
            return
        
        # Handle 206 (Partial Content) - indicates SCIM-managed staff, not an error
        if response.status_code in [200, 201, 204, 206]:
            if response.status_code == 206:
                print(f"⚠ Partial content (206) - staff may be SCIM-managed: {unique_email}")
            else:
                print(f"✓ Validation test succeeded: {response.status_code}")
            
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
                print(f"[WARN] Could not extract staff ID from validation response for {unique_email}")
                print(f"[WARN] Response status: {response.status_code}, content preview: {response.text[:200]}")
        elif response.status_code in [400, 422]:
            print(f"⚠ Validation error (expected): {response.status_code}")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
