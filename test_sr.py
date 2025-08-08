from support_resistance import SupportResistanceAnalyzer

# Test the analyzer
analyzer = SupportResistanceAnalyzer()

# Test single coin
print("Testing Bitcoin analysis...")
analysis = analyzer.analyze_coin('bitcoin', 'Bitcoin', 'BTC', ['1h', '4h'])

if analysis:
    print(f"Current price: ${analysis['current_price']}")
    for tf, data in analysis['timeframes'].items():
        print(f"\n{tf} timeframe:")
        print(f"  Supports: {data['supports']}")
        print(f"  Resistances: {data['resistances']}")
        print(f"  Nearest support: {data['nearest_support']} ({data['support_distance_pct']}% away)")
        print(f"  Nearest resistance: {data['nearest_resistance']} ({data['resistance_distance_pct']}% away)")

# Test scanning
print("\n\nTesting opportunity scan...")
opportunities = analyzer.scan_all_coins(15, 10, ['1h'], False)
print(f"Found {len(opportunities)} opportunities")

for opp in opportunities[:3]:  # Show first 3
    coin = opp['coin']
    print(f"\n{coin['name']}: ${coin['current_price']}")
    for o in opp['opportunities']:
        print(f"  {o['signal']} - {o['type']} at ${o['level']} ({o['distance_pct']}% away) - {o['timeframe']}")