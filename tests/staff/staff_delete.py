"""
Staff API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class StaffDeleteTest(BaseResourceTest):
    """Load tests for Staff API DELETE endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_start_time = time.time()
        self._test_duration = None  # Will be set from environment
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Valid group IDs (visible in UI, not soft deleted)
        self._team_ids = [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]  # Valid team IDs (visible in UI, not soft deleted)
    
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
    
    def _get_unique_email(self, prefix="deletestaff"):
        """Generate a unique email address"""
        timestamp = int(time.time() * 1000) % 100000
        instance_id = id(self) % 100000
        random_num = random.randint(1000, 9999)
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
    
    def _create_test_staff(self):
        """Create a test staff member for deletion"""
        unique_email = self._get_unique_email()
        
        staff_data = {
            "first_name": f"DeleteTest_{int(time.time() * 1000) % 100000}_{random.randint(1000, 9999)}",
            "last_name": f"Staff{random.randint(1000, 9999)}",
            "email_address": unique_email,
            "group_ids": self._get_random_group_ids(random.randint(1, 2)),
            "team_ids": self._get_random_team_ids(random.randint(1, 2)),
        }
        
        try:
            response = self.post_resource("/staff", staff_data, f"Create Test Staff {unique_email}")
            if response.status_code in [200, 201]:
                # Extract staff ID from response
                if response.content:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        staff_id = (response_data.get("staff_id") or 
                                  response_data.get("id") or
                                  (response_data.get("staff", {}).get("staff_id")) or
                                  (response_data.get("staff", {}).get("id")))
                        if staff_id:
                            print(f"✓ Created test staff {staff_id} for deletion")
                            return staff_id
        except Exception as e:
            print(f"✗ Error creating test staff: {e}")
        
        return None
    
    # DELETE Operations
    @task(3)
    @tag('delete', 'staff', 'test_only')
    def delete_test_staff_only(self):
        """Delete only test staff (safe for production)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test staff first, then delete it
        staff_id = self._create_test_staff()
        if not staff_id:
            print("✗ Could not create test staff for deletion")
            return
        
        # Small delay to ensure staff is created
        time.sleep(0.1)
        
        print(f"Deleting test staff: {staff_id}")
        try:
            response = self.delete_resource(f"/staff/{staff_id}", f"Delete Test Staff {staff_id}")
            print(f"DELETE response received: {response.status_code}")
        except Exception as e:
            print(f"✗ DELETE request failed with exception: {e}")
            return
        
        if response.status_code in [200, 204]:
            print(f"✓ Successfully deleted test staff: {staff_id}")
        else:
            print(f"✗ Failed to delete test staff {staff_id}: {response.status_code}")
    
    @task(2)
    @tag('delete', 'staff', 'create_and_delete')
    def create_and_delete_staff(self):
        """Create a staff member and then delete it immediately"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping create-and-delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test staff first
        staff_id = self._create_test_staff()
        if not staff_id:
            print("✗ Could not create test staff for deletion")
            return
        
        # Small delay to ensure staff is created
        time.sleep(0.1)
        
        # Now delete the staff we just created
        print(f"Deleting newly created staff: {staff_id}")
        try:
            response = self.delete_resource(f"/staff/{staff_id}", f"Delete New Staff {staff_id}")
            print(f"DELETE response received: {response.status_code}")
        except Exception as e:
            print(f"✗ DELETE request failed with exception: {e}")
            return
        
        if response.status_code in [200, 204]:
            print(f"✓ Successfully deleted newly created staff: {staff_id}")
        else:
            print(f"✗ Failed to delete newly created staff {staff_id}: {response.status_code}")
    
    @task(1)
    @tag('delete', 'staff', 'hard_delete')
    def hard_delete_test_staff(self):
        """Hard delete test staff (requires soft delete first)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping hard delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test staff first
        staff_id = self._create_test_staff()
        if not staff_id:
            print("✗ Could not create test staff for hard deletion")
            return
        
        # Small delay to ensure staff is created
        time.sleep(0.1)
        
        # First, soft delete the staff
        print(f"Soft deleting test staff: {staff_id}")
        try:
            soft_delete_response = self.delete_resource(f"/staff/{staff_id}", f"Soft Delete Test Staff {staff_id}")
            print(f"Soft DELETE response received: {soft_delete_response.status_code}")
            
            if soft_delete_response.status_code not in [200, 204]:
                print(f"✗ Failed to soft delete test staff {staff_id}: {soft_delete_response.status_code}")
                return
            
            # Small delay before hard delete
            time.sleep(0.1)
            
            # Now hard delete the staff
            print(f"Hard deleting test staff: {staff_id}")
            hard_delete_response = self.delete_resource(f"/staff/{staff_id}/hard", f"Hard Delete Test Staff {staff_id}")
            print(f"Hard DELETE response received: {hard_delete_response.status_code}")
            
            if hard_delete_response.status_code in [200, 204]:
                print(f"✓ Successfully hard deleted test staff: {staff_id}")
            elif hard_delete_response.status_code == 428:
                print(f"⚠ Hard delete requires soft delete first (428) - this should not happen as we soft deleted first")
            else:
                print(f"✗ Failed to hard delete test staff {staff_id}: {hard_delete_response.status_code}")
        except Exception as e:
            print(f"✗ Hard delete request failed with exception: {e}")
    
    @task(1)
    @tag('delete', 'staff', 'safe_testing')
    def safe_delete_testing(self):
        """Safe DELETE testing with test staff only"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping safe delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create multiple test staff and delete them
        test_staff = []
        for i in range(3):
            staff_id = self._create_test_staff()
            if staff_id:
                test_staff.append(staff_id)
                time.sleep(0.1)  # Small delay between creations
        
        # Delete all test staff
        deleted_count = 0
        for staff_id in test_staff:
            try:
                response = self.delete_resource(f"/staff/{staff_id}", f"Delete Test Staff {staff_id}")
                if response.status_code in [200, 204]:
                    print(f"✓ Successfully deleted test staff: {staff_id}")
                    deleted_count += 1
                else:
                    print(f"✗ Failed to delete test staff {staff_id}: {response.status_code}")
            except Exception as e:
                print(f"✗ Error deleting test staff {staff_id}: {e}")
        
        print(f"Safe delete test completed: {deleted_count}/{len(test_staff)} staff deleted")
