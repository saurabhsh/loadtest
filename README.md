# Load Testing with Locust

This repository contains load testing scripts using Locust for API performance testing.

## Files

- `main.py` - Main load testing script with OAuth2 authentication
- `config/settings.py` - Configuration management with environment variables
- `auth/token_manager.py` - Thread-safe OAuth2 token management
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed to Git)
- `.gitignore` - Git ignore patterns for Python projects

## Setup

1. Install Locust:
   ```bash
   pip install locust
   ```

2. Update credentials in `.env` file:
   - Replace `CLIENT_ID` and `CLIENT_SECRET` with your actual values
   - Update the `API_HOST` URL if needed

## Usage

Run the load test:
```bash
locust -f main.py
```

Then open http://localhost:8089 in your browser to configure and run the test.

## Features

- OAuth2 Client Credentials authentication
- Shared token caching (authenticates only once)
- Thread-safe token management
- Configurable user count and spawn rate
