"""
Configuration management for History Tweet Bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration from environment variables"""
    
    def __init__(self):
        # Twitter API credentials
        self.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
        self.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
        self.TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
        self.TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
        self.TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Bot settings
        self.AUTO_TWEET = os.getenv('AUTO_TWEET', 'true').lower() == 'true'
        
        # Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.DATABASE_PATH = self.DATA_DIR / 'history.db'
        
        # Create data directory if it doesn't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        
        # Validate credentials
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate that required credentials are present"""
        required = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_SECRET',
            'TWITTER_BEARER_TOKEN'
        ]
        
        missing = []
        for cred in required:
            if not getattr(self, cred):
                missing.append(cred)
        
        if missing:
            print(f"⚠️  Warning: Missing credentials: {', '.join(missing)}")
            print("ℹ️  Bot will run in demo mode (no actual API calls)")
    
    def is_configured(self):
        """Check if bot is fully configured"""
        return all([
            self.TWITTER_API_KEY,
            self.TWITTER_API_SECRET,
            self.TWITTER_ACCESS_TOKEN,
            self.TWITTER_ACCESS_SECRET,
            self.TWITTER_BEARER_TOKEN
        ])
