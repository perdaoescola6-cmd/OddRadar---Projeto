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
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables from parent directory
load_dotenv(dotenv_path="../.env")

logger = logging.getLogger(__name__)

class FootballAPI:
    def __init__(self):
        self.api_key = os.getenv("APISPORTS_KEY")
        self.base_url = os.getenv("APISPORTS_BASE_URL", "https://v3.football.api-sports.io")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client
        if self.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not found - LLM features disabled")
        
        logger.info(f"FootballAPI initialized - API Key present: {bool(self.api_key)}")
        
        # Cache in memory with TTL
        self.cache = {}
        self.CACHE_TTL = 300  # 5 minutes
        
        # Common team aliases (API-Football official names)
        # Comprehensive list covering major leagues worldwide
        self.team_aliases = {
            # Portugal
            "benfica": "Benfica", "sl benfica": "Benfica",
            "porto": "FC Porto", "fc porto": "FC Porto",
            "sporting": "Sporting CP", "sporting cp": "Sporting CP", "sporting lisboa": "Sporting CP",
            "braga": "SC Braga", "sc braga": "SC Braga",
            
            # England - Premier League
            "chelsea": "Chelsea", "arsenal": "Arsenal", "liverpool": "Liverpool",
            "manchester united": "Manchester United", "man united": "Manchester United", "man utd": "Manchester United",
            "manchester city": "Manchester City", "man city": "Manchester City",
            "tottenham": "Tottenham", "spurs": "Tottenham", "tottenham hotspur": "Tottenham",
            "newcastle": "Newcastle", "newcastle united": "Newcastle",
            "west ham": "West Ham", "west ham united": "West Ham",
            "aston villa": "Aston Villa", "villa": "Aston Villa",
            "everton": "Everton", "wolves": "Wolves", "wolverhampton": "Wolves",
            "brighton": "Brighton", "crystal palace": "Crystal Palace",
            "fulham": "Fulham", "brentford": "Brentford", "bournemouth": "Bournemouth",
            "nottingham forest": "Nottingham Forest", "nottingham": "Nottingham Forest",
            "leicester": "Leicester", "leicester city": "Leicester",
            "leeds": "Leeds", "leeds united": "Leeds",
            "southampton": "Southampton",
            
            # Spain - La Liga
            "real madrid": "Real Madrid", "barcelona": "Barcelona", "barca": "Barcelona",
            "atletico madrid": "Atletico Madrid", "atletico": "Atletico Madrid",
            "sevilla": "Sevilla", "valencia": "Valencia", "villarreal": "Villarreal",
            "real betis": "Real Betis", "betis": "Real Betis",
            "athletic bilbao": "Athletic Club", "bilbao": "Athletic Club", "athletic club": "Athletic Club",
            "real sociedad": "Real Sociedad", "sociedad": "Real Sociedad",
            "celta vigo": "Celta Vigo", "celta": "Celta Vigo",
            "getafe": "Getafe", "osasuna": "Osasuna", "mallorca": "Mallorca",
            "rayo vallecano": "Rayo Vallecano", "rayo": "Rayo Vallecano",
            "girona": "Girona", "alaves": "Alaves", "las palmas": "Las Palmas",
            
            # Germany - Bundesliga
            "bayern": "Bayern Munich", "bayern munich": "Bayern Munich", "bayern munchen": "Bayern Munich", "bayern de munique": "Bayern Munich",
            "dortmund": "Borussia Dortmund", "borussia dortmund": "Borussia Dortmund", "bvb": "Borussia Dortmund",
            "leverkusen": "Bayer Leverkusen", "bayer leverkusen": "Bayer Leverkusen", "bayer 04": "Bayer Leverkusen", "bayer": "Bayer Leverkusen",
            "rb leipzig": "RB Leipzig", "leipzig": "RB Leipzig", "rasenballsport leipzig": "RB Leipzig",
            "eintracht frankfurt": "Eintracht Frankfurt", "frankfurt": "Eintracht Frankfurt", "eintracht": "Eintracht Frankfurt",
            "wolfsburg": "VfL Wolfsburg", "vfl wolfsburg": "VfL Wolfsburg",
            "freiburg": "SC Freiburg", "sc freiburg": "SC Freiburg",
            "hoffenheim": "Hoffenheim", "tsg hoffenheim": "Hoffenheim",
            "mainz": "Mainz 05", "mainz 05": "Mainz 05",
            "augsburg": "Augsburg", "fc augsburg": "Augsburg",
            "werder bremen": "Werder Bremen", "bremen": "Werder Bremen",
            "borussia monchengladbach": "Borussia Monchengladbach", "monchengladbach": "Borussia Monchengladbach", "gladbach": "Borussia Monchengladbach",
            "union berlin": "Union Berlin", "fc union berlin": "Union Berlin",
            "koln": "FC Koln", "fc koln": "FC Koln", "cologne": "FC Koln",
            "hertha berlin": "Hertha Berlin", "hertha": "Hertha Berlin",
            "st. pauli": "FC St. Pauli", "st pauli": "FC St. Pauli", "fc st. pauli": "FC St. Pauli", "fc st pauli": "FC St. Pauli", "sankt pauli": "FC St. Pauli",
            "hamburg": "Hamburger SV", "hamburger sv": "Hamburger SV", "hsv": "Hamburger SV",
            "schalke": "Schalke 04", "schalke 04": "Schalke 04",
            "stuttgart": "VfB Stuttgart", "vfb stuttgart": "VfB Stuttgart",
            "heidenheim": "Heidenheim", "fc heidenheim": "Heidenheim",
            "bochum": "VfL Bochum", "vfl bochum": "VfL Bochum",
            "darmstadt": "Darmstadt 98", "darmstadt 98": "Darmstadt 98",
            
            # Italy - Serie A
            "juventus": "Juventus", "juve": "Juventus",
            "milan": "AC Milan", "ac milan": "AC Milan",
            "inter": "Inter", "inter milan": "Inter", "internazionale": "Inter",
            "napoli": "Napoli", "ssc napoli": "Napoli",
            "roma": "AS Roma", "as roma": "AS Roma",
            "lazio": "Lazio", "ss lazio": "Lazio",
            "atalanta": "Atalanta", "fiorentina": "Fiorentina",
            "bologna": "Bologna", "torino": "Torino",
            "udinese": "Udinese", "sassuolo": "Sassuolo",
            "monza": "Monza", "empoli": "Empoli",
            "lecce": "Lecce", "cagliari": "Cagliari",
            "verona": "Verona", "hellas verona": "Verona",
            "genoa": "Genoa", "salernitana": "Salernitana",
            "frosinone": "Frosinone", "como": "Como",
            
            # France - Ligue 1
            "psg": "Paris Saint Germain", "paris saint germain": "Paris Saint Germain", "paris sg": "Paris Saint Germain", "paris": "Paris Saint Germain",
            "marseille": "Marseille", "olympique marseille": "Marseille", "om": "Marseille",
            "lyon": "Lyon", "olympique lyon": "Lyon", "ol": "Lyon",
            "monaco": "Monaco", "as monaco": "Monaco",
            "lille": "Lille", "losc lille": "Lille", "losc": "Lille",
            "nice": "Nice", "ogc nice": "Nice",
            "lens": "Lens", "rc lens": "Lens",
            "rennes": "Rennes", "stade rennais": "Rennes",
            "strasbourg": "Strasbourg", "rc strasbourg": "Strasbourg",
            "nantes": "Nantes", "fc nantes": "Nantes",
            "toulouse": "Toulouse", "montpellier": "Montpellier",
            "reims": "Reims", "stade reims": "Reims",
            "brest": "Brest", "stade brest": "Brest",
            
            # Brazil - Brasileirão
            "flamengo": "Flamengo", "mengao": "Flamengo",
            "palmeiras": "Palmeiras", "verdao": "Palmeiras",
            "corinthians": "Corinthians", "timao": "Corinthians",
            "sao paulo": "Sao Paulo", "spfc": "Sao Paulo",
            "santos": "Santos", "peixe": "Santos",
            "gremio": "Gremio", "imortal": "Gremio",
            "internacional": "Internacional", "inter de porto alegre": "Internacional", "colorado": "Internacional",
            "cruzeiro": "Cruzeiro", "raposa": "Cruzeiro",
            "botafogo": "Botafogo", "fogao": "Botafogo",
            "fluminense": "Fluminense", "flu": "Fluminense",
            "vasco": "Vasco DA Gama", "vasco da gama": "Vasco DA Gama",
            "atletico mineiro": "Atletico-MG", "atletico-mg": "Atletico-MG", "galo": "Atletico-MG",
            "athletico paranaense": "Athletico-PR", "athletico-pr": "Athletico-PR", "furacao": "Athletico-PR",
            "bahia": "Bahia", "fortaleza": "Fortaleza",
            "cuiaba": "Cuiaba", "goias": "Goias",
            "america mineiro": "America-MG", "america-mg": "America-MG",
            "bragantino": "RB Bragantino", "red bull bragantino": "RB Bragantino",
            
            # Netherlands - Eredivisie
            "ajax": "Ajax", "afc ajax": "Ajax",
            "psv": "PSV Eindhoven", "psv eindhoven": "PSV Eindhoven",
            "feyenoord": "Feyenoord",
            "az alkmaar": "AZ Alkmaar", "az": "AZ Alkmaar",
            "twente": "FC Twente", "fc twente": "FC Twente",
            
            # Scotland
            "celtic": "Celtic", "glasgow celtic": "Celtic",
            "rangers": "Rangers", "glasgow rangers": "Rangers",
            
            # Turkey
            "galatasaray": "Galatasaray", "fenerbahce": "Fenerbahce", "besiktas": "Besiktas",
            
            # Argentina
            "boca juniors": "Boca Juniors", "boca": "Boca Juniors",
            "river plate": "River Plate", "river": "River Plate",
            "racing club": "Racing Club", "racing": "Racing Club",
            "independiente": "Independiente",
            "san lorenzo": "San Lorenzo",
            "estudiantes": "Estudiantes",
            "velez sarsfield": "Velez Sarsfield", "velez": "Velez Sarsfield",
            "rosario central": "Rosario Central",
            "newells old boys": "Newells Old Boys", "newells": "Newells Old Boys",
            "talleres": "Talleres Cordoba", "talleres cordoba": "Talleres Cordoba",
            "argentinos juniors": "Argentinos Juniors",
            "lanus": "Lanus", "defensa y justicia": "Defensa Y Justicia",
            "godoy cruz": "Godoy Cruz", "union santa fe": "Union Santa Fe",
            "banfield": "Banfield", "huracan": "Huracan",
            
            # Saudi Arabia - Saudi Pro League (keys normalized without hyphens)
            "al hilal": "Al-Hilal", "alhilal": "Al-Hilal", "hilal": "Al-Hilal",
            "al nassr": "Al-Nassr", "alnassr": "Al-Nassr", "nassr": "Al-Nassr",
            "al ittihad": "Al-Ittihad", "alittihad": "Al-Ittihad", "ittihad": "Al-Ittihad",
            "al ahli": "Al-Ahli Saudi", "alahli": "Al-Ahli Saudi", "ahli saudi": "Al-Ahli Saudi", "al ahli saudi": "Al-Ahli Saudi",
            "al shabab": "Al-Shabab", "alshabab": "Al-Shabab", "shabab": "Al-Shabab",
            "al fateh": "Al-Fateh", "alfateh": "Al-Fateh", "fateh": "Al-Fateh",
            "al taawoun": "Al-Taawoun", "altaawoun": "Al-Taawoun", "taawoun": "Al-Taawoun",
            "al ettifaq": "Al-Ettifaq", "alettifaq": "Al-Ettifaq", "ettifaq": "Al-Ettifaq",
            "al khaleej": "Al Khaleej Saihat", "alkhaleej": "Al Khaleej Saihat", "khaleej": "Al Khaleej Saihat", "al khaleej fc": "Al Khaleej Saihat", "alkhaleej fc": "Al Khaleej Saihat", "al khaleej saihat": "Al Khaleej Saihat",
            "al qadsiah": "Al-Qadisiyah FC", "alqadsiah": "Al-Qadisiyah FC", "qadsiah": "Al-Qadisiyah FC", "al qadsiah fc": "Al-Qadisiyah FC", "alqadsiah fc": "Al-Qadisiyah FC", "al qadisiyah": "Al-Qadisiyah FC", "alqadisiyah": "Al-Qadisiyah FC", "qadisiyah": "Al-Qadisiyah FC", "al qadisiyah fc": "Al-Qadisiyah FC",
            "al feiha": "Al-Feiha", "alfeiha": "Al-Feiha", "feiha": "Al-Feiha",
            "al raed": "Al-Raed", "alraed": "Al-Raed", "raed": "Al-Raed",
            "al riyadh": "Al-Riyadh", "alriyadh": "Al-Riyadh",
            "al okhdood": "Al-Okhdood", "alokhdood": "Al-Okhdood", "okhdood": "Al-Okhdood",
            "al akhdoud": "Al-Okhdood", "alakhdoud": "Al-Okhdood",
            "damac": "Damac FC", "damac fc": "Damac FC",
            "al wehda": "Al-Wehda", "alwehda": "Al-Wehda", "wehda": "Al-Wehda",
            "al hazem": "Al-Hazem", "alhazem": "Al-Hazem",
            "al tai": "Al-Tai", "altai": "Al-Tai",
            "abha": "Abha Club", "abha club": "Abha Club",
            
            # Mexico - Liga MX
            "club america": "Club America", "america": "Club America",
            "guadalajara": "Guadalajara", "chivas": "Guadalajara",
            "cruz azul": "Cruz Azul",
            "monterrey": "Monterrey", "rayados": "Monterrey",
            "tigres": "Tigres UANL", "tigres uanl": "Tigres UANL",
            "pumas": "Pumas UNAM", "pumas unam": "Pumas UNAM",
            "santos laguna": "Santos Laguna",
            "leon": "Leon", "club leon": "Leon",
            "toluca": "Toluca",
            "pachuca": "Pachuca",
            "atlas": "Atlas",
            "necaxa": "Necaxa",
            "puebla": "Puebla",
            "queretaro": "Queretaro",
            "mazatlan": "Mazatlan FC", "mazatlan fc": "Mazatlan FC",
            "juarez": "FC Juarez", "fc juarez": "FC Juarez",
            "tijuana": "Club Tijuana", "club tijuana": "Club Tijuana", "xolos": "Club Tijuana",
            
            # Chile - Primera Division
            "colo colo": "Colo Colo", "colo-colo": "Colo Colo",
            "universidad de chile": "Universidad De Chile", "u de chile": "Universidad De Chile", "la u": "Universidad De Chile",
            "universidad catolica": "Universidad Catolica", "catolica": "Universidad Catolica",
            "cobreloa": "Cobreloa",
            "huachipato": "Huachipato",
            "union espanola": "Union Espanola",
            "audax italiano": "Audax Italiano",
            "ohiggins": "O'Higgins", "o'higgins": "O'Higgins",
            "cobresal": "Cobresal",
            "everton chile": "Everton de Vina", "everton de vina": "Everton de Vina",
            
            # Colombia - Primera A
            "atletico nacional": "Atletico Nacional", "nacional medellin": "Atletico Nacional",
            "millonarios": "Millonarios",
            "america de cali": "America de Cali",
            "deportivo cali": "Deportivo Cali",
            "junior barranquilla": "Junior FC", "junior fc": "Junior FC", "junior": "Junior FC",
            "santa fe": "Independiente Santa Fe", "independiente santa fe": "Independiente Santa Fe",
            "deportes tolima": "Deportes Tolima", "tolima": "Deportes Tolima",
            "once caldas": "Once Caldas",
            "envigado": "Envigado",
            "la equidad": "La Equidad",
            
            # Japan - J-League
            "vissel kobe": "Vissel Kobe", "kobe": "Vissel Kobe",
            "kawasaki frontale": "Kawasaki Frontale", "kawasaki": "Kawasaki Frontale",
            "yokohama f marinos": "Yokohama F. Marinos", "yokohama marinos": "Yokohama F. Marinos",
            "urawa reds": "Urawa Red Diamonds", "urawa red diamonds": "Urawa Red Diamonds",
            "kashima antlers": "Kashima Antlers", "kashima": "Kashima Antlers",
            "fc tokyo": "FC Tokyo", "tokyo": "FC Tokyo",
            "nagoya grampus": "Nagoya Grampus", "nagoya": "Nagoya Grampus",
            "cerezo osaka": "Cerezo Osaka", "osaka": "Cerezo Osaka",
            "gamba osaka": "Gamba Osaka",
            "sanfrecce hiroshima": "Sanfrecce Hiroshima", "hiroshima": "Sanfrecce Hiroshima",
            
            # South Korea - K-League
            "jeonbuk": "Jeonbuk Motors", "jeonbuk motors": "Jeonbuk Motors",
            "ulsan": "Ulsan Hyundai", "ulsan hyundai": "Ulsan Hyundai",
            "pohang steelers": "Pohang Steelers", "pohang": "Pohang Steelers",
            "suwon samsung": "Suwon Bluewings", "suwon bluewings": "Suwon Bluewings",
            "fc seoul": "FC Seoul", "seoul": "FC Seoul",
            "daegu fc": "Daegu FC", "daegu": "Daegu FC",
            "incheon united": "Incheon United", "incheon": "Incheon United",
            "gangwon fc": "Gangwon FC", "gangwon": "Gangwon FC",
            
            # USA - MLS
            "la galaxy": "LA Galaxy", "galaxy": "LA Galaxy",
            "lafc": "Los Angeles FC", "los angeles fc": "Los Angeles FC",
            "inter miami": "Inter Miami", "miami": "Inter Miami",
            "new york red bulls": "New York Red Bulls", "red bulls": "New York Red Bulls",
            "new york city fc": "New York City FC", "nycfc": "New York City FC",
            "atlanta united": "Atlanta United",
            "seattle sounders": "Seattle Sounders", "sounders": "Seattle Sounders",
            "portland timbers": "Portland Timbers", "timbers": "Portland Timbers",
            "austin fc": "Austin FC", "austin": "Austin FC",
            "nashville sc": "Nashville SC", "nashville": "Nashville SC",
            "columbus crew": "Columbus Crew", "crew": "Columbus Crew",
            "philadelphia union": "Philadelphia Union",
            "fc cincinnati": "FC Cincinnati", "cincinnati": "FC Cincinnati",
            "toronto fc": "Toronto FC", "toronto": "Toronto FC",
            "cf montreal": "CF Montreal", "montreal": "CF Montreal",
            "vancouver whitecaps": "Vancouver Whitecaps", "whitecaps": "Vancouver Whitecaps",
            
            # China - Chinese Super League
            "shanghai port": "Shanghai Port", "shanghai sipg": "Shanghai Port",
            "shandong taishan": "Shandong Taishan", "shandong": "Shandong Taishan",
            "guangzhou fc": "Guangzhou FC", "guangzhou": "Guangzhou FC",
            "beijing guoan": "Beijing Guoan", "beijing": "Beijing Guoan",
            "shanghai shenhua": "Shanghai Shenhua", "shenhua": "Shanghai Shenhua",
            "wuhan three towns": "Wuhan Three Towns", "wuhan": "Wuhan Three Towns",
            "chengdu rongcheng": "Chengdu Rongcheng", "chengdu": "Chengdu Rongcheng",
            
            # UAE - UAE League
            "al ain": "Al-Ain", "al-ain": "Al-Ain", "ain": "Al-Ain",
            "al wahda uae": "Al-Wahda", "al wahda": "Al-Wahda", "al-wahda": "Al-Wahda",
            "shabab al ahli": "Shabab Al-Ahli", "shabab al-ahli": "Shabab Al-Ahli",
            "al jazira": "Al-Jazira", "al-jazira": "Al-Jazira", "jazira": "Al-Jazira",
            "al nasr dubai": "Al-Nasr Dubai", "al nasr uae": "Al-Nasr Dubai",
            "baniyas": "Baniyas",
            "al sharjah": "Al-Sharjah", "al-sharjah": "Al-Sharjah", "sharjah": "Al-Sharjah",
            
            # Qatar - Qatar Stars League
            "al sadd": "Al-Sadd", "al-sadd": "Al-Sadd", "sadd": "Al-Sadd",
            "al duhail": "Al-Duhail", "al-duhail": "Al-Duhail", "duhail": "Al-Duhail",
            "al rayyan": "Al-Rayyan", "al-rayyan": "Al-Rayyan", "rayyan": "Al-Rayyan",
            "al arabi qatar": "Al-Arabi", "al arabi": "Al-Arabi", "al-arabi": "Al-Arabi",
            "al gharafa": "Al-Gharafa", "al-gharafa": "Al-Gharafa", "gharafa": "Al-Gharafa",
            "al wakrah": "Al-Wakrah", "al-wakrah": "Al-Wakrah", "wakrah": "Al-Wakrah",
            
            # Belgium - Pro League
            "club brugge": "Club Brugge", "brugge": "Club Brugge",
            "anderlecht": "Anderlecht", "rsc anderlecht": "Anderlecht",
            "genk": "Genk", "krc genk": "Genk",
            "standard liege": "Standard Liege", "standard": "Standard Liege",
            "gent": "Gent", "kaa gent": "Gent",
            "antwerp": "Antwerp", "royal antwerp": "Antwerp",
            "union sg": "Union St. Gilloise", "union st gilloise": "Union St. Gilloise",
            
            # Denmark - Superliga
            "fc copenhagen": "FC Copenhagen", "copenhagen": "FC Copenhagen",
            "fc midtjylland": "FC Midtjylland", "midtjylland": "FC Midtjylland",
            "brondby": "Brondby",
            "nordsjaelland": "FC Nordsjaelland", "fc nordsjaelland": "FC Nordsjaelland",
            "aarhus": "AGF Aarhus", "agf": "AGF Aarhus",
            
            # Poland - Ekstraklasa
            "legia warsaw": "Legia Warszawa", "legia": "Legia Warszawa", "legia warszawa": "Legia Warszawa",
            "lech poznan": "Lech Poznan", "lech": "Lech Poznan",
            "rakow czestochowa": "Rakow", "rakow": "Rakow",
            "jagiellonia": "Jagiellonia",
            "pogon szczecin": "Pogon Szczecin", "pogon": "Pogon Szczecin",
            
            # Czech Republic - Czech League
            "sparta prague": "Sparta Praha", "sparta praha": "Sparta Praha", "sparta": "Sparta Praha",
            "slavia prague": "Slavia Praha", "slavia praha": "Slavia Praha", "slavia": "Slavia Praha",
            "viktoria plzen": "Viktoria Plzen", "plzen": "Viktoria Plzen",
            "banik ostrava": "Banik Ostrava",
            
            # Brazil - Série B and more
            "sport recife": "Sport Recife", "sport": "Sport Recife",
            "vitoria": "Vitoria", "ec vitoria": "Vitoria",
            "ceara": "Ceara", "ceara sc": "Ceara",
            "coritiba": "Coritiba",
            "criciuma": "Criciuma",
            "chapecoense": "Chapecoense",
            "avai": "Avai",
            "ponte preta": "Ponte Preta",
            "guarani": "Guarani",
            "novorizontino": "Novorizontino",
            "mirassol": "Mirassol",
            "ituano": "Ituano",
            "juventude": "Juventude",
            "operario": "Operario-PR", "operario pr": "Operario-PR",
            "vila nova": "Vila Nova",
            "goias": "Goias",
            "csa": "CSA",
            "abc": "ABC",
            "botafogo pb": "Botafogo-PB", "botafogo-pb": "Botafogo-PB",
            "nautico": "Nautico",
            "santa cruz": "Santa Cruz",
            "remo": "Remo",
            "paysandu": "Paysandu",
            "sampaio correa": "Sampaio Correa",
            "tombense": "Tombense",
            "athletic club": "Athletic Club-MG",
            
            # Brazil - Estaduais
            "sao paulo fc": "Sao Paulo",
            "palmeiras sp": "Palmeiras",
            "corinthians sp": "Corinthians",
            "santos sp": "Santos",
            "red bull bragantino": "RB Bragantino",
            "inter de limeira": "Inter de Limeira",
            "agua santa": "Agua Santa",
            "sao bernardo": "Sao Bernardo",
            "portuguesa": "Portuguesa",
            "ferroviaria": "Ferroviaria",
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
    
    async def translate_team_name_with_llm(self, user_input: str) -> Dict:
        """Use LLM to extract and translate team names from user input"""
        if not self.openai_client:
            return {"teams": [], "mode": "match", "ambiguous": False}
        
        try:
            prompt = f"""Você é um especialista em futebol mundial. O usuário digitou: "{user_input}"

TAREFA: Extraia os nomes dos times e traduza para o nome oficial usado pela API-Football.

REGRAS DE PRIORIDADE (quando houver ambiguidade):
1. Sempre priorize times das TOP 5 ligas europeias (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
2. Depois priorize times brasileiros (Série A)
3. Depois times portugueses (Primeira Liga)

EXEMPLOS DE DESAMBIGUAÇÃO:
- "Atletico" sozinho → perguntar (pode ser Atletico Madrid, Atletico Mineiro, Atletico Paranaense, etc)
- "Atletico Madrid" → "Atletico Madrid"
- "Atletico Mineiro" ou "Galo" → "Atletico-MG"
- "Sporting" sozinho → "Sporting CP" (Portugal, mais famoso)
- "Inter" sozinho → "Inter" (Inter Milan, mais famoso que Internacional)
- "Internacional" ou "Inter de Porto Alegre" → "Internacional"
- "United" sozinho → "Manchester United"
- "City" sozinho → "Manchester City"

NOMES OFICIAIS API-FOOTBALL:
- Benfica, FC Porto, Sporting CP, SC Braga
- Flamengo, Palmeiras, Corinthians, Sao Paulo, Santos, Gremio, Internacional, Atletico-MG, Cruzeiro, Botafogo, Fluminense, Vasco DA Gama
- Chelsea, Liverpool, Manchester United, Manchester City, Arsenal, Tottenham
- Real Madrid, Barcelona, Atletico Madrid, Sevilla, Valencia
- Juventus, AC Milan, Inter, Napoli, AS Roma, Lazio
- Bayern Munich, Borussia Dortmund, RB Leipzig
- Paris Saint Germain, Marseille, Lyon

Responda APENAS em JSON válido:

Se identificar os times claramente:
{{"teams": ["Time 1", "Time 2"], "mode": "match", "ambiguous": false}}

Se for estatísticas de um time:
{{"teams": ["Time"], "mode": "stats", "ambiguous": false}}

Se o nome for AMBÍGUO (ex: "Atletico", "Sporting", "United" sem contexto):
{{"teams": [], "mode": "match", "ambiguous": true, "options": ["Atletico Madrid", "Atletico-MG", "Atletico Paranaense"], "question": "Qual Atlético você quer dizer?"}}

Se não conseguir identificar:
{{"teams": [], "mode": "unknown", "ambiguous": false}}"""

            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=250
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up response
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            logger.info(f"LLM translated '{user_input}' to: {result}")
            return result
            
        except Exception as e:
            logger.error(f"LLM translation error: {str(e)}")
            return {"teams": [], "mode": "match", "ambiguous": False}
    
    async def _make_request(self, endpoint: str, params: Dict = None, max_retries: int = 2) -> Dict:
        """Make HTTP request with timeout and retry"""
        if not self.api_key:
            logger.error("APISPORTS_KEY not configured!")
            raise Exception("API key not configured. Please set APISPORTS_KEY in .env")
        
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
        """Search for teams by name with fallback variations"""
        # First replace hyphens with spaces, then clean
        query_with_spaces = query.replace('-', ' ').replace('.', ' ')
        # Clean query - API only accepts alphanumeric and spaces
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query_with_spaces).strip()
        # Normalize multiple spaces
        clean_query = re.sub(r'\s+', ' ', clean_query)
        
        # Generate search variations to try
        search_variations = [clean_query]
        
        words = clean_query.split()
        
        # For Arabic teams (Al-X pattern), try just the main name
        if len(words) >= 2 and words[0].lower() == "al":
            # "Al Qadisiyah FC" -> "Qadisiyah"
            main_name = words[1] if len(words) > 1 else ""
            if main_name and len(main_name) >= 3:
                search_variations.insert(0, main_name)  # Try main name first
            # Also try "Al X" without FC/Club suffix
            if len(words) > 2:
                search_variations.append(' '.join(words[:2]))
        
        # Add variations: last word only (for cases like "FC St Pauli" -> "Pauli")
        if len(words) > 1:
            search_variations.append(words[-1])  # Last word
            if len(words) > 2:
                search_variations.append(' '.join(words[-2:]))  # Last 2 words
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for v in search_variations:
            if v.lower() not in seen and len(v) >= 3:
                seen.add(v.lower())
                unique_variations.append(v)
        
        # Try each variation until we find results
        for search_term in unique_variations:
            cache_key = f"search_teams_{search_term}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached
            
            try:
                params = {"search": search_term}
                logger.info(f"[SEARCH] Trying: '{search_term}' (original: '{query}')")
                result = await self._make_request("teams", params)
                if result:
                    self._set_cache(cache_key, result)
                    return result
            except Exception as e:
                logger.warning(f"Search failed for '{search_term}': {str(e)}")
                continue
        
        logger.warning(f"[SEARCH] No results for any variation of '{query}'")
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
        """Resolve team name to team info with fuzzy matching and context awareness"""
        original_name = team_name
        normalized_name = self._normalize_text(team_name)
        
        logger.info(f"[RESOLVE] Resolving team: '{original_name}' (normalized: '{normalized_name}')")
        
        # Check aliases first
        alias_name = None
        if normalized_name in self.team_aliases:
            alias_name = self.team_aliases[normalized_name]
            logger.info(f"[RESOLVE] Found alias: '{normalized_name}' -> '{alias_name}'")
        
        # Context-aware resolution for opponent matching
        if context_fixtures:
            for fixture in context_fixtures:
                opponent = fixture.get("teams", {}).get("away", {}) if fixture.get("teams", {}).get("home", {}).get("name", "").lower() == team_name.lower() else fixture.get("teams", {}).get("home", {})
                if opponent and self._normalize_text(opponent.get("name", "")) == normalized_name:
                    logger.info(f"[RESOLVE] Found in context: {opponent.get('name')}")
                    return opponent
        
        # Try searching with alias first, then original name
        search_names = []
        if alias_name:
            search_names.append(alias_name)
        search_names.append(original_name)
        
        teams = []
        for search_name in search_names:
            try:
                teams = await self.search_teams(search_name)
                if teams:
                    logger.info(f"[RESOLVE] API returned {len(teams)} teams for '{search_name}'")
                    break
            except Exception as e:
                logger.error(f"[RESOLVE] API error searching '{search_name}': {str(e)}")
                continue
        
        if not teams:
            logger.warning(f"[RESOLVE] No teams found for '{original_name}' (alias: {alias_name})")
            return None
        
        # Score and rank candidates
        candidates = []
        search_normalized = self._normalize_text(alias_name or original_name)
        
        for team in teams:
            team_info = team.get("team", team)  # Handle both formats
            team_name_api = team_info.get("name", "")
            team_name_normalized = self._normalize_text(team_name_api)
            
            # Skip women/U20/reserves unless explicitly requested
            skip_keywords = ["women", "feminino", "u20", "u21", "u23", "reserve", "b team", "ii", "sub-"]
            if any(keyword in team_name_normalized for keyword in skip_keywords):
                continue
            
            # Calculate match score
            score = self._calculate_match_score(search_normalized, team_name_normalized)
            candidates.append({
                "team": team_info,
                "score": score,
                "name": team_name_api
            })
        
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Log top candidates
        if candidates:
            logger.info(f"[RESOLVE] Top candidates for '{original_name}':")
            for i, c in enumerate(candidates[:3]):
                logger.info(f"  {i+1}. {c['name']} (score: {c['score']:.2f})")
        
        # Return best match if score is high enough
        if candidates and candidates[0]["score"] >= 0.5:
            best = candidates[0]
            logger.info(f"[RESOLVE] Selected: {best['name']} (score: {best['score']:.2f})")
            return best["team"]
        
        # Fallback to first result if no good match
        if candidates:
            fallback = candidates[0]
            logger.info(f"[RESOLVE] Fallback to: {fallback['name']} (score: {fallback['score']:.2f})")
            return fallback["team"]
        
        logger.warning(f"[RESOLVE] No valid candidates for '{original_name}'")
        return None
    
    def _calculate_match_score(self, search: str, candidate: str) -> float:
        """Calculate fuzzy match score between search term and candidate"""
        # Exact match
        if search == candidate:
            return 1.0
        
        # One contains the other
        if search in candidate:
            return 0.9
        if candidate in search:
            return 0.85
        
        # Word-level matching
        search_words = set(search.split())
        candidate_words = set(candidate.split())
        
        if search_words and candidate_words:
            common = search_words & candidate_words
            if common:
                # Jaccard similarity
                union = search_words | candidate_words
                jaccard = len(common) / len(union)
                return 0.5 + (jaccard * 0.4)
        
        # Character-level similarity (simple)
        if len(search) > 0 and len(candidate) > 0:
            # Count matching characters
            matches = sum(1 for c in search if c in candidate)
            return (matches / max(len(search), len(candidate))) * 0.5
        
        return 0.0
    
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
