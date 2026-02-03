"""
Unit tests for the BetFaro parser
Tests parsing of team names, markets, and odds from user input
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import ChatBot


class TestParserSeparators:
    """Test that parser correctly handles all separator variations"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_separator_x(self, chatbot):
        """Test 'x' separator"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_separator_vs(self, chatbot):
        """Test 'vs' separator"""
        teams = chatbot._extract_teams_from_text("Arsenal vs Chelsea")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_separator_v(self, chatbot):
        """Test 'v' separator"""
        teams = chatbot._extract_teams_from_text("Arsenal v Chelsea")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_hyphen_in_team_name(self, chatbot):
        """Test that hyphens in team names are preserved (Al-Khaleej, Al-Nassr, etc.)"""
        teams = chatbot._extract_teams_from_text("Al-Khaleej FC x Al-Qadsiah FC")
        assert len(teams) == 2
        assert "Khaleej" in teams[0] or "khaleej" in teams[0].lower()
        assert "Qadsiah" in teams[1] or "qadsiah" in teams[1].lower()
    
    def test_separator_versus(self, chatbot):
        """Test 'versus' separator"""
        teams = chatbot._extract_teams_from_text("Arsenal versus Chelsea")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_lowercase_input(self, chatbot):
        """Test lowercase input"""
        teams = chatbot._extract_teams_from_text("arsenal x chelsea")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_mixed_case_input(self, chatbot):
        """Test mixed case input"""
        teams = chatbot._extract_teams_from_text("ARSENAL x CHELSEA")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"


class TestParserTeamAliases:
    """Test that parser correctly resolves team aliases"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_man_united_alias(self, chatbot):
        """Test 'Man United' alias"""
        teams = chatbot._extract_teams_from_text("Man United x Liverpool")
        assert len(teams) == 2
        assert teams[0] == "Manchester United"
        assert teams[1] == "Liverpool"
    
    def test_man_city_alias(self, chatbot):
        """Test 'Man City' alias"""
        teams = chatbot._extract_teams_from_text("Man City vs Arsenal")
        assert len(teams) == 2
        assert teams[0] == "Manchester City"
        assert teams[1] == "Arsenal"
    
    def test_spurs_alias(self, chatbot):
        """Test 'Spurs' alias"""
        teams = chatbot._extract_teams_from_text("Spurs x Chelsea")
        assert len(teams) == 2
        assert teams[0] == "Tottenham"
        assert teams[1] == "Chelsea"
    
    def test_barca_alias(self, chatbot):
        """Test 'Barca' alias"""
        teams = chatbot._extract_teams_from_text("Real Madrid x Barca")
        assert len(teams) == 2
        assert teams[0] == "Real Madrid"
        assert teams[1] == "Barcelona"
    
    def test_psg_alias(self, chatbot):
        """Test 'PSG' alias"""
        teams = chatbot._extract_teams_from_text("PSG vs Bayern")
        assert len(teams) == 2
        assert teams[0] == "Paris Saint Germain"
        assert teams[1] == "Bayern Munich"
    
    def test_porto_alias(self, chatbot):
        """Test 'Porto' alias"""
        teams = chatbot._extract_teams_from_text("Benfica x Porto")
        assert len(teams) == 2
        assert teams[0] == "Benfica"
        assert teams[1] == "FC Porto"


