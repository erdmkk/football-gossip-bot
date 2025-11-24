"""
Automated Football News Bot
Fetches news from RSS feeds and tweets automatically
"""

import time
import schedule
from datetime import datetime, timedelta
import logging
from colorlog import ColoredFormatter
import random

from config import Config
from rss_reader import RSSReader
from news_converter import NewsToTweetConverter
from tweet_generator import TweetGenerator
from database import Database

# Setup colored logging
def setup_logger():
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger

logger = setup_logger()

class FootballNewsBot:
    """Automated football news tweet bot"""
    
    def __init__(self):
        logger.info("🚀 Initializing Football News Bot...")
        
        self.config = Config()
        self.db = Database(self.config.DATABASE_PATH)
        self.rss_reader = RSSReader()
        self.news_converter = NewsToTweetConverter()
        self.tweet_gen = TweetGenerator(self.config)
        
        # Tweet scheduling
        self.tweets_per_day = 15
        self.interval_hours = 24 / self.tweets_per_day  # ~1.6 hours
        self.daily_tweet_count = 0
        self.last_reset = datetime.now().date()
        
        logger.info(f"⏰ Schedule: {self.tweets_per_day} tweets/day")
        logger.info(f"📊 Interval: Every {self.interval_hours:.1f} hours")
        logger.info("✅ Bot initialized successfully!")
    
    def post_news_tweet(self):
        """Fetch news and post a tweet"""
        try:
            # Reset daily counter
            today = datetime.now().date()
            if today != self.last_reset:
                self.daily_tweet_count = 0
                self.last_reset = today
                logger.info("🔄 Daily counter reset")
            
            # Check daily limit
            if self.daily_tweet_count >= self.tweets_per_day:
                logger.warning(f"⏸️  Daily limit reached ({self.tweets_per_day} tweets)")
                return
            
            logger.info("📰 Fetching latest football news...")
            
            # Fetch news
            articles = self.rss_reader.fetch_latest_news(max_articles=10)
            
            if not articles:
                logger.warning("⚠️  No new articles found")
                return
            
            # Pick a random article (for variety)
            article = random.choice(articles)
            
            logger.info(f"📌 Selected: {article['title'][:60]}...")
            logger.info(f"🌐 Source: {article['source']}")
            
            # Convert to tweet
            tweet_text = self.news_converter.convert_to_tweet(article)
            
            logger.info(f"✍️  Generated tweet ({len(tweet_text)} chars)")
            logger.info(f"📝 Content: {tweet_text}")
            
            # Post tweet
            if self.config.AUTO_TWEET:
                success = self.tweet_gen.post_tweet(tweet_text)
                
                if success:
                    # Mark article as posted
                    self.rss_reader.mark_as_posted(article['id'])
                    
                    # Save to database
                    self.db.conn.execute('''
                        INSERT INTO tweets (tweet_text, posted_at)
                        VALUES (?, ?)
                    ''', (tweet_text, datetime.now().isoformat()))
                    self.db.conn.commit()
                    
                    self.daily_tweet_count += 1
                    
                    logger.info(f"✅ Tweet posted! ({self.daily_tweet_count}/{self.tweets_per_day} today)")
                else:
                    logger.error("❌ Failed to post tweet")
            else:
                logger.info("ℹ️  Auto-tweet disabled (demo mode)")
                self.daily_tweet_count += 1
        
        except Exception as e:
            logger.error(f"❌ Error in post_news_tweet: {e}")
    
    def run(self):
        """Start the bot with scheduling"""
        logger.info("=" * 60)
        logger.info("🤖 FOOTBALL NEWS BOT STARTED")
        logger.info("=" * 60)
        logger.info(f"⏰ Posting {self.tweets_per_day} tweets per day")
        logger.info(f"📊 Every {self.interval_hours:.1f} hours")
        logger.info(f"🔄 Next tweet in ~{int(self.interval_hours * 60)} minutes")
        logger.info("=" * 60)
        
        # Post first tweet immediately
        logger.info("🚀 Posting first tweet now...")
        self.post_news_tweet()
        
        # Schedule regular tweets
        # Convert hours to minutes for better precision
        interval_minutes = int(self.interval_hours * 60)
        schedule.every(interval_minutes).minutes.do(self.post_news_tweet)
        
        logger.info(f"✅ Scheduled to run every {interval_minutes} minutes")
        logger.info("🤖 Bot is running! Press Ctrl+C to stop.")
        logger.info("")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("=" * 60)
            logger.info("👋 Bot stopped by user")
            logger.info(f"📊 Tweets posted today: {self.daily_tweet_count}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    bot = FootballNewsBot()
    bot.run()
