"""
Picks Engine - Generates daily picks for Elite users
Analyzes fixtures from today and tomorrow, selects top 10 games,
and generates betting recommendations using the same pipeline as the chatbot.
"""
import httpx
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

logger = logging.getLogger(__name__)

# Priority leagues for Brazilian bettors
PRIORITY_LEAGUES = {
    # Tier 1 - Highest priority
    "tier1": [
        # Brazil
        71,   # Serie A
        72,   # Serie B
        73,   # Copa do Brasil
        # Europe Top 5
        39,   # Premier League
        140,  # La Liga
        135,  # Serie A Italy
        78,   # Bundesliga
        61,   # Ligue 1
        # European Cups
        2,    # Champions League
        3,    # Europa League
        848,  # Conference League
    ],
    # Tier 2 - High priority
    "tier2": [
        # South America
        13,   # Libertadores
        11,   # Copa Sudamericana
        128,  # Argentina Primera
        # Saudi Arabia
        307,  # Saudi Pro League
        # Other Europe
        94,   # Primeira Liga Portugal
        88,   # Eredivisie
        203,  # Super Lig Turkey
    ],
    # Tier 3 - Medium priority (Brazilian state championships)
    "tier3": [
        475,  # Paulistao
        476,  # Carioca
        477,  # Mineiro
        478,  # Gaucho
    ]
}

# Flatten for quick lookup
ALL_PRIORITY_LEAGUES = (
    PRIORITY_LEAGUES["tier1"] + 
    PRIORITY_LEAGUES["tier2"] + 
    PRIORITY_LEAGUES["tier3"]
)

