"""
Groups API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class GroupsDeleteTest(BaseResourceTest):
    """Load tests for Groups API DELETE endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    
    def _create_test_group(self):
        """Create a test group for deletion"""
        group_name = f"DeleteTest_{int(time.time() * 1000) % 100000}_{random.randint(1000, 9999)}"
        
        group_data = {
            "group_name": group_name,
            "description": f"Test group for deletion: {group_name}"
        }
        
        try:
            response = self.post_resource("/groups", group_data, f"Create Test Group {group_name}")
            if response.status_code in [200, 201]:
                # Extract group ID from response
                if response.content:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        group_id = (response_data.get("group_id") or 
                                  response_data.get("id") or
                                  (response_data.get("group", {}).get("group_id")) or
                                  (response_data.get("group", {}).get("id")))
                        if group_id:
                            print(f"✓ Created test group {group_id} for deletion")
                            return group_id
        except Exception as e:
            print(f"✗ Error creating test group: {e}")
        
        return None
    
    # DELETE Operations
    @task(3)
    @tag('delete', 'groups', 'test_only')
    def delete_test_groups_only(self):
        """Delete only test groups (safe for production)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test group first, then delete it
        group_id = self._create_test_group()
        if not group_id:
            print("✗ Could not create test group for deletion")
            return
        
        # Small delay to ensure group is created
        time.sleep(0.1)
        
        print(f"Deleting test group: {group_id}")
        try:
            response = self.delete_resource(f"/groups/{group_id}", f"Delete Test Group {group_id}")
            print(f"DELETE response received: {response.status_code}")
        except Exception as e:
            print(f"✗ DELETE request failed with exception: {e}")
            return
        
        if response.status_code in [200, 204]:
            print(f"✓ Successfully deleted test group: {group_id}")
        else:
            print(f"✗ Failed to delete test group {group_id}: {response.status_code}")
    
    @task(2)
    @tag('delete', 'groups', 'create_and_delete')
    def create_and_delete_group(self):
        """Create a group and then delete it immediately"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping create-and-delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test group first
        group_id = self._create_test_group()
        if not group_id:
            print("✗ Could not create test group for deletion")
            return
        
        # Small delay to ensure group is created
        time.sleep(0.1)
        
        # Now delete the group we just created
        print(f"Deleting newly created group: {group_id}")
        try:
            response = self.delete_resource(f"/groups/{group_id}", f"Delete New Group {group_id}")
            print(f"DELETE response received: {response.status_code}")
        except Exception as e:
            print(f"✗ DELETE request failed with exception: {e}")
            return
        
        if response.status_code in [200, 204]:
            print(f"✓ Successfully deleted newly created group: {group_id}")
        else:
            print(f"✗ Failed to delete newly created group {group_id}: {response.status_code}")
    
    @task(1)
    @tag('delete', 'groups', 'safe_testing')
    def safe_delete_testing(self):
        """Safe DELETE testing with test groups only"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping safe delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create multiple test groups and delete them
        test_groups = []
        for i in range(3):
            group_id = self._create_test_group()
            if group_id:
                test_groups.append(group_id)
                time.sleep(0.1)  # Small delay between creations
        
        # Delete all test groups
        deleted_count = 0
        for group_id in test_groups:
            try:
                response = self.delete_resource(f"/groups/{group_id}", f"Delete Test Group {group_id}")
                if response.status_code in [200, 204]:
                    print(f"✓ Successfully deleted test group: {group_id}")
                    deleted_count += 1
                else:
                    print(f"✗ Failed to delete test group {group_id}: {response.status_code}")
            except Exception as e:
                print(f"✗ Error deleting test group {group_id}: {e}")
        
        print(f"Safe delete test completed: {deleted_count}/{len(test_groups)} groups deleted")
