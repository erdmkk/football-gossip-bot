"""
Drama Score Calculator for Football Gossip Bot
Calculates viral potential of follow/unfollow events
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class DramaScorer:
    """Calculates drama/viral potential score for gossip events"""
    
    def __init__(self):
        # Rival teams mapping (for extra drama points)
        self.rivalries = {
            'Real Madrid': ['Barcelona', 'Atletico Madrid'],
            'Barcelona': ['Real Madrid'],
            'Manchester United': ['Manchester City', 'Liverpool'],
            'Manchester City': ['Manchester United', 'Liverpool'],
            'Liverpool': ['Manchester United', 'Manchester City', 'Everton'],
            'Arsenal': ['Tottenham'],
            'Tottenham': ['Arsenal'],
            'AC Milan': ['Inter Milan'],
            'Inter Milan': ['AC Milan'],
            'Juventus': ['Inter Milan', 'AC Milan'],
            'Paris Saint-Germain': ['Marseille'],
            'Bayern Munich': ['Borussia Dortmund'],
            'Borussia Dortmund': ['Bayern Munich'],
        }
        
        # High-profile players for extra points
        self.superstar_keywords = [
            'Ronaldo', 'Messi', 'Neymar', 'Mbappé', 'Haaland',
            'Salah', 'Kane', 'Benzema', 'Lewandowski', 'De Bruyne',
            'Vinicius', 'Bellingham', 'Pele', 'Maradona'
        ]
        
        # Controversial figures
        self.controversial_keywords = [
            'Piers Morgan', 'Joey Barton', 'Zlatan', 'Mourinho',
            'Roy Keane', 'Cristiano', 'Tebas', 'FIFA', 'UEFA'
        ]
    
    def calculate_score(self, change: Dict, athlete: Dict) -> int:
        """
        Calculate drama score (0-100) for a follow/unfollow event
        
        Higher score = more viral potential
        
        Scoring factors:
        - Unfollow vs Follow (unfollows are more dramatic)
        - Target popularity (follower count)
        - Rivalry connections
        - Controversial figures
        - Athlete's own popularity
        
        Args:
            change: Dict with change details
            athlete: Dict with athlete info
            
        Returns:
            Drama score (0-100)
        """
        score = 0
        change_type = change['type']
        target_name = change['target_name']
        target_handle = change['target_handle']
        target_followers = change.get('target_followers', 0)
        athlete_name = change['athlete']
        
        # Base score
        if change_type == 'unfollow':
            score += 40  # Unfollows are more dramatic
        else:
            score += 20  # Follows are interesting too
        
        # Target popularity score (based on followers)
        if target_followers > 10_000_000:
            score += 25
        elif target_followers > 1_000_000:
            score += 15
        elif target_followers > 100_000:
            score += 10
        else:
            score += 5
        
        # Superstar involvement
        if self._is_superstar(athlete_name):
            score += 15
        
        if self._is_superstar(target_name):
            score += 15
        
        # Rivalry bonus
        if self._is_rivalry(athlete, target_name):
            score += 40  # Big drama!
            logger.info(f"🔥 RIVALRY DETECTED: {athlete_name} <-> {target_name}")
        
        # Controversial figure bonus
        if self._is_controversial(target_name):
            score += 30
            logger.info(f"🎭 Controversial figure: {target_name}")
        
        # Unfollow + rivalry = mega drama
        if change_type == 'unfollow' and self._is_rivalry(athlete, target_name):
            score += 20  # Extra bonus
        
        # Cap at 100
        score = min(score, 100)
        
        logger.info(f"📊 Calculated drama score: {score}/100 for {athlete_name} {change_type} {target_name}")
        
        return score
    
    def _is_superstar(self, name: str) -> bool:
        """Check if person is a football superstar"""
        for keyword in self.superstar_keywords:
            if keyword.lower() in name.lower():
                return True
        return False
    
    def _is_controversial(self, name: str) -> bool:
        """Check if person is a controversial figure"""
        for keyword in self.controversial_keywords:
            if keyword.lower() in name.lower():
                return True
        return False
    
    def _is_rivalry(self, athlete: Dict, target_name: str) -> bool:
        """
        Check if there's a rivalry connection
        
        Args:
            athlete: Athlete dict (should have 'team' field)
            target_name: Name of target person
            
        Returns:
            True if rivalry detected
        """
        athlete_team = athlete.get('team', '')
        
        # Check if athlete's team has rivals
        if athlete_team in self.rivalries:
            rival_teams = self.rivalries[athlete_team]
            
            # Check if target is associated with rival team
            for rival_team in rival_teams:
                if rival_team.lower() in target_name.lower():
                    return True
        
        # Check if unfollowing a player from a rival team
        # (This would require more complex logic with player-team mappings)
        
        return False
    
    def get_explanation(self, score: int) -> str:
        """Get human-readable explanation of drama score"""
        if score >= 80:
            return "🔥🔥🔥 MEGA DRAMA - This is going viral!"
        elif score >= 60:
            return "🔥🔥 HIGH DRAMA - Great tweet potential"
        elif score >= 40:
            return "🔥 MEDIUM DRAMA - Worth tweeting"
        elif score >= 20:
            return "⚡ LOW DRAMA - Mildly interesting"
        else:
            return "😴 NO DRAMA - Skip this one"