class PicksEngine:
    def __init__(self):
        self.api_key = os.getenv("APISPORTS_KEY")
        self.base_url = os.getenv("APISPORTS_BASE_URL", "https://v3.football.api-sports.io")
        
        # Cache for picks (TTL 30 minutes)
        self.cache = {}
        self.CACHE_TTL = 1800  # 30 minutes
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self.cache:
            return False
        timestamp = self.cache[cache_key].get("timestamp", 0)
        return datetime.utcnow().timestamp() - timestamp < self.CACHE_TTL
    
    def _get_cache(self, cache_key: str) -> Optional[Dict]:
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow().timestamp()
        }
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Make HTTP request to API"""
        if not self.api_key:
            logger.error("APISPORTS_KEY not configured!")
            return []
        
        url = f"{self.base_url}/{endpoint}"
        headers = {"x-apisports-key": self.api_key}
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("response", [])
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return []
    
    async def get_fixtures_by_date(self, date_str: str) -> List[Dict]:
        """Get all fixtures for a specific date"""
        return await self._make_request("fixtures", {"date": date_str})
    
    async def get_team_fixtures(self, team_id: int, last: int = 10) -> List[Dict]:
        """Get last N fixtures for a team"""
        fixtures = await self._make_request("fixtures", {"team": team_id, "last": last})
        # Filter only finished games with scores
        return [
            f for f in fixtures 
            if f.get("goals", {}).get("home") is not None 
            and f.get("goals", {}).get("away") is not None
        ]
    
    def _get_league_priority(self, league_id: int) -> int:
        """Get priority score for a league (lower = higher priority)"""
        if league_id in PRIORITY_LEAGUES["tier1"]:
            return 1
        elif league_id in PRIORITY_LEAGUES["tier2"]:
            return 2
        elif league_id in PRIORITY_LEAGUES["tier3"]:
            return 3
        return 99  # Not priority
    
    def _filter_and_rank_fixtures(self, fixtures: List[Dict], max_count: int = 10) -> List[Dict]:
        """Filter fixtures to priority leagues and rank them"""
        # Filter only future games from priority leagues
        now = datetime.utcnow()
        priority_fixtures = []
        
        for f in fixtures:
            fixture_data = f.get("fixture", {})
            league = f.get("league", {})
            league_id = league.get("id")
            status = fixture_data.get("status", {}).get("short", "")
            
            # Only not started games
            if status not in ["NS", "TBD", "SUSP", "PST"]:
                continue
            
            # Check if priority league
            if league_id not in ALL_PRIORITY_LEAGUES:
                continue
            
            # Parse date
            try:
                date_str = fixture_data.get("date", "")
                game_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except:
                continue
            
            priority = self._get_league_priority(league_id)
            priority_fixtures.append({
                "fixture": f,
                "priority": priority,
                "date": game_date,
                "league_id": league_id
            })
        
        # Sort by priority (tier), then by date (earlier first)
        priority_fixtures.sort(key=lambda x: (x["priority"], x["date"]))
        
        # Return top N
        return [pf["fixture"] for pf in priority_fixtures[:max_count]]
    
    def _calculate_stats(self, fixtures: List[Dict], team_id: int) -> Dict:
        """Calculate statistics from fixtures for a team"""
        if not fixtures:
            return {}
        
        total = len(fixtures)
        wins = draws = losses = 0
        goals_for = goals_against = 0
        over_15 = over_25 = over_35 = 0
        btts = 0
        clean_sheets = 0
        failed_to_score = 0
        
        for f in fixtures:
            teams = f.get("teams", {})
            goals = f.get("goals", {})
            
            home_id = teams.get("home", {}).get("id")
            home_goals = goals.get("home", 0) or 0
            away_goals = goals.get("away", 0) or 0
            total_goals = home_goals + away_goals
            
            is_home = home_id == team_id
            team_goals = home_goals if is_home else away_goals
            opp_goals = away_goals if is_home else home_goals
            
            goals_for += team_goals
            goals_against += opp_goals
            
            # Result
            if team_goals > opp_goals:
                wins += 1
            elif team_goals == opp_goals:
                draws += 1
            else:
                losses += 1
            
            # Over/Under
            if total_goals > 1.5:
                over_15 += 1
            if total_goals > 2.5:
                over_25 += 1
            if total_goals > 3.5:
                over_35 += 1
            
            # BTTS
            if home_goals > 0 and away_goals > 0:
                btts += 1
            
            # Clean sheet / Failed to score
            if opp_goals == 0:
                clean_sheets += 1
            if team_goals == 0:
                failed_to_score += 1
        
        return {
            "total": total,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "avg_goals_for": round(goals_for / total, 2) if total > 0 else 0,
            "avg_goals_against": round(goals_against / total, 2) if total > 0 else 0,
            "over_15_rate": round(over_15 / total * 100, 1) if total > 0 else 0,
            "over_25_rate": round(over_25 / total * 100, 1) if total > 0 else 0,
            "over_35_rate": round(over_35 / total * 100, 1) if total > 0 else 0,
            "btts_rate": round(btts / total * 100, 1) if total > 0 else 0,
            "clean_sheet_rate": round(clean_sheets / total * 100, 1) if total > 0 else 0,
            "failed_to_score_rate": round(failed_to_score / total * 100, 1) if total > 0 else 0,
            "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
        }
    
    def _generate_picks_for_match(self, stats_a: Dict, stats_b: Dict, team_a_name: str, team_b_name: str) -> List[Dict]:
        """Generate betting picks for a match based on team stats"""
        picks = []
        
        # Calculate combined stats
        avg_over_25 = (stats_a.get("over_25_rate", 0) + stats_b.get("over_25_rate", 0)) / 2
        avg_over_15 = (stats_a.get("over_15_rate", 0) + stats_b.get("over_15_rate", 0)) / 2
        avg_btts = (stats_a.get("btts_rate", 0) + stats_b.get("btts_rate", 0)) / 2
        
        # Combined goals
        avg_goals_total = (
            stats_a.get("avg_goals_for", 0) + stats_a.get("avg_goals_against", 0) +
            stats_b.get("avg_goals_for", 0) + stats_b.get("avg_goals_against", 0)
        ) / 2
        
        # Over 2.5 pick
        if avg_over_25 >= 50:
            confidence = min(avg_over_25, 99)
            confidence_level = "ALTA" if confidence >= 70 else "MÉDIA" if confidence >= 55 else "BAIXA"
            picks.append({
                "market": "Over 2.5",
                "confidence": round(confidence, 1),
                "confidence_level": confidence_level,
                "justification": f"Over 2.5 em {int(stats_a.get('over_25_rate', 0))}/10 ({team_a_name}) e {int(stats_b.get('over_25_rate', 0))}/10 ({team_b_name})"
            })
        
        # Under 2.5 pick (if low scoring)
        if avg_over_25 < 45:
            confidence = min(100 - avg_over_25, 99)
            confidence_level = "ALTA" if confidence >= 70 else "MÉDIA" if confidence >= 55 else "BAIXA"
            picks.append({
                "market": "Under 2.5",
                "confidence": round(confidence, 1),
                "confidence_level": confidence_level,
                "justification": f"Média de {avg_goals_total:.1f} gols por jogo combinado"
            })
        
        # Over 1.5 pick
        if avg_over_15 >= 70:
            confidence = min(avg_over_15, 99)
            confidence_level = "ALTA" if confidence >= 80 else "MÉDIA" if confidence >= 70 else "BAIXA"
            picks.append({
                "market": "Over 1.5",
                "confidence": round(confidence, 1),
                "confidence_level": confidence_level,
                "justification": f"Over 1.5 em {int(stats_a.get('over_15_rate', 0))}/10 e {int(stats_b.get('over_15_rate', 0))}/10"
            })
        
        # BTTS pick
        if avg_btts >= 55:
            confidence = min(avg_btts, 99)
            confidence_level = "ALTA" if confidence >= 70 else "MÉDIA" if confidence >= 55 else "BAIXA"
            picks.append({
                "market": "BTTS Sim",
                "confidence": round(confidence, 1),
                "confidence_level": confidence_level,
                "justification": f"Ambos marcaram em {int(stats_a.get('btts_rate', 0))}/10 e {int(stats_b.get('btts_rate', 0))}/10"
            })
        
        # BTTS No pick
        if avg_btts < 40:
            confidence = min(100 - avg_btts, 99)
            confidence_level = "ALTA" if confidence >= 70 else "MÉDIA" if confidence >= 55 else "BAIXA"
            picks.append({
                "market": "BTTS Não",
                "confidence": round(confidence, 1),
                "confidence_level": confidence_level,
                "justification": f"Clean sheets: {int(stats_a.get('clean_sheet_rate', 0))}% e {int(stats_b.get('clean_sheet_rate', 0))}%"
            })
        
        # Sort by confidence and return top 2
        picks.sort(key=lambda x: x["confidence"], reverse=True)
        return picks[:2]
    
    async def analyze_fixture(self, fixture: Dict) -> Optional[Dict]:
        """Analyze a single fixture and generate picks"""
        try:
            fixture_data = fixture.get("fixture", {})
            teams = fixture.get("teams", {})
            league = fixture.get("league", {})
            
            home_team = teams.get("home", {})
            away_team = teams.get("away", {})
            
            home_id = home_team.get("id")
            away_id = away_team.get("id")
            home_name = home_team.get("name", "Time A")
            away_name = away_team.get("name", "Time B")
            
            if not home_id or not away_id:
                return None
            
            # Get last 10 fixtures for each team
            home_fixtures = await self.get_team_fixtures(home_id, 15)
            away_fixtures = await self.get_team_fixtures(away_id, 15)
            
            # Filter official matches (exclude friendlies)
            home_fixtures = self._filter_official_matches(home_fixtures)[:10]
            away_fixtures = self._filter_official_matches(away_fixtures)[:10]
            
            if len(home_fixtures) < 5 or len(away_fixtures) < 5:
                logger.warning(f"Insufficient data for {home_name} vs {away_name}")
                return None
            
            # Calculate stats
            stats_home = self._calculate_stats(home_fixtures, home_id)
            stats_away = self._calculate_stats(away_fixtures, away_id)
            
            # Generate picks
            picks = self._generate_picks_for_match(stats_home, stats_away, home_name, away_name)
            
            if not picks:
                return None
            
            # Format date
            date_str = fixture_data.get("date", "")
            try:
                game_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                formatted_date = game_date.strftime("%d/%m %H:%M")
            except:
                formatted_date = "TBD"
            
            return {
                "fixture_id": fixture_data.get("id"),
                "home_team": home_name,
                "away_team": away_name,
                "league": league.get("name", ""),
                "league_country": league.get("country", ""),
                "date": formatted_date,
                "date_iso": date_str,
                "picks": picks,
                "stats": {
                    "home": stats_home,
                    "away": stats_away
                },
                "games_analyzed": len(home_fixtures) + len(away_fixtures)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing fixture: {str(e)}")
            return None
    
    def _filter_official_matches(self, fixtures: List[Dict]) -> List[Dict]:
        """Filter out friendlies and non-official matches"""
        FRIENDLY_KEYWORDS = [
            "friendly", "amistoso", "charity", "beneficente", "test match",
            "exhibition", "testimonial", "memorial", "trophy friendly",
            "pre-season", "pre season", "preseason", "club friendly"
        ]
        EXCLUDED_TYPES = ["friendly", "club friendly", "international friendly"]
        
        official = []
        for f in fixtures:
            league = f.get("league", {})
            league_name = league.get("name", "").lower()
            league_type = league.get("type", "").lower()
            
            if league_type in EXCLUDED_TYPES:
                continue
            
            if any(kw in league_name for kw in FRIENDLY_KEYWORDS):
                continue
            
            official.append(f)
        
        return official
    
    async def get_daily_picks(self, range_type: str = "both", force_refresh: bool = False) -> Dict:
        """
        Get daily picks for today and/or tomorrow
        range_type: "today", "tomorrow", or "both"
        """
        cache_key = f"picks_{range_type}"
        
        # Check cache
        if not force_refresh:
            cached = self._get_cache(cache_key)
            if cached:
                logger.info(f"Returning cached picks for {range_type}")
                return cached
        
        logger.info(f"Generating picks for {range_type}")
        
        # Get dates
        today = datetime.utcnow().strftime("%Y-%m-%d")
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        all_fixtures = []
        
        # Fetch fixtures
        if range_type in ["today", "both"]:
            today_fixtures = await self.get_fixtures_by_date(today)
            all_fixtures.extend(today_fixtures)
            logger.info(f"Fetched {len(today_fixtures)} fixtures for today")
        
        if range_type in ["tomorrow", "both"]:
            tomorrow_fixtures = await self.get_fixtures_by_date(tomorrow)
            all_fixtures.extend(tomorrow_fixtures)
            logger.info(f"Fetched {len(tomorrow_fixtures)} fixtures for tomorrow")
        
        # Remove duplicates by fixture ID
        seen_ids = set()
        unique_fixtures = []
        for f in all_fixtures:
            fid = f.get("fixture", {}).get("id")
            if fid and fid not in seen_ids:
                seen_ids.add(fid)
                unique_fixtures.append(f)
        
        logger.info(f"Total unique fixtures: {len(unique_fixtures)}")
        
        # Filter and rank to get top 10
        top_fixtures = self._filter_and_rank_fixtures(unique_fixtures, max_count=10)
        logger.info(f"Selected {len(top_fixtures)} priority fixtures")
        
        # Analyze each fixture
        picks_results = []
        analyzed = 0
        failed = 0
        
        for fixture in top_fixtures:
            result = await self.analyze_fixture(fixture)
            if result:
                picks_results.append(result)
                analyzed += 1
            else:
                failed += 1
        
        # Sort by best pick confidence
        picks_results.sort(
            key=lambda x: max(p["confidence"] for p in x["picks"]) if x["picks"] else 0,
            reverse=True
        )
        
        result = {
            "picks": picks_results,
            "meta": {
                "range": range_type,
                "generated_at": datetime.utcnow().isoformat(),
                "total_fixtures_fetched": len(unique_fixtures),
                "priority_fixtures": len(top_fixtures),
                "analyzed_success": analyzed,
                "analyzed_failed": failed
            }
        }
        
        # Cache result
        self._set_cache(cache_key, result)
        
        return result


# Singleton instance
picks_engine = PicksEngine()
