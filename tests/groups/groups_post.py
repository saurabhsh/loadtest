"""
Groups API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class GroupsPostTest(BaseResourceTest):
    """Load tests for Groups API POST endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    
    # POST Operations
    @task(3)
    @tag('post', 'groups', 'basic')
    def create_group(self):
        """Create Group - Basic group creation with minimal required fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping basic create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("BasicGroup")
        
        # Basic group data with minimal required fields
        group_data = {
            "group_name": group_name
        }
        
        print(f"Creating basic group: {group_name}")
        try:
            response = self.post_resource("/groups", group_data, f"Create Group {group_name}")
            print(f"POST response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created group: {group_name}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from response for {group_name}")
        else:
            print(f"✗ Failed to create group {group_name}: {response.status_code}")
    
    @task(2)
    @tag('post', 'groups', 'with_description')
    def create_group_with_description(self):
        """Create Group with Description - Test group creation with description field"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping description create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("DescGroup")
        
        # Group data with description
        group_data = {
            "group_name": group_name,
            "description": f"Group with description: {group_name} - Created for load testing"
        }
        
        print(f"Creating group with description: {group_name}")
        try:
            response = self.post_resource("/groups", group_data, f"Create Group with Description {group_name}")
            print(f"POST description response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST description request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created group with description: {group_name}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from description response for {group_name}")
        else:
            print(f"✗ Failed to create group with description {group_name}: {response.status_code}")
    
    @task(2)
    @tag('post', 'groups', 'all_fields')
    def create_group_with_all_fields(self):
        """Create Group with All Fields - Test group creation with all available fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping all fields create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("FullGroup")
        
        # Group data with all available fields
        group_data = {
            "group_name": group_name,
            "description": f"Complete group with all fields: {group_name}",
            "location": "Test Location, Test City",
            "notes": f"Test notes for {group_name} - created via POST API",
            "deleted": False
        }
        
        print(f"Creating group with all fields: {group_name}")
        try:
            response = self.post_resource("/groups", group_data, f"Create Group with All Fields {group_name}")
            print(f"POST all fields response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST all fields request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created group with all fields: {group_name}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from all fields response for {group_name}")
        else:
            print(f"✗ Failed to create group with all fields {group_name}: {response.status_code}")
    
    @task(1)
    @tag('post', 'groups', 'location_notes')
    def create_group_with_location_and_notes(self):
        """Create Group with Location and Notes - Test group creation focusing on location and notes"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping location/notes create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        group_name = self._get_unique_group_name("LocationGroup")
        
        # Group data with location and notes
        location_data = {
            "group_name": group_name,
            "description": f"Group with location and notes: {group_name}",
            "location": f"Office {random.randint(1, 10)}, Floor {random.randint(1, 5)}, Building {random.randint(1, 3)}",
            "notes": f"Special notes for {group_name} - testing location and notes functionality via POST"
        }
        
        print(f"Creating group with location and notes: {group_name}")
        try:
            response = self.post_resource("/groups", location_data, f"Create Group with Location {group_name}")
            print(f"POST location response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST location request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created group with location and notes: {group_name}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from location response for {group_name}")
        else:
            print(f"✗ Failed to create group with location and notes {group_name}: {response.status_code}")
    
    @task(1)
    @tag('post', 'groups', 'business_scenarios')
    def create_group_business_scenarios(self):
        """Create Group Business Scenarios - Test group creation with realistic business data"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping business scenario create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Business scenario group types
        business_scenarios = [
            {
                "name_prefix": "CustomerService",
                "description": "Customer Service Team",
                "location": "Main Office, Customer Service Floor",
                "notes": "Handles customer inquiries and support tickets"
            },
            {
                "name_prefix": "TechnicalSupport",
                "description": "Technical Support Team", 
                "location": "IT Department, Technical Floor",
                "notes": "Provides technical assistance and troubleshooting"
            },
            {
                "name_prefix": "SalesTeam",
                "description": "Sales Team",
                "location": "Sales Department, Ground Floor",
                "notes": "Manages sales operations and client relationships"
            },
            {
                "name_prefix": "QualityAssurance",
                "description": "Quality Assurance Team",
                "location": "QA Lab, Testing Floor",
                "notes": "Ensures product quality and testing procedures"
            }
        ]
        
        scenario = random.choice(business_scenarios)
        group_name = self._get_unique_group_name(scenario["name_prefix"])
        
        # Group data with business scenario
        business_data = {
            "group_name": group_name,
            "description": scenario["description"],
            "location": scenario["location"],
            "notes": scenario["notes"]
        }
        
        print(f"Creating business scenario group: {group_name}")
        try:
            response = self.post_resource("/groups", business_data, f"Create Business Group {group_name}")
            print(f"POST business scenario response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST business scenario request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created business scenario group: {group_name}")
            
            # Extract group ID and delete immediately
            group_id = self._extract_group_id_from_response(response)
            if group_id:
                self._delete_group(group_id)
            else:
                print(f"⚠ Could not extract group ID from business scenario response for {group_name}")
        else:
            print(f"✗ Failed to create business scenario group {group_name}: {response.status_code}")