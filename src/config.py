"""
Configuration management for Football Gossip Bot
"""

import os
import json
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
        self.CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))
        self.MIN_DRAMA_SCORE = int(os.getenv('MIN_DRAMA_SCORE', '30'))
        self.AUTO_TWEET = os.getenv('AUTO_TWEET', 'true').lower() == 'true'
        
        # Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.ATHLETES_FILE = self.DATA_DIR / 'athletes.json'
        self.DATABASE_PATH = self.DATA_DIR / 'gossip.db'
        
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
    
    def get_athletes(self):
        """Load list of tracked athletes from JSON file"""
        if not self.ATHLETES_FILE.exists():
            print(f"⚠️  Athletes file not found: {self.ATHLETES_FILE}")
            return []
        
        try:
            with open(self.ATHLETES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('athletes', [])
        except Exception as e:
            print(f"❌ Error loading athletes: {e}")
            return []
    
    def is_configured(self):
        """Check if bot is fully configured"""
        return all([
            self.TWITTER_API_KEY,
            self.TWITTER_API_SECRET,
            self.TWITTER_ACCESS_TOKEN,
            self.TWITTER_ACCESS_SECRET,
            self.TWITTER_BEARER_TOKEN
        ])
