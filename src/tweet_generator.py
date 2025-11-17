"""
Tweet Generator for Football Gossip Bot
Creates engaging tweet content from follow/unfollow events
"""

import tweepy
import random
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class TweetGenerator:
    """Generates and posts engaging tweets about football gossip"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        
        # Initialize Twitter API for posting
        if config.is_configured():
            try:
                self.client = tweepy.Client(
                    bearer_token=config.TWITTER_BEARER_TOKEN,
                    consumer_key=config.TWITTER_API_KEY,
                    consumer_secret=config.TWITTER_API_SECRET,
                    access_token=config.TWITTER_ACCESS_TOKEN,
                    access_token_secret=config.TWITTER_ACCESS_SECRET
                )
                logger.info("✅ Tweet Generator initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twitter client: {e}")
        else:
            logger.warning("⚠️  Running in demo mode (no actual tweets will be posted)")
    
    def generate(self, change: Dict, athlete: Dict) -> str:
        """
        Generate engaging tweet content from a follow/unfollow change
        
        Args:
            change: Dict with change details (type, athlete, target, etc.)
            athlete: Dict with athlete info
            
        Returns:
            Tweet text (max 280 characters)
        """
        change_type = change['type']
        athlete_name = change['athlete']
        target_name = change['target_name']
        target_handle = change['target_handle']
        drama_score = change.get('drama_score', 0)
        
        if change_type == 'unfollow':
            tweet = self._generate_unfollow_tweet(
                athlete_name, target_name, target_handle, drama_score
            )
        else:  # follow
            tweet = self._generate_follow_tweet(
                athlete_name, target_name, target_handle, drama_score
            )
        
        # Add hashtags
        tweet = self._add_hashtags(tweet, athlete_name, target_name)
        
        # Ensure it's under 280 characters
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        return tweet
    
    def _generate_unfollow_tweet(self, athlete: str, target: str, handle: str, score: int) -> str:
        """Generate tweet for unfollow event"""
        templates = [
            f"🚨 JUST IN: {athlete} just UNFOLLOWED {target}!\n\nWhat happened? 👀🍿",
            f"⚡ DRAMA ALERT: {athlete} has unfollowed {target} ({handle})\n\nTrouble in paradise? 🤔",
            f"👀 {athlete} quietly unfollowed {target}\n\nThe plot thickens... 🍿",
            f"🔥 BREAKING: {athlete} is no longer following {target}\n\nSomething went down! 👀",
            f"💥 {athlete} unfollowed {target}!\n\nWho else noticed this? 🕵️",
            f"🚨 {athlete} just hit the unfollow button on {target}\n\nDrama incoming! 🍿👀",
        ]
        
        # Higher drama = more dramatic template
        if score > 70:
            templates = [
                f"🚨🚨🚨 MAJOR DRAMA: {athlete} UNFOLLOWED {target}!\n\nThis is HUGE! 🔥👀🍿",
                f"💣 BOMBSHELL: {athlete} just unfollowed {target} ({handle})\n\nFootball Twitter is NOT ready for this! 🤯",
            ]
        
        return random.choice(templates)
    
    def _generate_follow_tweet(self, athlete: str, target: str, handle: str, score: int) -> str:
        """Generate tweet for follow event"""
        templates = [
            f"⚡ {athlete} just followed {target}!\n\nInteresting... 👀",
            f"👀 {athlete} started following {target} ({handle})\n\nNew bromance incoming? 🤝",
            f"🔔 {athlete} is now following {target}\n\nTransfer hint? 🤔",
            f"✨ {athlete} followed {target}!\n\nWhat does this mean? 👀",
            f"📱 {athlete} just hit that follow button on {target}\n\nSomething brewing? ☕",
        ]
        
        # Special templates for high-profile follows
        if score > 60:
            templates = [
                f"🚨 {athlete} just followed {target}!\n\nThe GOATs recognizing GOATs 🐐🤝🐐",
                f"⚡ HUGE: {athlete} started following {target} ({handle})\n\nFootball fans, pay attention! 👀",
            ]
        
        return random.choice(templates)
    
    def _add_hashtags(self, tweet: str, athlete: str, target: str) -> str:
        """Add relevant hashtags to tweet"""
        hashtags = []
        
        # Athlete-specific hashtags
        athlete_tags = {
            'Cristiano Ronaldo': ['CR7', 'Ronaldo'],
            'Lionel Messi': ['Messi', 'LeoMessi'],
            'Kylian Mbappé': ['Mbappe', 'KylianMbappe'],
            'Erling Haaland': ['Haaland'],
            'Neymar': ['NeymarJr', 'Neymar'],
            'Mohamed Salah': ['Salah', 'MoSalah'],
        }
        
        # Add athlete tags
        for key, tags in athlete_tags.items():
            if key in athlete:
                hashtags.extend([f'#{tag}' for tag in tags[:1]])  # Add one tag
                break
        
        # Add general tags
        hashtags.append('#FootballTwitter')
        
        # Combine tweet with hashtags (if space allows)
        hashtag_str = ' '.join(hashtags[:2])  # Max 2 hashtags
        
        if len(tweet) + len(hashtag_str) + 2 <= 280:
            return f"{tweet}\n\n{hashtag_str}"
        
        return tweet
    
    def post_tweet(self, text: str) -> bool:
        """
        Post a tweet to Twitter
        
        Args:
            text: Tweet text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.info(f"📝 Demo mode - Would tweet: {text}")
            return True
        
        try:
            response = self.client.create_tweet(text=text)
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"✅ Tweet posted successfully! ID: {tweet_id}")
                logger.info(f"📝 Content: {text}")
                return True
            else:
                logger.error("❌ Failed to post tweet - no response data")
                return False
                
        except tweepy.TooManyRequests:
            logger.error("❌ Rate limit exceeded - cannot post tweet")
            return False
        except tweepy.Forbidden as e:
            logger.error(f"❌ Forbidden - check API permissions: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error posting tweet: {e}")
            return False
    
    def post_test_tweet(self) -> bool:
        """Post a test tweet to verify API connection"""
        test_text = f"🤖 Football Gossip Bot is live! Testing at {datetime.now().strftime('%H:%M')} ⚽"
        return self.post_tweet(test_text)
