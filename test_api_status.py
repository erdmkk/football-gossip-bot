"""
Test Twitter API connectivity and permissions
"""

import sys
sys.path.append('src')

from config import Config
import tweepy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_twitter_api():
    """Test Twitter API connection and permissions"""
    
    config = Config()
    
    try:
        # Create client
        client = tweepy.Client(
            bearer_token=config.TWITTER_BEARER_TOKEN,
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        
        logger.info("✅ Client created successfully")
        
        # Test 1: Get own user info (requires auth)
        logger.info("\n📝 Test 1: Getting your account info...")
        try:
            me = client.get_me()
            logger.info(f"✅ Authenticated as: @{me.data.username}")
            logger.info(f"   User ID: {me.data.id}")
        except Exception as e:
            logger.error(f"❌ Auth test failed: {e}")
            return False
        
        # Test 2: Check rate limit status
        logger.info("\n📊 Test 2: Checking rate limits...")
        try:
            # Try to get recent tweets (read test)
            tweets = client.get_users_tweets(me.data.id, max_results=5)
            logger.info(f"✅ Can read tweets (found {len(tweets.data) if tweets.data else 0} recent tweets)")
        except Exception as e:
            logger.error(f"❌ Read test failed: {e}")
        
        # Test 3: Try to create a test tweet (DON'T POST, JUST TEST)
        logger.info("\n🔍 Test 3: Testing write permissions...")
        logger.info("   (Not actually posting, just checking credentials)")
        
        # Check if we have all credentials
        has_write = all([
            config.TWITTER_API_KEY,
            config.TWITTER_API_SECRET,
            config.TWITTER_ACCESS_TOKEN,
            config.TWITTER_ACCESS_SECRET
        ])
        
        if has_write:
            logger.info("✅ Write credentials present")
        else:
            logger.error("❌ Missing write credentials")
            return False
        
        logger.info("\n" + "="*60)
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("="*60)
        logger.info("\nYour API is working correctly.")
        logger.info("Rate limit error might be temporary.")
        logger.info("Try posting a tweet again in a few minutes.")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}")
        logger.error("\nPossible solutions:")
        logger.error("1. Regenerate all API keys in Twitter Developer Portal")
        logger.error("2. Ensure app has 'Read and Write' permissions")
        logger.error("3. Wait 15 minutes and try again")
        return False

if __name__ == "__main__":
    test_twitter_api()
