"""
Teams API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import random


class TeamsGetTest(BaseResourceTest):
    """Load tests for Teams API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._team_ids = []  # Will be populated dynamically
        self._team_ids_cached = False
        # Valid team IDs range: 34-45 (visible in UI, not soft deleted)
        self._valid_team_id_range = list(range(34, 46))
    
    def _cache_team_ids_from_response(self):
        """Cache team IDs from the teams list response"""
        if not self._team_ids_cached:
            try:
                response = self.client.get("/teams")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'teams' in data and isinstance(data['teams'], list):
                        teams = data['teams']
                        cached_ids = []
                        for team in teams:
                            if isinstance(team, dict) and 'team_id' in team:
                                team_id = team['team_id']
                                # Only cache IDs in valid range (34-45)
                                if team_id in self._valid_team_id_range:
                                    cached_ids.append(team_id)
                            elif isinstance(team, dict) and 'id' in team:
                                team_id = team['id']
                                # Only cache IDs in valid range (34-45)
                                if team_id in self._valid_team_id_range:
                                    cached_ids.append(team_id)
                        
                        if cached_ids:
                            self._team_ids = cached_ids
                            print(f"Cached {len(cached_ids)} team IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No team IDs found in valid range, using fallback IDs")
                            self._team_ids = list(range(34, 46))
                    elif isinstance(data, list):
                        # Handle if response is directly a list
                        cached_ids = []
                        for team in data:
                            if isinstance(team, dict) and 'team_id' in team:
                                team_id = team['team_id']
                                if team_id in self._valid_team_id_range:
                                    cached_ids.append(team_id)
                            elif isinstance(team, dict) and 'id' in team:
                                team_id = team['id']
                                if team_id in self._valid_team_id_range:
                                    cached_ids.append(team_id)
                        
                        if cached_ids:
                            self._team_ids = cached_ids
                            print(f"Cached {len(cached_ids)} team IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No team IDs found in valid range, using fallback IDs")
                            self._team_ids = list(range(34, 46))
                    else:
                        print("Unexpected response format, using fallback IDs")
                        self._team_ids = list(range(34, 46))
                else:
                    print(f"Failed to fetch teams list for caching: {response.status_code}")
                    self._team_ids = list(range(34, 46))
            except Exception as e:
                print(f"Error caching team IDs: {e}")
                self._team_ids = list(range(34, 46))
            
            self._team_ids_cached = True
    
    # GET Operations
    @task(3)
    @tag('read', 'teams')
    def get_teams_list(self):
        """Get all teams - most common operation"""
        response = self.get_resource("/teams", "Teams List")
        
        if response.status_code == 200:
            self._cache_team_ids_from_response()
    
    @task(2)
    @tag('read', 'teams')
    def get_team_by_id(self):
        """Get specific team by ID"""
        # Ensure we have cached team IDs
        if not self._team_ids_cached:
            self._cache_team_ids_from_response()
        
        if not self._team_ids:
            print("No team IDs available for testing, skipping individual team request")
            return
        
        team_id = random.choice(self._team_ids)
        self.get_resource(f"/teams/{team_id}", f"Team by ID {team_id}")
