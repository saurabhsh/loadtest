"""
Users API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class UsersPostTest(BaseResourceTest):
    """Load tests for Users API POST endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_ids = [100, 101, 102, 103, 104, 105]  # Known user IDs for testing
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Valid group IDs (visible in UI, not soft deleted)
        self._team_ids = [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]  # Valid team IDs (visible in UI, not soft deleted)
        self._created_users = []  # Track users created by this instance
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
    
    def _get_unique_email(self, prefix="testuser"):
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
    
    def _role_supports_can_audit(self, role):
        """Check if a role supports can_audit permission"""
        # can_audit can only be assigned to roles that have both 'score' and 'reports' permissions
        roles_with_audit = [
            "score_reports_analytics",
            "score_calibrate_report_analytics",
            "reports_analytics",
            "score_reports"
        ]
        return role in roles_with_audit
    
    def _delete_user(self, user_id):
        """Delete a user by ID"""
        try:
            print(f"Deleting user {user_id}...")
            response = self.delete_resource(f"/users/{user_id}", f"Delete User {user_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted user {user_id}")
                return True
            else:
                print(f"✗ Failed to delete user {user_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting user {user_id}: {e}")
            return False
    
    def _extract_user_id_from_response(self, response):
        """Extract user ID from response"""
        try:
            if response.content:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Try different possible field names
                    user_id = (response_data.get("user_id") or 
                              response_data.get("id") or
                              (response_data.get("user", {}).get("user_id")) or
                              (response_data.get("user", {}).get("id")))
                    return user_id
        except Exception as e:
            print(f"Could not extract user ID from response: {e}")
        return None
    
    # POST Operations
    @task(3)
    @tag('post', 'users', 'basic')
    def create_user(self):
        """Create a new user with all required fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping basic create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("postuser")
        
        role = "employee"
        user_data = {
            "first_name": f"Post{random.randint(1000, 9999)}",
            "last_name": f"User{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "role": role,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),  # Required: 1-3 random group IDs
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),  # Required: 1-3 random team IDs
            "support_access": random.choice([True, False]),  # Required: boolean
            "billing_access": random.choice([True, False]),  # Required: boolean
            "can_audit": False,  # Required: boolean - employee role doesn't support can_audit
            "read_only": random.choice([True, False]),  # Required: boolean
            "must_change_password": random.choice([True, False]),  # Required: boolean
            "date_format": random.choice(["DD-MM-YYYY", "MM-DD-YYYY"])  # Required: valid enum value
        }
        
        print(f"Creating user with email: {unique_email}")
        try:
            response = self.post_resource("/users", user_data, f"Create User {unique_email}")
            print(f"POST response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created user: {unique_email}")
            
            # Extract user ID and delete immediately
            user_id = self._extract_user_id_from_response(response)
            if user_id:
                self._delete_user(user_id)
            else:
                print(f"⚠ Could not extract user ID from response for {unique_email}")
        else:
            print(f"✗ Failed to create user {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('post', 'users', 'all_fields')
    def create_user_with_all_fields(self):
        """Create a user with all available schema fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping all fields create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("fulluser")
        
        # User data with all available fields
        role = random.choice(["global_admin", "employee", "team_admin", "group_admin"])
        full_data = {
            "first_name": f"FullData{random.randint(1000, 9999)}",
            "last_name": f"User{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "role": role,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),  # Required: 1-3 random group IDs
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),  # Required: 1-3 random team IDs
            "support_access": random.choice([True, False]),  # Required: boolean
            "billing_access": random.choice([True, False]),  # Required: boolean
            "can_audit": self._role_supports_can_audit(role) and random.choice([True, False]),  # Required: boolean - only True if role supports it
            "read_only": random.choice([True, False]),  # Required: boolean
            "must_change_password": random.choice([True, False]),  # Required: boolean
            "date_format": random.choice(["DD-MM-YYYY", "MM-DD-YYYY"])  # Required: valid enum value
        }
        
        print(f"Creating user with all fields: {unique_email}")
        try:
            response = self.post_resource("/users", full_data, f"Create User with All Fields {unique_email}")
            print(f"POST all fields response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST all fields request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created user with all fields: {unique_email}")
            
            # Extract user ID and delete immediately
            user_id = self._extract_user_id_from_response(response)
            if user_id:
                self._delete_user(user_id)
            else:
                print(f"⚠ Could not extract user ID from all fields response for {unique_email}")
        else:
            print(f"✗ Failed to create user with all fields {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('post', 'users', 'password')
    def create_user_password(self):
        """Create user password (only if user doesn't have one)"""
        # Use cached user IDs
        if not self._user_ids:
            print("No user IDs available for password creation testing")
            return
        
        user_id = random.choice(self._user_ids)
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        random_num = random.randint(1000, 9999)  # Random 4-digit number
        password_data = {
            "password": f"TestPass{timestamp}{random_num}"
        }
        
        print(f"Creating password for user ID: {user_id}")
        try:
            # Use response context manager to control success/failure
            # 409 Conflict is expected when password already exists, so mark it as success
            with self.client.post(f"/users/{user_id}/password", json=password_data, catch_response=True) as response:
                if response.status_code in [200, 201]:
                    print(f"✓ Successfully created password for user {user_id}")
                    response.success()
                elif response.status_code == 409:
                    print(f"⚠ Password already exists for user {user_id} (409 Conflict - expected)")
                    response.success()  # Mark 409 as success since it's expected behavior
                else:
                    print(f"✗ Failed to create password for user {user_id}: {response.status_code}")
                    response.failure(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"✗ POST password request failed with exception: {e}")
    
    @task(1)
    @tag('post', 'users', 'minimal')
    def create_user_minimal(self):
        """Create a user with minimal required fields only"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping minimal create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("minimaluser")
        
        # Minimal required data (all boolean fields and date_format are required)
        role = "employee"
        minimal_data = {
            "first_name": f"Minimal{random.randint(1000, 9999)}",
            "last_name": f"User{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "role": role,
            "group_ids": self._get_random_group_ids(1),  # Required: at least 1 group ID
            "team_ids": self._get_random_team_ids(1),  # Required: at least 1 team ID
            "support_access": False,  # Required: boolean
            "billing_access": False,  # Required: boolean
            "can_audit": False,  # Required: boolean - employee role doesn't support can_audit
            "read_only": False,  # Required: boolean
            "must_change_password": False,  # Required: boolean
            "date_format": "MM-DD-YYYY"  # Required: valid enum value (DD-MM-YYYY or MM-DD-YYYY)
        }
        
        print(f"Creating user with minimal data: {unique_email}")
        try:
            response = self.post_resource("/users", minimal_data, f"Create Minimal User {unique_email}")
            print(f"POST minimal response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST minimal request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created minimal user: {unique_email}")
            
            # Extract user ID and delete immediately
            user_id = self._extract_user_id_from_response(response)
            if user_id:
                self._delete_user(user_id)
            else:
                print(f"⚠ Could not extract user ID from minimal response for {unique_email}")
        else:
            print(f"✗ Failed to create minimal user {unique_email}: {response.status_code}")
