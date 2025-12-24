"""
Teams API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class TeamsPostTest(BaseResourceTest):
    """Load tests for Teams API POST endpoints"""
    
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
    
    # POST Operations
    @task(2)
    @tag('create', 'teams')
    def create_team(self):
        """Create a new team"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping basic create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        team_name = self._get_unique_team_name("TestTeam")
        team_data = {
            "team_name": team_name,
            "group_id": self._get_random_group_id(),
            "deleted": False
        }
        
        print(f"Creating basic team: {team_name}")
        try:
            response = self.post_resource("/teams", team_data, f"Create Team {team_name}")
            print(f"POST response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created team: {team_name}")
            
            # Extract team ID and delete immediately
            team_id = self._extract_team_id_from_response(response)
            if team_id:
                self._delete_team(team_id)
            else:
                print(f"⚠ Could not extract team ID from response for {team_name}")
        else:
            print(f"✗ Failed to create team {team_name}: {response.status_code}")
    
    @task(1)
    @tag('create', 'teams')
    def create_team_with_members(self):
        """Create team with initial members"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"[INFO] Stopping members create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        team_name = self._get_unique_team_name("TeamWithMembers")
        team_data = {
            "team_name": team_name,
            "group_id": self._get_random_group_id(),
            "deleted": False,
            "description": "Team created with initial members",
            "member_ids": [1, 2, 3]
        }
        
        print(f"Creating team with members: {team_name}")
        try:
            response = self.post_resource("/teams", team_data, f"Create Team with Members {team_name}")
            print(f"POST members response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST members request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created team with members: {team_name}")
            
            # Extract team ID and delete immediately
            team_id = self._extract_team_id_from_response(response)
            if team_id:
                self._delete_team(team_id)
            else:
                print(f"⚠ Could not extract team ID from members response for {team_name}")
        else:
            print(f"✗ Failed to create team with members {team_name}: {response.status_code}")
