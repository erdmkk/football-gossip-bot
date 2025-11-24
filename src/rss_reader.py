"""
RSS Feed Reader for Football News
Fetches latest football news from multiple sources
"""

import feedparser
import logging
from datetime import datetime
from typing import List, Dict
import time

logger = logging.getLogger(__name__)

class RSSReader:
    """Reads football news from RSS feeds"""
    
    def __init__(self):
        # Popular football news RSS feeds
        self.feeds = [
            {
                'name': 'BBC Sport Football',
                'url': 'http://feeds.bbci.co.uk/sport/football/rss.xml',
                'weight': 1.0
            },
            {
                'name': 'Sky Sports Football',
                'url': 'https://www.skysports.com/rss/12040',
                'weight': 1.0
            },
            {
                'name': 'ESPN FC',
                'url': 'https://www.espn.com/espn/rss/soccer/news',
                'weight': 0.9
            },
            {
                'name': 'Goal.com',
                'url': 'https://www.goal.com/feeds/en/news',
                'weight': 0.8
            },
            {
                'name': 'The Guardian Football',
                'url': 'https://www.theguardian.com/football/rss',
                'weight': 0.9
            }
        ]
        
        self.posted_articles = set()  # Track posted articles to avoid duplicates
    
    def fetch_latest_news(self, max_articles: int = 20) -> List[Dict]:
        """
        Fetch latest news from all RSS feeds
        
        Returns:
            List of news articles with title, summary, link, etc.
        """
        all_articles = []
        
        for feed_info in self.feeds:
            try:
                logger.info(f"📡 Fetching from {feed_info['name']}...")
                
                feed = feedparser.parse(feed_info['url'])
                
                if feed.entries:
                    for entry in feed.entries[:5]:  # Get top 5 from each feed
                        article = {
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', entry.get('description', '')),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'source': feed_info['name'],
                            'weight': feed_info['weight'],
                            'id': entry.get('id', entry.get('link', ''))
                        }
                        
                        # Skip if already posted
                        if article['id'] not in self.posted_articles:
                            all_articles.append(article)
                    
                    logger.info(f"✅ Found {len(feed.entries[:5])} articles from {feed_info['name']}")
                else:
                    logger.warning(f"⚠️  No articles from {feed_info['name']}")
                
                time.sleep(1)  # Be polite to servers
                
            except Exception as e:
                logger.error(f"❌ Error fetching {feed_info['name']}: {e}")
                continue
        
        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        logger.info(f"📰 Total articles fetched: {len(all_articles)}")
        
        return all_articles[:max_articles]
    
    def mark_as_posted(self, article_id: str):
        """Mark an article as posted to avoid duplicates"""
        self.posted_articles.add(article_id)
    
    def get_trending_topics(self, articles: List[Dict]) -> List[str]:
        """Extract trending topics/keywords from articles"""
        keywords = []
        
        for article in articles:
            title = article['title'].lower()
            
            # Extract player names, teams, etc.
            # Simple keyword extraction (can be improved with NLP)
            words = title.split()
            for word in words:
                if len(word) > 4 and word.isalpha():
                    keywords.append(word.capitalize())
        
        # Count frequency
        from collections import Counter
        trending = Counter(keywords).most_common(10)
        
        return [word for word, count in trending if count > 1]
