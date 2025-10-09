import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuration settings for the load testing application"""
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', 'https://www.staging.scorebuddy.co.uk/1777161849/api/v1')
    
    # OAuth2 Configuration
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    SCOPE = os.getenv('SCOPE', 
        'staff:read staff:write staff:delete '
        'users:read users:write users:delete '
        'teams:read teams:write teams:delete '
        'groups:read groups:write groups:delete '
        'scores:read '
        'scorecards:read '
        'integrations:read integrations:write integrations:delete'
    )
    
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
            error_msg = f"Missing required environment variables: {', '.join(missing)}\n"
            error_msg += "Please create a .env file with the following variables:\n"
            error_msg += "API_HOST=your_api_host\n"
            error_msg += "CLIENT_ID=your_client_id\n"
            error_msg += "CLIENT_SECRET=your_client_secret"
            raise ValueError(error_msg)
        
        return True

# Create a global settings instance
settings = Settings()
