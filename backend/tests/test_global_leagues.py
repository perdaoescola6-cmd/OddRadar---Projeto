"""
Multi-league tests for global coverage
Tests teams from Brazil, Saudi Arabia, Europe, Americas, Asia
"""
import pytest
import sys
sys.path.insert(0, '..')

from football_api import FootballAPI


class TestSaudiArabiaLeague:
    """Test Saudi Pro League teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_al_khaleej(self, api):
        """Test Al-Khaleej resolution"""
        team = await api.resolve_team("Al-Khaleej FC")
        assert team is not None, "Al-Khaleej should be found"
        assert "Khaleej" in team.get("name", ""), f"Expected Khaleej in name, got {team.get('name')}"
    
    @pytest.mark.asyncio
    async def test_al_qadsiah(self, api):
        """Test Al-Qadsiah resolution"""
        team = await api.resolve_team("Al-Qadsiah FC")
        assert team is not None, "Al-Qadsiah should be found"
        assert "Qadisiyah" in team.get("name", "") or "Qadsiah" in team.get("name", ""), f"Expected Qadisiyah in name, got {team.get('name')}"
    
    @pytest.mark.asyncio
    async def test_al_hilal(self, api):
        """Test Al-Hilal resolution"""
        team = await api.resolve_team("Al-Hilal")
        assert team is not None, "Al-Hilal should be found"
        assert "Hilal" in team.get("name", ""), f"Expected Hilal in name, got {team.get('name')}"
    
    @pytest.mark.asyncio
    async def test_al_nassr(self, api):
        """Test Al-Nassr resolution"""
        team = await api.resolve_team("Al-Nassr")
        assert team is not None, "Al-Nassr should be found"
        assert "Nassr" in team.get("name", ""), f"Expected Nassr in name, got {team.get('name')}"
    
    @pytest.mark.asyncio
    async def test_al_ittihad(self, api):
        """Test Al-Ittihad resolution"""
        team = await api.resolve_team("Al-Ittihad")
        assert team is not None, "Al-Ittihad should be found"


class TestBrazilLeagues:
    """Test Brazilian leagues - Série A, B, Estaduais"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_flamengo(self, api):
        """Test Flamengo resolution"""
        team = await api.resolve_team("Flamengo")
        assert team is not None, "Flamengo should be found"
        assert "Flamengo" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_palmeiras(self, api):
        """Test Palmeiras resolution"""
        team = await api.resolve_team("Palmeiras")
        assert team is not None, "Palmeiras should be found"
    
    @pytest.mark.asyncio
    async def test_corinthians(self, api):
        """Test Corinthians resolution"""
        team = await api.resolve_team("Corinthians")
        assert team is not None, "Corinthians should be found"
    
    @pytest.mark.asyncio
    async def test_atletico_mineiro(self, api):
        """Test Atlético Mineiro resolution with alias"""
        team = await api.resolve_team("Galo")
        assert team is not None, "Atlético-MG (Galo) should be found"
    
    @pytest.mark.asyncio
    async def test_cruzeiro(self, api):
        """Test Cruzeiro resolution"""
        team = await api.resolve_team("Cruzeiro")
        assert team is not None, "Cruzeiro should be found"
    
    @pytest.mark.asyncio
    async def test_sport_recife(self, api):
        """Test Sport Recife (Série B) resolution"""
        team = await api.resolve_team("Sport Recife")
        assert team is not None, "Sport Recife should be found"
    
    @pytest.mark.asyncio
    async def test_vitoria(self, api):
        """Test Vitória resolution"""
        team = await api.resolve_team("Vitoria")
        assert team is not None, "Vitória should be found"


class TestArgentinaLeague:
    """Test Argentine Primera División teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_boca_juniors(self, api):
        """Test Boca Juniors resolution"""
        team = await api.resolve_team("Boca Juniors")
        assert team is not None, "Boca Juniors should be found"
        assert "Boca" in team.get("name", "")
    
    @pytest.mark.asyncio
    async def test_river_plate(self, api):
        """Test River Plate resolution"""
        team = await api.resolve_team("River Plate")
        assert team is not None, "River Plate should be found"
    
    @pytest.mark.asyncio
    async def test_racing_club(self, api):
        """Test Racing Club resolution"""
        team = await api.resolve_team("Racing Club")
        assert team is not None, "Racing Club should be found"


class TestMexicoLeague:
    """Test Liga MX teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_club_america(self, api):
        """Test Club América resolution"""
        team = await api.resolve_team("Club America")
        assert team is not None, "Club América should be found"
    
    @pytest.mark.asyncio
    async def test_chivas(self, api):
        """Test Chivas (Guadalajara) resolution"""
        team = await api.resolve_team("Chivas")
        assert team is not None, "Chivas should be found"
    
    @pytest.mark.asyncio
    async def test_tigres(self, api):
        """Test Tigres UANL resolution"""
        team = await api.resolve_team("Tigres")
        assert team is not None, "Tigres should be found"
    
    @pytest.mark.asyncio
    async def test_monterrey(self, api):
        """Test Monterrey resolution"""
        team = await api.resolve_team("Monterrey")
        assert team is not None, "Monterrey should be found"


