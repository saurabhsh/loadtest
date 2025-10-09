# Load Testing with Locust

This repository contains load testing scripts using Locust for API performance testing.

## Files

- `tests/` - Main test directory with industry-standard structure
  - `base/base_test.py` - Base test class with common functionality
  - `users/` - Users API tests (separated by HTTP method)
    - `users_get.py` - Users GET operations
    - `users_post.py` - Users POST operations
    - `users_put.py` - Users PUT operations
    - `users_delete.py` - Users DELETE operations
  - `teams/` - Teams API tests (separated by HTTP method)
    - `teams_get.py` - Teams GET operations
    - `teams_post.py` - Teams POST operations
    - `teams_put.py` - Teams PUT operations
    - `teams_delete.py` - Teams DELETE operations
  - `staff/` - Staff API tests (separated by HTTP method)
  - `groups/` - Groups API tests (separated by HTTP method)
  - `scores/` - Scores API tests (GET only)
  - `scorecards/` - Scorecards API tests (GET only)
  - `integrations/` - Integrations API tests (separated by HTTP method)
- `config/settings.py` - Configuration management with environment variables
- `auth/token_manager.py` - Thread-safe OAuth2 token management
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed to Git)
- `.gitignore` - Git ignore patterns for Python projects
- `main.py` - Legacy single-file test (deprecated)

## Setup

1. Install Locust:
   ```bash
   pip install locust
   ```

2. Update credentials in `.env` file:
   - Replace `CLIENT_ID` and `CLIENT_SECRET` with your actual values
   - Update the `API_HOST` URL if needed

## Usage

### Running All Tests
```bash
locust -f tests/
```

### Running Specific Resource Tests
```bash
# Run all users tests (GET, POST, PUT, DELETE)
locust -f tests/users/

# Run all teams tests
locust -f tests/teams/

# Run all staff tests
locust -f tests/staff/
```

### Running Tests by HTTP Method
```bash
# Run only GET operations across all resources
locust -f tests/ --tags read

# Run only POST operations
locust -f tests/ --tags create

# Run only PUT operations
locust -f tests/ --tags update

# Run only DELETE operations (when enabled)
locust -f tests/ --tags delete
```

### Running Specific Resource + HTTP Method
```bash
# Run only users GET operations
locust -f tests/users/users_get.py

# Run only users POST operations
locust -f tests/users/users_post.py

# Run only teams PUT operations
locust -f tests/teams/teams_put.py

# Run only staff DELETE operations
locust -f tests/staff/staff_delete.py
```

### Running Tests by Resource and Operation
```bash
# Run only users GET operations
locust -f tests/users/users_get.py --tags users read

# Run only teams POST operations
locust -f tests/teams/teams_post.py --tags teams create

# Run multiple operation types
locust -f tests/users/ --tags users read create
```

### Legacy Single File (Deprecated)
```bash
locust -f main.py
```

Then open http://localhost:8089 in your browser to configure and run the test.

## Features

- **Industry-standard test structure** - Resource-based organization with tags
- **OAuth2 Client Credentials authentication** - Secure API access
- **Shared token caching** - Authenticates only once for efficiency
- **Thread-safe token management** - Safe concurrent access
- **Tag-based test execution** - Run specific operations or resources
- **Comprehensive API coverage** - GET, POST, PUT, DELETE operations
- **Configurable user count and spawn rate** - Flexible load testing
- **DELETE operations commented out** - Safe testing without data loss
