from support_resistance_simple import SupportResistanceAnalyzer

analyzer = SupportResistanceAnalyzer()

# Test real-time prices
print("Testing real-time prices...")

coins_to_test = ['bitcoin', 'ethereum', 'cardano', 'solana']

for coin_id in coins_to_test:
    price = analyzer.get_current_price(coin_id)
    print(f"{coin_id}: ${price}")

print("\nTesting top coins API...")
coins = analyzer.get_top_coins(5)
for coin in coins[:3]:
    print(f"{coin['name']}: ${coin['current_price']}")

print("\nTesting analysis with real prices...")
analysis = analyzer.analyze_coin('ethereum', 'Ethereum', 'ETH', ['1h'])
print(f"ETH Current Price: ${analysis['current_price']}")
print(f"Recommendations: {len(analysis['recommendations'])}")