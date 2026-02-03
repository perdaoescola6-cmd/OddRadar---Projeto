"""
Script para testar se a API suporta jogos futuros (fixtures)
"""
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(dotenv_path='../.env')

api_key = os.getenv('APISPORTS_KEY')
base_url = 'https://v3.football.api-sports.io'
headers = {'x-apisports-key': api_key}

FLAMENGO_ID = 127
INTERNACIONAL_ID = 119
BRASILEIRAO_ID = 71  # Serie A Brazil

def test_fixtures_next(team_id, team_name, count=10):
    """Teste: Fixtures FUTUROS por time (next=N)"""
    print(f"\n{'='*60}")
    print(f"TESTE: Fixtures FUTUROS de {team_name} (next={count})")
    print(f"Endpoint: /fixtures?team={team_id}&next={count}")
    print('='*60)
    
    response = httpx.get(f'{base_url}/fixtures', headers=headers, params={'team': team_id, 'next': count})
    data = response.json()
    fixtures = data.get('response', [])
    
    print(f"Status: {response.status_code}")
    print(f"Total de fixtures retornados: {len(fixtures)}")
    
    if fixtures:
        print("\nPróximos jogos:")
        for f in fixtures[:5]:
            fixture = f.get('fixture', {})
            teams = f.get('teams', {})
            league = f.get('league', {})
            date = fixture.get('date', '')[:10]
            home = teams.get('home', {}).get('name', '?')
            away = teams.get('away', {}).get('name', '?')
            comp = league.get('name', '?')
            print(f"  {date} | {home} x {away} | {comp}")
    
    return fixtures

def test_fixtures_by_date(date_str):
    """Teste: Fixtures por DATA específica"""
    print(f"\n{'='*60}")
    print(f"TESTE: Fixtures por DATA ({date_str})")
    print(f"Endpoint: /fixtures?date={date_str}")
    print('='*60)
    
    response = httpx.get(f'{base_url}/fixtures', headers=headers, params={'date': date_str})
    data = response.json()
    fixtures = data.get('response', [])
    
    print(f"Status: {response.status_code}")
    print(f"Total de fixtures retornados: {len(fixtures)}")
    
    # Filtrar jogos brasileiros
    brazil_fixtures = [f for f in fixtures if f.get('league', {}).get('country') == 'Brazil']
    print(f"Jogos no Brasil: {len(brazil_fixtures)}")
    
    if brazil_fixtures:
        print("\nJogos no Brasil:")
        for f in brazil_fixtures[:10]:
            fixture = f.get('fixture', {})
            teams = f.get('teams', {})
            league = f.get('league', {})
            home = teams.get('home', {}).get('name', '?')
            away = teams.get('away', {}).get('name', '?')
            comp = league.get('name', '?')
            print(f"  {home} x {away} | {comp}")
    
    return fixtures

def test_fixtures_by_league(league_id, season=2025):
    """Teste: Fixtures por LIGA"""
    print(f"\n{'='*60}")
    print(f"TESTE: Fixtures do Brasileirão (league={league_id}, season={season})")
    print(f"Endpoint: /fixtures?league={league_id}&season={season}")
    print('='*60)
    
    response = httpx.get(f'{base_url}/fixtures', headers=headers, params={'league': league_id, 'season': season})
    data = response.json()
    fixtures = data.get('response', [])
    
    print(f"Status: {response.status_code}")
    print(f"Total de fixtures retornados: {len(fixtures)}")
    
    # Separar futuros e passados
    now = datetime.now()
    future = []
    past = []
    
    for f in fixtures:
        date_str = f.get('fixture', {}).get('date', '')
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if date.replace(tzinfo=None) > now:
                future.append(f)
            else:
                past.append(f)
        except:
            pass
    
    print(f"Jogos FUTUROS: {len(future)}")
    print(f"Jogos PASSADOS: {len(past)}")
    
    if future:
        print("\nPróximos jogos do Brasileirão:")
        for f in future[:10]:
            fixture = f.get('fixture', {})
            teams = f.get('teams', {})
            date = fixture.get('date', '')[:10]
            home = teams.get('home', {}).get('name', '?')
            away = teams.get('away', {}).get('name', '?')
            print(f"  {date} | {home} x {away}")
    
    return fixtures, future, past

