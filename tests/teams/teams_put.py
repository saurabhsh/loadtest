"""
Teams API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class TeamsPutTest(BaseResourceTest):
    """Load tests for Teams API PUT endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_teams = []  # Track teams created by this instance
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Valid group IDs (visible in UI, not soft deleted)
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
    
    def _get_unique_team_name(self, prefix="TestTeam"):
        """Generate a unique team name"""
        timestamp = int(time.time() * 1000) % 100000
        random_num = random.randint(1000, 9999)
        return f"{prefix}_{timestamp}_{random_num}"
    
    def _get_random_group_id(self):
        """Get a random valid group ID"""
        return random.choice(self._group_ids)
    
    def _delete_team(self, team_id):
        """Delete a team by ID"""
        try:
            print(f"Deleting team {team_id}...")
            response = self.delete_resource(f"/teams/{team_id}", f"Delete Team {team_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted team {team_id}")
                return True
            else:
                print(f"✗ Failed to delete team {team_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting team {team_id}: {e}")
            return False
    
    def _extract_team_id_from_response(self, response):
        """Extract team ID from response"""
        try:
            if response.content:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Try different possible field names
                    team_id = (response_data.get("team_id") or 
                              response_data.get("id") or
                              (response_data.get("team", {}).get("team_id")) or
                              (response_data.get("team", {}).get("id")))
                    return team_id
        except Exception as e:
            print(f"Could not extract team ID from response: {e}")
        return None
    
    # PUT Operations
    @task(3)
    @tag('put', 'teams', 'upsert')
    def upsert_team(self):
        """Upsert a team (create or update)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping new requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        team_name = self._get_unique_team_name("UpsertTeam")
        
        # Team data with required fields based on actual API schema
        # Required fields: team_name, group_id, deleted
        team_data = {
            "team_name": team_name,
            "group_id": self._get_random_group_id(),
            "deleted": False
        }
        
        print(f"Upserting team with name: {team_name}")
        try:
            response = self.put_resource("/teams", team_data, f"Upsert Team {team_name}")
            print(f"PUT response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Successfully upserted team: {team_name}")
            
            # Extract team ID and delete immediately
            team_id = self._extract_team_id_from_response(response)
            if team_id:
                self._delete_team(team_id)
            else:
                print(f"⚠ Could not extract team ID from response for {team_name}")
        else:
            print(f"✗ Failed to upsert team {team_name}: {response.status_code}")
    
    @task(1)
    @tag('put', 'teams', 'validation')
    def test_put_validation(self):
        """Test PUT validation with minimal data"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping validation requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        team_name = self._get_unique_team_name("MinimalTeam")
        
        # Test with minimal required data
        minimal_data = {
            "team_name": team_name,
            "group_id": self._get_random_group_id(),
            "deleted": False
        }
        
        print(f"Testing PUT validation with minimal data: {team_name}")
        try:
            response = self.put_resource("/teams", minimal_data, f"Validation Test {team_name}")
            print(f"PUT validation response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT validation request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Validation test succeeded: {response.status_code}")
            
            # Extract team ID and delete immediately
            team_id = self._extract_team_id_from_response(response)
            if team_id:
                self._delete_team(team_id)
            else:
                print(f"⚠ Could not extract team ID from validation response for {team_name}")
        elif response.status_code in [400, 422]:
            print(f"⚠ Validation error (expected): {response.status_code}")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    
    @task(1)
    @tag('put', 'teams', 'full_data')
    def test_put_with_all_fields(self):
        """Test PUT with all available team fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping full data requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        team_name = self._get_unique_team_name("FullDataTeam")
        
        # Test with all available fields
        full_data = {
            "team_name": team_name,
            "group_id": self._get_random_group_id(),
            "deleted": False,
            "description": f"Complete team with all fields: {team_name}. Created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        print(f"Testing PUT with all fields: {team_name}")
        try:
            response = self.put_resource("/teams", full_data, f"Full Data Test {team_name}")
            print(f"PUT full data response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT full data request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Full data test succeeded: {response.status_code}")
            
            # Extract team ID and delete immediately
            team_id = self._extract_team_id_from_response(response)
            if team_id:
                self._delete_team(team_id)
            else:
                print(f"⚠ Could not extract team ID from full data response for {team_name}")
        else:
            print(f"✗ Full data test failed: {response.status_code}")
