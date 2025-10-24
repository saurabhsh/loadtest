"""
Scores API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import random


class ScoresGetTest(BaseResourceTest):
    """Load tests for Scores API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._score_ids = []  # Will be populated dynamically
        self._score_ids_cached = False
    
    def _cache_score_ids_from_response(self):
        """Cache score IDs from the scores list response"""
        if not self._score_ids_cached:
            try:
                response = self.client.get("/scores")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'scores' in data and isinstance(data['scores'], list):
                        scores = data['scores']
                        cached_ids = []
                        for score in scores:
                            if isinstance(score, dict) and 'score_id' in score:
                                cached_ids.append(score['score_id'])
                            elif isinstance(score, dict) and 'id' in score:
                                cached_ids.append(score['id'])
                        
                        if cached_ids:
                            self._score_ids = cached_ids
                            print(f"Cached {len(cached_ids)} score IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No score IDs found in API response, will retry on next request")
                    elif isinstance(data, list):
                        # Handle if response is directly a list
                        cached_ids = []
                        for score in data:
                            if isinstance(score, dict) and 'score_id' in score:
                                cached_ids.append(score['score_id'])
                            elif isinstance(score, dict) and 'id' in score:
                                cached_ids.append(score['id'])
                        
                        if cached_ids:
                            self._score_ids = cached_ids
                            print(f"Cached {len(cached_ids)} score IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No score IDs found in API response, will retry on next request")
                    else:
                        print("Unexpected response format, will retry on next request")
                else:
                    print(f"Failed to fetch scores list for caching: {response.status_code}")
            except Exception as e:
                print(f"Error caching score IDs: {e}")
            
            self._score_ids_cached = True
    
    # GET Operations
    @task(4)
    @tag('get', 'scores', 'list')
    def get_scores_list(self):
        """Get Scores List - Primary endpoint for fetching all scores"""
        print("Attempting to get scores list...")
        response = self.get_resource("/scores", "Scores")
        print(f"Scores list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                scores_data = response.json()
                # Handle different response structures
                if isinstance(scores_data, dict) and 'scores' in scores_data:
                    score_count = len(scores_data['scores']) if isinstance(scores_data['scores'], list) else 'unknown'
                    print(f"Retrieved {score_count} scores")
                elif isinstance(scores_data, list):
                    print(f"Retrieved {len(scores_data)} scores")
                else:
                    print(f"Retrieved scores data")
                
                # Cache score IDs for subsequent individual score requests
                self._cache_score_ids_from_response()
            except Exception as e:
                print(f"Error parsing scores response: {e}")
        else:
            print(f"Scores list failed: {response.text}")
    
    @task(3)
    @tag('get', 'scores', 'individual')
    def get_score_by_id(self):
        """Get Score By Id - Fetch a specific score by its ID"""
        # Ensure we have cached score IDs
        if not self._score_ids_cached:
            self._cache_score_ids_from_response()
        
        if not self._score_ids:
            print("No score IDs available for testing, skipping individual score request")
            return
        
        score_id = random.choice(self._score_ids)
        print(f"Testing with score ID: {score_id}")
        response = self.get_resource(f"/scores/{score_id}", f"Score {score_id}")
        print(f"Score by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                score_data = response.json()
                print(f"Successfully retrieved score {score_id}")
            except Exception as e:
                print(f"Error parsing score {score_id} response: {e}")
        else:
            print(f"Score by ID failed: {response.text}")
    
    @task(2)
    @tag('get', 'scores', 'reviews')
    def get_scores_reviews(self):
        """Get Scores Reviews - Fetch scores reviews data"""
        print("Attempting to get scores reviews...")
        response = self.get_resource("/scores/reviews", "Scores Reviews")
        print(f"Scores reviews response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                reviews_data = response.json()
                # Handle different response structures
                if isinstance(reviews_data, dict) and 'reviews' in reviews_data:
                    review_count = len(reviews_data['reviews']) if isinstance(reviews_data['reviews'], list) else 'unknown'
                    print(f"Retrieved {review_count} reviews")
                elif isinstance(reviews_data, list):
                    print(f"Retrieved {len(reviews_data)} reviews")
                else:
                    print(f"Retrieved reviews data")
            except Exception as e:
                print(f"Error parsing reviews response: {e}")
        else:
            print(f"Scores reviews failed: {response.text}")
    
    @task(1)
    @tag('get', 'scores', 'query_params')
    def get_scores_with_query_params(self):
        """Get Scores with query parameters - Test API flexibility"""
        print("Testing scores list with query parameters...")
        
        # Test with common query parameters that might be supported
        query_params = [
            {},  # No params
            {"limit": 10},  # Limit results
            {"offset": 0},  # Pagination
            {"sort": "score_id"},  # Sorting
            {"from_last_edit_date": "2024-01-01"},  # Date filtering
            {"to_last_edit_date": "2024-12-31"},  # Date filtering
        ]
        
        for params in query_params:
            try:
                response = self.client.get("/scores", params=params)
                print(f"Scores with params {params}: {response.status_code}")
                
                if response.status_code not in [200, 400, 422]:  # 400/422 might be expected for invalid params
                    print(f"Unexpected status for params {params}: {response.text}")
            except Exception as e:
                print(f"Error testing scores with params {params}: {e}")
    
