import httpx
import json
import unicodedata
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import os
import logging

logger = logging.getLogger(__name__)

class FootballAPI:
    def __init__(self):
        self.api_key = os.getenv("APISPORTS_KEY")
        self.base_url = os.getenv("APISPORTS_BASE_URL", "https://v3.football.api-sports.io")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Cache in memory with TTL
        self.cache = {}
        self.CACHE_TTL = 300  # 5 minutes
        
        # Common team aliases
        self.team_aliases = {
            "chelsa": "chelsea",
            "atletico mineiro": "atlético mineiro",
            "argentinos junior": "argentinos juniors",
            "argentinos jrs": "argentinos juniors",
            "benfica": "sl benfica",
            "porto": "fc porto",
            " sporting": "sporting cp",
            "braga": "sc braga",
            "manchester united": "man utd",
            "manchester city": "man city",
            "tottenham": "spurs",
            "west ham": "west ham united",
            "newcastle": "newcastle united",
            "leicester": "leicester city",
            "wolves": "wolverhampton",
            "brighton": "brighton & hove albion",
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self.cache:
            return False
        timestamp = self.cache[cache_key].get("timestamp")
        return datetime.utcnow().timestamp() - timestamp < self.CACHE_TTL
    
    def _get_cache(self, cache_key: str) -> Optional[any]:
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        return None
    
    def _set_cache(self, cache_key: str, data: any):
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow().timestamp()
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        text = unicodedata.normalize('NFKD', text.lower())
        text = ''.join(c for c in text if not unicodedata.combining(c))
        return re.sub(r'[^\w\s]', '', text).strip()
    
    async def _make_request(self, endpoint: str, params: Dict = None, max_retries: int = 2) -> Dict:
        """Make HTTP request with timeout and retry"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "x-apisports-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get("errors"):
                        logger.error(f"API Error: {data['errors']}")
                        raise Exception(f"API Error: {data['errors']}")
                    
                    return data.get("response", [])
                    
            except httpx.TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1} for {endpoint}")
                if attempt == max_retries:
                    raise Exception("Request timeout after retries")
            except Exception as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(1)
    
    async def search_teams(self, query: str) -> List[Dict]:
        """Search for teams by name"""
        cache_key = f"search_teams_{query}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            params = {"search": query}
            result = await self._make_request("teams", params)
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error searching teams: {str(e)}")
            return []
    
    async def get_team_fixtures(self, team_id: int, last: int = 10) -> List[Dict]:
        """Get team fixtures with scores"""
        cache_key = f"fixtures_{team_id}_{last}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            params = {"team": team_id, "last": last}
            fixtures = await self._make_request("fixtures", params)
            
            # Filter fixtures with actual scores
            scored_fixtures = []
            for fixture in fixtures:
                if fixture.get("goals") and fixture["goals"].get("home") is not None and fixture["goals"].get("away") is not None:
                    scored_fixtures.append(fixture)
            
            self._set_cache(cache_key, scored_fixtures)
            return scored_fixtures
            
        except Exception as e:
            logger.error(f"Error getting fixtures: {str(e)}")
            return []
    
    async def resolve_team(self, team_name: str, context_fixtures: List[Dict] = None) -> Optional[Dict]:
        """Resolve team name to team info with context awareness"""
        normalized_name = self._normalize_text(team_name)
        
        # Check aliases first
        if normalized_name in self.team_aliases:
            team_name = self.team_aliases[normalized_name]
            normalized_name = self._normalize_text(team_name)
        
        # Context-aware resolution for opponent matching
        if context_fixtures:
            for fixture in context_fixtures:
                opponent = fixture.get("teams", {}).get("away", {}) if fixture.get("teams", {}).get("home", {}).get("name", "").lower() == team_name.lower() else fixture.get("teams", {}).get("home", {})
                if opponent and self._normalize_text(opponent.get("name", "")) == normalized_name:
                    return opponent
        
        # Search API
        teams = await self.search_teams(team_name)
        if not teams:
            return None
        
        # Prioritize main men's team
        main_team = None
        for team in teams:
            team_name_normalized = self._normalize_text(team.get("name", ""))
            
            # Skip women/U20/reserves unless explicitly requested
            if any(keyword in team_name_normalized for keyword in ["women", "feminino", "u20", "u21", "u23", "reserve", "b team", "ii"]):
                continue
            
            # Check for exact match or very close match
            if team_name_normalized == normalized_name or normalized_name in team_name_normalized:
                main_team = team
                break
        
        # Fallback to first result if no main team found
        return main_team or teams[0] if teams else None
    
    async def parse_user_input(self, text: str) -> Dict:
        """Parse user input using GPT or fallback heuristics"""
        cache_key = f"parse_{hash(text)}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # Try GPT parsing first
        try:
            if self.openai_api_key:
                result = await self._parse_with_gpt(text)
                if result:
                    self._set_cache(cache_key, result)
                    return result
        except Exception as e:
            logger.warning(f"GPT parsing failed: {str(e)}")
        
        # Fallback to heuristics
        result = self._parse_with_heuristics(text)
        self._set_cache(cache_key, result)
        return result
    
    async def _parse_with_gpt(self, text: str) -> Optional[Dict]:
        """Parse input using OpenAI GPT"""
        import openai
        
        client = openai.AsyncClient(api_key=self.openai_api_key)
        
        prompt = f"""
        Parse this football betting request and return JSON:
        
        "{text}"
        
        Rules:
        - If contains "x", "vs", "v", "-" between two teams: intent = "match"
        - Otherwise: intent = "team"
        
        For "team" intent, return:
        {{
            "intent": "team",
            "team": "team name",
            "n": 10,
            "home_away": "all",
            "metrics": ["over_2_5", "btts", "win_rate"]
        }}
        
        For "match" intent, return:
        {{
            "intent": "match",
            "team_a": "Team A name",
            "team_b": "Team B name",
            "n": 10,
            "split_mode": "A_HOME_B_AWAY"
        }}
        
        Common variations:
        - "over 2.5" -> over_2_5
        - "btts" -> btts
        - "win rate" -> win_rate
        - "last 10" -> n: 10
        - "away" -> home_away: "away"
        - "home" -> home_away: "home"
        
        Return ONLY valid JSON.
        """
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    
    def _parse_with_heuristics(self, text: str) -> Dict:
        """Fallback parsing using regex and patterns"""
        text_lower = text.lower()
        
        # Check for match intent
        match_patterns = [
            r'(.+?)\s*(?:x|vs|v|-)\s*(.+)',
            r'(.+?)\s*(?:contra|versus)\s*(.+)',
        ]
        
        for pattern in match_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return {
                    "intent": "match",
                    "team_a": match.group(1).strip(),
                    "team_b": match.group(2).strip(),
                    "n": self._extract_number(text) or 10,
                    "split_mode": "A_HOME_B_AWAY"
                }
        
        # Default to team intent
        return {
            "intent": "team",
            "team": text_lower,
            "n": self._extract_number(text) or 10,
            "home_away": self._extract_home_away(text) or "all",
            "metrics": self._extract_metrics(text)
        }
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        numbers = re.findall(r'\b(\d+)\b', text)
        return int(numbers[-1]) if numbers else None
    
    def _extract_home_away(self, text: str) -> Optional[str]:
        """Extract home/away filter"""
        text_lower = text.lower()
        if "away" in text_lower or "fora" in text_lower or "visitante" in text_lower:
            return "away"
        elif "home" in text_lower or "casa" in text_lower or "mandante" in text_lower:
            return "home"
        return "all"
    
    def _extract_metrics(self, text: str) -> List[str]:
        """Extract metrics from text"""
        text_lower = text.lower()
        metrics = []
        
        metric_mapping = {
            "over 0.5": "over_0_5",
            "over 1.5": "over_1_5", 
            "over 2.5": "over_2_5",
            "over 3.5": "over_3_5",
            "btts": "btts",
            "both teams score": "btts",
            "win rate": "win_rate",
            "winrate": "win_rate",
            "draw rate": "draw_rate",
            "loss rate": "loss_rate",
            "clean sheet": "clean_sheet_rate",
            "failed to score": "failed_to_score_rate",
            "avg goals": "avg_goals_for",
            "avg goals for": "avg_goals_for",
            "avg goals against": "avg_goals_against",
            "avg total goals": "avg_total_goals",
        }
        
        for pattern, metric in metric_mapping.items():
            if pattern in text_lower:
                metrics.append(metric)
        
        # Default metrics if none found
        if not metrics:
            metrics = ["over_2_5", "btts", "win_rate"]
        
        return metrics
