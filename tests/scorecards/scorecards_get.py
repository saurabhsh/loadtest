"""
Scorecards API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class ScorecardsGetTest(BaseResourceTest):
    """Load tests for Scorecards API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scorecard_ids = []  # Will be populated dynamically
        self._category_ids = []   # Will be populated dynamically
        self._scorecard_ids_cached = False
        self._category_ids_cached = False
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
    
    def _cache_scorecard_ids_from_response(self):
        """Cache scorecard IDs from the scorecards list response"""
        if not self._scorecard_ids_cached:
            try:
                # Use a higher limit to get more scorecards including the 70-89 range
                response = self.client.get("/scorecards?limit=100")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'scorecard' in data and isinstance(data['scorecard'], list):
                        scorecards = data['scorecard']
                        cached_ids = []
                        for scorecard in scorecards:
                            if isinstance(scorecard, dict) and 'scorecard_id' in scorecard:
                                cached_ids.append(scorecard['scorecard_id'])
                        
                        if cached_ids:
                            self._scorecard_ids = cached_ids
                            print(f"Cached {len(cached_ids)} scorecard IDs from API response: {cached_ids[:5]}...")
                            # Check if we got the UI range IDs
                            ui_range_ids = [id for id in cached_ids if 70 <= id <= 89]
                            if ui_range_ids:
                                print(f"Found UI range IDs (70-89): {ui_range_ids}")
                        else:
                            print("No scorecard IDs found in API response, using comprehensive fallback IDs")
                            self._scorecard_ids = [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]  # UI range IDs
                    else:
                        print("Unexpected response format, using comprehensive fallback IDs")
                        self._scorecard_ids = [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]  # UI range IDs
                else:
                    print(f"Failed to fetch scorecards list for caching: {response.status_code}")
                    self._scorecard_ids = [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]  # UI range IDs
            except Exception as e:
                print(f"Error caching scorecard IDs: {e}")
                self._scorecard_ids = [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]  # UI range IDs
            
            self._scorecard_ids_cached = True
    
    def _cache_category_ids_from_response(self):
        """Cache category IDs from the categories response"""
        if not self._category_ids_cached:
            try:
                response = self.client.get("/scorecards/categories")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'categories' in data and isinstance(data['categories'], list):
                        categories = data['categories']
                        cached_ids = []
                        for category in categories:
                            if isinstance(category, dict) and 'category_id' in category:
                                cached_ids.append(category['category_id'])
                        
                        if cached_ids:
                            self._category_ids = cached_ids
                            print(f"Cached {len(cached_ids)} category IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No category IDs found in API response, using real fallback IDs")
                            self._category_ids = [5, 8, 27, 44, 45, 46]  # Real IDs from system
                    else:
                        print("Unexpected categories response format, using real fallback IDs")
                        self._category_ids = [5, 8, 27, 44, 45, 46]  # Real IDs from system
                else:
                    print(f"Failed to fetch categories list for caching: {response.status_code}")
                    self._category_ids = [5, 8, 27, 44, 45, 46]  # Real IDs from system
            except Exception as e:
                print(f"Error caching category IDs: {e}")
                self._category_ids = [5, 8, 27, 44, 45, 46]  # Real IDs from system
            
            self._category_ids_cached = True
    
    # GET Operations
    @task(3)
    @tag('get', 'scorecards', 'list')
    def get_scorecards_list(self):
        """Get Scorecards List - Primary endpoint for fetching all scorecards"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping scorecards list requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        print("Attempting to get scorecards list...")
        response = self.get_resource("/scorecards", "Scorecards")
        print(f"Scorecards list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                scorecards_data = response.json()
                print(f"Retrieved {len(scorecards_data) if isinstance(scorecards_data, list) else 'unknown'} scorecards")
                
                # Cache scorecard IDs for subsequent individual scorecard requests
                self._cache_scorecard_ids_from_response()
            except Exception as e:
                print(f"Error parsing scorecards response: {e}")
        else:
            print(f"Scorecards list failed: {response.text}")
    
    @task(2)
    @tag('get', 'scorecards', 'individual')
    def get_scorecard_by_id(self):
        """Get Scorecard By Id - Fetch a specific scorecard by its ID"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping scorecard by ID requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Ensure we have cached scorecard IDs
        if not self._scorecard_ids_cached:
            self._cache_scorecard_ids_from_response()
        
        if not self._scorecard_ids:
            print("No scorecard IDs available for testing")
            return
        
        scorecard_id = random.choice(self._scorecard_ids)
        print(f"Testing with scorecard ID: {scorecard_id}")
        response = self.get_resource(f"/scorecards/{scorecard_id}", f"Scorecard {scorecard_id}")
        print(f"Scorecard by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                scorecard_data = response.json()
                print(f"Successfully retrieved scorecard {scorecard_id}")
            except Exception as e:
                print(f"Error parsing scorecard {scorecard_id} response: {e}")
        else:
            print(f"Scorecard by ID failed: {response.text}")
    
    @task(2)
    @tag('get', 'scorecards', 'categories')
    def get_scorecard_categories(self):
        """Get Scorecard Categories - Fetch all scorecard categories"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping categories requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        print("Attempting to get scorecard categories...")
        response = self.get_resource("/scorecards/categories", "Scorecard Categories")
        print(f"Categories response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                categories_data = response.json()
                print(f"Retrieved {len(categories_data) if isinstance(categories_data, list) else 'unknown'} categories")
                
                # Cache category IDs for subsequent individual category requests
                self._cache_category_ids_from_response()
            except Exception as e:
                print(f"Error parsing categories response: {e}")
        else:
            print(f"Categories list failed: {response.text}")
    
    @task(1)
    @tag('get', 'scorecards', 'category_by_id')
    def get_scorecard_category_by_id(self):
        """Get Scorecard Category By Id - Fetch a specific category by its ID"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping category by ID requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Ensure we have cached category IDs
        if not self._category_ids_cached:
            self._cache_category_ids_from_response()
        
        if not self._category_ids:
            print("No category IDs available for testing")
            return
        
        category_id = random.choice(self._category_ids)
        print(f"Testing with category ID: {category_id}")
        response = self.get_resource(f"/scorecards/categories/{category_id}", f"Category {category_id}")
        print(f"Category by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                category_data = response.json()
                print(f"Successfully retrieved category {category_id}")
            except Exception as e:
                print(f"Error parsing category {category_id} response: {e}")
        else:
            print(f"Category by ID failed: {response.text}")
    
    @task(1)
    @tag('get', 'scorecards', 'query_params')
    def get_scorecards_with_query_params(self):
        """Get Scorecards with query parameters - Test API flexibility"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping query params requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        print("Testing scorecards list with query parameters...")
        
        # Test with common query parameters that might be supported
        query_params = [
            {},  # No params
            {"limit": 10},  # Limit results
            {"offset": 0},  # Pagination
            {"sort": "scorecard_id"},  # Sorting
            {"filter": "active"},  # Filtering
        ]
        
        for params in query_params:
            try:
                response = self.client.get("/scorecards", params=params)
                print(f"Scorecards with params {params}: {response.status_code}")
                
                if response.status_code not in [200, 400, 422]:  # 400/422 might be expected for invalid params
                    print(f"Unexpected status for params {params}: {response.text}")
            except Exception as e:
                print(f"Error testing scorecards with params {params}: {e}")
    
    @task(1)
    @tag('get', 'scorecards', 'nested_endpoints')
    def get_scorecard_nested_data(self):
        """Get Scorecard Nested Data - Test nested endpoints like versions, questions"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping nested data requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Ensure we have cached scorecard IDs
        if not self._scorecard_ids_cached:
            self._cache_scorecard_ids_from_response()
        
        if not self._scorecard_ids:
            print("No scorecard IDs available for nested testing")
            return
        
        scorecard_id = random.choice(self._scorecard_ids)
        
        # Test nested endpoints
        nested_endpoints = [
            f"/scorecards/{scorecard_id}/versions",
            f"/scorecards/{scorecard_id}/sections",
            f"/scorecards/{scorecard_id}/events",
            f"/scorecards/{scorecard_id}/comments",
        ]
        
        for endpoint in nested_endpoints:
            try:
                response = self.client.get(endpoint)
                endpoint_name = endpoint.split('/')[-1]  # Get the last part (versions, sections, etc.)
                print(f"Scorecard {scorecard_id} {endpoint_name}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"  Retrieved {len(data)} {endpoint_name}")
                        else:
                            print(f"  Retrieved {endpoint_name} data")
                    except Exception as e:
                        print(f"  Error parsing {endpoint_name} response: {e}")
                elif response.status_code not in [404, 403]:  # 404/403 might be expected
                    print(f"  Unexpected status for {endpoint_name}: {response.text}")
            except Exception as e:
                print(f"Error testing {endpoint}: {e}")
    
