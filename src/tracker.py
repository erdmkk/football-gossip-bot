"""
Twitter Follow/Unfollow Tracker for Football Athletes
"""

import tweepy
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class FollowTracker:
    """Tracks follow/unfollow activities of football athletes"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.api = None
        self.following_cache = {}  # Cache of previous following lists
        
        # Initialize Twitter API
        if config.is_configured():
            try:
                self._init_twitter_api()
                logger.info("✅ Twitter API initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twitter API: {e}")
        else:
            logger.warning("⚠️  Running in demo mode (no Twitter API credentials)")
    
    def _init_twitter_api(self):
        """Initialize Twitter API v2 client and v1.1 API"""
        # Twitter API v2
        self.client = tweepy.Client(
            bearer_token=self.config.TWITTER_BEARER_TOKEN,
            consumer_key=self.config.TWITTER_API_KEY,
            consumer_secret=self.config.TWITTER_API_SECRET,
            access_token=self.config.TWITTER_ACCESS_TOKEN,
            access_token_secret=self.config.TWITTER_ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        
        # Twitter API v1.1 (for some operations)
        auth = tweepy.OAuth1UserHandler(
            self.config.TWITTER_API_KEY,
            self.config.TWITTER_API_SECRET,
            self.config.TWITTER_ACCESS_TOKEN,
            self.config.TWITTER_ACCESS_SECRET
        )
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
    
    def check_athlete(self, athlete: Dict) -> List[Dict]:
        """
        Check for follow/unfollow changes for a specific athlete
        
        Args:
            athlete: Dict with 'name', 'twitter_handle', etc.
            
        Returns:
            List of changes (follow/unfollow events)
        """
        if not self.client:
            logger.info(f"📍 Demo mode: Simulating check for {athlete['name']}")
            return self._simulate_changes(athlete)
        
        try:
            username = athlete['twitter_handle'].replace('@', '')
            logger.info(f"🔍 Checking {athlete['name']} (@{username})")
            
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"⚠️  User not found: {username}")
                return []
            
            user_id = user.data.id
            
            # Get current following list
            current_following = self._get_following_list(user_id)
            
            # Get previous following list from cache
            cache_key = f"{athlete['twitter_handle']}"
            previous_following = self.following_cache.get(cache_key, set())
            
            # Detect changes
            changes = []
            
            if previous_following:
                # Detect new follows
                new_follows = current_following - previous_following
                for followed_id in new_follows:
                    followed_user = self._get_user_info(followed_id)
                    if followed_user:
                        changes.append({
                            'type': 'follow',
                            'athlete': athlete['name'],
                            'athlete_handle': athlete['twitter_handle'],
                            'target_name': followed_user['name'],
                            'target_handle': followed_user['handle'],
                            'target_followers': followed_user['followers'],
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Detect unfollows
                unfollows = previous_following - current_following
                for unfollowed_id in unfollows:
                    unfollowed_user = self._get_user_info(unfollowed_id)
                    if unfollowed_user:
                        changes.append({
                            'type': 'unfollow',
                            'athlete': athlete['name'],
                            'athlete_handle': athlete['twitter_handle'],
                            'target_name': unfollowed_user['name'],
                            'target_handle': unfollowed_user['handle'],
                            'target_followers': unfollowed_user['followers'],
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Update cache
            self.following_cache[cache_key] = current_following
            
            if changes:
                logger.info(f"🔥 Found {len(changes)} changes for {athlete['name']}")
            else:
                logger.info(f"✅ No changes for {athlete['name']}")
            
            # Rate limiting delay
            time.sleep(2)
            
            return changes
            
        except tweepy.TooManyRequests:
            logger.warning("⚠️  Rate limit reached, waiting...")
            time.sleep(900)  # Wait 15 minutes
            return []
        except Exception as e:
            logger.error(f"❌ Error checking {athlete['name']}: {e}")
            return []
    
    def _get_following_list(self, user_id: str) -> set:
        """Get set of user IDs that a user is following"""
        following_ids = set()
        
        try:
            # Get following (max 1000 for now to avoid rate limits)
            following = self.client.get_users_following(
                user_id,
                max_results=1000,
                user_fields=['id']
            )
            
            if following.data:
                following_ids = {str(user.id) for user in following.data}
            
            return following_ids
            
        except Exception as e:
            logger.error(f"❌ Error getting following list: {e}")
            return set()
    
    def _get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get basic info about a Twitter user"""
        try:
            user = self.client.get_user(
                id=user_id,
                user_fields=['username', 'name', 'public_metrics']
            )
            
            if user.data:
                return {
                    'name': user.data.name,
                    'handle': f"@{user.data.username}",
                    'followers': user.data.public_metrics['followers_count']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user info: {e}")
            return None
    
    def _simulate_changes(self, athlete: Dict) -> List[Dict]:
        """Simulate changes for demo mode (when no API credentials)"""
        # Return empty list most of the time
        # This is just for testing without actual API
        import random
        
        if random.random() < 0.1:  # 10% chance of simulated change
            return [{
                'type': random.choice(['follow', 'unfollow']),
                'athlete': athlete['name'],
                'athlete_handle': athlete['twitter_handle'],
                'target_name': 'Demo User',
                'target_handle': '@demouser',
                'target_followers': 1000000,
                'timestamp': datetime.now().isoformat()
            }]
        
        return []
