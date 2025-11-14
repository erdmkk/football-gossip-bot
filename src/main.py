#!/usr/bin/env python3
"""
Football Gossip Bot - Main Application
Tracks football stars' Twitter activities and generates viral content
"""

import time
import schedule
from datetime import datetime
from colorlog import ColoredFormatter
import logging

from config import Config
from tracker import FollowTracker
from tweet_generator import TweetGenerator
from database import Database
from drama_scorer import DramaScorer

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

class FootballGossipBot:
    def __init__(self):
        logger.info("🚀 Initializing Football Gossip Bot...")
        
        self.config = Config()
        self.db = Database(self.config.DATABASE_PATH)
        self.tracker = FollowTracker(self.config)
        self.tweet_gen = TweetGenerator(self.config)
        self.scorer = DramaScorer()
        
        logger.info("✅ Bot initialized successfully!")
    
    def check_and_tweet(self):
        """Main bot loop - check for changes and tweet"""
        logger.info("🔍 Checking for new gossip...")
        
        try:
            # Get all tracked athletes
            athletes = self.config.get_athletes()
            logger.info(f"📊 Tracking {len(athletes)} athletes")
            
            changes_found = 0
            tweets_posted = 0
            
            for athlete in athletes:
                try:
                    # Check for follow/unfollow changes
                    changes = self.tracker.check_athlete(athlete)
                    
                    if changes:
                        changes_found += len(changes)
                        logger.info(f"🔥 Found {len(changes)} changes for {athlete['name']}")
                        
                        for change in changes:
                            # Calculate drama score
                            drama_score = self.scorer.calculate_score(change, athlete)
                            change['drama_score'] = drama_score
                            
                            logger.info(f"📊 Drama Score: {drama_score}/100")
                            
                            # Save to database
                            self.db.save_change(change)
                            
                            # Tweet if drama score is high enough
                            if drama_score >= self.config.MIN_DRAMA_SCORE:
                                if self.config.AUTO_TWEET:
                                    tweet_text = self.tweet_gen.generate(change, athlete)
                                    success = self.tweet_gen.post_tweet(tweet_text)
                                    
                                    if success:
                                        tweets_posted += 1
                                        logger.info(f"✅ Tweet posted: {tweet_text[:50]}...")
                                    else:
                                        logger.error("❌ Failed to post tweet")
                                else:
                                    logger.info("ℹ️  Auto-tweet disabled, skipping post")
                            else:
                                logger.info(f"⏭️  Drama score too low ({drama_score} < {self.config.MIN_DRAMA_SCORE}), skipping")
                    
                    # Respect rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error checking {athlete.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"✨ Check complete! Changes: {changes_found}, Tweets: {tweets_posted}")
            
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
    
    def run(self):
        """Start the bot with scheduling"""
        logger.info(f"⏰ Starting bot with {self.config.CHECK_INTERVAL_MINUTES} minute intervals")
        
        # Run immediately on start
        self.check_and_tweet()
        
        # Schedule regular checks
        schedule.every(self.config.CHECK_INTERVAL_MINUTES).minutes.do(self.check_and_tweet)
        
        logger.info("🤖 Bot is running! Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    bot = FootballGossipBot()
    bot.run()