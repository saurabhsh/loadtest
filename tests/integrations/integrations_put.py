"""
Integrations API load tests - PUT operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest
import time
import random


class IntegrationsPutTest(BaseResourceTest):
    """Load tests for Integrations API PUT endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_integrations = []  # Track integrations created by this instance
        self._group_ids = [32, 33, 34, 35, 36, 37]  # Valid group IDs (visible in UI, not soft deleted)
        self._test_start_time = time.time()
        self._test_duration = None  # Will be set from environment
    
    def _get_random_group_ids(self, count=1):
        """Get random group IDs from valid groups (32-37)"""
        if count >= len(self._group_ids):
            return self._group_ids.copy()
        return random.sample(self._group_ids, count)
    
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
    
    # PUT Operations
    @task(3)
    @tag('put', 'integrations', 'upsert')
    def upsert_integration(self):
        """Upsert an integration (create or update)"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping new requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_label = self._get_unique_integration_name("UpsertIntegration")
        
        # Integration data with required fields based on actual API schema
        # Required fields: label, integration_type, data_retention (with policy and rules), group_ids
        integration_data = {
            "label": unique_label,
            "description": f"Upserted integration: {unique_label}. Created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "integration_type": "internal",
            "data_retention": {
                "policy": "limited",  # Only "limited" is valid when rules are provided
                "rules": {
                    "interval": random.choice(["days", "weeks", "months", "years"]),
                    "numeracy": random.randint(1, 12)
                }
            },
            "group_ids": self._get_random_group_ids(random.randint(1, 2))  # At least 1 group ID required
        }
        
        print(f"Upserting integration with label: {unique_label}")
        try:
            response = self.put_resource("/integrations", integration_data, f"Upsert Integration {unique_label}")
            print(f"PUT response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Successfully upserted integration: {unique_label}")
            
            # Extract integration ID and delete immediately
            integration_id = self._extract_integration_id_from_response(response)
            if integration_id:
                self._delete_integration(integration_id)
            else:
                print(f"⚠ Could not extract integration ID from response for {unique_label}")
        else:
            print(f"✗ Failed to upsert integration {unique_label}: {response.status_code}")
    
    @task(1)
    @tag('put', 'integrations', 'validation')
    def test_put_validation(self):
        """Test PUT validation with minimal data"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping validation requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_label = self._get_unique_integration_name("MinimalIntegration")
        
        # Test with minimal required data
        minimal_data = {
            "label": unique_label,
            "description": f"Minimal integration test: {unique_label}",
            "integration_type": "internal",
            "data_retention": {
                "policy": "limited",
                "rules": {
                    "interval": "days",
                    "numeracy": 1
                }
            },
            "group_ids": self._get_random_group_ids(1)  # At least 1 group ID required
        }
        
        print(f"Testing PUT validation with minimal data: {unique_label}")
        try:
            response = self.put_resource("/integrations", minimal_data, f"Validation Test {unique_label}")
            print(f"PUT validation response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT validation request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Validation test succeeded: {response.status_code}")
            
            # Extract integration ID and delete immediately
            integration_id = self._extract_integration_id_from_response(response)
            if integration_id:
                self._delete_integration(integration_id)
            else:
                print(f"⚠ Could not extract integration ID from validation response for {unique_label}")
        elif response.status_code in [400, 422]:
            print(f"⚠ Validation error (expected): {response.status_code}")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    
    @task(1)
    @tag('put', 'integrations', 'full_data')
    def test_put_with_all_fields(self):
        """Test PUT with all available integration fields"""
        # Check if we should stop creating new requests
        if self._should_stop_creating_requests():
            elapsed = time.time() - self._test_start_time
            print(f"⏰ Stopping full data requests - {elapsed:.1f}s elapsed, stopping 5s before end")
            return
        
        unique_label = self._get_unique_integration_name("FullDataIntegration")
        
        # Test with all available fields
        full_data = {
            "label": unique_label,
            "description": f"Complete integration with all fields: {unique_label}. Created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "integration_type": "internal",
            "data_retention": {
                "policy": "limited",
                "rules": {
                    "interval": random.choice(["days", "weeks", "months", "years"]),
                    "numeracy": random.randint(1, 12)
                }
            },
            "group_ids": self._get_random_group_ids(random.randint(1, 3))  # 1-3 random group IDs
        }
        
        print(f"Testing PUT with all fields: {unique_label}")
        try:
            response = self.put_resource("/integrations", full_data, f"Full Data Test {unique_label}")
            print(f"PUT full data response received: {response.status_code}")
        except Exception as e:
            print(f"✗ PUT full data request failed with exception: {e}")
            return
        
        if response.status_code in [200, 201, 204]:
            print(f"✓ Full data test succeeded: {response.status_code}")
            
            # Extract integration ID and delete immediately
            integration_id = self._extract_integration_id_from_response(response)
            if integration_id:
                self._delete_integration(integration_id)
            else:
                print(f"⚠ Could not extract integration ID from full data response for {unique_label}")
        else:
            print(f"✗ Full data test failed: {response.status_code}")
    
