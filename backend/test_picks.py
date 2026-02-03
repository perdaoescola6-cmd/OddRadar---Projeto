"""Test picks engine"""
import asyncio
import sys
sys.path.insert(0, '.')
from picks_engine import picks_engine

async def test():
    result = await picks_engine.get_daily_picks('both', False)
    picks = result.get('picks', [])
    print(f"Total picks: {len(picks)}")
    print(f"Meta: {result.get('meta')}")
    print("\n=== PICKS ===")
    for p in picks:
        print(f"\n{p['home_team']} vs {p['away_team']}")
        print(f"  Liga: {p['league']} | Data: {p['date']}")
        print(f"  Jogos analisados: {p['games_analyzed']}")
        for pick in p['picks']:
            print(f"  -> {pick['market']}: {pick['confidence']}% ({pick['confidence_level']})")
            print(f"     {pick['justification']}")

asyncio.run(test())
