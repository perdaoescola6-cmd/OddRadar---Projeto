import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from football_api import FootballAPI
    api = FootballAPI()
    
    search_terms = [
        "St Pauli",
        "Pauli",
        "Sankt Pauli",
        "Hamburg St Pauli",
    ]
    
    for term in search_terms:
        print(f"\nSearching: '{term}'")
        teams = await api.search_teams(term)
        print(f"  Found {len(teams)} teams")
        for t in teams[:3]:
            team_info = t.get("team", t)
            name = team_info.get("name")
            team_id = team_info.get("id")
            print(f"    - {name} (ID: {team_id})")

if __name__ == "__main__":
    asyncio.run(test())