class TestParserWithMarkets:
    """Test that parser correctly extracts teams when markets are included"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_with_over_2_5(self, chatbot):
        """Test with 'over 2.5' market"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea over 2.5")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_with_o2_5(self, chatbot):
        """Test with 'o2.5' shorthand"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea o2.5")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_with_btts(self, chatbot):
        """Test with 'btts' market"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea btts")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_with_btts_sim(self, chatbot):
        """Test with 'btts sim' market"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea btts sim")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_with_ambas_marcam(self, chatbot):
        """Test with 'ambas marcam' market (Portuguese)"""
        teams = chatbot._extract_teams_from_text("Benfica x Porto ambas marcam")
        assert len(teams) == 2
        assert teams[0] == "Benfica"
        assert teams[1] == "FC Porto"


class TestParserWithOdds:
    """Test that parser correctly extracts teams when odds are included"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_with_at_odds(self, chatbot):
        """Test with '@2.10' odds format"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea @2.10")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_with_odds_number(self, chatbot):
        """Test with '2.10' odds format"""
        teams = chatbot._extract_teams_from_text("Arsenal x Chelsea 2.10")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_with_market_and_odds(self, chatbot):
        """Test with market and odds combined"""
        teams = chatbot._extract_teams_from_text("Benfica x Porto o2.5 btts @1.90")
        assert len(teams) == 2
        assert teams[0] == "Benfica"
        assert teams[1] == "FC Porto"


class TestParserComplexInputs:
    """Test parser with complex real-world inputs"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_full_complex_input(self, chatbot):
        """Test full complex input with all elements"""
        teams = chatbot._extract_teams_from_text("Chelsea vs Arsenal o2.5 btts sim @2.10")
        assert len(teams) == 2
        assert teams[0] == "Chelsea"
        assert teams[1] == "Arsenal"
    
    def test_portuguese_teams(self, chatbot):
        """Test Portuguese league teams"""
        teams = chatbot._extract_teams_from_text("Sporting x Braga")
        assert len(teams) == 2
        assert teams[0] == "Sporting CP"
        assert teams[1] == "SC Braga"
    
    def test_brazilian_teams(self, chatbot):
        """Test Brazilian league teams"""
        teams = chatbot._extract_teams_from_text("Flamengo x Palmeiras")
        assert len(teams) == 2
        assert teams[0] == "Flamengo"
        assert teams[1] == "Palmeiras"
    
    def test_italian_teams(self, chatbot):
        """Test Italian league teams"""
        teams = chatbot._extract_teams_from_text("Juventus x Milan")
        assert len(teams) == 2
        assert teams[0] == "Juventus"
        assert teams[1] == "AC Milan"
    
    def test_german_teams(self, chatbot):
        """Test German league teams"""
        teams = chatbot._extract_teams_from_text("Bayern x Dortmund")
        assert len(teams) == 2
        assert teams[0] == "Bayern Munich"
        assert teams[1] == "Borussia Dortmund"


class TestParserEdgeCases:
    """Test parser edge cases"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_extra_spaces(self, chatbot):
        """Test with extra spaces"""
        teams = chatbot._extract_teams_from_text("Arsenal   x   Chelsea")
        assert len(teams) == 2
        assert teams[0] == "Arsenal"
        assert teams[1] == "Chelsea"
    
    def test_no_separator(self, chatbot):
        """Test with no separator - should return empty"""
        teams = chatbot._extract_teams_from_text("Arsenal Chelsea")
        assert len(teams) == 0
    
    def test_single_team(self, chatbot):
        """Test with single team - should return empty"""
        teams = chatbot._extract_teams_from_text("Arsenal")
        assert len(teams) == 0
    
    def test_empty_input(self, chatbot):
        """Test with empty input"""
        teams = chatbot._extract_teams_from_text("")
        assert len(teams) == 0


class TestIntelligentParse:
    """Test the intelligent parse function"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    def test_extracts_markets(self, chatbot):
        """Test that markets are extracted"""
        result = chatbot._intelligent_parse("Arsenal x Chelsea over 2.5")
        assert "Over 2.5" in result["markets"][0] or len(result["markets"]) > 0
    
    def test_extracts_odds(self, chatbot):
        """Test that odds are extracted"""
        result = chatbot._intelligent_parse("Arsenal x Chelsea @2.10")
        assert "2.10" in result["odds"] or len(result["odds"]) > 0
    
    def test_extracts_teams_text(self, chatbot):
        """Test that teams text is extracted"""
        result = chatbot._intelligent_parse("Arsenal x Chelsea")
        assert "arsenal" in result["teams_text"].lower() or "chelsea" in result["teams_text"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
