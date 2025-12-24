"""
Groups API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class GroupsPutTest(BaseResourceTest):
    """Load tests for Groups API PUT endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group_ids = [36, 37]  # Known group IDs for testing
        self._created_groups = []  # Track groups created by this instance
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
    
    def _get_unique_group_name(self, prefix="TestGroup"):
        """Generate a unique group name"""
        timestamp = int(time.time() * 1000) % 100000
        random_num = random.randint(1000, 9999)
        return f"{prefix}_{timestamp}_{random_num}"
    
    def _delete_group(self, group_id):
        """Delete a group by ID"""
        try:
            print(f"Deleting group {group_id}...")
            response = self.delete_resource(f"/groups/{group_id}", f"Delete Group {group_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted group {group_id}")
                return True
            else:
                print(f"✗ Failed to delete group {group_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting group {group_id}: {e}")
            return False
    
    def _extract_group_id_from_response(self, response):
        """Extract group ID from response"""
        try:
            if response.content:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Try different possible field names
                    group_id = (response_data.get("group_id") or 
                              response_data.get("id") or
                              (response_data.get("group", {}).get("group_id")) or
                              (response_data.get("group", {}).get("id")))
                    return group_id
        except Exception as e:
            print(f"Could not extract group ID from response: {e}")
        return None
    
    @task(3)
    @tag('put', 'groups', 'upsert')
    def upsert_group(self):
        """Upsert a group (create or update)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping new requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("UpsertGroup")
        
        group_data = {
            "group_name": group_name,
            "description": f"Upserted group: {group_name}"
        }
        
        print(f"Upserting group with name: {group_name}")
        try:
            response = self.put_resource("/groups", group_data, f"Upsert Group {group_name}")
            print(f"PUT response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Successfully upserted group: {group_name}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from response for {group_name}")
        else:
            print(f"✗ Failed to upsert group {group_name}: {response.status_code}")
    
    @task(1)
    @tag('put', 'groups', 'validation')
    def test_put_validation(self):
        """Test PUT validation with minimal data"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping validation requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("MinimalGroup")
        
        # Test with minimal required data
        minimal_data = {
            "group_name": group_name
        }
        
        print(f"Testing PUT validation with minimal data: {group_name}")
        try:
            response = self.put_resource("/groups", minimal_data, f"Validation Test {group_name}")
            print(f"PUT validation response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT validation request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Validation test succeeded: {response.status_code}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from validation response for {group_name}")
        elif response.status_code in [400, 422]:
            print(f"⚠ Validation error (expected): {response.status_code}")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    
    @task(1)
    @tag('put', 'groups', 'full_data')
    def test_put_with_all_fields(self):
        """Test PUT with all available group fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping full data requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("FullDataGroup")
        
        # Test with all available fields
        full_data = {
            "group_name": group_name,
            "description": f"Complete group with all fields: {group_name}",
            "location": "Test Location, Test City",
            "notes": f"Test notes for {group_name} - created via API",
            "deleted": False
        }
        
        print(f"Testing PUT with all fields: {group_name}")
        try:
            response = self.put_resource("/groups", full_data, f"Full Data Test {group_name}")
            print(f"PUT full data response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT full data request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Full data test succeeded: {response.status_code}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from full data response for {group_name}")
        else:
            print(f"✗ Full data test failed: {response.status_code}")
    
    @task(1)
    @tag('put', 'groups', 'location_notes')
    def test_put_with_location_and_notes(self):
        """Test PUT with location and notes fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping location/notes requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("LocationGroup")
        
        # Test with location and notes
        location_data = {
            "group_name": group_name,
            "description": f"Group with location and notes: {group_name}",
            "location": f"Office {random.randint(1, 10)}, Floor {random.randint(1, 5)}",
            "notes": f"Special notes for {group_name} - testing location functionality"
        }
        
        print(f"Testing PUT with location and notes: {group_name}")
        try:
            response = self.put_resource("/groups", location_data, f"Location Test {group_name}")
            print(f"PUT location response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT location request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Location test succeeded: {response.status_code}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from location response for {group_name}")
        else:
            print(f"✗ Location test failed: {response.status_code}")