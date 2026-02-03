"""
End-to-end tests for the BetFaro chat flow
Tests the complete flow from user input to analysis output
"""
import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import ChatBot
from football_api import FootballAPI
from models import User, Subscription


class MockUser:
    """Mock user for testing"""
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"
        self.subscription = MockSubscription()
        self.daily_usage = {}


class MockSubscription:
    """Mock subscription for testing"""
    def __init__(self):
        self.plan = "Elite"
        self.status = "active"


class TestE2EBasicFlow:
    """Test basic end-to-end flow"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    @pytest.mark.asyncio
    async def test_arsenal_vs_chelsea(self, chatbot, user):
        """Test Arsenal vs Chelsea analysis"""
        response = await chatbot.process_message("Arsenal x Chelsea", user)
        assert response is not None
        assert len(response) > 0
        # Should not contain error messages
        assert "Ops! Algo deu errado" not in response
        assert "Error" not in response
    
    @pytest.mark.asyncio
    async def test_benfica_vs_porto(self, chatbot, user):
        """Test Benfica vs Porto analysis"""
        response = await chatbot.process_message("Benfica x Porto", user)
        assert response is not None
        assert len(response) > 0
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_real_madrid_vs_barcelona(self, chatbot, user):
        """Test Real Madrid vs Barcelona analysis"""
        response = await chatbot.process_message("Real Madrid x Barcelona", user)
        assert response is not None
        assert len(response) > 0
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_flamengo_vs_palmeiras(self, chatbot, user):
        """Test Flamengo vs Palmeiras analysis"""
        response = await chatbot.process_message("Flamengo x Palmeiras", user)
        assert response is not None
        assert len(response) > 0
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_juventus_vs_milan(self, chatbot, user):
        """Test Juventus vs Milan analysis"""
        response = await chatbot.process_message("Juventus x Milan", user)
        assert response is not None
        assert len(response) > 0
        assert "Ops! Algo deu errado" not in response


class TestE2EWithMarkets:
    """Test E2E flow with markets"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    @pytest.mark.asyncio
    async def test_with_over_2_5(self, chatbot, user):
        """Test with over 2.5 market"""
        response = await chatbot.process_message("Arsenal x Chelsea over 2.5", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_with_btts(self, chatbot, user):
        """Test with BTTS market"""
        response = await chatbot.process_message("Arsenal x Chelsea btts", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_with_odds(self, chatbot, user):
        """Test with odds"""
        response = await chatbot.process_message("Arsenal x Chelsea @2.10", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_full_complex_input(self, chatbot, user):
        """Test full complex input"""
        response = await chatbot.process_message("Benfica x Porto o2.5 btts @1.90", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response


class TestE2ESeparatorVariations:
    """Test E2E with different separator variations"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    @pytest.mark.asyncio
    async def test_separator_x(self, chatbot, user):
        """Test 'x' separator"""
        response = await chatbot.process_message("Liverpool x Arsenal", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_separator_vs(self, chatbot, user):
        """Test 'vs' separator"""
        response = await chatbot.process_message("Liverpool vs Arsenal", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_separator_v(self, chatbot, user):
        """Test 'v' separator"""
        response = await chatbot.process_message("Liverpool v Arsenal", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_separator_dash(self, chatbot, user):
        """Test '-' separator"""
        response = await chatbot.process_message("Liverpool - Arsenal", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response


class TestE2EAliases:
    """Test E2E with team aliases"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    @pytest.mark.asyncio
    async def test_man_united_alias(self, chatbot, user):
        """Test Man United alias"""
        response = await chatbot.process_message("Man United x Liverpool", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_man_city_alias(self, chatbot, user):
        """Test Man City alias"""
        response = await chatbot.process_message("Man City x Arsenal", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_spurs_alias(self, chatbot, user):
        """Test Spurs alias"""
        response = await chatbot.process_message("Spurs x Chelsea", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
    
    @pytest.mark.asyncio
    async def test_barca_alias(self, chatbot, user):
        """Test Barca alias"""
        response = await chatbot.process_message("Real Madrid x Barca", user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response


class TestE2EHelpCommand:
    """Test help command"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    @pytest.mark.asyncio
    async def test_help_command(self, chatbot, user):
        """Test /help command"""
        response = await chatbot.process_message("/help", user)
        assert response is not None
        assert "BetFaro" in response or "Como usar" in response
    
    @pytest.mark.asyncio
    async def test_help_word(self, chatbot, user):
        """Test 'help' word"""
        response = await chatbot.process_message("help", user)
        assert response is not None
    
    @pytest.mark.asyncio
    async def test_ajuda_word(self, chatbot, user):
        """Test 'ajuda' word (Portuguese)"""
        response = await chatbot.process_message("ajuda", user)
        assert response is not None


class TestE2EFallbackMessages:
    """Test that fallback messages are friendly"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    @pytest.mark.asyncio
    async def test_invalid_input_friendly(self, chatbot, user):
        """Test that invalid input returns friendly message"""
        response = await chatbot.process_message("asdfghjkl", user)
        assert response is not None
        # Should not contain technical errors
        assert "Error" not in response
        assert "Exception" not in response
        assert "Traceback" not in response
    
    @pytest.mark.asyncio
    async def test_single_word_friendly(self, chatbot, user):
        """Test that single word returns friendly message"""
        response = await chatbot.process_message("teste", user)
        assert response is not None
        assert "Error" not in response


class TestE2ENoErrorMessages:
    """Test that no error messages appear in common cases"""
    
    @pytest.fixture
    def chatbot(self):
        return ChatBot()
    
    @pytest.fixture
    def user(self):
        return MockUser()
    
    COMMON_INPUTS = [
        "Arsenal x Chelsea",
        "Arsenal vs Chelsea",
        "Benfica x Porto",
        "Real Madrid x Barcelona",
        "Liverpool x Man City",
        "Juventus x Inter",
        "Bayern x Dortmund",
        "PSG x Marseille",
        "Flamengo x Palmeiras",
        "Corinthians x Sao Paulo",
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_text", COMMON_INPUTS)
    async def test_common_inputs_no_error(self, chatbot, user, input_text):
        """Test that common inputs don't produce error messages"""
        response = await chatbot.process_message(input_text, user)
        assert response is not None
        assert "Ops! Algo deu errado" not in response
        assert "Error processing" not in response
        assert "Exception" not in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
