import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuration settings for the load testing application"""
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', 'https://www.staging.scorebuddy.co.uk/1777161849/api/v1')
    
    # OAuth2 Configuration
    CLIENT_ID = os.getenv('CLIENT_ID', 'saurabh')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', '356e674dc5f9b4a2f8a535a7d48fae4140bd4a4f79ca6f8afcda29b8d3ece914')
    SCOPE = os.getenv('SCOPE', 'staff:read users:read teams:read groups:read scores:read scorecards:read')
    
    # Authentication endpoint
    AUTH_ENDPOINT = '/authorisation/token'
    
    # Token configuration
    DEFAULT_TOKEN_EXPIRY = 3600  # 1 hour in seconds
    TOKEN_REFRESH_BUFFER = 60    # Refresh 1 minute before expiry
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        required_settings = ['API_HOST', 'CLIENT_ID', 'CLIENT_SECRET']
        missing = []
        
        for setting in required_settings:
            if not getattr(cls, setting):
                missing.append(setting)
        
        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")
        
        return True

# Create a global settings instance
settings = Settings()
