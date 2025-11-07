"""
Users API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class UsersPutTest(BaseResourceTest):
    """Load tests for Users API PUT endpoints"""
    
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
    
    @task(3)
    @tag('put', 'users', 'upsert')
    def upsert_user(self):
        """Upsert a user (create or update)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping new requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("upsertuser")
        
        role = "employee"
        user_data = {
            "first_name": f"Upsert{random.randint(1000, 9999)}",
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
        
        print(f"Upserting user with email: {unique_email}")
        try:
            response = self.put_resource("/users", user_data, f"Upsert User {unique_email}")
            print(f"PUT response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Successfully upserted user: {unique_email}")
            
            # Extract user ID and delete immediately
            user_id = self._extract_user_id_from_response(response)
            if user_id:
                self._delete_user(user_id)
            else:
                print(f"⚠ Could not extract user ID from response for {unique_email}")
        else:
            print(f"✗ Failed to upsert user {unique_email}: {response.status_code}")
    
    @task(2)
    @tag('put', 'users', 'password')
    def update_user_password(self):
        """Update user password"""
        # Use cached user IDs
        if not self._user_ids:
            print("No user IDs available for password update testing")
            return
        
        user_id = random.choice(self._user_ids)
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        random_num = random.randint(1000, 9999)  # Random 4-digit number
        password_data = {
            "password": f"NewPass{timestamp}{random_num}"
        }
        
        print(f"Updating password for user ID: {user_id}")
        try:
            response = self.put_resource(f"/users/{user_id}/password", password_data, f"Update User Password {user_id}")
            print(f"PUT password response received: {response.status_code}")
            
            if response.status_code in [200, 201, 204]:
                print(f"✓ Successfully updated password for user {user_id}")
            else:
                print(f"✗ Failed to update password for user {user_id}: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT password request failed with exception: {e}")
    
    @task(1)
    @tag('put', 'users', 'validation')
    def test_put_validation(self):
        """Test PUT validation with minimal data"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping validation requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("minimaluser")
        
        # Test with minimal required data (all boolean fields and date_format are required)
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
        
        print(f"Testing PUT validation with minimal data: {unique_email}")
        try:
            response = self.put_resource("/users", minimal_data, f"Validation Test {unique_email}")
            print(f"PUT validation response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT validation request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Validation test succeeded: {response.status_code}")
            
            # Extract user ID and delete immediately
            user_id = self._extract_user_id_from_response(response)
            if user_id:
                self._delete_user(user_id)
            else:
                print(f"⚠ Could not extract user ID from validation response for {unique_email}")
        elif response.status_code in [400, 422]:
            print(f"⚠ Validation error (expected): {response.status_code}")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    
    @task(1)
    @tag('put', 'users', 'full_data')
    def test_put_with_all_fields(self):
        """Test PUT with all available user fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping full data requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_email = self._get_unique_email("fulldatauser")
        
        # Test with all available fields
        role = "employee"
        full_data = {
            "first_name": f"FullData{random.randint(1000, 9999)}",
            "last_name": f"User{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "role": role,
            "group_ids": self._get_random_group_ids(random.randint(1, 3)),  # Required: 1-3 random group IDs from valid groups
            "team_ids": self._get_random_team_ids(random.randint(1, 3)),  # Required: 1-3 random team IDs from valid teams
            "support_access": random.choice([True, False]),  # Required: boolean
            "billing_access": random.choice([True, False]),  # Required: boolean
            "can_audit": False,  # Required: boolean - employee role doesn't support can_audit
            "read_only": random.choice([True, False]),  # Required: boolean
            "must_change_password": random.choice([True, False]),  # Required: boolean
            "date_format": random.choice(["DD-MM-YYYY", "MM-DD-YYYY"])  # Required: valid enum value (DD-MM-YYYY or MM-DD-YYYY)
        }
        
        print(f"Testing PUT with all fields: {unique_email}")
        try:
            response = self.put_resource("/users", full_data, f"Full Data Test {unique_email}")
            print(f"PUT full data response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT full data request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Full data test succeeded: {response.status_code}")
            
            # Extract user ID and delete immediately
            user_id = self._extract_user_id_from_response(response)
            if user_id:
                self._delete_user(user_id)
            else:
                print(f"⚠ Could not extract user ID from full data response for {unique_email}")
        else:
            print(f"✗ Full data test failed: {response.status_code}")
