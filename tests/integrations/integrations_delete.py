"""
Integrations API load tests - DELETE operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class IntegrationsDeleteTest(BaseResourceTest):
    """Load tests for Integrations API DELETE endpoints"""
    
    # DELETE Operations
    @task(3)
    @tag('delete', 'integrations')
    def delete_integration(self):
        """Delete Integration"""
        # TODO: Implement delete_integration
        pass
    
    @task(2)
    @tag('delete', 'integrations')
    def disable_integration(self):
        """Disable Integration"""
        # TODO: Implement disable_integration
        pass
    
