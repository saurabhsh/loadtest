"""
Users API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import random


class UsersGetTest(BaseResourceTest):
    """Load tests for Users API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_ids = []  # Will be populated dynamically
        self._user_ids_cached = False
    
    def _cache_user_ids_from_response(self):
        """Cache user IDs from the users list response"""
        if not self._user_ids_cached:
            try:
                response = self.client.get("/users")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'users' in data and isinstance(data['users'], list):
                        users = data['users']
                        cached_ids = []
                        for user in users:
                            if isinstance(user, dict) and 'user_id' in user:
                                cached_ids.append(user['user_id'])
                            elif isinstance(user, dict) and 'id' in user:
                                cached_ids.append(user['id'])
                        
                        if cached_ids:
                            self._user_ids = cached_ids
                            print(f"Cached {len(cached_ids)} user IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No user IDs found in API response, using fallback IDs")
                            self._user_ids = [100, 101, 102, 103, 104, 105]  # Fallback IDs
                    elif isinstance(data, list):
                        # Handle if response is directly a list
                        cached_ids = []
                        for user in data:
                            if isinstance(user, dict) and 'user_id' in user:
                                cached_ids.append(user['user_id'])
                            elif isinstance(user, dict) and 'id' in user:
                                cached_ids.append(user['id'])
                        
                        if cached_ids:
                            self._user_ids = cached_ids
                            print(f"Cached {len(cached_ids)} user IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No user IDs found in API response, using fallback IDs")
                            self._user_ids = [100, 101, 102, 103, 104, 105]  # Fallback IDs
                    else:
                        print("Unexpected response format, using fallback IDs")
                        self._user_ids = [100, 101, 102, 103, 104, 105]  # Fallback IDs
                else:
                    print(f"Failed to fetch users list for caching: {response.status_code}")
                    self._user_ids = [100, 101, 102, 103, 104, 105]  # Fallback IDs
            except Exception as e:
                print(f"Error caching user IDs: {e}")
                self._user_ids = [100, 101, 102, 103, 104, 105]  # Fallback IDs
            
            self._user_ids_cached = True
    
    # GET Operations
    @task(4)
    @tag('get', 'users', 'list')
    def get_users_list(self):
        """Get Users List - Primary endpoint for fetching all users"""
        print("Attempting to get users list...")
        response = self.get_resource("/users", "Users")
        print(f"Users list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                users_data = response.json()
                # Handle different response structures
                if isinstance(users_data, dict) and 'users' in users_data:
                    user_count = len(users_data['users']) if isinstance(users_data['users'], list) else 'unknown'
                    print(f"Retrieved {user_count} users")
                elif isinstance(users_data, list):
                    print(f"Retrieved {len(users_data)} users")
                else:
                    print(f"Retrieved users data")
                
                # Cache user IDs for subsequent individual user requests
                self._cache_user_ids_from_response()
            except Exception as e:
                print(f"Error parsing users response: {e}")
        else:
            print(f"Users list failed: {response.text}")
    
    @task(3)
    @tag('get', 'users', 'individual')
    def get_user_by_id(self):
        """Get User By Id - Fetch a specific user by its ID"""
        # Ensure we have cached user IDs
        if not self._user_ids_cached:
            self._cache_user_ids_from_response()
        
        if not self._user_ids:
            print("No user IDs available for testing, skipping individual user request")
            return
        
        user_id = random.choice(self._user_ids)
        print(f"Testing with user ID: {user_id}")
        response = self.get_resource(f"/users/{user_id}", f"User {user_id}")
        print(f"User by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                user_data = response.json()
                print(f"Successfully retrieved user {user_id}")
            except Exception as e:
                print(f"Error parsing user {user_id} response: {e}")
        else:
            print(f"User by ID failed: {response.text}")
    
    @task(1)
    @tag('get', 'users', 'query_params')
    def get_users_with_query_params(self):
        """Get Users with query parameters - Test API flexibility"""
        print("Testing users list with query parameters...")
        
        # Test with common query parameters that might be supported
        query_params = [
            {},  # No params
            {"limit": 10},  # Limit results
            {"offset": 0},  # Pagination
            {"sort": "user_id"},  # Sorting
            {"role": "admin"},  # Filter by role
            {"email_address": "test@example.com"},  # Filter by email
        ]
        
        for params in query_params:
            try:
                response = self.get_resource_with_params("/users", params, f"Users with params {params}")
                if response:
                    print(f"Users with params {params}: {response.status_code}")
                    
                    if response.status_code not in [200, 400, 422]:  # 400/422 might be expected for invalid params
                        print(f"Unexpected status for params {params}: {response.text}")
            except Exception as e:
                print(f"Error testing users with params {params}: {e}")
    
    # Note: GET /users/{user_id}/password returns 405 - method not allowed
    # This endpoint only supports POST/PUT operations
