"""
Automated History Bot
Posts historical events that happened on today's date
"""

import time
import schedule
from datetime import datetime, timedelta
import logging
from colorlog import ColoredFormatter
import random

from config import Config
from history_fetcher import HistoryFetcher
from history_converter import HistoryToTweetConverter
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

class HistoryBot:
    """Automated bot that tweets historical events during peak hours (17:00-21:00)"""
    
    def __init__(self):
        logger.info("🚀 Initializing History Bot...")
        
        self.config = Config()
        self.db = Database(self.config.DATABASE_PATH)
        self.history_fetcher = HistoryFetcher()
        self.history_converter = HistoryToTweetConverter()
        self.tweet_gen = TweetGenerator(self.config)
        
        # Tweet scheduling - 12:00-19:30, every 30 mins
        self.tweets_per_day = 15  # 30 min apart = 15 tweets in 7.5 hours
        self.peak_start_hour = 12
        self.peak_start_minute = 0
        self.peak_end_hour = 19
        self.peak_end_minute = 30
        
        # Tweet every 30 minutes
        self.interval_minutes = 30
        
        self.daily_tweet_count = 0
        self.last_reset = datetime.now().date()
        
        logger.info(f"⏰ Active Hours: {self.peak_start_hour}:{self.peak_start_minute:02d}-{self.peak_end_hour}:00")
        logger.info(f"📊 Schedule: {self.tweets_per_day} tweets during active hours")
        logger.info(f"⏱️  Interval: Every {self.interval_minutes} minutes")
        logger.info("✅ Bot initialized successfully!")
    
    def is_peak_hour(self):
        """Check if current time is within active hours (09:10-21:10)"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Check if after 09:10
        if current_hour < self.peak_start_hour:
            return False
        elif current_hour == self.peak_start_hour and current_minute < self.peak_start_minute:
            return False
        
        # Check if before 21:10
        if current_hour > self.peak_end_hour:
            return False
        elif current_hour == self.peak_end_hour and current_minute >= self.peak_end_minute:
            return False
            
        return True
    
    def post_history_tweet(self):
        """Fetch historical event and post a tweet"""
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
            
            logger.info("📚 Fetching historical events for today...")
            
            # Fetch events
            events = self.history_fetcher.fetch_today_events()
            
            if not events:
                logger.warning("⚠️  No events found for today")
                return
            
            # Select interesting event
            event = self.history_fetcher.select_interesting_event(events)
            
            if not event:
                logger.warning("⚠️  Could not select event")
                return
            
            logger.info(f"📌 Selected: {event['text'][:80]}...")
            logger.info(f"📅 Year: {event['year']}")
            logger.info(f"📖 Type: {event['type']}")
            
            # Get additional details
            details = self.history_fetcher.get_event_details(event)
            
            if details:
                logger.info(f"📝 Got details: {details[:100]}...")
            
            # Convert to tweet
            tweet_text = self.history_converter.convert_to_tweet(event, details)
            
            logger.info(f"✍️  Generated tweet ({len(tweet_text)} chars)")
            logger.info(f"📝 Content:\n{tweet_text}")
            logger.info("─" * 60)
            
            # Post tweet
            if self.config.AUTO_TWEET:
                success = self.tweet_gen.post_tweet(tweet_text)
                
                if success:
                    # Mark event as posted
                    self.history_fetcher.mark_as_posted(event)
                    
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
            logger.error(f"❌ Error in post_history_tweet: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Start the bot - posts at 12:00, then every 30 minutes until 19:30"""
        logger.info("=" * 60)
        logger.info("📜 HISTORY BOT STARTED")
        logger.info("=" * 60)
        logger.info(f"📅 Today: {datetime.now().strftime('%B %d, %Y')}")
        logger.info(f"⏰ Active Hours: 12:00-19:30")
        logger.info(f"📊 Posting 15 tweets during the day")
        logger.info(f"⏱️  Every 30 minutes")
        logger.info("=" * 60)
        
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Check if we're within active hours
        is_active = False
        if current_hour > self.peak_start_hour or (current_hour == self.peak_start_hour and current_minute >= self.peak_start_minute):
            if current_hour < self.peak_end_hour or (current_hour == self.peak_end_hour and current_minute <= self.peak_end_minute):
                is_active = True
        
        if is_active:
            # We're in active hours - post immediately
            logger.info("🚀 We're in active hours! Posting first tweet now...")
            logger.info("")
            self.post_history_tweet()
        else:
            # Not in active hours - wait
            if current_hour < self.peak_start_hour or (current_hour == self.peak_start_hour and current_minute < self.peak_start_minute):
                logger.info(f"⏰ Waiting for active hours to start at 12:00")
            else:
                logger.info(f"⏰ Active hours ended for today. Will resume tomorrow at 12:00")
        
        # Schedule regular tweets every 30 minutes
        schedule.every(self.interval_minutes).minutes.do(self.post_history_tweet)
        
        logger.info("")
        logger.info(f"✅ Scheduled to post every {self.interval_minutes} minutes")
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
    bot = HistoryBot()
    bot.run()