class TestJapanKoreaLeagues:
    """Test J-League and K-League teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_vissel_kobe(self, api):
        """Test Vissel Kobe resolution"""
        team = await api.resolve_team("Vissel Kobe")
        assert team is not None, "Vissel Kobe should be found"
    
    @pytest.mark.asyncio
    async def test_kawasaki(self, api):
        """Test Kawasaki Frontale resolution"""
        team = await api.resolve_team("Kawasaki Frontale")
        assert team is not None, "Kawasaki Frontale should be found"
    
    @pytest.mark.asyncio
    async def test_ulsan(self, api):
        """Test Ulsan Hyundai resolution"""
        team = await api.resolve_team("Ulsan Hyundai")
        assert team is not None, "Ulsan Hyundai should be found"


class TestMLSLeague:
    """Test MLS teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_inter_miami(self, api):
        """Test Inter Miami resolution"""
        team = await api.resolve_team("Inter Miami")
        assert team is not None, "Inter Miami should be found"
    
    @pytest.mark.asyncio
    async def test_la_galaxy(self, api):
        """Test LA Galaxy resolution"""
        team = await api.resolve_team("LA Galaxy")
        assert team is not None, "LA Galaxy should be found"
    
    @pytest.mark.asyncio
    async def test_atlanta_united(self, api):
        """Test Atlanta United resolution"""
        team = await api.resolve_team("Atlanta United")
        assert team is not None, "Atlanta United should be found"


class TestMiddleEastLeagues:
    """Test UAE and Qatar league teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_al_ain(self, api):
        """Test Al-Ain (UAE) resolution"""
        team = await api.resolve_team("Al-Ain")
        assert team is not None, "Al-Ain should be found"
    
    @pytest.mark.asyncio
    async def test_al_sadd(self, api):
        """Test Al-Sadd (Qatar) resolution"""
        team = await api.resolve_team("Al-Sadd")
        assert team is not None, "Al-Sadd should be found"


class TestEuropeanLeagues:
    """Test European league teams beyond top 5"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_club_brugge(self, api):
        """Test Club Brugge (Belgium) resolution"""
        team = await api.resolve_team("Club Brugge")
        assert team is not None, "Club Brugge should be found"
    
    @pytest.mark.asyncio
    async def test_fc_copenhagen(self, api):
        """Test FC Copenhagen (Denmark) resolution"""
        team = await api.resolve_team("FC Copenhagen")
        assert team is not None, "FC Copenhagen should be found"
    
    @pytest.mark.asyncio
    async def test_legia_warsaw(self, api):
        """Test Legia Warsaw (Poland) resolution"""
        team = await api.resolve_team("Legia Warsaw")
        assert team is not None, "Legia Warsaw should be found"
    
    @pytest.mark.asyncio
    async def test_sparta_prague(self, api):
        """Test Sparta Prague (Czech) resolution"""
        team = await api.resolve_team("Sparta Prague")
        assert team is not None, "Sparta Prague should be found"
    
    @pytest.mark.asyncio
    async def test_galatasaray(self, api):
        """Test Galatasaray (Turkey) resolution"""
        team = await api.resolve_team("Galatasaray")
        assert team is not None, "Galatasaray should be found"


class TestChileColombiaLeagues:
    """Test Chilean and Colombian league teams"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_colo_colo(self, api):
        """Test Colo Colo (Chile) resolution"""
        team = await api.resolve_team("Colo Colo")
        assert team is not None, "Colo Colo should be found"
    
    @pytest.mark.asyncio
    async def test_universidad_chile(self, api):
        """Test Universidad de Chile resolution"""
        team = await api.resolve_team("Universidad de Chile")
        assert team is not None, "Universidad de Chile should be found"
    
    @pytest.mark.asyncio
    async def test_atletico_nacional(self, api):
        """Test Atlético Nacional (Colombia) resolution"""
        team = await api.resolve_team("Atletico Nacional")
        assert team is not None, "Atlético Nacional should be found"
    
    @pytest.mark.asyncio
    async def test_millonarios(self, api):
        """Test Millonarios (Colombia) resolution"""
        team = await api.resolve_team("Millonarios")
        assert team is not None, "Millonarios should be found"


class TestAliasNormalization:
    """Test that aliases work with various input formats"""
    
    @pytest.fixture
    def api(self):
        return FootballAPI()
    
    @pytest.mark.asyncio
    async def test_hyphen_variations(self, api):
        """Test that hyphens are handled correctly"""
        # With hyphen
        team1 = await api.resolve_team("Al-Hilal")
        # Without hyphen
        team2 = await api.resolve_team("Al Hilal")
        
        assert team1 is not None, "Al-Hilal (with hyphen) should be found"
        assert team2 is not None, "Al Hilal (without hyphen) should be found"
    
    @pytest.mark.asyncio
    async def test_fc_suffix_variations(self, api):
        """Test that FC suffix is handled correctly"""
        team1 = await api.resolve_team("Al-Khaleej")
        team2 = await api.resolve_team("Al-Khaleej FC")
        
        assert team1 is not None, "Al-Khaleej should be found"
        assert team2 is not None, "Al-Khaleej FC should be found"
    
    @pytest.mark.asyncio
    async def test_case_insensitive(self, api):
        """Test case insensitivity"""
        team1 = await api.resolve_team("FLAMENGO")
        team2 = await api.resolve_team("flamengo")
        team3 = await api.resolve_team("Flamengo")
        
        assert team1 is not None, "FLAMENGO should be found"
        assert team2 is not None, "flamengo should be found"
        assert team3 is not None, "Flamengo should be found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
