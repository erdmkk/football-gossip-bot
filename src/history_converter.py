"""
History to Tweet Converter
Converts historical events into clean Turkish tweets
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class HistoryToTweetConverter:
    """Converts historical events into clean Turkish tweets"""
    
    def __init__(self):
        # TÜRKÇE tweet şablonu - Sade ve güçlü
        # Emoji içeriğe göre dinamik seçilecek
        self.template = "{emoji} {year} yılında bugün:\n\n{text}"
        
        # İçerik tipine göre emoji mapping
        self.emoji_map = {
            'war': '⚔️',
            'death': '🕯️', 
            'disaster': '⚠️',
            'politics': '🏛️',
            'science': '🔬',
            'space': '🚀',
            'religion': '✝️',
            'revolution': '✊',
            'explosion': '💥',
            'default': '📅'
        }
    
    def convert_to_tweet(self, event: Dict, details: str = "") -> str:
        """
        Convert historical event to clean Turkish tweet
        Just the event + smart emoji + fixed hashtags
        
        Args:
            event: Dict with year, text, type, etc.
            details: Not used anymore (kept for compatibility)
            
        Returns:
            Tweet text with event + emoji + hashtags
        """
        year = event.get('year', 'Unknown')
        text = event.get('text', '')
        
        # Select emoji based on content
        emoji = self._select_emoji(text, event.get('type', 'event'))
        
        # Generate clean tweet
        tweet = self.template.format(
            emoji=emoji,
            year=year,
            text=text
        )
        
        # Add fixed hashtags
        tweet = self._add_fixed_hashtags(tweet)
        
        logger.info(f"📏 Tweet length: {len(tweet)}/280 chars")
        
        return tweet
    
    def _select_emoji(self, text: str, event_type: str) -> str:
        """Select emoji based on event content"""
        text_lower = text.lower()
        
        # Check for specific keywords
        if any(w in text_lower for w in ['savaş', 'war', 'battle', 'çarpışma', 'muharebe']):
            return self.emoji_map['war']
        elif any(w in text_lower for w in ['öldü', 'died', 'death', 'ölüm', 'öldürüldü', 'idam', 'infaz']):
            return self.emoji_map['death']
        elif any(w in text_lower for w in ['deprem', 'yangın', 'patlama', 'felaket', 'katliam', 'disaster']):
            return self.emoji_map['disaster']
        elif any(w in text_lower for w in ['devrim', 'isyan', 'ayaklanma', 'darbe']):
            return self.emoji_map['revolution']
        elif any(w in text_lower for w in ['kral', 'sultan', 'padişah', 'imparator', 'meclis', 'başkan']):
            return self.emoji_map['politics']
        elif any(w in text_lower for w in ['uzay', 'space', 'moon', 'mars', 'roket']):
            return self.emoji_map['space']
        elif any(w in text_lower for w in ['keşif', 'buluş', 'discovery', 'bilim']):
            return self.emoji_map['science']
        elif any(w in text_lower for w in ['patlama', 'bomba', 'explosion']):
            return self.emoji_map['explosion']
        else:
            return self.emoji_map['default']
    
    def _add_fixed_hashtags(self, tweet: str) -> str:
        """Add fixed hashtags: #TarihteBugün #Tarih"""
        hashtags = "#TarihteBugün #Tarih"
        
        # Always add (should fit since we removed details)
        return f"{tweet}\n\n{hashtags}"


