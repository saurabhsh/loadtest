"""
Teams API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class TeamsDeleteTest(BaseResourceTest):
    """Load tests for Teams API DELETE endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_teams = []  # Track teams created by this instance
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Valid group IDs (visible in UI, not soft deleted)
        # Protected team IDs range: 34-45 (pre-existing teams, never delete)
        self._protected_team_ids = list(range(34, 46))
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
    
    def _get_unique_team_name(self, prefix="DeleteTest"):
        """Generate a unique team name"""
        timestamp = int(time.time() * 1000) % 100000
        random_num = random.randint(1000, 9999)
        return f"{prefix}_{timestamp}_{random_num}"
    
    def _get_random_group_id(self):
        """Get a random valid group ID"""
        return random.choice(self._group_ids)
    
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
    
    def _create_test_team(self):
        """Create a test team for deletion"""
        team_name = self._get_unique_team_name("DeleteTest")
        
        team_data = {
            "team_name": team_name,
            "group_id": self._get_random_group_id(),
            "deleted": False
        }
        
        try:
            response = self.post_resource("/teams", team_data, f"Create Test Team {team_name}")
            if response.status_code in [200, 201]:
                team_id = self._extract_team_id_from_response(response)
                if team_id:
                    # Safety check: ensure we never track protected team IDs
                    if team_id not in self._protected_team_ids:
                        self._created_teams.append(team_id)
                        print(f"✓ Created test team {team_id} for deletion")
                        return team_id
                    else:
                        print(f"⚠ Warning: Created team {team_id} is in protected range, not tracking")
                        return None
        except Exception as e:
            print(f"✗ Error creating test team: {e}")
        
        return None
    
    def _delete_team(self, team_id):
        """Delete a team by ID with safety check"""
        # Safety check: never delete protected team IDs (34-45)
        if team_id in self._protected_team_ids:
            print(f"⚠ Safety check: Skipping deletion of protected team ID {team_id} (pre-existing team)")
            return False
        
        try:
            print(f"Deleting team {team_id}...")
            response = self.delete_resource(f"/teams/{team_id}", f"Delete Team {team_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted team {team_id}")
                # Remove from tracking list if present
                if team_id in self._created_teams:
                    self._created_teams.remove(team_id)
                return True
            else:
                print(f"✗ Failed to delete team {team_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting team {team_id}: {e}")
            return False
    
    # DELETE Operations
    @task(3)
    @tag('delete', 'teams', 'test_only')
    def delete_test_teams_only(self):
        """Delete only test teams (safe for production)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test team first, then delete it
        team_id = self._create_test_team()
        if not team_id:
            print("✗ Could not create test team for deletion")
            return
        
        # Small delay to ensure team is created
        time.sleep(0.1)
        
        print(f"Deleting test team: {team_id}")
        try:
            response = self.delete_resource(f"/teams/{team_id}", f"Delete Test Team {team_id}")
            print(f"DELETE response received: {response.status_code}")
        except Exception as e:
            print(f"✗ DELETE request failed with exception: {e}")
            return
        
        if response.status_code in [200, 204]:
            print(f"✓ Successfully deleted test team: {team_id}")
        else:
            print(f"✗ Failed to delete test team {team_id}: {response.status_code}")
    
    @task(2)
    @tag('delete', 'teams', 'create_and_delete')
    def create_and_delete_team(self):
        """Create a team and then delete it immediately"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping create-and-delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create a test team first
        team_id = self._create_test_team()
        if not team_id:
            print("✗ Could not create test team for deletion")
            return
        
        # Small delay to ensure team is created
        time.sleep(0.1)
        
        # Now delete the team we just created
        print(f"Deleting newly created team: {team_id}")
        try:
            response = self.delete_resource(f"/teams/{team_id}", f"Delete New Team {team_id}")
            print(f"DELETE response received: {response.status_code}")
        except Exception as e:
            print(f"✗ DELETE request failed with exception: {e}")
            return
        
        if response.status_code in [200, 204]:
            print(f"✓ Successfully deleted newly created team: {team_id}")
        else:
            print(f"✗ Failed to delete newly created team {team_id}: {response.status_code}")
    
    @task(1)
    @tag('delete', 'teams', 'safe_testing')
    def safe_delete_testing(self):
        """Safe DELETE testing with test teams only"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping safe delete requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Create multiple test teams and delete them
        test_teams = []
        for i in range(3):
            team_id = self._create_test_team()
            if team_id:
                test_teams.append(team_id)
                time.sleep(0.1)  # Small delay between creations
        
        # Delete all test teams
        deleted_count = 0
        for team_id in test_teams:
            try:
                response = self.delete_resource(f"/teams/{team_id}", f"Delete Test Team {team_id}")
                if response.status_code in [200, 204]:
                    print(f"✓ Successfully deleted test team: {team_id}")
                    deleted_count += 1
                else:
                    print(f"✗ Failed to delete test team {team_id}: {response.status_code}")
            except Exception as e:
                print(f"✗ Error deleting test team {team_id}: {e}")
        
        print(f"Safe delete test completed: {deleted_count}/{len(test_teams)} teams deleted")
