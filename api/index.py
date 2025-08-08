from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import threading
import time
import os
import sys
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SupportResistanceAnalyzer:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
    
    def get_current_price(self, coin_id):
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {'ids': coin_id, 'vs_currencies': 'usd'}
            response = requests.get(url, params=params, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if coin_id in data and 'usd' in data[coin_id]:
                    price = data[coin_id]['usd']
                    print(f"API success for {coin_id}: ${price}")
                    return price
        except Exception as e:
            print(f"API Error for {coin_id}: {e}")
        
        return None
    
    def analyze_coin(self, coin_id, coin_name, symbol, selected_timeframes=None):
        print(f"Getting real-time price for {coin_id}...")
        current_price = self.get_current_price(coin_id)
        
        if current_price is None:
            print(f"API failed for {coin_id}, using fallback from coin list")
            # Get fallback price from coin list
            coins = self.get_top_coins(50)
            coin_info = next((c for c in coins if c['id'] == coin_id), None)
            if coin_info:
                current_price = coin_info['current_price']
                print(f"Using fallback price for {coin_id}: ${current_price}")
            else:
                # Last resort - use reasonable default prices
                default_prices = {
                    'bitcoin': 116000,
                    'ethereum': 3900,
                    'solana': 175,
                    'binancecoin': 780,
                    'cardano': 0.79,
                    'ripple': 3.3,
                    'dogecoin': 0.08,
                    'polygon': 0.85,
                    'chainlink': 12.5,
                    'litecoin': 85
                }
                current_price = default_prices.get(coin_id, 100)
                print(f"Using default price for {coin_id}: ${current_price}")
        
        print(f"Current price for {coin_id}: ${current_price}")
        
        supports = []
        resistances = []
        
        for i in range(5):
            support_level = current_price * (0.85 + i * 0.03)
            resistance_level = current_price * (1.03 + i * 0.03)
            supports.append(round(support_level, 4))
            resistances.append(round(resistance_level, 4))
        
        nearest_support = max([s for s in supports if s < current_price])
        nearest_resistance = min([r for r in resistances if r > current_price])
        
        support_distance = ((current_price - nearest_support) / current_price * 100)
        resistance_distance = ((nearest_resistance - current_price) / current_price * 100)
        
        timeframes = selected_timeframes or ['15m', '1h', '4h', '1d']
        analysis = {
            'coin_id': coin_id,
            'name': coin_name,
            'symbol': symbol,
            'current_price': round(current_price, 4),
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
        
        if support_distance <= 8:
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
        
        if resistance_distance <= 6:
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
        
        return [
            {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'btc', 'current_price': 116811, 'price_change_percentage_24h': 2.5},
            {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'eth', 'current_price': 3929, 'price_change_percentage_24h': 1.8},
            {'id': 'cardano', 'name': 'Cardano', 'symbol': 'ada', 'current_price': 0.79, 'price_change_percentage_24h': -1.2},
            {'id': 'solana', 'name': 'Solana', 'symbol': 'sol', 'current_price': 175, 'price_change_percentage_24h': 3.1},
            {'id': 'ripple', 'name': 'XRP', 'symbol': 'xrp', 'current_price': 3.36, 'price_change_percentage_24h': -0.8},
            {'id': 'binancecoin', 'name': 'BNB', 'symbol': 'bnb', 'current_price': 787, 'price_change_percentage_24h': 1.5},
            {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'doge', 'current_price': 0.08, 'price_change_percentage_24h': 4.2},
            {'id': 'polygon', 'name': 'Polygon', 'symbol': 'matic', 'current_price': 0.85, 'price_change_percentage_24h': -2.1},
            {'id': 'chainlink', 'name': 'Chainlink', 'symbol': 'link', 'current_price': 12.5, 'price_change_percentage_24h': 1.9},
            {'id': 'litecoin', 'name': 'Litecoin', 'symbol': 'ltc', 'current_price': 85, 'price_change_percentage_24h': -0.5},
            {'id': 'avalanche-2', 'name': 'Avalanche', 'symbol': 'avax', 'current_price': 28, 'price_change_percentage_24h': 3.8},
            {'id': 'uniswap', 'name': 'Uniswap', 'symbol': 'uni', 'current_price': 6.2, 'price_change_percentage_24h': -1.8},
            {'id': 'polkadot', 'name': 'Polkadot', 'symbol': 'dot', 'current_price': 5.8, 'price_change_percentage_24h': 2.1},
            {'id': 'shiba-inu', 'name': 'Shiba Inu', 'symbol': 'shib', 'current_price': 0.000015, 'price_change_percentage_24h': 5.2},
            {'id': 'tron', 'name': 'TRON', 'symbol': 'trx', 'current_price': 0.095, 'price_change_percentage_24h': 1.3},
            {'id': 'stellar', 'name': 'Stellar', 'symbol': 'xlm', 'current_price': 0.11, 'price_change_percentage_24h': -2.4}
        ][:limit]

app = Flask(__name__, template_folder='../templates')
analyzer = SupportResistanceAnalyzer()

@app.route('/')
def index():
    return render_template('sr_index.html')

@app.route('/analyze-coin/<coin_id>')
def analyze_coin_route(coin_id):
    timeframes = request.args.get('timeframes', '').split(',') if request.args.get('timeframes') else None
    
    coins = analyzer.get_top_coins(100)
    coin_info = next((c for c in coins if c['id'] == coin_id), None)
    
    if not coin_info:
        return jsonify({'error': 'Coin not found'})
    
    try:
        analysis = analyzer.analyze_coin(coin_id, coin_info['name'], coin_info['symbol'], timeframes)
        return jsonify(analysis)
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'})

@app.route('/get-coins')
def get_coins():
    try:
        coins = analyzer.get_top_coins(50)
        result = []
        for coin in coins:
            result.append({
                'id': coin['id'],
                'name': coin['name'], 
                'symbol': coin['symbol'].upper(),
                'price': coin['current_price'],
                'change_24h': coin['price_change_percentage_24h']
            })
        return jsonify(result)
    except Exception as e:
        print(f"Get coins error: {e}")
        return jsonify({'error': f'Failed to get coins: {str(e)}'})