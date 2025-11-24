"""
News to Tweet Converter
Converts RSS news articles into viral tweet format
"""

import random
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class NewsToTweetConverter:
    """Converts news articles into engaging tweet content"""
    
    def __init__(self):
        # Viral tweet templates with more context
        self.breaking_templates = [
            "🚨 BREAKING NEWS!\n\n{title}\n\n{context}\n\n{hook}",
            "⚡ JUST IN: {title}\n\n{detail}\n\n{reaction}",
            "🔥 HUGE DEVELOPMENT!\n\n{title}\n\n{insight}\n\n{commentary}",
            "👀 You won't believe this...\n\n{title}\n\n{opinion}\n\n{question}",
            "💥 MASSIVE: {title}\n\n{extra}\n\n{drama}",
            "📰 LATEST: {title}\n\n{background}\n\n{hook}",
        ]
        
        self.transfer_templates = [
            "🚨 TRANSFER ALERT!\n\n{title}\n\n{rumor}\n\n{speculation}",
            "💰 BIG MONEY MOVE?\n\n{title}\n\n{details}\n\n{question}",
            "✈️ HERE WE GO? {title}\n\n{status}\n\n{excitement}",
            "📝 CONTRACT TALK: {title}\n\n{figures}\n\n{question}",
        ]
        
        self.match_templates = [
            "⚽ MATCH REPORT!\n\n{title}\n\n{highlights}\n\n{reaction}",
            "🏆 WHAT A GAME!\n\n{title}\n\n{stats}\n\n{celebration}",
            "😱 UNBELIEVABLE!\n\n{title}\n\n{context}\n\n{shock}",
            "🎯 FINAL SCORE: {title}\n\n{summary}\n\n{reaction}",
        ]
        
        # Enhanced hooks and reactions
        self.hooks = [
            "This is absolutely massive! 🔥",
            "Football Twitter is going to explode! 🤯",
            "Nobody saw this coming! 😱",
            "What a turn of events! 🌪️",
            "The drama never stops in football! 🍿",
            "This could change everything! ⚡",
            "Incredible scenes! 🎭",
        ]
        
        self.reactions = [
            "What are your thoughts on this? 🤔",
            "Drop your reaction below! 👇",
            "Who predicted this? 🙋‍♂️",
            "This changes the whole landscape! ⚡",
            "Absolute scenes! 🔥",
            "Is this really happening? 😮",
            "Game changer alert! 🚨",
        ]
        
        self.questions = [
            "What do you make of this? 💭",
            "Good move or disaster? 🤔",
            "Will this actually happen? 👀",
            "Your predictions below! 🔮",
            "Who's involved next? 👇",
            "Rate this on a scale of 1-10! 📊",
        ]
        
        # Contextual additions
        self.contexts = [
            "Sources close to the club confirm this developing story.",
            "This comes as a major surprise to fans and pundits alike.",
            "Breaking developments in the last hour suggest this is real.",
            "Multiple reliable sources are now reporting this.",
            "This has been rumored for weeks, now it's confirmed!",
        ]
        
        self.details = [
            "According to reports from reliable insiders.",
            "This could reshape the entire season.",
            "Fans are already reacting massively online.",
            "The announcement has sent shockwaves through the sport.",
        ]
        
        # Keywords for categorization
        self.transfer_keywords = ['transfer', 'deal', 'bid', 'sign', 'contract', 'move', 'agree']
        self.match_keywords = ['win', 'lose', 'goal', 'score', 'match', 'game', 'victory', 'defeat']
        self.drama_keywords = ['sack', 'fire', 'leave', 'quit', 'row', 'clash', 'crisis', 'emergency']
    
    def convert_to_tweet(self, article: Dict) -> str:
        """
        Convert news article to engaging tweet
        
        Args:
            article: Dict with title, summary, etc.
            
        Returns:
            Tweet text (max 280 chars)
        """
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        # Clean title (remove source names, etc.)
        title = self._clean_title(title)
        
        # Determine category
        category = self._categorize_news(title, summary)
        
        # Select appropriate template and extras
        if category == 'transfer':
            template = random.choice(self.transfer_templates)
            extra_context = random.choice(self.contexts)
        elif category == 'match':
            template = random.choice(self.match_templates)
            extra_context = random.choice(self.details)
        elif category == 'drama':
            template = random.choice(self.breaking_templates)
            extra_context = random.choice(self.contexts)
        else:
            template = random.choice(self.breaking_templates)
            extra_context = random.choice(self.details)
        
        # Generate tweet with rich content
        tweet = template.format(
            title=title,
            hook=random.choice(self.hooks),
            reaction=random.choice(self.reactions),
            question=random.choice(self.questions),
            commentary=random.choice(self.hooks),
            drama=random.choice(self.hooks),
            speculation=random.choice(self.questions),
            excitement=random.choice(self.reactions),
            celebration=random.choice(self.reactions),
            shock=random.choice(self.hooks),
            context=extra_context,
            detail=random.choice(self.details),
            insight=random.choice(self.contexts),
            opinion=random.choice(self.details),
            extra=random.choice(self.contexts),
            background=random.choice(self.details),
            rumor=random.choice(self.contexts),
            details=random.choice(self.details),
            status=random.choice(self.contexts),
            figures=random.choice(self.details),
            highlights=random.choice(self.details),
            stats=random.choice(self.contexts),
            summary=random.choice(self.details)
        )
        
        # Add smart hashtags based on content
        tweet = self._add_smart_hashtags(tweet, title, summary, category)
        
        # Ensure under 280 characters
        if len(tweet) > 280:
            # Shorten by removing extra context
            tweet = self._shorten_tweet(template, title, category)
        
        # Final trim
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        return tweet
    
    def _clean_title(self, title: str) -> str:
        """Remove unnecessary parts from title"""
        # Remove source names in brackets
        title = re.sub(r'\[.*?\]', '', title)
        title = re.sub(r'\(.*?\)', '', title)
        
        # Remove common prefixes
        prefixes = ['LIVE:', 'BREAKING:', 'UPDATE:', 'EXCLUSIVE:']
        for prefix in prefixes:
            title = title.replace(prefix, '')
        
        return title.strip()
    
    def _categorize_news(self, title: str, summary: str) -> str:
        """Categorize news article"""
        text = (title + ' ' + summary).lower()
        
        # Check for transfer news
        if any(keyword in text for keyword in self.transfer_keywords):
            return 'transfer'
        
        # Check for match news
        if any(keyword in text for keyword in self.match_keywords):
            return 'match'
        
        # Check for drama
        if any(keyword in text for keyword in self.drama_keywords):
            return 'drama'
        
        return 'general'
    
    def _add_hashtags(self, tweet: str, title: str) -> str:
        """Add relevant hashtags to tweet"""
        # Extract team names (basic approach)
        teams = self._extract_teams(title)
        
        hashtags = []
        
        # Add team hashtags
        for team in teams[:1]:  # Max 1 team hashtag
            hashtag = f"#{team.replace(' ', '')}"
            if len(hashtag) < 20:  # Reasonable length
                hashtags.append(hashtag)
        
        # Add general hashtag
        hashtags.append('#FootballNews')
        
        # Combine if space allows
        hashtag_str = ' '.join(hashtags[:2])
        
        if len(tweet) + len(hashtag_str) + 2 <= 280:
            return f"{tweet}\n\n{hashtag_str}"
        
        return tweet
    
    def _add_smart_hashtags(self, tweet: str, title: str, summary: str, category: str) -> str:
        """Add smart, context-aware hashtags"""
        hashtags = []
        text = (title + ' ' + summary).lower()
        
        # Extract team names
        teams = self._extract_teams(title)
        
        # Category-specific hashtags
        if category == 'transfer':
            hashtags.append('#TransferNews')
            if 'rumor' in text or 'rumour' in text:
                hashtags.append('#TransferRumors')
        elif category == 'match':
            hashtags.append('#MatchDay')
            if 'goal' in text or 'score' in text:
                hashtags.append('#Goals')
        elif category == 'drama':
            hashtags.append('#FootballDrama')
        
        # Player-specific hashtags
        star_players = ['Ronaldo', 'Messi', 'Haaland', 'Mbappe', 'Neymar', 'Salah', 'Kane']
        for player in star_players:
            if player.lower() in text:
                hashtags.append(f'#{player}')
                break
        
        # Team hashtags (max 1)
        if teams:
            team_tag = f"#{teams[0].replace(' ', '')}"
            if len(team_tag) < 20:
                hashtags.append(team_tag)
        
        # General football hashtag
        if not hashtags:
            hashtags.append('#Football')
        
        # Add hashtags (max 3 for readability)
        selected_tags = hashtags[:3]
        hashtag_str = ' '.join(selected_tags)
        
        if len(tweet) + len(hashtag_str) + 2 <= 280:
            return f"{tweet}\n\n{hashtag_str}"
        elif len(tweet) + len(selected_tags[0]) + 2 <= 280:
            return f"{tweet}\n\n{selected_tags[0]}"
        
        return tweet
    
    def _shorten_tweet(self, template: str, title: str, category: str) -> str:
        """Create shorter version of tweet"""
        # Simpler templates for when we need to shorten
        if category == 'transfer':
            short = f"🚨 {title}\n\n{random.choice(self.questions)}"
        elif category == 'match':
            short = f"⚽ {title}\n\n{random.choice(self.reactions)}"
        else:
            short = f"🔥 {title}\n\n{random.choice(self.hooks)}"
        
        return short
    
    def _extract_teams(self, text: str) -> list:
        """Extract team names from text"""
        # Common football teams
        teams = [
            'Manchester United', 'Manchester City', 'Liverpool', 'Chelsea', 
            'Arsenal', 'Tottenham', 'Real Madrid', 'Barcelona', 'Bayern Munich',
            'PSG', 'Juventus', 'AC Milan', 'Inter Milan', 'Atletico Madrid'
        ]
        
        found_teams = []
        for team in teams:
            if team.lower() in text.lower():
                found_teams.append(team)
        
        return found_teams
