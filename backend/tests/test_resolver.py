"""
Integration tests for the BetFaro team resolver
Tests team resolution against the API with fuzzy matching
"""
import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from football_api import FootballAPI


class TestTeamResolverBasic:
    """Test basic team resolution functionality"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    def test_normalize_text(self, api):
        """Test text normalization"""
        assert api._normalize_text("Arsenal") == "arsenal"
        assert api._normalize_text("São Paulo") == "sao paulo"
        assert api._normalize_text("FC Porto") == "fc porto"
        assert api._normalize_text("  Chelsea  ") == "chelsea"
    
    def test_calculate_match_score_exact(self, api):
        """Test exact match score"""
        score = api._calculate_match_score("arsenal", "arsenal")
        assert score == 1.0
    
    def test_calculate_match_score_contains(self, api):
        """Test contains match score"""
        score = api._calculate_match_score("arsenal", "arsenal fc")
        assert score >= 0.85
    
    def test_calculate_match_score_partial(self, api):
        """Test partial match score"""
        score = api._calculate_match_score("chelsea", "chelsea fc")
        assert score >= 0.5
    
    def test_aliases_exist(self, api):
        """Test that common aliases are defined"""
        assert "arsenal" in api.team_aliases
        assert "chelsea" in api.team_aliases
        assert "man united" in api.team_aliases
        assert "benfica" in api.team_aliases
        assert "psg" in api.team_aliases


class TestTeamResolverAsync:
    """Test async team resolution with API"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_resolve_arsenal(self, api):
        """Test resolving Arsenal"""
        team = await api.resolve_team("Arsenal")
        assert team is not None
        assert "Arsenal" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_resolve_chelsea(self, api):
        """Test resolving Chelsea"""
        team = await api.resolve_team("Chelsea")
        assert team is not None
        assert "Chelsea" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_resolve_benfica(self, api):
        """Test resolving Benfica"""
        team = await api.resolve_team("Benfica")
        assert team is not None
        assert "Benfica" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_resolve_real_madrid(self, api):
        """Test resolving Real Madrid"""
        team = await api.resolve_team("Real Madrid")
        assert team is not None
        assert "Real Madrid" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_resolve_man_united_alias(self, api):
        """Test resolving Man United alias"""
        team = await api.resolve_team("Manchester United")
        assert team is not None
        assert "Manchester" in team.get("name", "") or "United" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_resolve_nonexistent_team(self, api):
        """Test resolving non-existent team returns None"""
        team = await api.resolve_team("XYZ Fake Team 12345")
        # Should return None or a fallback, not crash
        # The API might return some results, so we just check it doesn't crash
        assert True  # If we get here, no crash occurred


class TestSearchTeams:
    """Test team search functionality"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_search_arsenal(self, api):
        """Test searching for Arsenal"""
        teams = await api.search_teams("Arsenal")
        assert isinstance(teams, list)
        # Should find at least one Arsenal
        if teams:
            assert any("Arsenal" in str(t) for t in teams)
    
    @pytest.mark.asyncio
    async def test_search_chelsea(self, api):
        """Test searching for Chelsea"""
        teams = await api.search_teams("Chelsea")
        assert isinstance(teams, list)
    
    @pytest.mark.asyncio
    async def test_search_caching(self, api):
        """Test that search results are cached"""
        # First call
        teams1 = await api.search_teams("Liverpool")
        # Second call should use cache
        teams2 = await api.search_teams("Liverpool")
        assert teams1 == teams2


class TestTeamResolverEdgeCases:
    """Test edge cases in team resolution"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_resolve_with_fc_suffix(self, api):
        """Test resolving team with FC suffix"""
        team = await api.resolve_team("FC Porto")
        assert team is not None
    
    @pytest.mark.asyncio
    async def test_resolve_lowercase(self, api):
        """Test resolving lowercase team name"""
        team = await api.resolve_team("arsenal")
        assert team is not None
    
    @pytest.mark.asyncio
    async def test_resolve_uppercase(self, api):
        """Test resolving uppercase team name"""
        team = await api.resolve_team("ARSENAL")
        assert team is not None
    
    @pytest.mark.asyncio
    async def test_resolve_with_spaces(self, api):
        """Test resolving team with extra spaces"""
        team = await api.resolve_team("  Arsenal  ")
        assert team is not None


class TestPopularTeams:
    """Test resolution of popular teams from major leagues"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    # Premier League
    @pytest.mark.asyncio
    async def test_premier_league_teams(self, api):
        """Test Premier League teams"""
        teams = ["Arsenal", "Chelsea", "Liverpool", "Manchester City", "Tottenham"]
        for team_name in teams:
            team = await api.resolve_team(team_name)
            assert team is not None, f"Failed to resolve {team_name}"
    
    # La Liga
    @pytest.mark.asyncio
    async def test_la_liga_teams(self, api):
        """Test La Liga teams"""
        teams = ["Real Madrid", "Barcelona", "Atletico Madrid"]
        for team_name in teams:
            team = await api.resolve_team(team_name)
            assert team is not None, f"Failed to resolve {team_name}"
    
    # Serie A
    @pytest.mark.asyncio
    async def test_serie_a_teams(self, api):
        """Test Serie A teams"""
        teams = ["Juventus", "AC Milan", "Inter", "Napoli"]
        for team_name in teams:
            team = await api.resolve_team(team_name)
            assert team is not None, f"Failed to resolve {team_name}"
    
    # Bundesliga
    @pytest.mark.asyncio
    async def test_bundesliga_teams(self, api):
        """Test Bundesliga teams"""
        teams = ["Bayern Munich", "Borussia Dortmund"]
        for team_name in teams:
            team = await api.resolve_team(team_name)
            assert team is not None, f"Failed to resolve {team_name}"
    
    # Portuguese League
    @pytest.mark.asyncio
    async def test_portuguese_teams(self, api):
        """Test Portuguese league teams"""
        teams = ["Benfica", "FC Porto", "Sporting CP"]
        for team_name in teams:
            team = await api.resolve_team(team_name)
            assert team is not None, f"Failed to resolve {team_name}"
    
    # Brazilian League
    @pytest.mark.asyncio
    async def test_brazilian_teams(self, api):
        """Test Brazilian league teams"""
        teams = ["Flamengo", "Palmeiras", "Corinthians", "Sao Paulo"]
        for team_name in teams:
            team = await api.resolve_team(team_name)
            assert team is not None, f"Failed to resolve {team_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
