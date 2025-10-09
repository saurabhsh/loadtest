"""
Scorecards API load tests - GET operations only
"""
from locust import task, tag
from tests.base.base_test import BaseResourceTest


class ScorecardsGetTest(BaseResourceTest):
    """Load tests for Scorecards API GET endpoints"""
    
    # GET Operations
    @task(3)
    @tag('get', 'scorecards')
    def get_scorecards_list(self):
        """Get Scorecards List"""
        # TODO: Implement get_scorecards_list
        pass
    
    @task(2)
    @tag('get', 'scorecards')
    def get_scorecard_categories(self):
        """Get Scorecard Categories"""
        # TODO: Implement get_scorecard_categories
        pass
    
    @task(1)
    @tag('get', 'scorecards')
    def get_scorecard_by_id(self):
        """Get Scorecard By Id"""
        # TODO: Implement get_scorecard_by_id
        pass
    
    @task(1)
    @tag('get', 'scorecards')
    def get_scorecard_category_by_id(self):
        """Get Scorecard Category By Id"""
        # TODO: Implement get_scorecard_category_by_id
        pass
    
