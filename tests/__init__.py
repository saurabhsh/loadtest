"""
Main test runner for ScoreBuddy API load tests
Import all test classes here for easy execution
"""
# Users tests
from tests.users.users_get import UsersGetTest
from tests.users.users_post import UsersPostTest
from tests.users.users_put import UsersPutTest
from tests.users.users_delete import UsersDeleteTest

# Teams tests
from tests.teams.teams_get import TeamsGetTest
from tests.teams.teams_post import TeamsPostTest
from tests.teams.teams_put import TeamsPutTest
from tests.teams.teams_delete import TeamsDeleteTest

# Staff tests
from tests.staff.staff_get import StaffGetTest
from tests.staff.staff_post import StaffPostTest
from tests.staff.staff_put import StaffPutTest
from tests.staff.staff_delete import StaffDeleteTest

# Groups tests
from tests.groups.groups_get import GroupsGetTest
from tests.groups.groups_post import GroupsPostTest
from tests.groups.groups_put import GroupsPutTest
from tests.groups.groups_delete import GroupsDeleteTest

# Scores tests (read-only)
from tests.scores.scores_get import ScoresGetTest

# Scorecards tests (read-only)
from tests.scorecards.scorecards_get import ScorecardsGetTest

# Integrations tests
from tests.integrations.integrations_get import IntegrationsGetTest
from tests.integrations.integrations_post import IntegrationsPostTest
from tests.integrations.integrations_put import IntegrationsPutTest
from tests.integrations.integrations_delete import IntegrationsDeleteTest

# Export all test classes
__all__ = [
    # Users
    'UsersGetTest', 'UsersPostTest', 'UsersPutTest', 'UsersDeleteTest',
    # Teams
    'TeamsGetTest', 'TeamsPostTest', 'TeamsPutTest', 'TeamsDeleteTest',
    # Staff
    'StaffGetTest', 'StaffPostTest', 'StaffPutTest', 'StaffDeleteTest',
    # Groups
    'GroupsGetTest', 'GroupsPostTest', 'GroupsPutTest', 'GroupsDeleteTest',
    # Scores
    'ScoresGetTest',
    # Scorecards
    'ScorecardsGetTest',
    # Integrations
    'IntegrationsGetTest', 'IntegrationsPostTest', 'IntegrationsPutTest', 'IntegrationsDeleteTest'
]
