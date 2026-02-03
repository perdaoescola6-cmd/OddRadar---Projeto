from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime
from .football_api import FootballAPI
from .models import User, Subscription

class ChatBot:
    def __init__(self):
        self.api = FootballAPI()
    
    async def process_message(self, user_input: str, user: User) -> str:
        """Process user message and return response"""
        try:
            # Parse user input
            parsed = await self.api.parse_user_input(user_input)
            
            if parsed["intent"] == "match":
                return await self._analyze_match(parsed, user)
            else:
                return await self._analyze_team(parsed, user)
                
        except Exception as e:
            return f"❌ Erro ao processar sua solicitação. Por favor, tente novamente.\n\nDetalhes: {str(e)}"
    
    async def _analyze_match(self, parsed: Dict, user: User) -> str:
        """Analyze match between two teams"""
        team_a_name = parsed["team_a"]
        team_b_name = parsed["team_b"]
        n = parsed.get("n", 10)
        split_mode = parsed.get("split_mode", "A_HOME_B_AWAY")
        
        # Resolve teams
        team_a = await self.api.resolve_team(team_a_name)
        if not team_a:
            return f"❌ Time '{team_a_name}' não encontrado. Verifique a digitação."
        
        team_b = await self.api.resolve_team(team_b_name, context_fixtures=[])
        if not team_b:
            return f"❌ Time '{team_b_name}' não encontrado. Verifique a digitação."
        
        # Get fixtures for both teams
        fixtures_a = await self.api.get_team_fixtures(team_a["id"], n * 2)  # Get more for filtering
        fixtures_b = await self.api.get_team_fixtures(team_b["id"], n * 2)
        
        # Filter fixtures based on split mode
        filtered_a = self._filter_fixtures_by_venue(fixtures_a, team_a["id"], "home" if split_mode == "A_HOME_B_AWAY" else "all")
        filtered_b = self._filter_fixtures_by_venue(fixtures_b, team_b["id"], "away" if split_mode == "A_HOME_B_AWAY" else "all")
        
        # Take last N from each
        filtered_a = filtered_a[-n:]
        filtered_b = filtered_b[-n:]
        
        if len(filtered_a) < 5 or len(filtered_b) < 5:
            # Fallback to all fixtures if insufficient sample
            filtered_a = fixtures_a[-n:]
            filtered_b = fixtures_b[-n:]
            split_mode = "ALL"
        
        # Generate analysis
        return self._generate_match_analysis(team_a, team_b, filtered_a, filtered_b, split_mode)
    
    async def _analyze_team(self, parsed: Dict, user: User) -> str:
        """Analyze team statistics"""
        team_name = parsed["team"]
        n = parsed.get("n", 10)
        home_away = parsed.get("home_away", "all")
        metrics = parsed.get("metrics", ["over_2_5", "btts", "win_rate"])
        
        # Resolve team
        team = await self.api.resolve_team(team_name)
        if not team:
            return f"❌ Time '{team_name}' não encontrado. Verifique a digitação."
        
        # Get fixtures
        fixtures = await self.api.get_team_fixtures(team["id"], n * 2)
        
        # Filter by venue
        filtered = self._filter_fixtures_by_venue(fixtures, team["id"], home_away)
        filtered = filtered[-n:]
        
        # Generate analysis
        return self._generate_team_analysis(team, filtered, home_away, metrics)
    
    def _filter_fixtures_by_venue(self, fixtures: List[Dict], team_id: int, venue: str) -> List[Dict]:
        """Filter fixtures by home/away/all"""
        if venue == "all":
            return fixtures
        
        filtered = []
        for fixture in fixtures:
            teams = fixture.get("teams", {})
            if venue == "home" and teams.get("home", {}).get("id") == team_id:
                filtered.append(fixture)
            elif venue == "away" and teams.get("away", {}).get("id") == team_id:
                filtered.append(fixture)
        
        return filtered
    
    def _generate_match_analysis(self, team_a: Dict, team_b: Dict, fixtures_a: List[Dict], fixtures_b: List[Dict], split_mode: str) -> str:
        """Generate premium match analysis"""
        # Calculate statistics for both teams
        stats_a = self._calculate_team_stats(fixtures_a, team_a["id"])
        stats_b = self._calculate_team_stats(fixtures_b, team_b["id"])
        
        # Generate response
        response = []
        response.append(f"⚽ **{team_a['name']} x {team_b['name']}**")
        response.append(f"📊 Amostra: {len(fixtures_a)} jogos ({team_a['name']}) + {len(fixtures_b)} jogos ({team_b['name']})")
        response.append(f"🏠 Modo: {split_mode}")
        response.append("")
        
        # Recent form
        response.append("📈 **FORMA RECENTE**")
        response.append(f"{team_a['name']}: {self._get_form_string(fixtures_a[-4:], team_a['id'])}")
        response.append(f"{team_b['name']}: {self._get_form_string(fixtures_b[-4:], team_b['id'])}")
        response.append("")
        
        # Full-time stats
        response.append("⏱️ **ESTATÍSTICAS TEMPO INTEGRAL**")
        response.append(f"🎯 Over 2.5: {stats_a['over_2_5']:.1f}% vs {stats_b['over_2_5']:.1f}%")
        response.append(f"🤝 BTTS: {stats_a['btts']:.1f}% vs {stats_b['btts']:.1f}%")
        response.append(f"⚽ Média gols: {stats_a['avg_total_goals']:.1f} vs {stats_b['avg_total_goals']:.1f}")
        response.append("")
        
        # Half-time stats
        response.append("⏰ **ESTATÍSTICAS 1º TEMPO**")
        ht_stats_a = self._calculate_ht_stats(fixtures_a, team_a["id"])
        ht_stats_b = self._calculate_ht_stats(fixtures_b, team_b["id"])
        response.append(f"🎯 HT Over 0.5: {ht_stats_a['ht_over_0_5']:.1f}% vs {ht_stats_b['ht_over_0_5']:.1f}%")
        response.append(f"🎯 HT Over 1.5: {ht_stats_a['ht_over_1_5']:.1f}% vs {ht_stats_b['ht_over_1_5']:.1f}%")
        response.append("")
        
        # Advanced stats (corners/cards)
        corners_a, cards_a = self._calculate_advanced_stats(fixtures_a)
        corners_b, cards_b = self._calculate_advanced_stats(fixtures_b)
        
        if corners_a['sample'] > 0 and corners_b['sample'] > 0:
            response.append("🚩 **ESCANTEIOS**")
            response.append(f"📊 Média: {corners_a['avg']:.1f} vs {corners_b['avg']:.1f}")
            response.append(f"🎯 Over 8.5: {corners_a['over_8_5']:.1f}% vs {corners_b['over_8_5']:.1f}%")
            response.append(f"🎯 Over 9.5: {corners_a['over_9_5']:.1f}% vs {corners_b['over_9_5']:.1f}%")
            response.append(f"🎯 Over 10.5: {corners_a['over_10_5']:.1f}% vs {corners_b['over_10_5']:.1f}%")
            response.append("")
        
        if cards_a['sample'] > 0 and cards_b['sample'] > 0:
            response.append("🟨 **CARTÕES**")
            response.append(f"📊 Média: {cards_a['avg']:.1f} vs {cards_b['avg']:.1f}")
            response.append(f"🎯 Over 3.5: {cards_a['over_3_5']:.1f}% vs {cards_b['over_3_5']:.1f}%")
            response.append(f"🎯 Over 4.5: {cards_a['over_4_5']:.1f}% vs {cards_b['over_4_5']:.1f}%")
            response.append("")
        
        # Main Picks
        response.append("✅ **MAIN PICKS**")
        picks = self._generate_main_picks(stats_a, stats_b, ht_stats_a, ht_stats_b, corners_a, corners_b, cards_a, cards_b)
        for pick in picks:
            response.append(pick)
        response.append("")
        
        # Trends
        response.append("📊 **TRENDS**")
        trends = self._generate_trends(fixtures_a, fixtures_b, team_a["name"], team_b["name"])
        for trend in trends[:5]:  # Limit to 5 trends
            response.append(trend)
        
        return "\n".join(response)
    
    def _generate_team_analysis(self, team: Dict, fixtures: List[Dict], home_away: str, metrics: List[str]) -> str:
        """Generate team statistics analysis"""
        if not fixtures:
            return f"❌ Sem dados suficientes para {team['name']}."
        
        stats = self._calculate_team_stats(fixtures, team["id"])
        ht_stats = self._calculate_ht_stats(fixtures, team["id"])
        
        response = []
        response.append(f"📊 **{team['name']} - Últimos {len(fixtures)} jogos**")
        if home_away != "all":
            response.append(f"🏠 Filtro: {home_away.upper()}")
        response.append("")
        
        # Recent games
        response.append("📋 **JOGOS RECENTES**")
        for fixture in fixtures[-10:]:
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            home_team = teams.get("home", {})
            away_team = teams.get("away", {})
            
            home_goals = goals.get("home", 0)
            away_goals = goals.get("away", 0)
            
            # Determine result for analyzed team
            if home_team.get("id") == team["id"]:
                result = "W" if home_goals > away_goals else "D" if home_goals == away_goals else "L"
                score_line = f"{home_team['name']} {home_goals}-{away_goals} {away_team['name']} ({result})"
            else:
                result = "W" if away_goals > home_goals else "D" if away_goals == home_goals else "L"
                score_line = f"{away_team['name']} {away_goals}-{home_goals} {home_team['name']} ({result})"
            
            response.append(f"• {score_line}")
        
        response.append("")
        
        # Requested metrics
        response.append("📈 **MÉTRICAS**")
        metric_display = {
            "over_0_5": f"Over 0.5: {stats['over_0_5']:.1f}%",
            "over_1_5": f"Over 1.5: {stats['over_1_5']:.1f}%",
            "over_2_5": f"Over 2.5: {stats['over_2_5']:.1f}%",
            "over_3_5": f"Over 3.5: {stats['over_3_5']:.1f}%",
            "btts": f"BTTS: {stats['btts']:.1f}%",
            "win_rate": f"Vitórias: {stats['win_rate']:.1f}%",
            "draw_rate": f"Empates: {stats['draw_rate']:.1f}%",
            "loss_rate": f"Derrotas: {stats['loss_rate']:.1f}%",
            "clean_sheet_rate": f"Clean Sheet: {stats['clean_sheet_rate']:.1f}%",
            "failed_to_score_rate": f"Não marcou: {stats['failed_to_score_rate']:.1f}%",
            "avg_goals_for": f"Média gols pró: {stats['avg_goals_for']:.1f}",
            "avg_goals_against": f"Média gols contra: {stats['avg_goals_against']:.1f}",
            "avg_total_goals": f"Média total gols: {stats['avg_total_goals']:.1f}",
        }
        
        for metric in metrics:
            if metric in metric_display:
                response.append(f"• {metric_display[metric]}")
        
        return "\n".join(response)
    
    def _calculate_team_stats(self, fixtures: List[Dict], team_id: int) -> Dict:
        """Calculate team statistics"""
        if not fixtures:
            return {}
        
        stats = {
            "over_0_5": 0,
            "over_1_5": 0,
            "over_2_5": 0,
            "over_3_5": 0,
            "btts": 0,
            "win_rate": 0,
            "draw_rate": 0,
            "loss_rate": 0,
            "clean_sheet_rate": 0,
            "failed_to_score_rate": 0,
            "avg_goals_for": 0,
            "avg_goals_against": 0,
            "avg_total_goals": 0,
        }
        
        total_goals_for = 0
        total_goals_against = 0
        wins = draws = losses = 0
        clean_sheets = failed_to_score = 0
        
        for fixture in fixtures:
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            home_team = teams.get("home", {})
            away_team = teams.get("away", {})
            
            home_goals = goals.get("home", 0)
            away_goals = goals.get("away", 0)
            total_goals = home_goals + away_goals
            
            # Determine goals for/against based on team position
            if home_team.get("id") == team_id:
                goals_for = home_goals
                goals_against = away_goals
            else:
                goals_for = away_goals
                goals_against = home_goals
            
            total_goals_for += goals_for
            total_goals_against += goals_against
            
            # Over markets
            if total_goals > 0: stats["over_0_5"] += 1
            if total_goals > 1: stats["over_1_5"] += 1
            if total_goals > 2: stats["over_2_5"] += 1
            if total_goals > 3: stats["over_3_5"] += 1
            
            # BTTS
            if goals_for > 0 and goals_against > 0:
                stats["btts"] += 1
            
            # Result
            if goals_for > goals_against:
                wins += 1
            elif goals_for == goals_against:
                draws += 1
            else:
                losses += 1
            
            # Clean sheet / failed to score
            if goals_against == 0:
                clean_sheets += 1
            if goals_for == 0:
                failed_to_score += 1
        
        # Calculate percentages and averages
        total = len(fixtures)
        stats["over_0_5"] = (stats["over_0_5"] / total) * 100
        stats["over_1_5"] = (stats["over_1_5"] / total) * 100
        stats["over_2_5"] = (stats["over_2_5"] / total) * 100
        stats["over_3_5"] = (stats["over_3_5"] / total) * 100
        stats["btts"] = (stats["btts"] / total) * 100
        stats["win_rate"] = (wins / total) * 100
        stats["draw_rate"] = (draws / total) * 100
        stats["loss_rate"] = (losses / total) * 100
        stats["clean_sheet_rate"] = (clean_sheets / total) * 100
        stats["failed_to_score_rate"] = (failed_to_score / total) * 100
        stats["avg_goals_for"] = total_goals_for / total
        stats["avg_goals_against"] = total_goals_against / total
        stats["avg_total_goals"] = (total_goals_for + total_goals_against) / total
        
        return stats
    
    def _calculate_ht_stats(self, fixtures: List[Dict], team_id: int) -> Dict:
        """Calculate half-time statistics"""
        if not fixtures:
            return {"ht_over_0_5": 0, "ht_over_1_5": 0}
        
        ht_over_0_5 = 0
        ht_over_1_5 = 0
        
        for fixture in fixtures:
            # Note: API-Football doesn't provide HT goals in basic fixtures
            # This is a placeholder - would need /fixtures/statistics endpoint
            # For now, estimate based on typical distribution
            ft_goals = fixture.get("goals", {}).get("home", 0) + fixture.get("goals", {}).get("away", 0)
            
            # Rough estimation: ~60% of FT goals come in HT
            ht_goals_estimated = max(0, ft_goals - 1)
            
            if ht_goals_estimated > 0: ht_over_0_5 += 1
            if ht_goals_estimated > 1: ht_over_1_5 += 1
        
        total = len(fixtures)
        return {
            "ht_over_0_5": (ht_over_0_5 / total) * 100,
            "ht_over_1_5": (ht_over_1_5 / total) * 100
        }
    
    def _calculate_advanced_stats(self, fixtures: List[Dict]) -> Tuple[Dict, Dict]:
        """Calculate corners and cards statistics"""
        corners = {"sample": 0, "avg": 0, "over_8_5": 0, "over_9_5": 0, "over_10_5": 0}
        cards = {"sample": 0, "avg": 0, "over_3_5": 0, "over_4_5": 0}
        
        # Note: This would require /fixtures/statistics endpoint
        # For now, return empty stats
        return corners, cards
    
    def _get_form_string(self, fixtures: List[Dict], team_id: int) -> str:
        """Get form string for last games"""
        form = []
        for fixture in fixtures:
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            home_team = teams.get("home", {})
            away_team = teams.get("away", {})
            
            home_goals = goals.get("home", 0)
            away_goals = goals.get("away", 0)
            
            if home_team.get("id") == team_id:
                result = "W" if home_goals > away_goals else "D" if home_goals == away_goals else "L"
            else:
                result = "W" if away_goals > home_goals else "D" if away_goals == home_goals else "L"
            
            form.append(result)
        
        return " ".join(form)
    
    def _generate_main_picks(self, stats_a: Dict, stats_b: Dict, ht_a: Dict, ht_b: Dict, corners_a: Dict, corners_b: Dict, cards_a: Dict, cards_b: Dict) -> List[str]:
        """Generate main picks with probabilities"""
        picks = []
        
        # Goal picks
        avg_over_2_5 = (stats_a.get("over_2_5", 0) + stats_b.get("over_2_5", 0)) / 2
        avg_btts = (stats_a.get("btts", 0) + stats_b.get("btts", 0)) / 2
        avg_over_1_5 = (stats_a.get("over_1_5", 0) + stats_b.get("over_1_5", 0)) / 2
        
        picks.append(f"⚽ Over 2.5: {avg_over_2_5:.1f}%")
        picks.append(f"⚽ Under 2.5: {100 - avg_over_2_5:.1f}%")
        picks.append(f"⚽ BTTS SIM: {avg_btts:.1f}%")
        picks.append(f"⚽ BTTS NÃO: {100 - avg_btts:.1f}%")
        picks.append(f"⚽ Over 1.5: {avg_over_1_5:.1f}%")
        
        # HT picks
        avg_ht_over_0_5 = (ht_a.get("ht_over_0_5", 0) + ht_b.get("ht_over_0_5", 0)) / 2
        avg_ht_over_1_5 = (ht_a.get("ht_over_1_5", 0) + ht_b.get("ht_over_1_5", 0)) / 2
        
        picks.append(f"⏰ HT Over 0.5: {avg_ht_over_0_5:.1f}%")
        picks.append(f"⏰ HT Over 1.5: {avg_ht_over_1_5:.1f}%")
        
        # Double chance
        team_a_win_rate = stats_a.get("win_rate", 0)
        team_b_win_rate = stats_b.get("win_rate", 0)
        draw_rate = (stats_a.get("draw_rate", 0) + stats_b.get("draw_rate", 0)) / 2
        
        picks.append(f"🛡️ Dupla Chance 1X: {team_a_win_rate + draw_rate:.1f}%")
        picks.append(f"🛡️ Dupla Chance X2: {team_b_win_rate + draw_rate:.1f}%")
        
        # Team to score
        team_a_score_rate = 100 - stats_a.get("failed_to_score_rate", 0)
        team_b_score_rate = 100 - stats_b.get("failed_to_score_rate", 0)
        
        picks.append(f"🎯 {stats_a.get('team_name', 'Time A')} marca: {team_a_score_rate:.1f}%")
        picks.append(f"🎯 {stats_b.get('team_name', 'Time B')} marca: {team_b_score_rate:.1f}%")
        
        # Combination picks (approximate probability)
        under_3_5 = (100 - ((stats_a.get("over_3_5", 0) + stats_b.get("over_3_5", 0)) / 2))
        combo_1x_under_3_5 = (team_a_win_rate + draw_rate + under_3_5) / 2
        picks.append(f"🔥 Under 3.5 & 1X: ~{combo_1x_under_3_5:.1f}%")
        
        return picks
    
    def _generate_trends(self, fixtures_a: List[Dict], fixtures_b: List[Dict], team_a_name: str, team_b_name: str) -> List[str]:
        """Generate trend insights"""
        trends = []
        
        # Analyze patterns
        if len(fixtures_a) >= 5:
            a_over_2_5_recent = sum(1 for f in fixtures_a[-5:] if (f.get("goals", {}).get("home", 0) + f.get("goals", {}).get("away", 0)) > 2)
            trends.append(f"📈 {team_a_name}: {a_over_2_5_recent}/5 últimos jogos com Over 2.5")
        
        if len(fixtures_b) >= 5:
            b_btts_recent = sum(1 for f in fixtures_b[-5:] if f.get("goals", {}).get("home", 0) > 0 and f.get("goals", {}).get("away", 0) > 0)
            trends.append(f"📈 {team_b_name}: {b_btts_recent}/5 últimos jogos com BTTS")
        
        # Head to head (if available)
        # This would require additional API calls to get H2H fixtures
        
        return trends
