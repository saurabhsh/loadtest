"""
Integrations API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import random


class IntegrationsGetTest(BaseResourceTest):
    """Load tests for Integrations API GET endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._integration_ids = []  # Will be populated dynamically
        self._integration_ids_cached = False
    
    def _cache_integration_ids_from_response(self):
        """Cache integration IDs from the integrations list response"""
        if not self._integration_ids_cached:
            try:
                response = self.client.get("/integrations")
                if response.status_code == 200:
                    data = response.json()
                    # Handle the actual API response structure
                    if 'integrations' in data and isinstance(data['integrations'], list):
                        integrations = data['integrations']
                        cached_ids = []
                        for integration in integrations:
                            if isinstance(integration, dict) and 'integration_id' in integration:
                                cached_ids.append(integration['integration_id'])
                            elif isinstance(integration, dict) and 'id' in integration:
                                cached_ids.append(integration['id'])
                        
                        if cached_ids:
                            self._integration_ids = cached_ids
                            print(f"Cached {len(cached_ids)} integration IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No integration IDs found in API response, using fallback IDs")
                            self._integration_ids = [1, 2, 3, 4, 5]  # Fallback IDs
                    elif isinstance(data, list):
                        # Handle if response is directly a list
                        cached_ids = []
                        for integration in data:
                            if isinstance(integration, dict) and 'integration_id' in integration:
                                cached_ids.append(integration['integration_id'])
                            elif isinstance(integration, dict) and 'id' in integration:
                                cached_ids.append(integration['id'])
                        
                        if cached_ids:
                            self._integration_ids = cached_ids
                            print(f"Cached {len(cached_ids)} integration IDs from API response: {cached_ids[:5]}...")
                        else:
                            print("No integration IDs found in API response, using fallback IDs")
                            self._integration_ids = [1, 2, 3, 4, 5]  # Fallback IDs
                    else:
                        print("Unexpected response format, using fallback IDs")
                        self._integration_ids = [1, 2, 3, 4, 5]  # Fallback IDs
                else:
                    print(f"Failed to fetch integrations list for caching: {response.status_code}")
                    self._integration_ids = [1, 2, 3, 4, 5]  # Fallback IDs
            except Exception as e:
                print(f"Error caching integration IDs: {e}")
                self._integration_ids = [1, 2, 3, 4, 5]  # Fallback IDs
            
            self._integration_ids_cached = True
    
    # GET Operations
    @task(3)
    @tag('get', 'integrations', 'list')
    def get_integrations_list(self):
        """Get Integrations List - Primary endpoint for fetching all integrations"""
        print("Attempting to get integrations list...")
        response = self.get_resource("/integrations", "Integrations")
        print(f"Integrations list response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                integrations_data = response.json()
                # Handle different response structures
                if isinstance(integrations_data, dict) and 'integrations' in integrations_data:
                    integration_count = len(integrations_data['integrations']) if isinstance(integrations_data['integrations'], list) else 'unknown'
                    print(f"Retrieved {integration_count} integrations")
                elif isinstance(integrations_data, list):
                    print(f"Retrieved {len(integrations_data)} integrations")
                else:
                    print(f"Retrieved integrations data")
                
                # Cache integration IDs for subsequent individual integration requests
                self._cache_integration_ids_from_response()
            except Exception as e:
                print(f"Error parsing integrations response: {e}")
        else:
            print(f"Integrations list failed: {response.text}")
    
    @task(2)
    @tag('get', 'integrations', 'individual')
    def get_integration_by_id(self):
        """Get Integration By Id - Fetch a specific integration by its ID"""
        # Ensure we have cached integration IDs
        if not self._integration_ids_cached:
            self._cache_integration_ids_from_response()
        
        if not self._integration_ids:
            print("No integration IDs available for testing, skipping individual integration request")
            return
        
        integration_id = random.choice(self._integration_ids)
        print(f"Testing with integration ID: {integration_id}")
        response = self.get_resource(f"/integrations/{integration_id}", f"Integration {integration_id}")
        print(f"Integration by ID response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                integration_data = response.json()
                print(f"Successfully retrieved integration {integration_id}")
            except Exception as e:
                print(f"Error parsing integration {integration_id} response: {e}")
        else:
            print(f"Integration by ID failed: {response.text}")
    
    @task(1)
    @tag('get', 'integrations', 'cases')
    def get_integration_cases(self):
        """Get Integration Cases - Fetch cases for a specific integration"""
        # Ensure we have cached integration IDs
        if not self._integration_ids_cached:
            self._cache_integration_ids_from_response()
        
        if not self._integration_ids:
            print("No integration IDs available for testing, skipping integration cases request")
            return
        
        integration_id = random.choice(self._integration_ids)
        print(f"Testing integration cases with integration ID: {integration_id}")
        response = self.get_resource(f"/integrations/{integration_id}/cases", f"Integration {integration_id} Cases")
        print(f"Integration cases response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                cases_data = response.json()
                # Handle different response structures
                if isinstance(cases_data, dict) and 'cases' in cases_data:
                    case_count = len(cases_data['cases']) if isinstance(cases_data['cases'], list) else 'unknown'
                    print(f"Retrieved {case_count} cases for integration {integration_id}")
                elif isinstance(cases_data, list):
                    print(f"Retrieved {len(cases_data)} cases for integration {integration_id}")
                else:
                    print(f"Successfully retrieved cases for integration {integration_id}")
            except Exception as e:
                print(f"Error parsing integration cases response: {e}")
        else:
            print(f"Integration cases failed: {response.text}")
    
