from support_resistance_simple import SupportResistanceAnalyzer

analyzer = SupportResistanceAnalyzer()

# Test scan
print("Testing scan...")
opportunities = analyzer.scan_all_coins(15, 10, ['1h', '4h'], False)

print(f"\nFound {len(opportunities)} opportunities:")
for opp in opportunities:
    coin = opp['coin']
    print(f"\n{coin['name']}: ${coin['current_price']:.2f}")
    for o in opp['opportunities']:
        print(f"  {o['signal']} - {o['type']} at ${o['level']} ({o['distance_pct']:.1f}% away)")

# Test single coin
print("\n\nTesting Bitcoin analysis...")
analysis = analyzer.analyze_coin('bitcoin', 'Bitcoin', 'BTC', ['1h'])
if analysis['recommendations']:
    for rec in analysis['recommendations']:
        print(f"{rec['type']} - {rec['confidence']} - Entry: ${rec['entry_price']}")