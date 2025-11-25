"""
Wikipedia "On This Day" History Fetcher
Fetches historical events that happened on today's date
"""

import requests
import logging
from datetime import datetime
from typing import List, Dict
import random

logger = logging.getLogger(__name__)

class HistoryFetcher:
    """Fetches historical events from Wikipedia API"""
    
    def __init__(self):
        self.base_url = "https://api.wikimedia.org/feed/v1/wikipedia/tr/onthisday"  # Türkçe Wikipedia
        self.headers = {
            'User-Agent': 'HistoryBot/1.0 (Educational Purpose)'
        }
        
        self.posted_events = set()  # Track posted events to avoid duplicates
        
        # Keywords for prioritizing dramatic events
        self.priority_keywords = [
            'savaş', 'öldü', 'öldürüldü', 'suikast', 'katliam', 'devrim', 
            'İmparator', 'Kral', 'Sultan', 'mitoloji', 'tanrı', 'efsane',
            'felaket', 'deprem', 'yangın', 'patlama', 'çöküş', 'yıkım',
            'infaz', 'idam', 'isyan', 'darbe', 'istila', 'kuşatma',
            'Napoleon', 'Hitler', 'Stalin', 'Atatürk', 'Fatih', 'Kanuni'
        ]
    
    def fetch_today_events(self) -> List[Dict]:
        """
        Fetch events that happened on today's date in history
        
        Returns:
            List of historical events with year, text, and details
        """
        today = datetime.now()
        month = today.month
        day = today.day
        
        # Wikipedia API endpoint: /all/MM/DD
        url = f"{self.base_url}/all/{month}/{day}"
        
        try:
            logger.info(f"📡 Fetching events for {month}/{day} from Wikipedia...")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            all_events = []
            
            # Get events (things that happened)
            if 'events' in data:
                for event in data['events']:
                    all_events.append({
                        'type': 'event',
                        'year': event.get('year', 'Unknown'),
                        'text': event.get('text', ''),
                        'pages': event.get('pages', []),
                        'date': f"{month}/{day}"
                    })
            
            # Get births (famous people born)
            if 'births' in data:
                for birth in data['births'][:5]:  # Limit births
                    all_events.append({
                        'type': 'birth',
                        'year': birth.get('year', 'Unknown'),
                        'text': birth.get('text', ''),
                        'pages': birth.get('pages', []),
                        'date': f"{month}/{day}"
                    })
            
            # Get deaths (famous people died)
            if 'deaths' in data:
                for death in data['deaths'][:5]:  # Limit deaths
                    all_events.append({
                        'type': 'death',
                        'year': death.get('year', 'Unknown'),
                        'text': death.get('text', ''),
                        'pages': death.get('pages', []),
                        'date': f"{month}/{day}"
                    })
            
            logger.info(f"✅ Found {len(all_events)} historical events")
            
            # Filter out already posted
            new_events = [e for e in all_events if self._get_event_id(e) not in self.posted_events]
            
            logger.info(f"📰 {len(new_events)} new events available")
            
            return new_events
            
        except requests.RequestException as e:
            logger.error(f"❌ Error fetching from Wikipedia: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return []
    
    def get_event_details(self, event: Dict) -> str:
        """
        Get additional details about an event from Turkish Wikipedia
        Tries to get relevant info from the event's own page
        
        Args:
            event: Event dictionary
            
        Returns:
            Summary text with more details in Turkish
        """
        if not event.get('pages'):
            return ""
        
        try:
            # Get the first related page
            page = event['pages'][0]
            page_title = page.get('normalizedtitle', page.get('title', ''))
            
            # Try Turkish Wikipedia first
            extract_url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{page_title}"
            
            response = requests.get(extract_url, headers=self.headers, timeout=10)
            
            # If Turkish page doesn't exist, try English
            if response.status_code == 404:
                extract_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
                response = requests.get(extract_url, headers=self.headers, timeout=10)
            
            response.raise_for_status()
            data = response.json()
            
            # Get extract (summary)
            extract = data.get('extract', '')
            
            # Clean and return full extract (converter will handle sizing)
            if extract:
                # Remove parenthetical notes
                import re
                extract = re.sub(r'\([^)]*\)', '', extract)
                extract = ' '.join(extract.split())  # Clean whitespace
                
                return extract
            
            return ""
            
        except Exception as e:
            logger.debug(f"Could not fetch details: {e}")
            return ""
    
    def mark_as_posted(self, event: Dict):
        """Mark an event as posted to avoid duplicates"""
        event_id = self._get_event_id(event)
        self.posted_events.add(event_id)
    
    def _get_event_id(self, event: Dict) -> str:
        """Generate unique ID for an event"""
        return f"{event['type']}_{event['year']}_{event['text'][:50]}"
    
    def select_interesting_event(self, events: List[Dict]) -> Dict:
        """
        Select dramatic/mythological/chaotic event
        Priority: wars, deaths, mythology, catastrophes, famous figures
        Returns random selection from TOP 15 most important events
        """
        if not events:
            return None
        
        # Score ALL events
        scored_events = []
        for event in events:
            text = event.get('text', '').lower()
            year = event.get('year', 0)
            event_type = event.get('type', '')
            
            # Calculate importance score
            score = 0
            
            # Keyword matching - HIGH priority
            for keyword in self.priority_keywords:
                if keyword.lower() in text:
                    score += 10
            
            # Type bonuses
            if event_type == 'death':
                score += 15  # Deaths are highly dramatic
            elif event_type == 'event':
                score += 5
            
            # Era bonuses - prioritize dramatic periods
            try:
                year_int = int(year)
                if 1914 <= year_int <= 1945:  # World Wars
                    score += 20
                elif year_int < 500:  # Ancient/mythological
                    score += 15
                elif 500 <= year_int <= 1500:  # Medieval
                    score += 10
                elif 1900 <= year_int <= 2000:  # Modern history
                    score += 8
            except:
                pass
                
            scored_events.append((score, event))
        
        # Sort by score (highest first)
        scored_events.sort(reverse=True, key=lambda x: x[0])
        
        # Take TOP 15 most important events
        top_15 = scored_events[:15]
        
        logger.info(f"🏆 Selected top 15 events from {len(scored_events)} total")
        logger.debug(f"Top event score: {top_15[0][0] if top_15 else 0}")
        
        # Randomly select from top 15
        if top_15:
            selected = random.choice(top_15)[1]
            
            # Try to get detailed summary
            detailed = self.get_event_details(selected)
            if detailed:
                selected['detailed_summary'] = detailed
            
            return selected
        
        return random.choice(events)
