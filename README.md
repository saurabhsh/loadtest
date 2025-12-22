# Load Testing with Locust

This repository contains load testing scripts using Locust for API performance testing.

## Files

- `tests/` - Main test directory with industry-standard structure
  - `base/base_test.py` - Base test class with common functionality
  - `users/` - Users API tests (separated by HTTP method)
    - `users_get.py` - Users GET operations
    - `users_post.py` - Users POST operations
    - `users_put.py` - Users PUT operations
    - `users_delete.py` - Users DELETE operations (**currently disabled/commented out**; planned for future)
  - `teams/` - Teams API tests (separated by HTTP method)
    - `teams_get.py` - Teams GET operations
    - `teams_post.py` - Teams POST operations
    - `teams_put.py` - Teams PUT operations
    - `teams_delete.py` - Teams DELETE operations
  - `staff/` - Staff API tests (separated by HTTP method)
    - `staff_get.py` - Staff GET operations
    - `staff_post.py` - Staff POST operations
    - `staff_put.py` - Staff PUT operations
    - `staff_delete.py` - Staff DELETE operations
  - `groups/` - Groups API tests (separated by HTTP method)
    - `groups_get.py` - Groups GET operations
    - `groups_post.py` - Groups POST operations
    - `groups_put.py` - Groups PUT operations
    - `groups_delete.py` - Groups DELETE operations
  - `scores/` - Scores API tests (GET only)
    - `scores_get.py` - Scores GET operations
  - `scorecards/` - Scorecards API tests (GET only)
    - `scorecards_get.py` - Scorecards GET operations
  - `integrations/` - Integrations API tests (separated by HTTP method)
    - `integrations_get.py` - Integrations GET operations
    - `integrations_post.py` - Integrations POST operations
    - `integrations_put.py` - Integrations PUT operations
    - `integrations_delete.py` - Integrations DELETE operations (**TODO: placeholder; not implemented yet**)
- `config/settings.py` - Configuration management with environment variables
- `auth/token_manager.py` - Thread-safe OAuth2 token management
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed to Git)
- `.gitignore` - Git ignore patterns for Python projects
- `main.py` - Legacy single-file test (deprecated)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update credentials in `.env` file:
   - Replace `CLIENT_ID` and `CLIENT_SECRET` with your actual values
   - Update the `API_HOST` URL if needed

## Usage

### Recommended: Run by file (avoid accidental mixed operations)
Running by file is the most predictable way to execute tests. It avoids accidentally mixing GET/POST/PUT/DELETE when using tags.

Examples:
```bash
# Users POST only (with graceful stop to allow cleanup to finish)
locust -f tests/users/users_post.py --host https://YOUR_HOST --users 50 --spawn-rate 10 --run-time 25s --stop-timeout 180s --headless
```

#### Why `--stop-timeout` matters
Locust stops generating new tasks after `--run-time`, but some requests may still be in-flight.
`--stop-timeout 180s` lets those finish gracefully (useful for scripts that create and then delete/cleanup).

### Running Specific Resource + HTTP Method in Headless mode (Example commands for 'Staff' endpoint)
```bash
# Run only staff GET operations
locust -f tests/staff/staff_get.py --host https://www.staging.scorebuddy.co.uk/1848761120/api/v1 --users 50 --spawn-rate 10 --run-time 25s --stop-timeout 180s --headless

# Run only staff POST operations
locust -f tests/staff/staff_post.py --host https://www.staging.scorebuddy.co.uk/1848761120/api/v1 --users 50 --spawn-rate 10 --run-time 25s --stop-timeout 180s --headless

# Run only staff PUT operations
locust -f tests/staff/staff_put.py --host https://www.staging.scorebuddy.co.uk/1848761120/api/v1 --users 50 --spawn-rate 10 --run-time 25s --stop-timeout 180s --headless

# Run only staff DELETE operations
locust -f tests/staff/staff_post.py --host https://www.staging.scorebuddy.co.uk/1848761120/api/v1 --users 50 --spawn-rate 10 --run-time 25s --stop-timeout 180s --headless
```
## Locust UI Mode Run - get rid of '--headless' from the command used to run the tests
```bash
# Run only staff GET operations
locust -f tests/staff/staff_get.py --host https://www.staging.scorebuddy.co.uk/1848761120/api/v1 --users 50 --spawn-rate 10 --run-time 25s --stop-timeout 180s --headless
```
Then open http://localhost:8089 in your browser to configure and run the test.

## GitHub Actions (run tests in the cloud)

This repo includes a GitHub Actions workflow at `.github/workflows/load-test.yml` that runs Locust **by file name** and uploads an HTML report + CSV results.

### 1) Add repository secrets (one-time)
In GitHub:
- Repository → **Settings**
- **Secrets and variables** → **Actions**
- **New repository secret**

Add these secrets:
- `CLIENT_ID`
- `CLIENT_SECRET`
- `API_HOST`

Notes:
- You usually **do not** need to add `SCOPE` because the code has a default in `config/settings.py`.
- Never commit `.env` to GitHub (it’s in `.gitignore`).

### 2) Run the workflow
In GitHub:
- Repository → **Actions**
- Select workflow: **Locust Load Test (Run by Endpoints)**
- Click **Run workflow**

Fill the inputs:
- `test_file`: pick the exact file you want (example: `tests/staff/staff_get.py`)
- `users`: total simulated users
- `spawn_rate`: how many users start per second
- `duration`: test duration (example: `30s`, `1m`)
- `stop_timeout`: graceful shutdown time (example: `180s`) to let in-flight requests/cleanup finish

### 3) Download results
After the workflow completes:
- Open the run → scroll to **Artifacts**
- Download `locust-results`
- Open `report.html` in your browser

## Features

- **Industry-standard test structure** - Resource-based organization by endpoint and HTTP method
- **OAuth2 Client Credentials authentication** - Secure API access
- **Shared token caching** - Authenticates only once for efficiency
- **Thread-safe token management** - Safe concurrent access
- **Run by file** - Predictable execution by selecting a specific test file or folder
- **Comprehensive API coverage** - GET, POST, PUT, DELETE operations
- **Configurable user count and spawn rate** - Flexible load testing
- **Safe cleanup patterns** - Many create/update tests attempt to delete test data; use `--stop-timeout` to allow cleanup to complete
