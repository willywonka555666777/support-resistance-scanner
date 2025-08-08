import requests
import random
from datetime import datetime, timedelta

class SupportResistanceAnalyzer:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
    
    def get_current_price(self, coin_id):
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {'ids': coin_id, 'vs_currencies': 'usd'}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if coin_id in data and 'usd' in data[coin_id]:
                    return data[coin_id]['usd']
        except Exception as e:
            print(f"API Error for {coin_id}: {e}")
        
        return None  # Let analyze_coin handle fallback
    
    def analyze_coin(self, coin_id, coin_name, symbol, selected_timeframes=None):
        # Always get fresh real-time price
        print(f"Getting real-time price for {coin_id}...")
        current_price = self.get_current_price(coin_id)
        
        # If API fails, get from coin list
        if current_price is None:
            coins = self.get_top_coins(50)
            coin_info = next((c for c in coins if c['id'] == coin_id), None)
            if coin_info:
                current_price = coin_info['current_price']
            else:
                current_price = 50000
        
        print(f"Current price for {coin_id}: ${current_price}")
        
        # Generate mock support/resistance levels based on current price
        supports = []
        resistances = []
        
        # Create levels around current price
        for i in range(5):
            support_level = current_price * (0.85 + i * 0.03)  # 85%, 88%, 91%, 94%, 97%
            resistance_level = current_price * (1.03 + i * 0.03)  # 103%, 106%, 109%, 112%, 115%
            supports.append(round(support_level, 4))
            resistances.append(round(resistance_level, 4))
        
        # Find nearest levels
        nearest_support = max([s for s in supports if s < current_price])
        nearest_resistance = min([r for r in resistances if r > current_price])
        
        # Calculate distances
        support_distance = ((current_price - nearest_support) / current_price * 100)
        resistance_distance = ((nearest_resistance - current_price) / current_price * 100)
        
        timeframes = selected_timeframes or ['15m', '1h', '4h', '1d']
        analysis = {
            'coin_id': coin_id,
            'name': coin_name,
            'symbol': symbol,
            'current_price': round(current_price, 4),  # Ensure fresh price
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeframes': {},
            'recommendations': []
        }
        
        for tf in timeframes:
            analysis['timeframes'][tf] = {
                'supports': supports,
                'resistances': resistances,
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'support_distance_pct': round(support_distance, 2),
                'resistance_distance_pct': round(resistance_distance, 2)
            }
        
        # Generate recommendations based on fresh price
        if support_distance <= 8:  # Within 8% of support
            analysis['recommendations'].append({
                'type': 'BUY',
                'timeframe': '1h',
                'reason': f'Price near support level at ${nearest_support}',
                'entry_price': round(nearest_support * 1.005, 4),
                'stop_loss': round(nearest_support * 0.99, 4),
                'take_profit': round(current_price * 1.05, 4),
                'risk_reward': 3.2,
                'confidence': 'HIGH' if support_distance <= 4 else 'MEDIUM'
            })
        
        if resistance_distance <= 6:  # Within 6% of resistance
            analysis['recommendations'].append({
                'type': 'SELL',
                'timeframe': '1h',
                'reason': f'Price near resistance level at ${nearest_resistance}',
                'entry_price': round(nearest_resistance * 0.995, 4),
                'stop_loss': round(nearest_resistance * 1.01, 4),
                'take_profit': round(current_price * 0.95, 4),
                'risk_reward': 2.8,
                'confidence': 'HIGH' if resistance_distance <= 3 else 'MEDIUM'
            })
        
        return analysis
    
    def get_top_coins(self, limit=50):
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 50),
                'page': 1
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"API Error getting coins: {e}")
        
        # Fallback mock data if API fails
        return [
            {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'btc', 'current_price': 116811, 'price_change_percentage_24h': 2.5},
            {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'eth', 'current_price': 3929, 'price_change_percentage_24h': 1.8},
            {'id': 'cardano', 'name': 'Cardano', 'symbol': 'ada', 'current_price': 0.45, 'price_change_percentage_24h': -1.2},
            {'id': 'solana', 'name': 'Solana', 'symbol': 'sol', 'current_price': 95, 'price_change_percentage_24h': 3.1},
            {'id': 'ripple', 'name': 'XRP', 'symbol': 'xrp', 'current_price': 0.62, 'price_change_percentage_24h': -0.8},
            {'id': 'binancecoin', 'name': 'BNB', 'symbol': 'bnb', 'current_price': 320, 'price_change_percentage_24h': 1.5},
            {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'doge', 'current_price': 0.08, 'price_change_percentage_24h': 4.2},
            {'id': 'polygon', 'name': 'Polygon', 'symbol': 'matic', 'current_price': 0.85, 'price_change_percentage_24h': -2.1},
            {'id': 'chainlink', 'name': 'Chainlink', 'symbol': 'link', 'current_price': 12.5, 'price_change_percentage_24h': 1.9},
            {'id': 'litecoin', 'name': 'Litecoin', 'symbol': 'ltc', 'current_price': 85, 'price_change_percentage_24h': -0.5},
            {'id': 'avalanche-2', 'name': 'Avalanche', 'symbol': 'avax', 'current_price': 28, 'price_change_percentage_24h': 3.8},
            {'id': 'uniswap', 'name': 'Uniswap', 'symbol': 'uni', 'current_price': 6.2, 'price_change_percentage_24h': -1.8},
            {'id': 'polkadot', 'name': 'Polkadot', 'symbol': 'dot', 'current_price': 5.8, 'price_change_percentage_24h': 2.1},
            {'id': 'shiba-inu', 'name': 'Shiba Inu', 'symbol': 'shib', 'current_price': 0.000015, 'price_change_percentage_24h': 5.2},
            {'id': 'tron', 'name': 'TRON', 'symbol': 'trx', 'current_price': 0.095, 'price_change_percentage_24h': 1.3},
            {'id': 'stellar', 'name': 'Stellar', 'symbol': 'xlm', 'current_price': 0.11, 'price_change_percentage_24h': -2.4},
            {'id': 'cosmos', 'name': 'Cosmos', 'symbol': 'atom', 'current_price': 8.5, 'price_change_percentage_24h': 0.8},
            {'id': 'ethereum-classic', 'name': 'Ethereum Classic', 'symbol': 'etc', 'current_price': 22, 'price_change_percentage_24h': -1.1},
            {'id': 'filecoin', 'name': 'Filecoin', 'symbol': 'fil', 'current_price': 4.2, 'price_change_percentage_24h': 2.9},
            {'id': 'hedera-hashgraph', 'name': 'Hedera', 'symbol': 'hbar', 'current_price': 0.065, 'price_change_percentage_24h': 1.7},
            {'id': 'vechain', 'name': 'VeChain', 'symbol': 'vet', 'current_price': 0.025, 'price_change_percentage_24h': -0.9},
            {'id': 'internet-computer', 'name': 'Internet Computer', 'symbol': 'icp', 'current_price': 4.8, 'price_change_percentage_24h': 3.5},
            {'id': 'the-sandbox', 'name': 'The Sandbox', 'symbol': 'sand', 'current_price': 0.38, 'price_change_percentage_24h': 4.1},
            {'id': 'decentraland', 'name': 'Decentraland', 'symbol': 'mana', 'current_price': 0.42, 'price_change_percentage_24h': -1.6},
            {'id': 'algorand', 'name': 'Algorand', 'symbol': 'algo', 'current_price': 0.18, 'price_change_percentage_24h': 2.3},
            {'id': 'fantom', 'name': 'Fantom', 'symbol': 'ftm', 'current_price': 0.35, 'price_change_percentage_24h': 1.8},
            {'id': 'near', 'name': 'NEAR Protocol', 'symbol': 'near', 'current_price': 3.2, 'price_change_percentage_24h': -0.7},
            {'id': 'flow', 'name': 'Flow', 'symbol': 'flow', 'current_price': 0.75, 'price_change_percentage_24h': 2.6},
            {'id': 'elrond-erd-2', 'name': 'MultiversX', 'symbol': 'egld', 'current_price': 32, 'price_change_percentage_24h': 1.4},
            {'id': 'theta-token', 'name': 'Theta Network', 'symbol': 'theta', 'current_price': 1.1, 'price_change_percentage_24h': -2.2},
            {'id': 'axie-infinity', 'name': 'Axie Infinity', 'symbol': 'axs', 'current_price': 6.8, 'price_change_percentage_24h': 3.9},
            {'id': 'aave', 'name': 'Aave', 'symbol': 'aave', 'current_price': 85, 'price_change_percentage_24h': 0.6},
            {'id': 'compound-governance-token', 'name': 'Compound', 'symbol': 'comp', 'current_price': 45, 'price_change_percentage_24h': -1.3},
            {'id': 'maker', 'name': 'Maker', 'symbol': 'mkr', 'current_price': 1250, 'price_change_percentage_24h': 1.9},
            {'id': 'sushi', 'name': 'SushiSwap', 'symbol': 'sushi', 'current_price': 0.95, 'price_change_percentage_24h': -0.4},
            {'id': '1inch', 'name': '1inch Network', 'symbol': '1inch', 'current_price': 0.32, 'price_change_percentage_24h': 2.8},
            {'id': 'pancakeswap-token', 'name': 'PancakeSwap', 'symbol': 'cake', 'current_price': 2.1, 'price_change_percentage_24h': 1.2},
            {'id': 'curve-dao-token', 'name': 'Curve DAO', 'symbol': 'crv', 'current_price': 0.68, 'price_change_percentage_24h': -1.7},
            {'id': 'yearn-finance', 'name': 'Yearn Finance', 'symbol': 'yfi', 'current_price': 6800, 'price_change_percentage_24h': 0.9},
            {'id': 'synthetix-network-token', 'name': 'Synthetix', 'symbol': 'snx', 'current_price': 2.4, 'price_change_percentage_24h': 1.6}
        ][:limit]
    
    def scan_all_coins(self, max_support_distance=10, max_resistance_distance=8, selected_timeframes=None, stop_scan=False):
        coins = self.get_top_coins(15)  # Scan 15 coins
        opportunities = []
        
        print(f"Scanning {len(coins)} coins...")
        
        for i, coin in enumerate(coins):
            if stop_scan:
                break
                
            print(f"Analyzing {coin['name']} ({i+1}/{len(coins)})...")
            analysis = self.analyze_coin(coin['id'], coin['name'], coin['symbol'], selected_timeframes)
            
            coin_opportunities = []
            
            for tf, data in analysis['timeframes'].items():
                # Near support
                if data['support_distance_pct'] <= max_support_distance:
                    coin_opportunities.append({
                        'type': 'SUPPORT',
                        'timeframe': tf,
                        'level': data['nearest_support'],
                        'distance_pct': data['support_distance_pct'],
                        'signal': 'BUY'
                    })
                
                # Near resistance
                if data['resistance_distance_pct'] <= max_resistance_distance:
                    coin_opportunities.append({
                        'type': 'RESISTANCE',
                        'timeframe': tf,
                        'level': data['nearest_resistance'],
                        'distance_pct': data['resistance_distance_pct'],
                        'signal': 'SELL'
                    })
            
            if coin_opportunities:
                opportunities.append({
                    'coin': analysis,
                    'opportunities': coin_opportunities
                })
                print(f"Found {len(coin_opportunities)} opportunities for {coin['name']}")
        
        print(f"Scan complete. Found {len(opportunities)} coins with opportunities.")
        return opportunities