def test_head_to_head(team1_id, team2_id, team1_name, team2_name):
    """Teste: Head to Head (H2H)"""
    print(f"\n{'='*60}")
    print(f"TESTE: Head to Head ({team1_name} x {team2_name})")
    print(f"Endpoint: /fixtures/headtohead?h2h={team1_id}-{team2_id}")
    print('='*60)
    
    response = httpx.get(f'{base_url}/fixtures/headtohead', headers=headers, params={'h2h': f'{team1_id}-{team2_id}'})
    data = response.json()
    fixtures = data.get('response', [])
    
    print(f"Status: {response.status_code}")
    print(f"Total de confrontos: {len(fixtures)}")
    
    # Separar futuros e passados
    now = datetime.now()
    future = []
    past = []
    
    for f in fixtures:
        date_str = f.get('fixture', {}).get('date', '')
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if date.replace(tzinfo=None) > now:
                future.append(f)
            else:
                past.append(f)
        except:
            pass
    
    print(f"Confrontos FUTUROS: {len(future)}")
    print(f"Confrontos PASSADOS: {len(past)}")
    
    if future:
        print("\nPróximos confrontos:")
        for f in future[:5]:
            fixture = f.get('fixture', {})
            teams = f.get('teams', {})
            league = f.get('league', {})
            date = fixture.get('date', '')[:16].replace('T', ' ')
            home = teams.get('home', {}).get('name', '?')
            away = teams.get('away', {}).get('name', '?')
            comp = league.get('name', '?')
            print(f"  {date} | {home} x {away} | {comp}")
    
    return fixtures, future, past

def search_flamengo_x_internacional():
    """Buscar especificamente Flamengo x Internacional"""
    print(f"\n{'='*60}")
    print("BUSCA ESPECÍFICA: Flamengo x Internacional (04/02)")
    print('='*60)
    
    # Método 1: Fixtures futuros do Flamengo
    print("\n1. Buscando nos próximos jogos do Flamengo...")
    response = httpx.get(f'{base_url}/fixtures', headers=headers, params={'team': FLAMENGO_ID, 'next': 20})
    flamengo_fixtures = response.json().get('response', [])
    
    found = None
    for f in flamengo_fixtures:
        teams = f.get('teams', {})
        home = teams.get('home', {})
        away = teams.get('away', {})
        if home.get('id') == INTERNACIONAL_ID or away.get('id') == INTERNACIONAL_ID:
            found = f
            break
    
    if found:
        fixture = found.get('fixture', {})
        teams = found.get('teams', {})
        league = found.get('league', {})
        print(f"\n✅ ENCONTRADO!")
        print(f"   Data: {fixture.get('date')}")
        print(f"   {teams.get('home', {}).get('name')} x {teams.get('away', {}).get('name')}")
        print(f"   Competição: {league.get('name')}")
        print(f"   Status: {fixture.get('status', {}).get('long')}")
    else:
        print("\n❌ Não encontrado nos próximos 20 jogos do Flamengo")
    
    # Método 2: Fixtures por data
    print("\n2. Buscando por data (2026-02-04)...")
    response = httpx.get(f'{base_url}/fixtures', headers=headers, params={'date': '2026-02-04'})
    date_fixtures = response.json().get('response', [])
    
    for f in date_fixtures:
        teams = f.get('teams', {})
        home = teams.get('home', {})
        away = teams.get('away', {})
        if (home.get('id') == FLAMENGO_ID and away.get('id') == INTERNACIONAL_ID) or \
           (home.get('id') == INTERNACIONAL_ID and away.get('id') == FLAMENGO_ID):
            fixture = f.get('fixture', {})
            league = f.get('league', {})
            print(f"\n✅ ENCONTRADO na data!")
            print(f"   Data: {fixture.get('date')}")
            print(f"   {home.get('name')} x {away.get('name')}")
            print(f"   Competição: {league.get('name')}")
            return True
    
    print("   Não encontrado na data 04/02")
    return found is not None

if __name__ == '__main__':
    print("\n" + "="*60)
    print("VALIDAÇÃO: API SUPORTA JOGOS FUTUROS?")
    print("="*60)
    
    # Teste 1: Fixtures futuros do Flamengo
    test_fixtures_next(FLAMENGO_ID, "Flamengo")
    
    # Teste 2: Fixtures futuros do Internacional
    test_fixtures_next(INTERNACIONAL_ID, "Internacional")
    
    # Teste 3: Fixtures por data (amanhã)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    test_fixtures_by_date(tomorrow)
    
    # Teste 4: Fixtures por data específica (04/02/2026)
    test_fixtures_by_date('2026-02-04')
    
    # Teste 5: Head to Head
    test_head_to_head(FLAMENGO_ID, INTERNACIONAL_ID, "Flamengo", "Internacional")
    
    # Teste 6: Busca específica
    search_flamengo_x_internacional()
    
    print("\n" + "="*60)
    print("FIM DOS TESTES")
    print("="*60)
