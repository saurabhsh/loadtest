"""
Scores API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class ScoresGetTest(BaseResourceTest):
    """Load tests for Scores API GET endpoints"""
    
    # GET Operations
    @task(3)
    @tag('get', 'scores')
    def get_scores_list(self):
        """Get Scores List"""
        # TODO: Implement get_scores_list
        pass
    
    @task(2)
    @tag('get', 'scores')
    def get_scores_by_user(self):
        """Get Scores By User"""
        # TODO: Implement get_scores_by_user
        pass
    
    @task(1)
    @tag('get', 'scores')
    def get_scores_reviews(self):
        """Get Scores Reviews"""
        # TODO: Implement get_scores_reviews
        pass
    
    @task(1)
    @tag('get', 'scores')
    def get_score_by_id(self):
        """Get Score By Id"""
        # TODO: Implement get_score_by_id
        pass
    
