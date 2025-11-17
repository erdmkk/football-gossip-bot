"""
Database operations for Football Gossip Bot
Stores follow/unfollow changes and historical data
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """SQLite database handler for gossip tracking"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            cursor = self.conn.cursor()
            
            # Create changes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    athlete TEXT NOT NULL,
                    athlete_handle TEXT NOT NULL,
                    target_name TEXT NOT NULL,
                    target_handle TEXT NOT NULL,
                    target_followers INTEGER,
                    drama_score INTEGER,
                    timestamp TEXT NOT NULL,
                    tweeted BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create athletes snapshot table (for tracking following lists)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS athlete_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    athlete_handle TEXT NOT NULL,
                    following_count INTEGER,
                    followers_count INTEGER,
                    snapshot_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create tweets table (for posted tweets)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_id INTEGER,
                    tweet_text TEXT NOT NULL,
                    tweet_id TEXT,
                    posted_at TEXT NOT NULL,
                    engagement_score INTEGER DEFAULT 0,
                    FOREIGN KEY (change_id) REFERENCES changes(id)
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_athlete_handle 
                ON changes(athlete_handle)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON changes(timestamp)
            ''')
            
            self.conn.commit()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def save_change(self, change: Dict) -> Optional[int]:
        """
        Save a follow/unfollow change to database
        
        Args:
            change: Dict with change details
            
        Returns:
            ID of inserted record or None
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO changes (
                    type, athlete, athlete_handle, target_name, 
                    target_handle, target_followers, drama_score, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                change['type'],
                change['athlete'],
                change['athlete_handle'],
                change['target_name'],
                change['target_handle'],
                change.get('target_followers', 0),
                change.get('drama_score', 0),
                change['timestamp']
            ))
            
            self.conn.commit()
            change_id = cursor.lastrowid
            
            logger.info(f"✅ Change saved to database (ID: {change_id})")
            return change_id
            
        except Exception as e:
            logger.error(f"❌ Error saving change: {e}")
            return None
    
    def save_tweet(self, change_id: int, tweet_text: str, tweet_id: str = None) -> bool:
        """
        Save posted tweet to database
        
        Args:
            change_id: ID of the change that triggered the tweet
            tweet_text: The tweet content
            tweet_id: Twitter tweet ID (if available)
            
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO tweets (change_id, tweet_text, tweet_id, posted_at)
                VALUES (?, ?, ?, ?)
            ''', (change_id, tweet_text, tweet_id, datetime.now().isoformat()))
            
            # Mark change as tweeted
            cursor.execute('''
                UPDATE changes SET tweeted = 1 WHERE id = ?
            ''', (change_id,))
            
            self.conn.commit()
            logger.info(f"✅ Tweet saved to database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving tweet: {e}")
            return False
    
    def get_recent_changes(self, limit: int = 50) -> List[Dict]:
        """Get recent changes from database"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT * FROM changes 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Error fetching changes: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Total changes
            cursor.execute('SELECT COUNT(*) as total FROM changes')
            total = cursor.fetchone()['total']
            
            # Follows vs unfollows
            cursor.execute('SELECT type, COUNT(*) as count FROM changes GROUP BY type')
            type_counts = {row['type']: row['count'] for row in cursor.fetchall()}
            
            # Total tweets
            cursor.execute('SELECT COUNT(*) as total FROM tweets')
            total_tweets = cursor.fetchone()['total']
            
            # Top athletes by activity
            cursor.execute('''
                SELECT athlete, COUNT(*) as changes 
                FROM changes 
                GROUP BY athlete 
                ORDER BY changes DESC 
                LIMIT 5
            ''')
            top_athletes = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_changes': total,
                'follows': type_counts.get('follow', 0),
                'unfollows': type_counts.get('unfollow', 0),
                'total_tweets': total_tweets,
                'top_athletes': top_athletes
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching stats: {e}")
            return {}
    
    def check_duplicate(self, change: Dict, hours: int = 24) -> bool:
        """
        Check if similar change was recorded recently
        
        Args:
            change: Change to check
            hours: Time window in hours
            
        Returns:
            True if duplicate found
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM changes 
                WHERE athlete_handle = ? 
                AND target_handle = ? 
                AND type = ?
                AND datetime(timestamp) > datetime('now', '-' || ? || ' hours')
            ''', (
                change['athlete_handle'],
                change['target_handle'],
                change['type'],
                hours
            ))
            
            result = cursor.fetchone()
            return result['count'] > 0
            
        except Exception as e:
            logger.error(f"❌ Error checking duplicate: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
