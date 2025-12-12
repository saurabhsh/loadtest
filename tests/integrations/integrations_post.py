"""
Integrations API load tests - POST operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class IntegrationsPostTest(BaseResourceTest):
    """Load tests for Integrations API POST endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._integration_ids = []  # Will be populated dynamically for nested endpoints
        self._integration_ids_cached = False
        self._created_integrations = []  # Track integrations created by this instance
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
    
    def _get_unique_integration_name(self, prefix="TestIntegration"):
        """Generate a unique integration name"""
        # Use full timestamp without modulo to avoid collisions
        timestamp = int(time.time() * 1000000)  # Microseconds for better precision
        # Include instance ID for uniqueness across concurrent Locust users
        instance_id = id(self) % 100000  # Unique per instance, modulo for shorter name
        # Larger random number range for better uniqueness
        random_num = random.randint(10000, 99999)
        return f"{prefix}_{instance_id}_{timestamp}_{random_num}"
    
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
    
    def _delete_integration(self, integration_id):
        """Delete an integration by ID"""
        try:
            print(f"Deleting integration {integration_id}...")
            response = self.delete_resource(f"/integrations/{integration_id}", f"Delete Integration {integration_id}")
            if response.status_code in [200, 204]:
                print(f"✓ Successfully deleted integration {integration_id}")
                return True
            else:
                print(f"✗ Failed to delete integration {integration_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting integration {integration_id}: {e}")
            return False
    
    def _extract_integration_id_from_response(self, response):
        """Extract integration ID from response"""
        try:
            if response.content:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Try different possible field names
                    integration_id = (response_data.get("integration_id") or 
                                    response_data.get("id") or
                                    (response_data.get("integration", {}).get("integration_id")) or
                                    (response_data.get("integration", {}).get("id")))
                    return integration_id
        except Exception as e:
            print(f"Could not extract integration ID from response: {e}")
        return None
    
    # POST Operations
    @task(3)
    @tag('post', 'integrations', 'basic')
    def create_integration(self):
        """Create Integration - Basic integration creation with required fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping basic create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_name = self._get_unique_integration_name("PostIntegration")
        
        # Basic integration data with required fields
        # Based on sample data in base_test.py: name, type, url
        integration_data = {
            "name": unique_name,
            "type": random.choice(["webhook", "api", "sftp", "email"]),  # Common integration types
            "url": f"https://example.com/webhook/{unique_name}"  # Unique URL
        }
        
        print(f"Creating basic integration: {unique_name}")
        try:
            response = self.post_resource("/integrations", integration_data, f"Create Integration {unique_name}")
            print(f"POST response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created integration: {unique_name}")
            
            # Extract integration ID and delete immediately
            integration_id = self._extract_integration_id_from_response(response)
            if integration_id:
                self._delete_integration(integration_id)
            else:
                print(f"⚠ Could not extract integration ID from response for {unique_name}")
        else:
            print(f"✗ Failed to create integration {unique_name}: {response.status_code}")
    
    @task(2)
    @tag('post', 'integrations', 'lists')
    def create_webhook_integration(self):
        """Create Integration List - Create a list for an existing integration"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping list create requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        # Ensure we have cached integration IDs
        if not self._integration_ids_cached:
            self._cache_integration_ids_from_response()
        
        if not self._integration_ids:
            print("No integration IDs available for testing, skipping integration list request")
            return
        
        integration_id = random.choice(self._integration_ids)
        unique_list_name = self._get_unique_integration_name("TestList")
        
        # List data - structure may vary based on API, using common fields
        list_data = {
            "name": unique_list_name,
            "description": f"Test list for integration {integration_id} - created via POST API"
        }
        
        print(f"Creating list for integration {integration_id}: {unique_list_name}")
        try:
            response = self.post_resource(f"/integrations/{integration_id}/lists", list_data, f"Create Integration List {unique_list_name}")
            print(f"POST list response received: {response.status_code}")
        except Exception as e:
            print(f"✗ POST list request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully created list for integration {integration_id}: {unique_list_name}")
            
            # Extract list ID from response if available
            try:
                if response.content:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        list_id = (response_data.get("list_id") or 
                                  response_data.get("id") or
                                  (response_data.get("list", {}).get("list_id")) or
                                  (response_data.get("list", {}).get("id")))
                        if list_id:
                            print(f"Created list with ID: {list_id}")
                            # Note: May need DELETE endpoint for lists if cleanup is required
            except Exception as e:
                print(f"Could not extract list ID from response: {e}")
        else:
            print(f"✗ Failed to create list for integration {integration_id}: {response.status_code}")
