"""
Groups API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class GroupsGetTest(BaseResourceTest):
    """Load tests for Groups API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Known group IDs
        self._group_ids_cached = False
    
    def _cache_group_ids_from_response(self):
        """Cache group IDs from the groups list response"""
        if not self._group_ids_cached:
            try:
                response = self.client.get("/groups")
                if response.status_code == 200:
                    groups_data = response.json()
                    if isinstance(groups_data, list):
                        # Extract IDs from the response
                        cached_ids = []
                        for group in groups_data:
                            if isinstance(group, dict) and 'id' in group:
                                cached_ids.append(group['id'])
                            elif isinstance(group, dict) and 'group_id' in group:
                                cached_ids.append(group['group_id'])
                        
                        if cached_ids:
                            self._group_ids = cached_ids
                            print(f"Cached {len(cached_ids)} group IDs from API response: {cached_ids}")
                        else:
                            print("No group IDs found in API response, using hardcoded IDs")
                    else:
                        print("Unexpected response format, using hardcoded IDs")
                else:
                    print(f"Failed to fetch groups list for caching: {response.status_code}")
            except Exception as e:
                print(f"Error caching group IDs: {e}")
            
            self._group_ids_cached = True
    
    # GET Operations
    @task(4)
    @tag('get', 'groups', 'list')
    def get_groups_list(self):
        """Get Groups List - Primary endpoint for fetching all groups"""
        print("Attempting to get groups list...")
        response = self.get_resource("/groups", "Groups")
        print(f"Groups list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                groups_data = response.json()
                print(f"Retrieved {len(groups_data) if isinstance(groups_data, list) else 'unknown'} groups")
                
                # Cache group IDs for subsequent individual group requests
                self._cache_group_ids_from_response()
            except Exception as e:
                print(f"Error parsing groups response: {e}")
        else:
            print(f"Groups list failed: {response.text}")
    
    @task(3)
    @tag('get', 'groups', 'individual')
    def get_group_by_id(self):
        """Get Group By Id - Fetch a specific group by its ID"""
        import random
        
        # Ensure we have cached group IDs
        if not self._group_ids_cached:
            self._cache_group_ids_from_response()
        
        group_id = random.choice(self._group_ids)
        print(f"Testing with group ID: {group_id}")
        response = self.get_resource(f"/groups/{group_id}", f"Group {group_id}")
        print(f"Group by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                group_data = response.json()
                print(f"Successfully retrieved group {group_id}")
            except Exception as e:
                print(f"Error parsing group {group_id} response: {e}")
        else:
            print(f"Group by ID failed: {response.text}")
    
    @task(1)
    @tag('get', 'groups', 'validation')
    def get_groups_with_query_params(self):
        """Get Groups with query parameters - Test API flexibility"""
        print("Testing groups list with query parameters...")
        
        # Test with common query parameters that might be supported
        query_params = [
            {},  # No params
            {"limit": 10},  # Limit results
            {"offset": 0},  # Pagination
            {"sort": "id"},  # Sorting
        ]
        
        for params in query_params:
            try:
                response = self.client.get("/groups", params=params)
                print(f"Groups with params {params}: {response.status_code}")
                
                if response.status_code not in [200, 400, 422]:  # 400/422 might be expected for invalid params
                    print(f"Unexpected status for params {params}: {response.text}")
            except Exception as e:
                print(f"Error testing groups with params {params}: {e}")