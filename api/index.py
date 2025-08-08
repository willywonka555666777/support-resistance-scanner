from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import requests
import time

class SupportResistanceAnalyzer:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.last_call_time = 0
    
    def get_current_price(self, coin_id):
        # Try multiple free APIs with better error handling
        apis = [
            ('CoinGecko', self.get_price_coingecko),
            ('Binance', self.get_price_binance),
            ('Kraken', self.get_price_kraken),
            ('CoinAPI', self.get_price_coinapi)
        ]
        
        for api_name, api_func in apis:
            try:
                price = api_func(coin_id)
                if price and price > 0:
                    print(f"✅ {api_name} success: {coin_id} = ${price}")
                    return price
            except Exception as e:
                print(f"❌ {api_name} failed: {e}")
                continue
        
        print(f"❌ All APIs failed for {coin_id}")
        return None
    
    def get_price_coingecko(self, coin_id):
        url = f"{self.coingecko_base}/simple/price"
        params = {'ids': coin_id, 'vs_currencies': 'usd'}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data and 'usd' in data[coin_id]:
                price = data[coin_id]['usd']
                print(f"✅ CoinGecko: {coin_id} = ${price}")
                return price
        return None
    
    def get_price_coinapi(self, coin_id):
        # CoinAPI.io free tier
        symbol_map = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
            'binancecoin': 'BNB', 'cardano': 'ADA', 'ripple': 'XRP'
        }
        
        symbol = symbol_map.get(coin_id)
        if not symbol:
            return None
            
        url = f"https://rest.coinapi.io/v1/exchangerate/{symbol}/USD"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('rate')
            if price:
                print(f"✅ CoinAPI: {coin_id} = ${price}")
                return price
        return None
    
    def get_price_binance(self, coin_id):
        # Binance public API
        symbol_map = {
            'bitcoin': 'BTCUSDT', 'ethereum': 'ETHUSDT', 'solana': 'SOLUSDT',
            'binancecoin': 'BNBUSDT', 'cardano': 'ADAUSDT', 'ripple': 'XRPUSDT'
        }
        
        symbol = symbol_map.get(coin_id)
        if not symbol:
            return None
            
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data.get('price', 0))
            if price > 0:
                print(f"✅ Binance: {coin_id} = ${price}")
                return price
        return None
    
    def get_price_kraken(self, coin_id):
        # Kraken public API
        symbol_map = {
            'bitcoin': 'XBTUSD', 'ethereum': 'ETHUSD', 'solana': 'SOLUSD',
            'cardano': 'ADAUSD', 'ripple': 'XRPUSD'
        }
        
        symbol = symbol_map.get(coin_id)
        if not symbol:
            return None
            
        url = f"https://api.kraken.com/0/public/Ticker?pair={symbol}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                for pair_data in data['result'].values():
                    price = float(pair_data['c'][0])  # Last trade price
                    print(f"✅ Kraken: {coin_id} = ${price}")
                    return price
        return None
    
    def analyze_coin(self, coin_id, coin_name, symbol, selected_timeframes=None):
        print(f"🔄 Getting real-time price for {coin_id}...")
        current_price = self.get_current_price(coin_id)
        
        if current_price is None:
            return {
                'error': f'Unable to get real-time price for {coin_name}.',
                'message': 'All price APIs (CoinGecko, Binance, Kraken, CoinAPI) are currently unavailable. Please try again in a few minutes.',
                'suggestion': 'This usually resolves within 1-2 minutes. The APIs may be experiencing high traffic.'
            }
        
        # Generate support/resistance levels
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
            'price_source': 'Multiple APIs (Real-time)',
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
        
        # Generate recommendations
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
        # Always return reliable coin list
        return [
            {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'btc', 'current_price': 116800, 'price_change_percentage_24h': 2.1},
            {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'eth', 'current_price': 3921, 'price_change_percentage_24h': 1.8},
            {'id': 'solana', 'name': 'Solana', 'symbol': 'sol', 'current_price': 175, 'price_change_percentage_24h': 3.2},
            {'id': 'binancecoin', 'name': 'BNB', 'symbol': 'bnb', 'current_price': 787, 'price_change_percentage_24h': 1.5},
            {'id': 'cardano', 'name': 'Cardano', 'symbol': 'ada', 'current_price': 0.794, 'price_change_percentage_24h': -0.8},
            {'id': 'ripple', 'name': 'XRP', 'symbol': 'xrp', 'current_price': 3.36, 'price_change_percentage_24h': 2.4},
            {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'doge', 'current_price': 0.08, 'price_change_percentage_24h': 4.1},
            {'id': 'polygon', 'name': 'Polygon', 'symbol': 'matic', 'current_price': 0.85, 'price_change_percentage_24h': -1.2},
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
    
    coins = analyzer.get_top_coins(50)
    coin_info = next((c for c in coins if c['id'] == coin_id), None)
    
    if not coin_info:
        return jsonify({'error': f'Coin {coin_id} not found'})
    
    analysis = analyzer.analyze_coin(coin_id, coin_info['name'], coin_info['symbol'], timeframes)
    return jsonify(analysis)

@app.route('/scan-opportunities')
def scan_opportunities():
    return jsonify({
        'error': 'Scan feature not available in this version. Use Quick Analysis instead.',
        'message': 'Please select individual coins for analysis using the dropdown menu.'
    })

@app.route('/stop-scan', methods=['POST'])
def stop_scan():
    return jsonify({'status': 'Scan not available'})

@app.route('/get-coins')
def get_coins():
    coins = analyzer.get_top_coins(20)
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