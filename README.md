# Load Testing with Locust

This repository contains load testing scripts using Locust for API performance testing.

## Files

- `load_test.py` - Main load testing script with OAuth2 authentication
- `.gitignore` - Git ignore patterns for Python projects

## Setup

1. Install Locust:
   ```bash
   pip install locust
   ```

2. Update credentials in `load_test.py`:
   - Replace `client_id` and `client_secret` with your actual values
   - Update the `host` URL if needed

## Usage

Run the load test:
```bash
locust -f load_test.py
```

Then open http://localhost:8089 in your browser to configure and run the test.

## Features

- OAuth2 Client Credentials authentication
- Shared token caching (authenticates only once)
- Thread-safe token management
- Configurable user count and spawn rate
